"""Hora del servidor de MT5 -> UTC: reglas documentadas, conversion vectorizada y deteccion del desfase.

MT5 devuelve las marcas (`time` de velas y ticks, `time_msc` de ticks) como segundos/ms desde 1970 en la HORA DEL SERVIDOR
del broker, escrita como si fuera UTC. La mayoria de brokers de FX usan "Nueva York + 7 h": el cierre de las 17:00 de NY cae
a las 00:00 del servidor todo el ano, asi que el servidor esta en UTC+2 en el invierno de EE. UU. y en UTC+3 en su verano.

Reglas (`--regla`):
- `ny+7` (por defecto): UTC+2, y UTC+3 mientras rige el horario de verano de EE. UU.: desde 2007, del segundo domingo de
  marzo a las 02:00 EST (07:00 UTC) al primer domingo de noviembre a las 02:00 EDT (06:00 UTC); 1987-2006, del primer
  domingo de abril al ultimo de octubre; antes de 1987, del ultimo domingo de abril al ultimo de octubre (se ignoran las
  excepciones de 1974-1975).
- `ue+2`: UTC+2, y UTC+3 con el horario de verano de la UE (ultimo domingo de marzo a ultimo de octubre, 01:00 UTC); la
  regla de 1996 se aplica a todos los anos.
- `fija:+N`: desfase constante de N horas.

Ambiguedades (solo con reglas con verano y solo si hay datos en esas horas, p. ej. cripto que cotiza en fin de semana):
la hora del servidor que se repite al volver al horario de invierno (08:00-08:59 del domingo con `ny+7`) se resuelve como
la PRIMERA aparicion (aun en verano); la que no existe al pasar al verano (09:00-09:59 del domingo con `ny+7`) se convierte
con el desfase de invierno. Ambas se cuentan y se declaran en el manifest.

Deteccion del desfase (dos metodos, ninguno toca credenciales):
1. En vivo: la marca del ultimo tick (`symbol_info_tick`) menos el reloj UTC, redondeada a media hora, si el mercado de FX
   esta abierto y el residuo es de menos de 5 min (tick fresco).
2. Historica (solo simbolos de FX): el cierre del viernes. Con cada regla candidata, el fin de la ultima vela antes de
   cada hueco de fin de semana se lleva a la hora de Nueva York; la coherencia de la regla es la fraccion de semanas que
   cierran a las 17:00 NY. La correcta da 17:00 en verano y en invierno (una regla fija equivocada acierta solo en una
   de las dos estaciones; una fija desplazada no acierta nunca).
"""
from __future__ import annotations

import datetime as dt
import re

import numpy as np

H = 3600
DIA = 86400
UTC = dt.timezone.utc
ANIO_MIN, ANIO_MAX = 1900, 2199


def _domingo(anio: int, mes: int, n: int) -> dt.date:
    """n-esimo domingo del mes (n >= 1) o el ultimo (n = -1)."""
    if n > 0:
        d = dt.date(anio, mes, 1)
        return d + dt.timedelta(days=(6 - d.weekday()) % 7 + 7 * (n - 1))
    sig = dt.date(anio + (mes == 12), mes % 12 + 1, 1)
    d = sig - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def _s(fecha: dt.date, hora_utc: int) -> int:
    return int(dt.datetime(fecha.year, fecha.month, fecha.day, tzinfo=UTC).timestamp()) + hora_utc * H


def verano_ee_uu(anio: int) -> tuple[int, int]:
    """[inicio, fin) del horario de verano de EE. UU. en segundos UTC."""
    if anio >= 2007:
        a, b = _domingo(anio, 3, 2), _domingo(anio, 11, 1)
    elif anio >= 1987:
        a, b = _domingo(anio, 4, 1), _domingo(anio, 10, -1)
    else:
        a, b = _domingo(anio, 4, -1), _domingo(anio, 10, -1)
    return _s(a, 7), _s(b, 6)  # 02:00 EST = 07:00 UTC; 02:00 EDT = 06:00 UTC


def verano_ue(anio: int) -> tuple[int, int]:
    return _s(_domingo(anio, 3, -1), 1), _s(_domingo(anio, 10, -1), 1)


def anio_de(s: np.ndarray) -> np.ndarray:
    return s.astype("datetime64[s]").astype("datetime64[Y]").astype(np.int64) + 1970


class Regla:
    """Desfase servidor - UTC: `base_s`, mas una hora mientras rige el verano de `verano` (None: fija)."""

    def __init__(self, nombre: str, base_s: int, verano=None) -> None:
        self.nombre, self.base_s, self.con_verano = nombre, int(base_s), verano is not None
        if verano is not None:
            tabla = [verano(a) for a in range(ANIO_MIN, ANIO_MAX + 1)]
            self._ini = np.array([t[0] for t in tabla], dtype=np.int64)
            self._fin = np.array([t[1] for t in tabla], dtype=np.int64)

    def en_verano(self, u) -> np.ndarray:
        u = np.asarray(u, dtype=np.int64)
        if not self.con_verano:
            return np.zeros(u.shape, dtype=bool)
        i = np.clip(anio_de(u) - ANIO_MIN, 0, ANIO_MAX - ANIO_MIN)
        return (u >= self._ini[i]) & (u < self._fin[i])

    def desfase(self, u) -> np.ndarray:
        """Desfase en segundos (servidor - UTC) en los instantes UTC `u` (segundos)."""
        return self.base_s + H * self.en_verano(u).astype(np.int64)

    def utc_a_servidor(self, u: int) -> int:
        return int(u) + int(self.desfase(np.array([u]))[0])

    def servidor_a_utc(self, s) -> tuple[np.ndarray, np.ndarray, int, int]:
        """Segundos de servidor -> (segundos UTC, desfase aplicado, n ambiguas, n inexistentes)."""
        s = np.asarray(s, dtype=np.int64)
        if not self.con_verano:
            return s - self.base_s, np.full(s.shape, self.base_s, dtype=np.int64), 0, 0
        u_ver, u_inv = s - (self.base_s + H), s - self.base_s
        ok_ver, ok_inv = self.en_verano(u_ver), ~self.en_verano(u_inv)
        u = np.where(ok_ver, u_ver, u_inv)
        return u, s - u, int(np.count_nonzero(ok_ver & ok_inv)), int(np.count_nonzero(~ok_ver & ~ok_inv))

    def servidor_ms_a_utc_ms(self, s_ms) -> tuple[np.ndarray, np.ndarray, int, int]:
        s_ms = np.asarray(s_ms, dtype=np.int64)
        _, d, amb, inex = self.servidor_a_utc(np.floor_divide(s_ms, 1000))
        return s_ms - d * 1000, d, amb, inex

    def describir(self) -> dict:
        return {"regla": self.nombre, "desfase_base_h": self.base_s / H, "verano": self.con_verano}


NUEVA_YORK = Regla("nueva_york", -5 * H, verano_ee_uu)  # hora local de NY, para el metodo del cierre del viernes
REGLA_DEFECTO = "ny+7"


def regla_desde_texto(txt: str) -> Regla:
    if txt == "ny+7":
        return Regla("ny+7", 2 * H, verano_ee_uu)
    if txt == "ue+2":
        return Regla("ue+2", 2 * H, verano_ue)
    m = re.fullmatch(r"fija:([+-]\d{1,2})", txt)
    if m and -12 <= int(m.group(1)) <= 14:
        return Regla(f"fija:{int(m.group(1)):+d}", int(m.group(1)) * H)
    raise ValueError(f"regla de hora desconocida {txt!r}: usa ny+7, ue+2 o fija:+N")


CANDIDATAS = ("ny+7", "ue+2", "fija:+2", "fija:+3")
CIERRE_FX_NY_MIN = 17 * 60  # el FX cierra el viernes a las 17:00 de Nueva York


def fx_abierto(ahora_utc_s: int) -> bool:
    """Mercado de FX abierto: de domingo 17:00 a viernes 17:00 hora de Nueva York."""
    ny = ahora_utc_s + int(NUEVA_YORK.desfase(np.array([ahora_utc_s]))[0])
    dia, minuto = (ny // DIA + 3) % 7, (ny % DIA) // 60  # 0 = lunes
    if dia == 5:
        return False
    if dia == 4:
        return minuto < 17 * 60
    if dia == 6:
        return minuto >= 17 * 60
    return True


def desfase_observado(tick_servidor_s: int, ahora_utc_s: int, tolerancia_s: int = 300) -> int | None:
    """Desfase servidor - UTC visto en un tick, redondeado a media hora; None si el tick no es fresco o no es plausible."""
    d = int(tick_servidor_s) - int(ahora_utc_s)
    h = int(round(d / 1800)) * 1800
    if abs(d - h) > tolerancia_s or not -12 * H <= h <= 14 * H:
        return None
    return h


def detectar_en_vivo(term, simbolos: list[str], ahora_utc_s: int, regla: Regla) -> dict:
    """Metodo 1: ultimo tick de unos simbolos liquidos frente al reloj UTC."""
    esperado = int(regla.desfase(np.array([ahora_utc_s]))[0])
    out = {"metodo": "ultimo tick frente al reloj UTC", "ahora_utc": iso(ahora_utc_s * 1000),
           "mercado_fx_abierto": fx_abierto(ahora_utc_s), "desfase_regla_h": esperado / H, "observaciones": []}
    if out["mercado_fx_abierto"]:
        for sim in simbolos:
            t = term.symbol_info_tick(sim)
            if t is None:
                continue
            obs = desfase_observado(int(t.time), ahora_utc_s)
            out["observaciones"].append({"simbolo": sim, "desfase_h": None if obs is None else obs / H})
    vistos = {o["desfase_h"] for o in out["observaciones"] if o["desfase_h"] is not None}
    out["concluyente"] = len(vistos) == 1
    out["coincide"] = (vistos == {esperado / H}) if out["concluyente"] else None
    return out


def cierre_semanal(time_servidor_s: np.ndarray, paso_s: int, nombre_regla: str) -> dict:
    """Metodo 2: hora de NY del cierre de la ultima vela de cada semana completa, con cada regla candidata."""
    s = np.asarray(time_servidor_s, dtype=np.int64)
    out = {"metodo": "cierre del viernes en hora de Nueva York", "regla_usada": nombre_regla, "por_regla": {}}
    if s.size == 0:
        out.update(semanas=0, mejor=None, concluyente=False, coherente=True)
        return out
    # Cierre de semana = ultima vela antes de un hueco de mas de 24 h (no la ultima de la semana del servidor: con un
    # servidor en hora fija la apertura del domingo cae aun en la semana anterior). La ultima semana del rango no entra.
    ultimas = np.nonzero(np.diff(s) > DIA)[0]
    fin = s[ultimas] + paso_s
    out["semanas"] = int(fin.size)
    for nombre in CANDIDATAS + (() if nombre_regla in CANDIDATAS else (nombre_regla,)):
        u = regla_desde_texto(nombre).servidor_a_utc(fin)[0]
        ny = u + NUEVA_YORK.desfase(u)
        viernes = ((ny // DIA + 3) % 7) == 4
        minutos = (ny[viernes] % DIA) // 60
        if minutos.size == 0:
            out["por_regla"][nombre] = {"semanas_viernes": 0, "cierre_ny_moda": None, "coherencia": 0.0}
            continue
        vals, cuentas = np.unique(minutos, return_counts=True)
        k = int(np.argmax(cuentas))
        out["por_regla"][nombre] = {"semanas_viernes": int(minutos.size),
                                    "cierre_ny_moda": f"{int(vals[k]) // 60:02d}:{int(vals[k]) % 60:02d}",
                                    "coherencia": round(float(np.count_nonzero(minutos == CIERRE_FX_NY_MIN)) / float(fin.size), 4)}
    coh = {n: v["coherencia"] for n, v in out["por_regla"].items()}
    mejor = max(coh.values())
    empatadas = sorted(n for n, c in coh.items() if c == mejor)
    out["mejor"] = empatadas
    out["concluyente"] = fin.size >= 6 and mejor >= 0.9 and len(empatadas) == 1
    usada = coh.get(nombre_regla)
    # Incoherente solo si hay evidencia: la regla usada queda claramente por debajo de la mejor en suficientes semanas.
    out["coherente"] = not (fin.size >= 6 and mejor >= 0.9 and usada is not None and usada < mejor - 0.02)
    return out


def iso(ms: int | None) -> str | None:
    if ms is None:
        return None
    return dt.datetime.fromtimestamp(int(ms) / 1000, tz=UTC).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

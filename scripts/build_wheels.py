"""Construye la rueda de quantdesk desde un commit fijo del motor (GAP-03).

Pasos: git archive del commit -> E:/quantdesk-lab/build/<commit>/ (directorio vacio; el arbol se verifica contra
el tar y no admite ficheros sobrantes) -> pip wheel con el backend del propio pyproject (scikit-build-core, Ninja,
entorno MSVC) -> E:/quantdesk-lab/wheels/ -> SHA256SUMS (se relee y se recalcula el hash de cada rueda). El motor
(S:/projects/quantdesk) sólo se lee con git archive/rev-parse. Temporales, cachés y artefactos van a
E:/quantdesk-lab; rustup usa S:/Apps/Home/.rustup con la toolchain de rust/rust-toolchain.toml. Si C: baja de
2 GiB libres, se para.

  D:/miniconda312/python.exe -X utf8 scripts/build_wheels.py --commit <sha40>
  D:/miniconda312/python.exe -X utf8 scripts/build_wheels.py --selftest   (no compila)
"""

import argparse
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path

LAB = Path("E:/quantdesk-lab")
TMP_DIR = LAB / "tmp" / "build-b"
ENGINE = Path("S:/projects/quantdesk")
PYTHON = Path("D:/miniconda312/python.exe")
VSWHERE = Path("C:/Program Files (x86)/Microsoft Visual Studio/Installer/vswhere.exe")
RUSTUP_HOME = Path("S:/Apps/Home/.rustup")
RUST_TOOLCHAIN = "1.97.1-x86_64-pc-windows-msvc"  # la que fija rust/rust-toolchain.toml
MIN_C_FREE = 2 * 1024**3
SHA_RE = re.compile(r"[0-9a-f]{40}")


def derive(commit):
    """Rutas del build para un commit completo (función pura)."""
    if not SHA_RE.fullmatch(commit):
        raise ValueError(f"commit no valido (40 hex en minusculas): {commit!r}")
    build = LAB / "build" / commit
    return {
        "build": build,
        "skbuild": build / "_skbuild",
        "target": build / "target",
        "wheels": LAB / "wheels",
        "tmp": TMP_DIR,
        "pip_cache": LAB / "cache" / "pip",
        "cargo_home": LAB / "cache" / "cargo",
    }


def tmp_env():
    """Temporales en E: para los procesos previos al build, git y vswhere (función pura)."""
    t = TMP_DIR.as_posix()
    return {"TEMP": t, "TMP": t, "TMPDIR": t}


def lab_env(p):
    """Entorno de build: temporales, cachés y rustup fuera de C: (función pura)."""
    return {
        # TMPDIR gana a TEMP en tempfile; Git Bash lo fija a /tmp, que es C:.
        "TEMP": p["tmp"].as_posix(), "TMP": p["tmp"].as_posix(), "TMPDIR": p["tmp"].as_posix(),
        "PIP_CACHE_DIR": p["pip_cache"].as_posix(), "CARGO_HOME": p["cargo_home"].as_posix(),
        "CARGO_TARGET_DIR": p["target"].as_posix(), "CMAKE_GENERATOR": "Ninja",
        "RUSTUP_HOME": RUSTUP_HOME.as_posix(), "RUSTUP_TOOLCHAIN": RUST_TOOLCHAIN,
    }


def sealed(extra):
    """Entorno de un subproceso: el del sistema con las claves de lab por encima (nunca TEMP de C:)."""
    return {**os.environ, **extra}


def sums_text(entries):
    """Formato sha256sum: '<hex>  <nombre>' por línea, ordenado por nombre (función pura)."""
    return "".join(f"{h}  {name}\n" for name, h in sorted(entries))


def c_free_ok(free_bytes):
    return free_bytes >= MIN_C_FREE


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args, env):
    # --no-optional-locks: no escribe el índice del motor. core.autocrlf=false: el tar lleva el
    # contenido exacto de los blobs del commit (el autocrlf del sistema cambiaría ficheros LF).
    cmd = ["git", "--no-optional-locks", "-c", "core.autocrlf=false", "-C", ENGINE.as_posix(), *args]
    return subprocess.run(cmd, check=True, capture_output=True, text=True, env=env).stdout.strip()


def resolve_commit(ref):
    try:
        return git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", env=sealed(tmp_env()))
    except subprocess.CalledProcessError:
        sys.exit(f"BLOQUEADO: commit no encontrado en {ENGINE}: {ref}")


def extract(tar, dest):
    """Extrae tar en dest, que debe no existir o estar vacío: no se mezcla con restos de otra pasada."""
    if dest.exists() and (not dest.is_dir() or any(dest.iterdir())):
        sys.exit(f"BLOQUEADO: {dest} ya tiene contenido; vaciarlo a mano (el script no borra nada)")
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tar) as tf:
        tf.extractall(dest, filter="data")


def archive(commit, p):
    """git archive del commit a un tar en E: y extracción en build/<commit>/ (vacío). Devuelve el tar."""
    tar = p["tmp"] / f"{commit}.tar"
    git("archive", "--format=tar", "-o", tar.as_posix(), commit, env=sealed(lab_env(p)))
    extract(tar, p["build"])
    return tar


def extra_files(root, known, outputs):
    """Rutas posix de los ficheros bajo root que no están en known. No entra en los outputs de primer nivel."""
    extra = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root).as_posix()
        if rel == ".":
            dirnames[:] = [d for d in dirnames if d not in outputs]
        for name in filenames:
            r = name if rel == "." else f"{rel}/{name}"
            if r not in known:
                extra.append(r)
    return sorted(extra)


def verify_tree(tar, root, outputs=()):
    """Cada fichero del tar debe estar en root con el mismo SHA-256, y no puede haber sobrantes salvo bajo
    los directorios de salida outputs de primer nivel. Devuelve (n, malos)."""
    n, bad, known = 0, [], set()
    with tarfile.open(tar) as tf:
        for m in tf.getmembers():
            if m.isdir():
                continue
            known.add(m.name)
            if not m.isfile():
                continue
            n += 1
            f = root / m.name
            if not f.is_file() or sha256_file(f) != hashlib.sha256(tf.extractfile(m).read()).hexdigest():
                bad.append(m.name)
    return n, bad + [f"sobra: {r}" for r in extra_files(root, known, outputs)]


def msvc_env(env):
    """Fusiona el entorno de vcvars64 (VS 2022, herramientas C++) en env; claves en mayusculas."""
    base = subprocess.run(
        [str(VSWHERE), "-latest", "-products", "*", "-requires",
         "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
        capture_output=True, text=True, check=True, env=env).stdout.strip()
    if not base:
        sys.exit("BLOQUEADO: vswhere no encuentra Visual Studio con herramientas C++")
    bat = Path(base) / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
    out = subprocess.run(f'cmd /d /s /c ""{bat}" >nul && set"', env=env, capture_output=True,
                         text=True, encoding="utf-8", errors="replace", check=True).stdout
    new = dict(env)
    for line in out.splitlines():
        k, sep, v = line.partition("=")
        if sep and k and not k.startswith("="):
            new[k.upper()] = v
    return new


def pip_wheel(p, env):
    """pip wheel del propio árbol con el backend del pyproject; el build dir de CMake cae en build/<commit>."""
    out = p["tmp"] / "wheel-out"
    shutil.rmtree(out, ignore_errors=True)
    cmd = [str(PYTHON), "-m", "pip", "wheel", str(p["build"]), "--no-deps", "--wheel-dir", str(out),
           "--config-settings", f"build-dir={p['skbuild'].as_posix()}"]
    subprocess.run(cmd, env=env, check=True)
    return out


def publish(out, wheels):
    """Mueve las ruedas nuevas a wheels/. No sobrescribe: si ya existe una con ese nombre, se para."""
    new = sorted(out.glob("*.whl"))
    if not new:
        sys.exit("BLOQUEADO: pip wheel no genero ninguna rueda")
    clash = [w.name for w in new if (wheels / w.name).exists()]
    if clash:
        sys.exit(f"BLOQUEADO: ya existen en {wheels}: {clash} (muevelas antes; no se sobrescriben)")
    wheels.mkdir(parents=True, exist_ok=True)
    for w in new:
        shutil.move(str(w), str(wheels / w.name))


def write_sums(wheels):
    entries = [(w.name, sha256_file(w)) for w in sorted(wheels.glob("*.whl"))]
    (wheels / "SHA256SUMS").write_text(sums_text(entries), encoding="utf-8", newline="\n")
    return entries


def sums_check(wheels):
    """Relee SHA256SUMS y recalcula el SHA-256 de cada rueda. Devuelve los fallos (lista vacía = OK)."""
    listed = {}
    for line in (wheels / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, _, name = line.partition("  ")
        listed[name] = digest
    real = {w.name: sha256_file(w) for w in wheels.glob("*.whl")}
    return [f"{n}: SHA256SUMS={listed.get(n)} real={real.get(n)}"
            for n in sorted(set(listed) | set(real)) if listed.get(n) != real.get(n)]


def _selftest_tree(d):
    tar = d / "t.tar"
    with tarfile.open(tar, "w") as tf:
        for name, data in (("a.txt", b"A"), ("sub/b.txt", b"B")):
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    root = d / "root"
    extract(tar, root)
    assert verify_tree(tar, root) == (2, []), verify_tree(tar, root)
    (root / "extra.txt").write_bytes(b"x")
    assert verify_tree(tar, root) == (2, ["sobra: extra.txt"]), verify_tree(tar, root)
    (root / "extra.txt").unlink()
    (root / "target").mkdir()
    (root / "target" / "o.bin").write_bytes(b"o")
    assert verify_tree(tar, root, outputs=("target",)) == (2, []), verify_tree(tar, root, outputs=("target",))
    assert verify_tree(tar, root) == (2, ["sobra: target/o.bin"]), verify_tree(tar, root)
    (root / "a.txt").write_bytes(b"Z")
    assert verify_tree(tar, root, outputs=("target",)) == (2, ["a.txt"]), verify_tree(tar, root, outputs=("target",))
    try:
        extract(tar, root)
    except SystemExit:
        pass
    else:
        raise AssertionError("extract acepto un directorio no vacio")


def _selftest_sums(d):
    w = d / "wheels"
    w.mkdir()
    (w / "a-1.whl").write_bytes(b"uno")
    (w / "b-1.whl").write_bytes(b"dos")
    write_sums(w)
    assert sums_check(w) == [], sums_check(w)
    text = (w / "SHA256SUMS").read_text(encoding="utf-8")
    (w / "SHA256SUMS").write_text(text.replace(sha256_file(w / "a-1.whl"), "0" * 64), encoding="utf-8", newline="\n")
    bad = sums_check(w)
    assert len(bad) == 1 and bad[0].startswith("a-1.whl:"), bad
    (w / "SHA256SUMS").write_text(sums_text([("b-1.whl", sha256_file(w / "b-1.whl"))]), encoding="utf-8", newline="\n")
    bad = sums_check(w)
    assert len(bad) == 1 and bad[0].startswith("a-1.whl:"), bad  # rueda sin entrada en SHA256SUMS


def selftest():
    c = "69fdb39d0b67969dbdafa77f5da656511342f175"
    p = derive(c)
    assert p["build"].as_posix() == f"E:/quantdesk-lab/build/{c}", p["build"]
    assert p["skbuild"].as_posix() == f"E:/quantdesk-lab/build/{c}/_skbuild", p["skbuild"]
    assert p["target"].as_posix() == f"E:/quantdesk-lab/build/{c}/target", p["target"]
    assert p["wheels"].as_posix() == "E:/quantdesk-lab/wheels", p["wheels"]
    assert p["tmp"].as_posix() == "E:/quantdesk-lab/tmp/build-b", p["tmp"]
    assert p["pip_cache"].as_posix() == "E:/quantdesk-lab/cache/pip", p["pip_cache"]
    assert p["cargo_home"].as_posix() == "E:/quantdesk-lab/cache/cargo", p["cargo_home"]
    e = lab_env(p)
    assert e["TEMP"] == e["TMP"] == e["TMPDIR"] == "E:/quantdesk-lab/tmp/build-b", e
    assert tmp_env() == {k: e[k] for k in ("TEMP", "TMP", "TMPDIR")}, (tmp_env(), e)
    assert sealed(tmp_env())["TEMP"] == "E:/quantdesk-lab/tmp/build-b", "el entorno sellado no pisa TEMP"
    assert e["CARGO_HOME"] == "E:/quantdesk-lab/cache/cargo" and e["PIP_CACHE_DIR"] == "E:/quantdesk-lab/cache/pip", e
    assert e["CARGO_TARGET_DIR"] == f"E:/quantdesk-lab/build/{c}/target", e
    assert e["RUSTUP_HOME"] == "S:/Apps/Home/.rustup" and e["RUSTUP_TOOLCHAIN"] == RUST_TOOLCHAIN, e
    for bad in ("", c.upper(), c[:-1], "../" + c[3:] + "x"):
        try:
            derive(bad)
        except ValueError:
            continue
        raise AssertionError(f"derive acepto {bad!r}")
    assert sums_text([("b.whl", "bb"), ("a.whl", "aa")]) == "aa  a.whl\nbb  b.whl\n"
    assert c_free_ok(3 * 1024**3) and not c_free_ok(2 * 1024**3 - 1)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=TMP_DIR) as tmp:
        _selftest_tree(Path(tmp))
        _selftest_sums(Path(tmp))
    print("selftest OK")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Rueda quantdesk desde un commit fijo del motor (GAP-03).")
    ap.add_argument("--commit", help="commit del motor (completo o abreviado)")
    ap.add_argument("--selftest", action="store_true", help="comprueba la logica pura, sin compilar")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.commit:
        ap.error("falta --commit")
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    commit = resolve_commit(a.commit)
    p = derive(commit)
    for k in ("build", "wheels", "tmp", "pip_cache", "cargo_home"):
        p[k].mkdir(parents=True, exist_ok=True)
    print(f"commit {commit}")
    free0 = shutil.disk_usage("C:/").free
    print(f"C: libre antes: {free0 / 1024**3:.2f} GiB")
    if not c_free_ok(free0):
        sys.exit("BLOQUEADO: C: por debajo de 2 GiB libres")
    if not (RUSTUP_HOME / "toolchains" / RUST_TOOLCHAIN / "bin" / "rustc.exe").is_file():
        sys.exit(f"BLOQUEADO: falta la toolchain {RUST_TOOLCHAIN} en {RUSTUP_HOME}")
    t0 = time.time()
    tar = archive(commit, p)
    print(f"git archive sha256={sha256_file(tar)} -> {tar.as_posix()}")
    n, bad = verify_tree(tar, p["build"])
    if bad:
        sys.exit(f"BLOQUEADO: arbol extraido distinto de git archive: {bad[:5]}")
    print(f"arbol = git archive: {n} ficheros verificados")
    env = msvc_env(sealed(lab_env(p)))
    print(f"cl: {shutil.which('cl', path=env.get('PATH'))}")
    out = pip_wheel(p, env)
    n, bad = verify_tree(tar, p["build"], outputs=(p["skbuild"].name, p["target"].name))
    if bad:
        sys.exit(f"BLOQUEADO: el build modifico ficheros del arbol: {bad[:5]}")
    publish(out, p["wheels"])
    for name, digest in write_sums(p["wheels"]):
        print(f"{digest}  {name}")
    bad = sums_check(p["wheels"])
    if bad:
        sys.exit(f"BLOQUEADO: SHA256SUMS no coincide con las ruedas: {bad}")
    print("SHA256SUMS comprobado: cada hash recalculado coincide")
    free1 = shutil.disk_usage("C:/").free
    print(f"duracion {time.time() - t0:.0f} s; C: libre despues: {free1 / 1024**3:.2f} GiB")
    if not c_free_ok(free1):
        sys.exit("BLOQUEADO: C: por debajo de 2 GiB libres tras el build")
    return 0


if __name__ == "__main__":
    sys.exit(main())

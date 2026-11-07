# Registro de consumo de cuentas

Aplicar [USAGE_PROTOCOL.md](../USAGE_PROTOCOL.md). CSV UTF-8, coma como separador, punto decimal,
fechas ISO 8601 UTC. Vacío significa desconocido/no aplicable; `0` requiere evidencia. Los ficheros
nacen sólo con su cabecera; un coordinador por cuenta los rellena. `COST_TABLE.md` es salida
derivada (por esquema, nivel, proveedor y perfil real). Este registro nunca se mueve al archivar.

# Registra o actualiza (idempotente) en el Programador de tareas de Windows todas las tareas del repo
# (scripts\*_tarea.xml). Se lanza con run_scheduler.cmd, desde la raiz del repo. Lo ejecuta el USUARIO, no un agente.
#
# - El nombre de cada tarea sale de su <URI> (p. ej. \quantdesk\publicador_mt5).
# - schtasks exige el XML en UTF-16; en el repo vive en UTF-8 (legible en git). Aqui se reescribe la declaracion y se
#   guarda una copia temporal UTF-16 con BOM, que es la que se registra.
# - /F sobrescribe si ya existe: ejecutarlo varias veces deja siempre la tarea igual que el XML del repo.
# - Sin /RU: la tarea queda a nombre del usuario que ejecuta el script, con su sesion (InteractiveToken). No pide ni
#   guarda contrasenas.
# Uso: run_scheduler.cmd            registra o actualiza todas
#      run_scheduler.cmd -Listar    solo muestra que tareas hay y su estado, sin tocar nada

param([switch]$Listar)

$ErrorActionPreference = 'Continue'
$repo = Split-Path -Parent $PSScriptRoot
$xmls = @(Get-ChildItem (Join-Path $repo 'scripts') -Filter '*_tarea.xml' | Sort-Object Name)
if ($xmls.Count -eq 0) { Write-Host 'No hay ficheros scripts\*_tarea.xml.'; exit 1 }

$fallos = 0
foreach ($f in $xmls) {
    $texto = [IO.File]::ReadAllText($f.FullName, [Text.Encoding]::UTF8).TrimStart([char]0xFEFF)
    try { $doc = [xml]$texto } catch { Write-Host "ERROR  $($f.Name): XML no valido: $($_.Exception.Message)"; $fallos++; continue }
    $uri = $doc.Task.RegistrationInfo.URI
    if (-not $uri) { Write-Host "ERROR  $($f.Name): falta <RegistrationInfo><URI>"; $fallos++; continue }
    $nombre = $uri.TrimStart('\')

    & schtasks.exe /Query /TN $nombre *> $null
    $existia = ($LASTEXITCODE -eq 0)

    if ($Listar) {
        if ($existia) { Write-Host "EXISTE $nombre  ($($f.Name))"; & schtasks.exe /Query /TN $nombre /FO LIST }
        else { Write-Host "FALTA  $nombre  ($($f.Name))" }
        continue
    }

    $utf16 = $texto -replace '^<\?xml[^>]*\?>', '<?xml version="1.0" encoding="UTF-16"?>'
    $tmp = Join-Path $env:TEMP ("quantdesk_" + $f.BaseName + ".xml")
    [IO.File]::WriteAllText($tmp, $utf16, [Text.Encoding]::Unicode)
    $salida = & schtasks.exe /Create /F /XML $tmp /TN $nombre 2>&1
    $rc = $LASTEXITCODE
    Remove-Item $tmp -ErrorAction SilentlyContinue
    if ($rc -eq 0) {
        $accion = if ($existia) { 'ACTUALIZADA' } else { 'CREADA' }
        Write-Host "$accion $nombre  ($($f.Name))"
    } else {
        Write-Host "ERROR  $nombre  ($($f.Name)), rc=${rc}: $salida"
        $fallos++
    }
}
exit $(if ($fallos) { 1 } else { 0 })

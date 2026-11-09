@echo off
rem Inicia o releva la raiz del LAUNCH de este repo en una pestana nueva de Windows Terminal (skill global sprint,
rem references\handoff.md). Con docs\plans\current\HANDOFF.md listo y sin aceptar, abre la sucesora, que entra por
rem su «Arranque». Sin HANDOFF (o con --first [--launch RUTA]), abre la raiz inicial, que ejecuta el bloque del
rem coordinador del LAUNCH. --dry-run solo muestra el comando. No necesita venv: el interprete lo elige
rem tools\claude-or.cmd de la skill. Generado por sprint install, igual en todos los repos.
cd /d "%~dp0"
call "%USERPROFILE%\.claude\skills\sprint\tools\claude-or.cmd" handoff launch %*
exit /b %ERRORLEVEL%

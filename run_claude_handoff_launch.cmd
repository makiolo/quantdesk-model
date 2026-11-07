@echo off
rem Relevo de la raiz del LAUNCH de quantdesk-model: abre la sucesora con el HANDOFF listo y sin aceptar
rem (docs\plans\current\HANDOFF.md) en una pestana nueva de Windows Terminal que entra por «Arranque».
rem Procedimiento: skill global sprint, references\handoff.md, «Sale la raiz». Generado por sprint install.
cd /d "%~dp0"
"D:\miniconda312\python.exe" -X utf8 "%USERPROFILE%\.claude\skills\sprint\tools\claude_or.py" handoff launch %*
exit /b %ERRORLEVEL%

@echo off
rem Recupera la raiz del LAUNCH de quantdesk-model tras un apagado o una raiz muerta sin relevo: reconstruye el
rem estado desde el transcript (informe en .git\sprint-runtime\handoff\RECOVERY-<fecha>.md) y abre la sucesora.
rem Procedimiento: skill global sprint, references\handoff.md, «Recuperacion en frio». Generado por sprint install.
cd /d "%~dp0"
"D:\miniconda312\python.exe" -X utf8 "%USERPROFILE%\.claude\skills\sprint\tools\claude_or.py" handoff recover %*
exit /b %ERRORLEVEL%

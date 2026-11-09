@echo off
rem Recupera la raiz del LAUNCH de este repo tras un apagado o una raiz muerta sin relevo (skill global sprint,
rem references\handoff.md, «Recuperacion en frio»): reconstruye el estado desde el transcript (informe en
rem .git\sprint-runtime\handoff\RECOVERY-<fecha>.md) y abre la sucesora. --dry-run escribe el informe pero no abre la pestana.
rem No necesita venv: el interprete lo elige tools\claude-or.cmd de la skill. Generado por sprint install.
cd /d "%~dp0"
call "%USERPROFILE%\.claude\skills\sprint\tools\claude-or.cmd" handoff recover %*
exit /b %ERRORLEVEL%

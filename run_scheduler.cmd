@echo off
rem Registra o actualiza (idempotente) en el Programador de tareas de Windows las tareas del repo (scripts\*_tarea.xml).
rem Uso: run_scheduler.cmd            registra o actualiza todas
rem      run_scheduler.cmd -Listar    solo muestra su estado
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\registrar_tareas.ps1" %*
exit /b %ERRORLEVEL%

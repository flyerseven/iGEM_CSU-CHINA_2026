@echo off
rem Double-click to preview the wiki locally (Flask dev server on port 8080).
rem Keeps a minimized server window running; close that window to stop.
rem Safe to run again while already serving.
cd /d %~dp0
netstat -ano | findstr ":8080 " | findstr LISTENING >nul
if errorlevel 1 (
  if exist venv\Scripts\python.exe (start /min "wiki-preview" venv\Scripts\python.exe app.py) else (start /min "wiki-preview" python app.py)
)
timeout /t 2 >nul
start "" http://127.0.0.1:8080/

@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Ambiente ausente. Siga a instalacao no README.
  exit /b 1
)
set "PYTHONUTF8=1"
set "HF_HUB_OFFLINE=1"
echo Lumifolio: abra http://127.0.0.1:8765 no navegador.
".venv\Scripts\python.exe" -m uvicorn lumifolio.web:app --host 127.0.0.1 --port 8765

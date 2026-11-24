@echo off
cd /d "%~dp0"
set "PYTHONUTF8=1"
if not exist ".venv\Scripts\python.exe" (
  py -3.13 -m venv .venv
  if errorlevel 1 exit /b 1
)
set "LUMI_PY=.venv\Scripts\python.exe"
"%LUMI_PY%" -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 exit /b 1
"%LUMI_PY%" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
"%LUMI_PY%" -m pip check
if errorlevel 1 exit /b 1
"%LUMI_PY%" -m lumifolio.embeddings
if errorlevel 1 exit /b 1
set "LUMI_OLLAMA=ollama"
where ollama >nul 2>nul
if errorlevel 1 (
  if not exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
    echo Instale e inicie o Ollama. Consulte o README.
    exit /b 1
  )
  set "LUMI_OLLAMA=%LOCALAPPDATA%\Programs\Ollama\ollama.exe"
)
"%LUMI_OLLAMA%" pull qwen2.5:3b
if errorlevel 1 exit /b 1
echo Preparacao concluida. Execute iniciar.cmd.

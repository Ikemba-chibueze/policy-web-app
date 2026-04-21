@echo off
echo =========================================
echo Setting up AI Annotation Tool Environment
echo =========================================

:: 1. Tell uv to install/verify the required packages
echo Checking dependencies...
uv add fastapi uvicorn pandas

echo.
echo =========================================
echo Starting the Server...
echo Open your browser to: http://localhost:8000
echo =========================================

:: 2. Run the server
uv run uvicorn server:app --host 0.0.0.0 --port 8000
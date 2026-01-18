@echo off
cd /d F:\NEURALROOTSAI\backend
call F:\NEURALROOTSAI\.venv\Scripts\activate.bat
rem Run from backend folder, import app as a local package
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause

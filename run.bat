@echo off
title Curriculium AI - Dev Hunter & Resume Tailor
echo =======================================================
echo    Iniciando Curriculium AI - Dev Job Hunter & Tailor
echo =======================================================
echo.
echo Abrindo painel em http://127.0.0.1:8000 ...
start http://127.0.0.1:8000
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause

@echo off
rem Starts the spoken-word search with the full corpus (Tatoeba + Common Voice)
rem and opens it in the browser. Close this window to stop it.
rem The standalone word-audio-search.html works without this, Tatoeba only.
cd /d "%~dp0spoken"
python serve.py
if errorlevel 1 pause

@echo off
rem Finishes the Common Voice setup: unpack the archive, then load it into the
rem search database. Safe to run more than once. Unpacking restarts from the
rem beginning each time, because tar cannot resume, so leave it running.
rem Expect roughly an hour for about a million files, then a few minutes to
rem index. When it finishes, start the app with Deutsch-hoeren.bat.

setlocal
set DEST=C:\data\commonvoice
set ARC=%~1
rem No archive given? Take the newest common-voice-*.tar.gz in DEST.
if "%ARC%"=="" for /f "delims=" %%F in ('dir /b /o-d "%DEST%\common-voice-*.tar.gz" 2^>nul') do (
  set ARC=%DEST%\%%F
  goto :found
)
:found
if not exist "%ARC%" (
  echo Archive not found. Pass it as an argument, or put the
  echo common-voice-*.tar.gz you downloaded into %DEST%
  pause
  exit /b 1
)
echo Using archive: %ARC%

echo.
echo [1/2] Unpacking. This takes a while and will look frozen. It is not.
tar -xzf "%ARC%" -C "%DEST%"
if errorlevel 1 (
  echo Unpacking failed.
  pause
  exit /b 1
)

echo.
echo [2/2] Loading into the search database.
cd /d "%~dp0spoken"
python _ingest.py --cv "%DEST%"
if errorlevel 1 (
  echo Ingest failed.
  pause
  exit /b 1
)

echo.
echo Done. Start the app with Deutsch-hoeren.bat
pause

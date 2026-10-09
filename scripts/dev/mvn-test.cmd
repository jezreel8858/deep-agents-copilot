@echo off
rem Shim: delega a mvn-test.sh via Git Bash. Exit 10 se bash (Git for Windows) ausente.
setlocal
set "DAC_BASH="
if exist "%ProgramFiles%\Git\bin\bash.exe" set "DAC_BASH=%ProgramFiles%\Git\bin\bash.exe"
if not defined DAC_BASH if exist "%ProgramFiles(x86)%\Git\bin\bash.exe" set "DAC_BASH=%ProgramFiles(x86)%\Git\bin\bash.exe"
if not defined DAC_BASH if exist "%LocalAppData%\Programs\Git\bin\bash.exe" set "DAC_BASH=%LocalAppData%\Programs\Git\bin\bash.exe"
if not defined DAC_BASH (
  echo [dac] ERRO^(10^): Git Bash nao encontrado; instale Git for Windows 1>&2
  exit /b 10
)
set "DAC_SH=%~dp0mvn-test.sh"
"%DAC_BASH%" "%DAC_SH:\=/%" %*
exit /b %ERRORLEVEL%

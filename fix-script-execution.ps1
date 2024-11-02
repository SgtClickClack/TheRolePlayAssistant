# fix-script-execution.ps1
# Purpose: Set PowerShell execution policy to RemoteSigned for the current user

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
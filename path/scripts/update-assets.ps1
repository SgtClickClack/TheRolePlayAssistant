# Script: update-assets.ps1
# Description: Updates asset paths and stages changes for Git.

# Navigate to the project directory (if not already there)
Set-Location -Path "C:\Users\JR\Documents\DojoPool\Dojo_Pool\TheRolePlayAssistant"

# Create necessary directories
mkdir -Path .\src\assets\images -Force
mkdir -Path .\src\assets\icons -Force

# Move items if the static directories exist
if (Test-Path .\static\images) {
    Move-Item -Path .\static\images\* -Destination .\src\assets\images\
} else {
    Write-Output "Path .\static\images does not exist."
}

if (Test-Path .\static\icons) {
    Move-Item -Path .\static\icons\* -Destination .\src\assets\icons\
} else {
    Write-Output "Path .\static\icons does not exist."
}

# Remove static directories if they exist
if (Test-Path .\static\images) {
    Remove-Item -Path .\static\images\ -Recurse -Force
} else {
    Write-Output "Path .\static\images does not exist."
}

if (Test-Path .\static\icons) {
    Remove-Item -Path .\static\icons\ -Recurse -Force
} else {
    Write-Output "Path .\static\icons does not exist."
}

# Update image paths in HTML files
Get-ChildItem -Path .\templates\*.html -Recurse | ForEach-Object {
    (Get-Content $_.FullName) -replace '/static/images/', '/assets/images/' | Set-Content $_.FullName
    (Get-Content $_.FullName) -replace '/static/icons/', '/assets/icons/' | Set-Content $_.FullName
}

# Update image and icon paths in CSS and JS files
Get-ChildItem -Path .\src\assets\* -Recurse -Include *.css, *.js | ForEach-Object {
    (Get-Content $_.FullName) -replace '/static/images/', '/assets/images/' | Set-Content $_.FullName
    (Get-Content $_.FullName) -replace '/static/icons/', '/assets/icons/' | Set-Content $_.FullName
}

# Stage all changes
git add .

# (Optional) Commit changes with a message
# git commit -m "Updated asset paths from static to assets directories"

# Inspect the Script Content

View the content of the script to ensure it's not empty or corrupted:
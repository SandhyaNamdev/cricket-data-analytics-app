@echo off
REM Configure these variables before running:
set REPO_NAME=cricket-ipl-analysis
set GITHUB_USER=YOUR_GITHUB_USERNAME
set REMOTE_URL=https://github.com/%GITHUB_USER%/%REPO_NAME%.git

REM Initialize git, add files, commit, and push to GitHub (requires git installed and authenticated)
if not exist .git (
  git init
) 

git add .

git commit -m "Initial commit: IPL Streamlit app"

git remote remove origin 2>nul

git remote add origin %REMOTE_URL%

git branch -M main

git push -u origin main
pause

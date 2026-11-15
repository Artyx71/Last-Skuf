@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0profile\windows" mkdir "%~dp0profile\windows"
set "AYAY_OPTIONS_PATH=%~dp0profile\windows\options.json"
set "AYAY_DIALOGUE_SAVE_PATH=%~dp0profile\windows\dialogue.json"
set "AYAY_P06_DIALOGUE_SAVE_PATH=%~dp0profile\windows\cast.json"
set "AYAY_CHAPTER_SAVE_PATH=%~dp0profile\windows\chapter.json"
set "AYAY_STORY_SAVE_PATH=%~dp0profile\windows\story.json"
"%~dp0windows\last-skuf.exe" -- --open-character-combat

@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is required to run this script. Please install Python and try again.
    exit /b 1
)

REM Check if necessary parameters are provided
IF "%~1"=="" (
    echo Usage: %0 ^<subreddit_name^> ^<output_file^> [max_size_MB]
    exit /b 1
)

REM Run the Python script with provided parameters
python main.py %*
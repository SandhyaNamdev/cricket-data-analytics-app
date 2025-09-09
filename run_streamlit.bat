@echo off
REM Install required packages and run the Streamlit app
python -m pip install --upgrade pip
pip install -r "%~dp0requirements.txt"
python -m streamlit run "%~dp0IPL.py"
pause

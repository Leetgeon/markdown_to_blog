@echo off
chcp 65001 >nul
echo ===================================================
echo   [Markdown to Blog Generator] 로컬 서버 실행기
echo ===================================================
echo.
echo 웹 브라우저가 잠시 후 자동으로 열립니다...
echo 창을 닫으면 서버가 종료됩니다.
echo.
streamlit run app.py
pause

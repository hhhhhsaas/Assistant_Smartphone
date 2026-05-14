@echo off
echo ============================================================
echo PHONE ADVISOR - STREAMLIT APP
echo ============================================================
echo.
echo Installing required packages...
pip install streamlit pandas numpy scikit-learn plotly -q
echo.
echo Starting Streamlit app...
echo.
echo The app will open in your browser at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
streamlit run app.py
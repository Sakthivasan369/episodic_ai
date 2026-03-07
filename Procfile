web: cd core && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --timeout-keep-alive 600
frontend: streamlit run frontend/app.py --server.port ${PORT:-8501} --server.address 0.0.0.0

#!/bin/bash

# Este script diz à Render como iniciar a aplicação Streamlit.
# Ele garante que o Streamlit use a porta correta fornecida pela Render.
streamlit run app.py --server.port $PORT --server.headless true --server.enableCORS false
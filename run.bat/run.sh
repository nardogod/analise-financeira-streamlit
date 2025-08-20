# Script para Windows (run.bat)
@echo off
echo 🏦 Iniciando Análise Financeira Streamlit...
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.8+ antes de continuar.
    pause
    exit /b 1
)

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo 📦 Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo 🔄 Ativando ambiente virtual...
call venv\Scripts\activate

REM Instalar dependências
echo 📋 Instalando dependências...
pip install -r requirements.txt

REM Criar pasta de dados se não existir
if not exist "data" mkdir data

REM Executar Streamlit
echo 🚀 Iniciando aplicação Streamlit...
echo Acesse: http://localhost:8501
echo.
streamlit run app.py

pause

# -------------------------------------------------------------------
# Script para Linux/Mac (run.sh)
#!/bin/bash

echo "🏦 Iniciando Análise Financeira Streamlit..."
echo

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ Python não encontrado. Instale Python 3.8+ antes de continuar."
        exit 1
    else
        PYTHON_CMD=python
    fi
else
    PYTHON_CMD=python3
fi

echo "✅ Python encontrado: $($PYTHON_CMD --version)"

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    $PYTHON_CMD -m venv venv
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
echo "📋 Instalando dependências..."
pip install -r requirements.txt

# Criar pasta de dados se não existir
if [ ! -d "data" ]; then
    mkdir data
    echo "📁 Pasta 'data' criada."
fi

# Executar Streamlit
echo "🚀 Iniciando aplicação Streamlit..."
echo "Acesse: http://localhost:8501"
echo
streamlit run app.py
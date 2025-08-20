import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

# Inicializa o Faker para gerar dados em português do Brasil
fake = Faker('pt_BR')

# --- Configurações ---
NUM_TRANSACOES = 200  # Aumentei para ter mais dados por mês
DATA_INICIAL = datetime(2023, 1, 1)
DATA_FINAL = datetime(2023, 12, 31)
NOME_ARQUIVO_SAIDA = "extrato_ficticio.csv"
SALARIO_MENSAL_BASE = 6800.00 # Defina um salário base
# --- Definições de Transações ---
CATEGORIAS_GASTOS = {
    "Alimentação": ["Supermercado Dia", "iFood", "Restaurante Sabor Caseiro", "Padaria Pão Quente"],
    "Transporte": ["Uber Viagem", "99 App", "Posto Shell", "Recarga Bilhete Único"],
    "Moradia": ["Aluguel", "Condomínio Edifício Sol", "Conta de Luz - Enel", "Conta de Internet - Vivo Fibra"],
    "Lazer": ["Cinema Cinemark", "Ingresso Show XYZ", "Spotify", "Netflix"],
    "Saúde": ["Drogaria São Paulo", "Consulta Dr. Silva", "Plano de Saúde Amil"],
    "Compras": ["Amazon.com.br", "Mercado Livre", "Lojas Renner"]
}

CATEGORIAS_ENTRADAS = {
    "Salário": ["Pagamento Salário - Empresa ABC"],
    "Transferência": ["PIX Recebido - Maria Souza", "TED Recebido - João Oliveira"],
    "Rendimentos": ["Rendimento Poupança", "Dividendos Ação XPTO"]
}

def gerar_transacao(data):
    """Gera uma única linha de transação."""
    # Decide se é entrada ou saída (85% de chance de ser saída)
    if random.random() < 0.85:
        # É uma saída/gasto
        categoria = random.choice(list(CATEGORIAS_GASTOS.keys()))
        descricao = random.choice(CATEGORIAS_GASTOS[categoria])
        valor = round(random.uniform(10.00, 450.00), 2) # <<< GASTOS: Altere aqui a faixa de valores de gastos
        return {
            "Data": data.strftime('%d/%m/%Y'),
            "Descrição": descricao,
            "Tipo": categoria,
            "Entradas": 0.0, # Entradas são zero
            "Saidas": -valor  # Saídas são negativas
        }
    else:
        # É uma entrada
        categoria = random.choice(list(CATEGORIAS_ENTRADAS.keys())) 
        # Forçar a categoria "Salário" a ser mais provável para entradas
        if random.random() < 0.7: # 70% de chance de uma entrada ser salário
            categoria = "Salário"
            # <<< SALÁRIO: Altere aqui para um valor próximo ao seu salário simulado
            valor = round(random.uniform(SALARIO_MENSAL_BASE * 0.95, SALARIO_MENSAL_BASE * 1.05), 2)
        else:
            # <<< OUTRAS ENTRADAS: Altere aqui para outras fontes de renda menores
            valor = round(random.uniform(50.00, 500.00), 2)
        descricao = random.choice(CATEGORIAS_ENTRADAS[categoria])
        return {
            "Data": data.strftime('%d/%m/%Y'),
            "Descrição": descricao,
            "Tipo": categoria,
            "Entradas": valor,
            "Saidas": 0.0
        }

def main():
    """Função principal para gerar o arquivo CSV.""" 
    print("Gerando dados fictícios...")
    datas = [fake.date_between(start_date=DATA_INICIAL, end_date=DATA_FINAL) for _ in range(NUM_TRANSACOES)]
    
    transacoes = [gerar_transacao(data) for data in sorted(datas)]
    
    df = pd.DataFrame(transacoes)
    df.to_csv(NOME_ARQUIVO_SAIDA, index=False, sep=',', encoding='utf-8')
    
    print(f"✅ Arquivo '{NOME_ARQUIVO_SAIDA}' gerado com sucesso com {len(df)} transações.")

if __name__ == "__main__":
    main()
# 💰 Análise Financeira de Extrato Bancário - Imersão Python Alura

Este projeto é o resultado da Imersão Python da Alura, focado em Análise de Dados. A aplicação web, desenvolvida com Streamlit, permite que usuários façam o upload de seus extratos bancários (em formato CSV ou Excel) e recebam uma análise financeira interativa e visual.

## 🎯 Valor para o Negócio

Este projeto demonstra a capacidade de transformar dados brutos e desestruturados em insights valiosos e acionáveis, uma habilidade crucial para qualquer negócio orientado a dados. O valor que posso agregar a uma empresa inclui:

- **Desenvolvimento Rápido de Ferramentas de Análise (Rapid Prototyping):** Habilidade de construir dashboards e ferramentas de dados interativas de forma ágil com Streamlit, permitindo que as equipes de negócio explorem dados e validem hipóteses rapidamente, sem a necessidade de longos ciclos de desenvolvimento.
- **Automação de Processos Manuais:** A aplicação automatiza a limpeza, processamento e visualização de dados financeiros, tarefas que frequentemente são manuais e propensas a erros. Isso se traduz em economia de tempo e aumento da confiabilidade dos dados.
- **Tomada de Decisão Baseada em Dados:** Ao apresentar informações financeiras complexas (como fluxo de caixa, maiores despesas e evolução do saldo) de maneira clara e visual, a ferramenta capacita gestores e analistas a tomar decisões mais informadas e estratégicas.
- **Flexibilidade e Robustez:** O código foi projetado para lidar com diferentes formatos de arquivos (`.csv`, `.xls`, `.xlsx`) e variações nos nomes das colunas (ex: "Data", "data", "Data Movimentação"), demonstrando a capacidade de criar soluções adaptáveis a diversas fontes de dados.
- **Comunicação Eficaz de Resultados:** A utilização de gráficos interativos (Plotly) facilita a comunicação de tendências e padrões complexos para stakeholders, mesmo para aqueles sem conhecimento técnico aprofundado.

## ✨ Funcionalidades Principais

- **Upload Flexível:** Suporte para arquivos CSV, XLS e XLSX. O sistema detecta automaticamente o formato e a codificação do arquivo.
- **Processamento Inteligente de Dados:**
  - Identificação automática de colunas essenciais (Data, Entradas, Saídas, Descrição).
  - Limpeza e conversão de valores monetários, lidando com diferentes formatos (ex: "R$ 1.234,56").
  - Tratamento de datas em múltiplos formatos.
- **Dashboard Interativo:**
  - **Métricas Resumidas:** Visão geral com Total de Entradas, Saídas, Saldo Líquido e mais.
  - **Filtros Dinâmicos:** Filtre os dados por período, tipo de movimentação (entradas/saídas) e categorias de transação.
  - **Visualizações Gráficas:**
    - Gráfico de barras interativo com os maiores gastos por categoria.
    - Gráfico de linhas mostrando a evolução do saldo ao longo do tempo.
- **Análise Detalhada:**
  - Tabela com todas as transações filtradas.
  - Ferramenta para selecionar uma descrição de transação específica e analisar todas as ocorrências relacionadas a ela.

## 🛠️ Tecnologias Utilizadas

Este projeto foi construído utilizando um ecossistema moderno de ferramentas Python para análise e visualização de dados:

- **Linguagem:** Python 3
- **Framework Web/Dashboard:** Streamlit
- **Análise e Manipulação de Dados:** Pandas, NumPy
- **Visualização de Dados:** Plotly (Plotly Express, Plotly Graph Objects)
- **Leitura de Arquivos Excel:** Openpyxl

## 🚀 Como Executar o Projeto

Para executar a aplicação localmente, siga os passos abaixo:

1.  **Clone o repositório:**

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd analise_financeira
    ```

2.  **Crie e ative um ambiente virtual:**

    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run app.py
    ```
    A aplicação será aberta automaticamente no seu navegador.

## ☁️  Deploy
### https://analise-financeira-streamlit.onrender.com/


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from typing import Optional, Tuple
import openpyxl  # Para arquivos Excel

# --- Configuração da página ---
st.set_page_config(
    layout="wide", 
    page_title="Análise Financeira de Extrato Bancário",
    page_icon="💰",
    initial_sidebar_state="expanded"
)

# --- Funções auxiliares ---
@st.cache_data
def load_and_process_data(uploaded_file, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Carrega e processa os dados do arquivo CSV ou Excel de extrato bancário.
    
    Args:
        uploaded_file: Arquivo CSV, XLS ou XLSX carregado pelo usuário
        sheet_name: O nome da planilha a ser lida (para arquivos Excel)
        
    Returns:
        DataFrame processado ou None se houver erro
    """
    try:
        # Determina o tipo do arquivo pela extensão
        file_name = uploaded_file.name.lower()
        file_type = file_name.split('.')[-1]
        
        # Leitura do arquivo baseada na extensão
        if file_type == 'csv':
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='latin-1')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='cp1252')
        
        elif file_type in ['xls', 'xlsx']:
            try:
                # A lógica de seleção da planilha foi movida para a interface principal.
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            except Exception as e:
                st.error(f"❌ Erro ao ler arquivo Excel: {str(e)}")
                return None
        
        else:
            st.error(f"❌ Formato de arquivo não suportado: {file_type}")
            return None
        
        if df.empty:
            st.error("❌ O arquivo está vazio.")
            return None
        
        # Log das informações do arquivo
        st.sidebar.success(f"✅ Arquivo {file_type.upper()} carregado com sucesso!")
        st.sidebar.info(f"📊 Colunas encontradas: {list(df.columns)}")
        st.sidebar.info(f"📈 Total de linhas: {len(df)}")
        
        # Remove colunas vazias comuns
        # Abordagem mais robusta para remover colunas "Unnamed" que o pandas cria
        unnamed_cols = [col for col in df.columns if 'unnamed' in str(col).lower()]
        df = df.drop(columns=unnamed_cols)
        
        # Remove linhas completamente vazias
        df = df.dropna(how='all')
        
        # Processamento da coluna Data
        date_column = None
        possible_date_columns = ['Data', 'DATE', 'data', 'Data Movimentação', 'Data da Transação']
        
        for col in possible_date_columns:
            if col in df.columns:
                date_column = col
                break
        
        if date_column:
            date_formats = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y']
            
            for date_format in date_formats:
                try:
                    df['Data'] = pd.to_datetime(df[date_column], format=date_format, errors='coerce')
                    successful_conversions = df['Data'].notna().sum()
                    
                    if successful_conversions > 0:
                        st.sidebar.info(f"📅 Formato de data detectado: {date_format}")
                        break
                except:
                    continue
            
            if df['Data'].isna().all():
                df['Data'] = pd.to_datetime(df[date_column], errors='coerce', dayfirst=True)
            
            invalid_dates = df['Data'].isna().sum()
            if invalid_dates > 0:
                st.warning(f"⚠️ {invalid_dates} linha(s) com datas inválidas foram removidas.")
                df = df.dropna(subset=['Data'])
                
            if date_column != 'Data' and date_column in df.columns:
                df = df.drop(columns=[date_column])
        else:
            st.error("❌ Coluna de data não encontrada.")
            return None
        
        # Processamento das colunas numéricas
        possible_numeric_columns = {
            'Entradas': ['Entradas', 'Entrada', 'Crédito', 'Credito', 'Credit', 'Receita'],
            'Saidas': ['Saidas', 'Saída', 'Saídas', 'Débito', 'Debito', 'Debit', 'Despesa'],
            'Saldo': ['Saldo', 'Balance', 'Saldo Final', 'Saldo Atual']
        }
        
        for target_col, possible_names in possible_numeric_columns.items():
            found_column = None
            for col_name in possible_names:
                if col_name in df.columns:
                    found_column = col_name
                    break
            
            if found_column:
                # Processamento step-by-step para evitar erros
                df[target_col] = df[found_column].astype(str)
                df[target_col] = df[target_col].str.replace('R$', '')
                df[target_col] = df[target_col].str.replace('$', '')
                df[target_col] = df[target_col].str.replace(' ', '')
                df[target_col] = df[target_col].str.replace('.', '')
                df[target_col] = df[target_col].str.replace(',', '.')
                df[target_col] = pd.to_numeric(df[target_col], errors='coerce').fillna(0)
                
                if found_column != target_col and found_column in df.columns:
                    df = df.drop(columns=[found_column])
            else:
                st.warning(f"⚠️ Coluna '{target_col}' não encontrada automaticamente.")
        
        # Processamento de outras colunas
        description_columns = ['Descrição', 'Descricao', 'Description', 'Histórico', 'Historico', 'Memo']
        for desc_col in description_columns:
            if desc_col in df.columns and 'Descrição' not in df.columns:
                df['Descrição'] = df[desc_col]
                if desc_col != 'Descrição':
                    df = df.drop(columns=[desc_col])
                break
        
        type_columns = ['Tipo', 'Type', 'Categoria', 'Category', 'Classificação', 'Classificacao']
        for type_col in type_columns:
            if type_col in df.columns and 'Tipo' not in df.columns:
                df['Tipo'] = df[type_col]
                if type_col != 'Tipo':
                    df = df.drop(columns=[type_col])
                break
        
        # Criação de colunas auxiliares
        if 'Entradas' in df.columns and 'Saidas' in df.columns:
            df['Valor_Liquido'] = df['Entradas'] + df['Saidas']
            df['Valor_Total_Transacionado'] = df['Entradas'] + abs(df['Saidas'])
        
        # Ordenação por data
        df = df.sort_values('Data').reset_index(drop=True)
        
        st.sidebar.success(f"🎉 Processamento concluído: {len(df)} transações válidas!")
        
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        st.error("💡 Verifique se o arquivo está no formato correto e tente novamente.")
        return None

def filter_data(df: pd.DataFrame, filter_type: str, transaction_types: list, 
                date_range: Tuple[datetime, datetime]) -> pd.DataFrame:
    """
    Aplica filtros aos dados conforme seleção do usuário.
    
    Args:
        df: DataFrame original
        filter_type: Tipo de filtro ('Todas as Transações', 'Entradas', 'Saídas')
        transaction_types: Lista de tipos de transação selecionados
        date_range: Tupla com data inicial e final
        
    Returns:
        DataFrame filtrado
    """
    df_filtered = df.copy()
    
    # Filtro por período
    if date_range:
        start_date, end_date = date_range
        df_filtered = df_filtered[
            (df_filtered['Data'] >= start_date) & 
            (df_filtered['Data'] <= end_date)
        ]
    
    # Filtro por tipo de movimentação
    if filter_type == 'Entradas':
        df_filtered = df_filtered[df_filtered['Entradas'] > 0]
    elif filter_type == 'Saídas':
        df_filtered = df_filtered[df_filtered['Saidas'] < 0]
    
    # Filtro por tipos de transação
    if transaction_types and 'Tipo' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['Tipo'].isin(transaction_types)]
    
    return df_filtered

def create_summary_metrics(df: pd.DataFrame) -> dict:
    """
    Calcula métricas resumidas dos dados.
    
    Args:
        df: DataFrame com os dados
        
    Returns:
        Dicionário com as métricas calculadas
    """
    if df.empty:
        return {}
    
    total_entradas = df['Entradas'].sum()
    total_saidas = abs(df['Saidas'].sum())
    saldo_liquido = total_entradas - total_saidas
    total_transacoes = len(df)
    valor_medio_transacao = df['Valor_Total_Transacionado'].mean()
    
    return {
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo_liquido': saldo_liquido,
        'total_transacoes': total_transacoes,
        'valor_medio_transacao': valor_medio_transacao
    }

def create_spending_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Cria gráfico de gastos por tipo de transação."""
    if 'Tipo' not in df.columns or 'Saidas' not in df.columns:
        return None
    
    spending_data = (df[df['Saidas'] < 0]
                    .groupby('Tipo')['Saidas']
                    .sum()
                    .abs()
                    .sort_values(ascending=True))
    
    if spending_data.empty:
        return None
    
    fig = px.bar(
        x=spending_data.values,
        y=spending_data.index,
        orientation='h',
        labels={'x': 'Total de Gastos (R$)', 'y': 'Tipo de Transação'},
        title='💸 Total de Gastos por Tipo de Transação',
        color=spending_data.values,
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        height=max(400, len(spending_data) * 30),
        showlegend=False,
        title_x=0.5
    )
    
    fig.update_traces(
        texttemplate='R$ %{x:,.2f}',
        textposition='outside'
    )
    
    return fig

def create_balance_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Cria gráfico de evolução do saldo."""
    if df.empty or 'Data' not in df.columns:
        return None
    
    df_sorted = df.sort_values('Data').copy()
    df_sorted['Saldo_Acumulado'] = df_sorted['Valor_Liquido'].cumsum()
    
    fig = px.line(
        df_sorted,
        x='Data',
        y='Saldo_Acumulado',
        title='📈 Evolução do Saldo Acumulado',
        labels={'Data': 'Data', 'Saldo_Acumulado': 'Saldo Acumulado (R$)'}
    )
    
    fig.update_traces(line=dict(width=3))
    fig.update_layout(title_x=0.5, hovermode='x unified')
    
    # Adiciona linha zero para referência
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    return fig

def display_transaction_analysis(df: pd.DataFrame):
    """Exibe análise detalhada de transações específicas."""
    if 'Descrição' not in df.columns or df.empty:
        st.info("📝 Coluna 'Descrição' não encontrada ou dados insuficientes.")
        return
    
    st.subheader("🔍 Análise Detalhada por Descrição")
    
    # Prepara dados das descrições
    description_summary = (df.groupby('Descrição')
                          .agg({
                              'Entradas': 'sum',
                              'Saidas': 'sum',
                              'Valor_Total_Transacionado': 'sum',
                              'Data': 'count'
                          })
                          .rename(columns={'Data': 'Quantidade'})
                          .sort_values('Valor_Total_Transacionado', ascending=False))
    
    if description_summary.empty:
        st.info("📄 Nenhuma descrição de transação encontrada.")
        return
    
    # Seleção da descrição
    selected_description = st.selectbox(
        "📋 Selecione uma Descrição para Análise Detalhada:",
        [''] + list(description_summary.index),
        help="Escolha uma descrição para ver detalhes das transações"
    )
    
    if selected_description:
        # Dados da descrição selecionada
        selected_data = df[df['Descrição'] == selected_description].copy()
        summary_data = description_summary.loc[selected_description]
        
        # Métricas em colunas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📊 Quantidade de Transações", 
                f"{int(summary_data['Quantidade'])}"
            )
        
        with col2:
            st.metric(
                "💚 Total de Entradas", 
                f"R$ {summary_data['Entradas']:,.2f}"
            )
        
        with col3:
            st.metric(
                "💔 Total de Saídas", 
                f"R$ {abs(summary_data['Saidas']):,.2f}"
            )
        
        with col4:
            st.metric(
                "💰 Total Transacionado", 
                f"R$ {summary_data['Valor_Total_Transacionado']:,.2f}",
                help="Soma absoluta de todas as movimentações (entradas + |saídas|)"
            )
        
        # Saldo líquido
        saldo_liquido = summary_data['Entradas'] + summary_data['Saidas']
        st.metric(
            "📈 Saldo Líquido", 
            f"R$ {saldo_liquido:,.2f}",
            delta=f"R$ {saldo_liquido:,.2f}"
        )
        
        # Tabela detalhada
        st.markdown("#### 📋 Detalhes das Transações")
        
        # Formata as colunas para exibição
        display_data = selected_data.copy()
        for col in ['Entradas', 'Saidas', 'Saldo', 'Valor_Total_Transacionado']:
            if col in display_data.columns:
                display_data[col] = display_data[col].apply(lambda x: f"R$ {x:,.2f}")
        
        display_data['Data'] = display_data['Data'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )
    else:
        # Exibe resumo de todas as descrições
        st.markdown("#### 📊 Resumo por Descrição (Top 10)")
        
        top_descriptions = description_summary.head(10).copy()
        
        # Formata valores para exibição
        for col in ['Entradas', 'Saidas', 'Valor_Total_Transacionado']:
            top_descriptions[col] = top_descriptions[col].apply(lambda x: f"R$ {x:,.2f}")
        
        st.dataframe(
            top_descriptions,
            use_container_width=True,
            column_config={
                "Quantidade": st.column_config.NumberColumn("Qtd. Transações"),
                "Entradas": st.column_config.TextColumn("Total Entradas"),
                "Saidas": st.column_config.TextColumn("Total Saídas"),
                "Valor_Total_Transacionado": st.column_config.TextColumn("Total Transacionado")
            }
        )

# --- Interface Principal ---
def main():
    # Título e introdução
    st.title("💰 Análise Financeira de Extrato Bancário")
    st.markdown("""
    <div style="padding: 1rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                border-radius: 10px; color: white; margin-bottom: 2rem;">
        <h4 style="margin: 0; color: white;">📊 Dashboard de Análise Financeira</h4>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
            Carregue seu extrato bancário em CSV, XLS ou XLSX e obtenha insights detalhados sobre suas finanças.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para controles
    st.sidebar.header("⚙️ Configurações de Análise")
    
    # Upload de arquivo
    uploaded_file = st.sidebar.file_uploader(
        "📁 Carregue seu extrato bancário",
        type=["csv", "xls", "xlsx"],
        help="Selecione um arquivo CSV, XLS ou XLSX com seu extrato bancário"
    )
    
    if uploaded_file is None:
        # Página inicial com instruções
        st.markdown("""
        ### 🚀 Como usar este aplicativo:
        
        1. **📁 Carregue seu arquivo** na barra lateral (CSV, XLS ou XLSX)
        2. **🎛️ Configure os filtros** conforme necessário
        3. **📊 Analise os resultados** nas diferentes seções
        4. **🔍 Explore transações específicas** para insights detalhados
        
        ### 📋 Formatos de arquivo suportados:
        - **📄 CSV**: Comma-Separated Values
        - **📊 XLS**: Excel 97-2003
        - **📈 XLSX**: Excel 2007+
        
        ### 📋 Colunas reconhecidas automaticamente:
        - **Data**: Data, DATE, Data Movimentação
        - **Entradas**: Entradas, Crédito, Receita
        - **Saídas**: Saídas, Débito, Despesas  
        - **Descrição**: Descrição, Histórico, Memo
        - **Tipo**: Tipo, Categoria, Classificação
        
        ---
        *Developed with ❤️ using Streamlit*
        """)
        return
    
    # Processamento dos dados
    # A lógica de seleção de planilha para arquivos Excel é tratada aqui, fora da função cacheada.
    selected_sheet = None
    if uploaded_file.name.lower().endswith(('xls', 'xlsx')):
        try:
            # Usamos seek(0) para garantir que o ponteiro do arquivo esteja no início
            uploaded_file.seek(0)
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            
            if len(sheet_names) > 1:
                st.sidebar.info(f"📋 Planilhas encontradas: {', '.join(sheet_names)}")
                selected_sheet = st.sidebar.selectbox(
                    "📊 Selecione a planilha:",
                    sheet_names,
                    help="Escolha a planilha que contém os dados do extrato"
                )
            else:
                selected_sheet = sheet_names[0]
        except Exception as e:
            st.error(f"❌ Erro ao inspecionar o arquivo Excel: {str(e)}")
            return

    with st.spinner("🔄 Processando dados..."):
        # Passamos o nome da planilha selecionada para a função de processamento
        df_processed = load_and_process_data(uploaded_file, sheet_name=selected_sheet)
    
    st.success(f"✅ Arquivo processado com sucesso! {len(df_processed)} transações encontradas.")
    
    # Controles de filtro na sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Filtros de Análise")
    
    # Filtro por período
    if not df_processed.empty:
        min_date = df_processed['Data'].min().date()
        max_date = df_processed['Data'].max().date()
        
        date_range = st.sidebar.date_input(
            "📅 Período de Análise",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            help="Selecione o período para análise"
        )
        
        # Converte para datetime
        if len(date_range) == 2:
            date_range = (
                pd.Timestamp(date_range[0]),
                pd.Timestamp(date_range[1])
            )
        else:
            date_range = None
    
    # Filtro por tipo de movimentação
    filter_type = st.sidebar.radio(
        "💱 Tipo de Movimentação:",
        ('Todas as Transações', 'Entradas', 'Saídas'),
        help="Filtre por tipo de movimentação financeira"
    )
    
    # Filtro por tipo de transação
    transaction_types = []
    if 'Tipo' in df_processed.columns:
        unique_types = sorted(df_processed['Tipo'].dropna().unique().tolist())
        transaction_types = st.sidebar.multiselect(
            "🏷️ Tipos de Transação:",
            unique_types,
            default=unique_types,
            help="Selecione os tipos de transação para incluir"
        )
    
    # Aplicação dos filtros
    df_filtered = filter_data(df_processed, filter_type, transaction_types, date_range)
    
    if df_filtered.empty:
        st.warning("⚠️ Nenhuma transação encontrada com os filtros selecionados.")
        return
    
    # Área principal com resultados
    st.header("📊 Resultados da Análise")
    
    # Métricas resumidas
    metrics = create_summary_metrics(df_filtered)
    
    if metrics:
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "💚 Total Entradas", 
                f"R$ {metrics['total_entradas']:,.2f}"
            )
        
        with col2:
            st.metric(
                "💔 Total Saídas", 
                f"R$ {metrics['total_saidas']:,.2f}"
            )
        
        with col3:
            st.metric(
                "📈 Saldo Líquido", 
                f"R$ {metrics['saldo_liquido']:,.2f}",
                delta=f"R$ {metrics['saldo_liquido']:,.2f}"
            )
        
        with col4:
            st.metric(
                "📋 Total Transações", 
                f"{metrics['total_transacoes']:,}"
            )
        
        with col5:
            st.metric(
                "📊 Valor Médio", 
                f"R$ {metrics['valor_medio_transacao']:,.2f}"
            )
    
    # Visualizações
    st.markdown("---")
    st.subheader("📈 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de gastos por tipo
        spending_chart = create_spending_chart(df_filtered)
        if spending_chart:
            st.plotly_chart(spending_chart, use_container_width=True)
        else:
            st.info("📊 Dados insuficientes para gráfico de gastos por tipo.")
    
    with col2:
        # Gráfico de evolução do saldo
        balance_chart = create_balance_chart(df_filtered)
        if balance_chart:
            st.plotly_chart(balance_chart, use_container_width=True)
        else:
            st.info("📊 Dados insuficientes para gráfico de evolução do saldo.")
    
    # Tabela de dados
    st.markdown("---")
    st.subheader("📋 Dados Detalhados")
    
    # Prepara dados para exibição
    display_df = df_filtered.copy()
    
    # Formata colunas monetárias
    money_columns = ['Entradas', 'Saidas', 'Saldo', 'Valor_Liquido', 'Valor_Total_Transacionado']
    for col in money_columns:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"R$ {x:,.2f}")
    
    # Formata data
    if 'Data' in display_df.columns:
        display_df['Data'] = display_df['Data'].dt.strftime('%d/%m/%Y')
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Análise detalhada de transações
    st.markdown("---")
    display_transaction_analysis(df_filtered)

if __name__ == "__main__":
    main()
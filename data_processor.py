"""
Módulo auxiliar para processamento de dados financeiros
Separado do app principal para melhor organização
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

class FinancialDataProcessor:
    """Classe para processamento de dados financeiros do extrato bancário"""
    
    def __init__(self):
        self.df_processed = None
        self.analysis_results = {}
    
    @staticmethod
    def clean_monetary_value(value):
        """Converte strings monetárias para float"""
        if pd.isna(value) or value == '':
            return 0.0
        
        if isinstance(value, str):
            # Remover aspas, R$, espaços e converter vírgula para ponto
            value = value.replace('"', '').replace('R$', '').replace(' ', '').replace(',', '.')
            
            # Se tem sinal negativo, manter
            if value.startswith('-'):
                return -float(value[1:]) if value[1:] and value[1:] != '-' else 0.0
            return float(value) if value else 0.0
        
        return float(value) if not pd.isna(value) else 0.0
    
    @staticmethod
    def categorize_operation(description):
        """Categoriza operações baseado na descrição"""
        if pd.isna(description):
            return 'Não Informado'
        
        desc = str(description).upper()
        
        category_rules = {
            'Pix Recebido': ['PIX'] and ['RECEBIDO'],
            'Pix Enviado': ['PIX'] and ['ENVIADO'],
            'Pagamento Cartão Crédito': ['PAGAMENTO'] and ['CARTAO CREDITO'],
            'Cartão de Débito': ['COMPRA CARTAO DEB'],
            'Transferência': ['TED', 'DOC'],
            'Salário': ['LIQUIDO DE VENCIMENTO'],
            'Contas/Serviços': ['AGUA', 'ESGOTO', 'CLARO', 'TELEFONE', 'DEBITO AUT'],
            'Boleto': ['BOLETO'],
            'Estorno': ['ESTORNO'],
            'Saque': ['SAQUE'],
            'Depósito': ['DEPOSITO', 'DEPÓSITO'],
            'Rendimento': ['REMUNERACAO APLICACAO'],
            'Taxas/IOF': ['IOF']
        }
        
        for category, keywords in category_rules.items():
            if isinstance(keywords[0], list):
                # Regra AND
                if all(any(kw in desc for kw in sublist) for sublist in keywords):
                    return category
            else:
                # Regra OR
                if any(keyword in desc for keyword in keywords):
                    return category
        
        return 'Outros'
    
    @staticmethod
    def categorize_establishment(description):
        """Categoriza estabelecimentos por tipo de negócio"""
        if pd.isna(description):
            return 'Não Informado'
        
        desc = str(description).upper()
        
        # Mapeamento de categorias com palavras-chave
        categories = {
            'Transporte': ['UBER', '99', 'TAXI', 'CABIFY', 'METRO'],
            'Alimentação': [
                'RESTAURANT', 'PIZZA', 'BURGER', 'FOOD', 'CAFE', 'BAR', 
                'LANCHE', 'HORTIFRUTI', 'MERCADO', 'SUBWAY', 'DONA MARIA',
                'EXTRA', 'NORDESTE', 'IMPERADOR'
            ],
            'Compras/Varejo': ['SHOPPING', 'LOJA', 'MAGAZINE', 'MINI EXTRA'],
            'Serviços/Utilities': [
                'CLARO', 'AGUA', 'ESGOTO', 'SABESP', 'ELETROPAULO', 
                'TELEFONE', 'SALON', 'CLINICA', 'HOSPITAL'
            ],
            'Habitação': ['CONDOMINIO', 'ALUGUEL', 'F. PEREIRA'],
            'Financeiro': [
                'BANCO', 'CAIXA', 'FINANCEIRA', 'WISE', 'CARTAO CREDITO', 
                'IOF', 'BCE', 'AITRADBRASIL'
            ],
            'Saúde': ['SAUDE', 'BRADESCO SAUDE', 'DROGASIL'],
            'Pessoas Físicas': [
                'PAMELA', 'CECILIA', 'LEONARDO', 'MARGARETE', 
                'LIDIANE', 'CARLOS', 'LORRAINE', 'MARLUCIA'
            ],
            'Renda/Trabalho': ['LIQUIDO DE VENCIMENTO', 'CNPJ', 'CAIXOTE COMERCIO'],
            'Educação/Serviços': ['COPIADORA', 'ENCADERNA', 'IDEAL FOTOS'],
            'Entretenimento': ['CLUBE DO INGRESSO'],
            'Tecnologia': ['LETS SOFTWARE', 'VETST ECNOLOGIA']
        }
        
        for category, keywords in categories.items():
            if any(keyword in desc for keyword in keywords):
                return category
        
        return 'Outros'
    
    @staticmethod
    def extract_establishment_name(description):
        """Extrai nome do estabelecimento da descrição"""
        if pd.isna(description):
            return 'Não Informado'
        
        desc = str(description).strip()
        
        # Padrões específicos para extração
        patterns = {
            'PIX': r'PIX (?:RECEBIDO|ENVIADO)\s+(.+?)(?:\s|$)',
            'CARTAO': r'COMPRA CARTAO DEB MC\s+\d{2}/\d{2}\s+(.+?)(?:\s|$)',
            'PAGAMENTO': r'PAGAMENTO DE BOLETO.*?(.+?)(?:\s|$)',
            'TED': r'TED (?:RECEBIDA|ENVIADA)\s+(.+?)(?:\s|$)',
            'LIQUIDO': r'LIQUIDO DE VENCIMENTO\s+(.+?)(?:\s|$)'
        }
        
        desc_upper = desc.upper()
        
        for pattern_type, pattern in patterns.items():
            if pattern_type in desc_upper:
                match = re.search(pattern, desc, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        # Fallback: pegar após o tipo da operação
        words = desc.split()
        if len(words) > 3:
            return ' '.join(words[3:]).strip()
        
        return desc.strip()
    
    def process_dataframe(self, df):
        """Processa o DataFrame principal"""
        df_clean = df.copy()
        
        # Converter datas
        df_clean['Data'] = pd.to_datetime(df_clean['Data'], format='%d/%m/%Y', errors='coerce')
        
        # Limpar valores monetários
        df_clean['Entradas_Limpo'] = df_clean['Entradas'].apply(self.clean_monetary_value)
        df_clean['Saidas_Limpo'] = df_clean['Saidas'].apply(self.clean_monetary_value)
        df_clean['Saldo_Limpo'] = df_clean['Saldo'].apply(self.clean_monetary_value)
        
        # Criar coluna de valor único (positivo para entradas, negativo para saídas)
        df_clean['Valor'] = df_clean['Entradas_Limpo'] + df_clean['Saidas_Limpo']
        
        # Aplicar categorizações
        df_clean['Categoria_Operacao'] = df_clean['Descricao'].apply(self.categorize_operation)
        df_clean['Categoria_Estabelecimento'] = df_clean['Descricao'].apply(self.categorize_establishment)
        df_clean['Estabelecimento'] = df_clean['Descricao'].apply(self.extract_establishment_name)
        
        # Adicionar colunas temporais
        df_clean['Ano'] = df_clean['Data'].dt.year
        df_clean['Mes'] = df_clean['Data'].dt.month
        df_clean['Dia'] = df_clean['Data'].dt.day
        df_clean['Dia_Semana'] = df_clean['Data'].dt.day_name()
        df_clean['Mes_Nome'] = df_clean['Data'].dt.month_name()
        df_clean['Trimestre'] = df_clean['Data'].dt.quarter
        
        # Adicionar flags úteis
        df_clean['Is_Weekend'] = df_clean['Data'].dt.weekday >= 5
        df_clean['Is_Entrada'] = df_clean['Valor'] > 0
        df_clean['Is_Saida'] = df_clean['Valor'] < 0
        
        # Remover linhas com dados inválidos
        df_clean = df_clean.dropna(subset=['Data', 'Valor'])
        df_clean = df_clean.reset_index(drop=True)
        
        self.df_processed = df_clean
        return df_clean
    
    def calculate_indicators(self, df):
        """Calcula indicadores de saúde financeira"""
        entradas = df[df['Valor'] > 0]
        saidas = df[df['Valor'] < 0]
        
        total_entradas = entradas['Valor'].sum()
        total_saidas = abs(saidas['Valor'].sum())
        saldo_liquido = total_entradas - total_saidas
        
        # Cálculos temporais
        periodo_inicio = df['Data'].min()
        periodo_fim = df['Data'].max()
        dias_periodo = (periodo_fim - periodo_inicio).days + 1
        dias_com_movimentacao = df['Data'].dt.date.nunique()
        
        # Indicadores principais
        indicators = {
            # Financeiros básicos
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_liquido': saldo_liquido,
            'giro_financeiro': total_entradas + total_saidas,
            
            # Taxas e percentuais
            'taxa_poupanca': ((saldo_liquido / total_entradas) * 100) if total_entradas > 0 else 0,
            'razao_entrada_saida': total_entradas / total_saidas if total_saidas > 0 else 0,
            
            # Médias temporais
            'gasto_medio_diario': total_saidas / dias_periodo if dias_periodo > 0 else 0,
            'entrada_media_diaria': total_entradas / dias_periodo if dias_periodo > 0 else 0,
            'transacoes_por_dia': len(df) / dias_periodo if dias_periodo > 0 else 0,
            
            # Tickets médios
            'ticket_medio_gasto': abs(saidas['Valor'].mean()) if len(saidas) > 0 else 0,
            'ticket_medio_entrada': entradas['Valor'].mean() if len(entradas) > 0 else 0,
            'ticket_medio_geral': df['Valor'].abs().mean(),
            
            # Valores extremos
            'maior_gasto_individual': abs(saidas['Valor'].min()) if len(saidas) > 0 else 0,
            'maior_entrada_individual': entradas['Valor'].max() if len(entradas) > 0 else 0,
            
            # Estatísticas operacionais
            'total_transacoes': len(df),
            'total_entradas_transacoes': len(entradas),
            'total_saidas_transacoes': len(saidas),
            'estabelecimentos_unicos': df['Estabelecimento'].nunique(),
            'categorias_gastos': df[df['Valor'] < 0]['Categoria_Estabelecimento'].nunique(),
            
            # Temporais
            'dias_periodo': dias_periodo,
            'dias_com_movimentacao': dias_com_movimentacao,
            'periodo_inicio': periodo_inicio,
            'periodo_fim': periodo_fim,
            
            # Volatilidade e dispersão
            'volatilidade_gastos': saidas['Valor'].std() if len(saidas) > 1 else 0,
            'volatilidade_entradas': entradas['Valor'].std() if len(entradas) > 1 else 0,
            
            # Concentração (será calculada abaixo)
            'concentracao_top5_gastos': 0,
            'concentracao_top3_estabelecimentos': 0
        }
        
        # Calcular concentração dos gastos
        if len(saidas) >= 5:
            top5_gastos = saidas.nlargest(5, 'Valor')['Valor'].sum()
            indicators['concentracao_top5_gastos'] = abs(top5_gastos) / total_saidas * 100 if total_saidas > 0 else 0
        
        # Concentração por estabelecimento
        gastos_por_estabelecimento = saidas.groupby('Estabelecimento')['Valor'].sum().abs().sort_values(ascending=False)
        if len(gastos_por_estabelecimento) >= 3:
            top3_estabelecimentos = gastos_por_estabelecimento.head(3).sum()
            indicators['concentracao_top3_estabelecimentos'] = (top3_estabelecimentos / total_saidas) * 100
        
        self.analysis_results = indicators
        return indicators
    
    def get_category_analysis(self, df):
        """Análise detalhada por categoria"""
        category_stats = {}
        
        # Análise de gastos por categoria
        gastos_categoria = df[df['Valor'] < 0].groupby('Categoria_Estabelecimento').agg({
            'Valor': ['count', 'sum', 'mean', 'std'],
            'Estabelecimento': 'nunique',
            'Data': lambda x: x.dt.date.nunique()
        }).round(2)
        
        gastos_categoria.columns = ['Qtd_Transacoes', 'Valor_Total', 'Valor_Medio', 'Desvio_Padrao', 'Estabelecimentos_Unicos', 'Dias_Ativos']
        gastos_categoria['Valor_Total'] = gastos_categoria['Valor_Total'].abs()
        gastos_categoria['Valor_Medio'] = gastos_categoria['Valor_Medio'].abs()
        
        category_stats['gastos'] = gastos_categoria.sort_values('Valor_Total', ascending=False)
        
        # Análise de entradas por categoria
        entradas_categoria = df[df['Valor'] > 0].groupby('Categoria_Estabelecimento').agg({
            'Valor': ['count', 'sum', 'mean']
        }).round(2)
        
        entradas_categoria.columns = ['Qtd_Transacoes', 'Valor_Total', 'Valor_Medio']
        category_stats['entradas'] = entradas_categoria.sort_values('Valor_Total', ascending=False)
        
        return category_stats
    
    def get_establishment_analysis(self, df):
        """Análise detalhada por estabelecimento"""
        establishment_stats = {}
        
        # Top estabelecimentos por gasto
        gastos_estabelecimento = df[df['Valor'] < 0].groupby('Estabelecimento').agg({
            'Valor': ['count', 'sum', 'mean', 'min'],
            'Data': ['min', 'max', lambda x: x.dt.date.nunique()],
            'Categoria_Estabelecimento': lambda x: x.mode().iloc[0] if len(x) > 0 else 'N/A'
        }).round(2)
        
        gastos_estabelecimento.columns = [
            'Qtd_Transacoes', 'Valor_Total', 'Valor_Medio', 'Maior_Gasto',
            'Primeira_Transacao', 'Ultima_Transacao', 'Dias_Ativos', 'Categoria_Principal'
        ]
        gastos_estabelecimento['Valor_Total'] = gastos_estabelecimento['Valor_Total'].abs()
        gastos_estabelecimento['Valor_Medio'] = gastos_estabelecimento['Valor_Medio'].abs()
        gastos_estabelecimento['Maior_Gasto'] = gastos_estabelecimento['Maior_Gasto'].abs()
        
        establishment_stats['gastos'] = gastos_estabelecimento.sort_values('Valor_Total', ascending=False)
        
        # Top fontes de entrada
        entradas_estabelecimento = df[df['Valor'] > 0].groupby('Estabelecimento').agg({
            'Valor': ['count', 'sum', 'mean'],
            'Data': ['min', 'max']
        }).round(2)
        
        entradas_estabelecimento.columns = ['Qtd_Transacoes', 'Valor_Total', 'Valor_Medio', 'Primeira_Transacao', 'Ultima_Transacao']
        establishment_stats['entradas'] = entradas_estabelecimento.sort_values('Valor_Total', ascending=False)
        
        # Gastos recorrentes (aparecem em múltiplos dias)
        recorrentes = gastos_estabelecimento[gastos_estabelecimento['Dias_Ativos'] >= 2].copy()
        recorrentes['Gasto_Medio_Por_Dia'] = recorrentes['Valor_Total'] / recorrentes['Dias_Ativos']
        establishment_stats['recorrentes'] = recorrentes.sort_values('Valor_Total', ascending=False)
        
        return establishment_stats
    
    def get_temporal_analysis(self, df):
        """Análise temporal dos dados"""
        temporal_stats = {}
        
        # Análise por dia da semana
        por_dia_semana = df.groupby('Dia_Semana').agg({
            'Valor': ['count', 'sum', 'mean']
        }).round(2)
        por_dia_semana.columns = ['Qtd_Operacoes', 'Valor_Total', 'Valor_Medio']
        temporal_stats['dia_semana'] = por_dia_semana
        
        # Análise por mês
        por_mes = df.groupby('Mes_Nome').agg({
            'Valor': ['count', 'sum', 'mean']
        }).round(2)
        por_mes.columns = ['Qtd_Operacoes', 'Valor_Total', 'Valor_Medio']
        temporal_stats['mes'] = por_mes
        
        # Fluxo diário
        fluxo_diario = df.groupby(df['Data'].dt.date).agg({
            'Valor': ['sum', 'count']
        }).round(2)
        fluxo_diario.columns = ['Saldo_Diario', 'Qtd_Transacoes']
        temporal_stats['diario'] = fluxo_diario
        
        # Top dias com mais movimentação
        top_dias = fluxo_diario.nlargest(5, 'Qtd_Transacoes')
        temporal_stats['top_dias_movimento'] = top_dias
        
        # Análise de tendência
        if len(fluxo_diario) > 1:
            gastos_diarios = df[df['Valor'] < 0].groupby(df['Data'].dt.date)['Valor'].sum().abs()
            if len(gastos_diarios) > 2:
                primeira_metade = gastos_diarios.iloc[:len(gastos_diarios)//2].mean()
                segunda_metade = gastos_diarios.iloc[len(gastos_diarios)//2:].mean()
                tendencia = ((segunda_metade - primeira_metade) / primeira_metade) * 100 if primeira_metade > 0 else 0
                temporal_stats['tendencia_gastos'] = {
                    'primeira_metade': primeira_metade,
                    'segunda_metade': segunda_metade,
                    'variacao_percentual': tendencia,
                    'direção': 'Crescente' if tendencia > 0 else 'Decrescente'
                }
        
        return temporal_stats
    
    def detect_anomalies(self, df):
        """Detecta transações anômalas usando métodos estatísticos"""
        anomalies = {}
        
        # Anomalias usando IQR (Interquartile Range)
        Q1 = df['Valor'].quantile(0.25)
        Q3 = df['Valor'].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        
        transacoes_anomalas = df[(df['Valor'] < limite_inferior) | (df['Valor'] > limite_superior)]
        
        anomalies['iqr'] = {
            'quantidade': len(transacoes_anomalas),
            'transacoes': transacoes_anomalas[['Data', 'Estabelecimento', 'Valor', 'Categoria_Estabelecimento']],
            'limites': {'inferior': limite_inferior, 'superior': limite_superior}
        }
        
        # Gastos muito acima da média por categoria
        gastos_por_categoria = df[df['Valor'] < 0].groupby('Categoria_Estabelecimento')['Valor'].agg(['mean', 'std'])
        
        anomalies_categoria = []
        for _, row in df[df['Valor'] < 0].iterrows():
            categoria = row['Categoria_Estabelecimento']
            valor_abs = abs(row['Valor'])
            
            if categoria in gastos_por_categoria.index:
                media_categoria = abs(gastos_por_categoria.loc[categoria, 'mean'])
                std_categoria = gastos_por_categoria.loc[categoria, 'std']
                
                if valor_abs > media_categoria + (2 * std_categoria):  # 2 desvios padrão
                    anomalies_categoria.append({
                        'data': row['Data'],
                        'estabelecimento': row['Estabelecimento'],
                        'valor': row['Valor'],
                        'categoria': categoria,
                        'media_categoria': -media_categoria,
                        'desvio': (valor_abs - media_categoria) / std_categoria if std_categoria > 0 else 0
                    })
        
        anomalies['categoria'] = anomalies_categoria
        
        # Dias sem movimentação
        periodo_completo = pd.date_range(start=df['Data'].min(), end=df['Data'].max(), freq='D')
        dias_com_transacao = set(df['Data'].dt.date)
        dias_sem_movimento = [dia.date() for dia in periodo_completo if dia.date() not in dias_com_transacao]
        
        anomalies['dias_sem_movimento'] = {
            'quantidade': len(dias_sem_movimento),
            'dias': dias_sem_movimento
        }
        
        return anomalies
    
    def generate_recommendations(self, indicators, df):
        """Gera recomendações personalizadas baseadas na análise"""
        recommendations = {
            'urgentes': [],
            'importantes': [],
            'sugestoes': [],
            'metas': {}
        }
        
        # Recomendações urgentes
        if indicators['taxa_poupanca'] < 0:
            recommendations['urgentes'].append({
                'titulo': 'Saldo Negativo Crítico',
                'descricao': f'Taxa de poupança em {indicators["taxa_poupanca"]:.1f}%. Gastos superam entradas.',
                'acao': 'Revisar imediatamente todos os gastos não essenciais'
            })
        
        if indicators['concentracao_top5_gastos'] > 70:
            recommendations['urgentes'].append({
                'titulo': 'Gastos Altamente Concentrados',
                'descricao': f'{indicators["concentracao_top5_gastos"]:.1f}% dos gastos em apenas 5 transações.',
                'acao': 'Diversificar e reduzir gastos principais'
            })
        
        # Recomendações importantes
        if 0 <= indicators['taxa_poupanca'] < 10:
            recommendations['importantes'].append({
                'titulo': 'Taxa de Poupança Baixa',
                'descricao': f'Taxa atual de {indicators["taxa_poupanca"]:.1f}%, abaixo do recomendado (15-20%).',
                'acao': 'Estabelecer meta de redução de gastos em 10-15%'
            })
        
        if indicators['ticket_medio_gasto'] > 200:
            recommendations['importantes'].append({
                'titulo': 'Ticket Médio Alto',
                'descricao': f'Gasto médio por transação: R$ {indicators["ticket_medio_gasto"]:.2f}',
                'acao': 'Considerar compras menores e mais frequentes'
            })
        
        # Sugestões gerais
        if indicators['estabelecimentos_unicos'] > 20:
            recommendations['sugestoes'].append({
                'titulo': 'Boa Diversificação',
                'descricao': f'Você utiliza {indicators["estabelecimentos_unicos"]} estabelecimentos diferentes.',
                'acao': 'Manter diversificação, mas focar nos mais econômicos'
            })
        
        # Análise de gastos recorrentes
        establishment_analysis = self.get_establishment_analysis(df)
        if len(establishment_analysis['recorrentes']) > 0:
            top_recorrente = establishment_analysis['recorrentes'].iloc[0]
            recommendations['importantes'].append({
                'titulo': 'Gasto Recorrente Principal',
                'descricao': f'{establishment_analysis["recorrentes"].index[0]}: R$ {top_recorrente["Valor_Total"]:.2f} em {top_recorrente["Dias_Ativos"]} dias',
                'acao': 'Renegociar ou buscar alternativa mais econômica'
            })
        
        # Metas sugeridas
        recommendations['metas'] = {
            'taxa_poupanca_objetivo': max(15, indicators['taxa_poupanca'] + 5),
            'reducao_gasto_diario': indicators['gasto_medio_diario'] * 0.9,
            'limite_ticket_medio': indicators['ticket_medio_gasto'] * 0.85,
            'meta_economia_mensal': indicators['gasto_medio_diario'] * 30 * 0.1  # 10% de economia
        }
        
        return recommendations
    
    def export_summary(self, df, indicators, filename='analise_financeira_summary.xlsx'):
        """Exporta resumo completo para Excel"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Resumo executivo
            resumo = pd.DataFrame([
                ['Total Entradas', f"R$ {indicators['total_entradas']:,.2f}"],
                ['Total Saídas', f"R$ {indicators['total_saidas']:,.2f}"],
                ['Saldo Líquido', f"R$ {indicators['saldo_liquido']:,.2f}"],
                ['Taxa Poupança', f"{indicators['taxa_poupanca']:.1f}%"],
                ['Gasto Médio Diário', f"R$ {indicators['gasto_medio_diario']:,.2f}"],
                ['Ticket Médio Gasto', f"R$ {indicators['ticket_medio_gasto']:,.2f}"],
                ['Total Transações', indicators['total_transacoes']],
                ['Estabelecimentos Únicos', indicators['estabelecimentos_unicos']]
            ], columns=['Indicador', 'Valor'])
            resumo.to_excel(writer, sheet_name='Resumo_Executivo', index=False)
            
            # Dados processados
            df.to_excel(writer, sheet_name='Dados_Processados', index=False)
            
            # Análise por categoria
            category_analysis = self.get_category_analysis(df)
            category_analysis['gastos'].to_excel(writer, sheet_name='Gastos_por_Categoria')
            
            # Top estabelecimentos
            establishment_analysis = self.get_establishment_analysis(df)
            establishment_analysis['gastos'].head(20).to_excel(writer, sheet_name='Top_Estabelecimentos')
            
        return filename
import pandas as pd
import numpy as np
import urllib
from sqlalchemy import create_engine

df = pd.read_csv('C:/Users/Rafael/OneDrive/Documentos/hospitalar.csv')

# ── Limpeza original ──────────────────────────────────────────────
df = df.drop_duplicates()
df['Admission_Deposit'] = pd.to_numeric(df['Admission_Deposit'], errors='coerce')
df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
df['Bed_Grade'] = df['Bed_Grade'].replace(np.nan, 0)

df.rename(columns={
    'Admission_Deposit': 'deposito',
    'Age': 'idade',
    'Type_of_Admission': 'tipo_admissao'
}, inplace=True)

# ── Colunas novas para enriquecer o dashboard ─────────────────────

# 1. Faixa etária (para gráfico de barras por idade)
bins = [0, 17, 35, 50, 65, 120]
labels = ['0-17', '18-35', '36-50', '51-65', '65+']
df['faixa_etaria'] = pd.cut(df['idade'], bins=bins, labels=labels, right=True)

# 2. Classificação do depósito (ticket do paciente)
df['classe_deposito'] = pd.cut(
    df['deposito'],
    bins=[0, 3000, 6000, 10000, 99999],
    labels=['Baixo', 'Médio', 'Alto', 'Premium']
)

# 3. Flag de paciente idoso (65+)
df['paciente_idoso'] = df['idade'].apply(lambda x: 'Sim' if x >= 65 else 'Não')

# 4. Tempo de permanência simulado (se não existir no CSV)
# Se já tiver a coluna 'Stay' no CSV, PULE este bloco
if 'Stay' not in df.columns:
    np.random.seed(42)
    df['dias_internacao'] = np.random.choice(
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 25, 30],
        size=len(df)
    )
else:
    # Converte o Stay original (ex: "0-10", "11-20") em número médio
    def parse_stay(s):
        try:
            parts = str(s).split('-')
            return (int(parts[0]) + int(parts[1])) / 2
        except:
            return np.nan
    df['dias_internacao'] = df['Stay'].apply(parse_stay)

# 5. Custo por dia de internação
df['custo_por_dia'] = (df['deposito'] / df['dias_internacao']).round(2)

# 6. Mês de admissão simulado (para análise temporal)
# Se tiver coluna de data real no CSV, use ela no lugar
if 'data_admissao' not in df.columns:
    np.random.seed(7)
    df['mes_admissao'] = np.random.randint(1, 13, size=len(df))
    df['nome_mes'] = df['mes_admissao'].map({
        1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun',
        7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'
    })

# 7. Score de risco (combina gravidade + tipo admissão)
gravidade_map = {'Minor': 1, 'Moderate': 2, 'Extreme': 3}
admissao_map = {'Emergency': 3, 'Urgent': 2, 'Trauma': 2, 'Elective': 1}

df['score_gravidade'] = df['Severity_of_Illness'].map(gravidade_map).fillna(1)
df['score_admissao'] = df['tipo_admissao'].map(admissao_map).fillna(1)
df['score_risco'] = df['score_gravidade'] + df['score_admissao']

df['nivel_risco'] = df['score_risco'].apply(
    lambda x: 'Crítico' if x >= 5 else ('Alto' if x >= 4 else ('Médio' if x >= 3 else 'Baixo'))
)

print("Colunas finais:")
print(df.dtypes)
print(f"\nTotal de registros: {len(df)}")
print(df.head())

# ── Envio para SQL Server ─────────────────────────────────────────
servidor = 'localhost'
banco = 'HospitalDB'

dados_conexao = (
    f"Driver={{ODBC Driver 17 for SQL Server}};"
    f"Server={servidor};"
    f"Database={banco};"
    f"Trusted_Connection=yes;"
)
params = urllib.parse.quote_plus(dados_conexao)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

try:
    df.to_sql('pacientes', con=engine, if_exists='replace', index=False)
    print("\nSUCESSO! Tabela 'pacientes' enviada com todas as colunas novas.")
except Exception as e:
    print(f"Erro: {e}")
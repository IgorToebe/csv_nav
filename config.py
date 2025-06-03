# config.py
import os
from dotenv import load_dotenv

load_dotenv() # Carrega variáveis de.env se existir

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_PATH = "nfs_data.db"
CSV_FILES = {
    "cabecalho": "202401_NFs_Cabecalho.csv",
    "itens": "202401_NFs_Itens.csv"
}

# Definição explícita do esquema para guiar o carregamento e as consultas
# Isso pode ser gerado inicialmente pelo DataCuratorAgent e depois codificado aqui
# ou mantido dinamicamente no estado do LangGraph se a curadoria for frequente.
# Para este exemplo, vamos definir um esquema básico esperado.
EXPECTED_SCHEMA = {
    "nfs_cabecalho": {
        "columns": {
            "CHAVE DE ACESSO": "TEXT", "MODELO": "TEXT", "SÉRIE": "TEXT", "NÚMERO": "INTEGER",
            "NATUREZA DA OPERAÇÃO": "TEXT", "DATA EMISSÃO": "TEXT", "EVENTO MAIS RECENTE": "TEXT",
            "DATA/HORA EVENTO MAIS RECENTE": "TEXT", "CPF/CNPJ Emitente": "TEXT",
            "RAZÃO SOCIAL EMITENTE": "TEXT", "INSCRIÇÃO ESTADUAL EMITENTE": "TEXT",
            "UF EMITENTE": "TEXT", "MUNICÍPIO EMITENTE": "TEXT", "CNPJ DESTINATÁRIO": "TEXT",
            "NOME DESTINATÁRIO": "TEXT", "UF DESTINATÁRIO": "TEXT",
            "INDICADOR IE DESTINATÁRIO": "TEXT", "DESTINO DA OPERAÇÃO": "TEXT",
            "CONSUMIDOR FINAL": "TEXT", "PRESENÇA DO COMPRADOR": "TEXT", "VALOR NOTA FISCAL": "REAL"
        },
        "primary_key": "CHAVE DE ACESSO",
        "csv_file": CSV_FILES["cabecalho"]
    },
    "nfs_itens": {
        "columns": {
            # Adicionar um ID autoincrementável para a tabela de itens
            "ID_ITEM": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "CHAVE DE ACESSO": "TEXT", "MODELO": "TEXT", "SÉRIE": "TEXT", "NÚMERO": "INTEGER",
            "NATUREZA DA OPERAÇÃO": "TEXT", "DATA EMISSÃO": "TEXT",
            "CPF/CNPJ Emitente": "TEXT", "RAZÃO SOCIAL EMITENTE": "TEXT",
            "INSCRIÇÃO ESTADUAL EMITENTE": "TEXT", "UF EMITENTE": "TEXT",
            "MUNICÍPIO EMITENTE": "TEXT", "CNPJ DESTINATÁRIO": "TEXT",
            "NOME DESTINATÁRIO": "TEXT", "UF DESTINATÁRIO": "TEXT",
            "INDICADOR IE DESTINATÁRIO": "TEXT", "DESTINO DA OPERAÇÃO": "TEXT",
            "CONSUMIDOR FINAL": "TEXT", "PRESENÇA DO COMPRADOR": "TEXT",
            "NÚMERO PRODUTO": "TEXT", "DESCRIÇÃO DO PRODUTO/SERVIÇO": "TEXT",
            "CÓDIGO NCM/SH": "TEXT", "NCM/SH (TIPO DE PRODUTO)": "TEXT", "CFOP": "TEXT",
            "QUANTIDADE": "REAL", "UNIDADE": "TEXT", "VALOR UNITÁRIO": "REAL", "VALOR TOTAL": "REAL"
        },
        # ID_ITEM será a PK, CHAVE DE ACESSO é FK
        "primary_key": "ID_ITEM",
        "foreign_keys": ["CHAVE DE ACESSO"],  # Specify the foreign key(s) here
        "csv_file": CSV_FILES["itens"]
    }
}

# Mapeamento de tipos Pandas para SQLAlchemy para uso no to_sql dtype
# Adicionar mais tipos conforme necessário
PANDAS_TO_SQLALCHEMY_TYPES = {
    "TEXT": "TEXT", # Mapeia para TEXT do SQLite
    "INTEGER": "INTEGER", # Mapeia para INTEGER do SQLite
    "REAL": "REAL" # Mapeia para REAL do SQLite
}
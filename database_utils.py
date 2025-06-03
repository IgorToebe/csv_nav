# database_utils.py
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import Text, Integer, Float # Importar tipos SQLAlchemy
from config import DB_PATH, PANDAS_TO_SQLALCHEMY_TYPES

def get_db_connection():
    """Retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def get_sqlalchemy_engine():
    """Retorna um engine SQLAlchemy para o banco de dados SQLite."""
    return create_engine(f"sqlite:///{DB_PATH}")

def create_table_from_schema(conn, table_name, schema_info):
    """Cria uma tabela no banco de dados se ela não existir."""
    cursor = conn.cursor()
    columns_definitions = []
    for col_name, col_type in schema_info["columns"].items():
        # Tratar chave primária diretamente na definição da coluna se for simples
        if schema_info.get("primary_key") == col_name and "PRIMARY KEY" not in col_type.upper():
            columns_definitions.append(f'"{col_name}" {col_type} PRIMARY KEY')
        elif "PRIMARY KEY" in col_type.upper(): # Se já estiver na definição (ex: ID_ITEM INTEGER PRIMARY KEY AUTOINCREMENT)
             columns_definitions.append(f'"{col_name}" {col_type}')
        else:
            columns_definitions.append(f'"{col_name}" {col_type}')

    # Adicionar chaves estrangeiras se definidas
    foreign_key_definitions = []
    if "foreign_keys" in schema_info:
        for fk in schema_info["foreign_keys"]:
            foreign_key_definitions.append(
                f'FOREIGN KEY ("{fk["column"]}") REFERENCES "{fk["references_table"]}" ("{fk["references_column"]}")'
            )
    
    all_definitions = columns_definitions + foreign_key_definitions
    create_table_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(all_definitions)});'
    
    try:
        cursor.execute(create_table_sql)
        conn.commit()
        # print(f"Tabela '{table_name}' verificada/criada com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao criar tabela {table_name}: {e}")
        print(f"SQL: {create_table_sql}")


def load_df_to_table(df, table_name, engine, schema_info):
    """Carrega um DataFrame do Pandas para uma tabela SQL, substituindo se existir."""
    
    # Sanitizar nomes de colunas do DataFrame para corresponder ao esquema esperado
    # Removendo caracteres problemáticos e garantindo consistência de maiúsculas/minúsculas
    # (O esquema em config.py usa nomes de colunas como estão nos CSVs)
    df_columns_sanitized = {col: col.replace('/', '_').replace(' ', '_') for col in df.columns}
    df.rename(columns=df_columns_sanitized, inplace=True)

    # Construir o mapa dtype para SQLAlchemy com base no schema_info
    dtype_map_sqlalchemy = {}
    for col_name_schema, col_type_schema in schema_info["columns"].items():
        # O nome da coluna no schema_info deve corresponder ao nome sanitizado no df
        # (ou o nome original se não precisou de sanitização)
        # Para simplificar, assumimos que os nomes no schema_info já são os "corretos" para o DB
        
        # Mapear tipo de string para tipo SQLAlchemy
        if col_type_schema == "TEXT":
            dtype_map_sqlalchemy[col_name_schema] = Text
        elif col_type_schema == "INTEGER":
             dtype_map_sqlalchemy[col_name_schema] = Integer
        elif col_type_schema == "REAL":
            dtype_map_sqlalchemy[col_name_schema] = Float
        # Adicionar outros mapeamentos se necessário

    # Garantir que apenas colunas definidas no esquema sejam enviadas para to_sql
    # e que a ordem das colunas no DataFrame corresponda à ordem esperada (opcional, mas bom para consistência)
    df_to_load = df[[col for col in schema_info["columns"].keys() if col in df.columns and col!= "ID_ITEM"]]


    df_to_load.to_sql(table_name, engine, if_exists='replace', index=False, dtype=dtype_map_sqlalchemy)
    # print(f"Dados carregados na tabela '{table_name}'.")


def get_table_info_for_prompt(engine):
    """Obtém informações do esquema de todas as tabelas para o prompt do LLM."""
    with engine.connect() as connection:
        inspector = pd.io.sql.SQLDatabase(engine).inspector
        table_names = inspector.get_table_names()
        table_info_parts = []
        for table_name in table_names:
            # Obter a instrução CREATE TABLE
            # A forma de obter o CREATE TABLE pode variar um pouco com SQLAlchemy puro
            # Uma maneira simples é consultar sqlite_master
            try:
                result = connection.execute(text(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';"))
                create_statement = result.scalar_one_or_none()
                if create_statement:
                    table_info_parts.append(create_statement)
            except Exception as e:
                print(f"Erro ao obter schema para {table_name}: {e}")
                # Fallback para colunas se CREATE TABLE falhar
                columns = inspector.get_columns(table_name)
                col_defs = [f"{col['name']} {col['type']}" for col in columns]
                table_info_parts.append(f"CREATE TABLE {table_name} ({', '.join(col_defs)});")

        return "\n\n".join(table_info_parts)
# agent_system.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
#from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional
import pandas as pd
import re
import sqlite3

from config import GOOGLE_API_KEY, EXPECTED_SCHEMA
from database_utils import get_sqlalchemy_engine, create_table_from_schema, load_df_to_table, get_table_info_for_prompt

# Definição do Estado do Grafo
class AgentState(TypedDict):
    user_query: str
    database_schema_info: Optional[str] = None # Informação do esquema para o LLM
    generated_sql_query: Optional[str] = None
    sql_query_result: Optional[str] = None
    formatted_answer: Optional[str] = None
    error_message: Optional[str] = None
    data_loaded: bool = False # Flag para controlar o carregamento inicial

# Inicialização do LLM Gemini
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=GOOGLE_API_KEY, temperature=0.1)
db_engine = get_sqlalchemy_engine() # Usar engine SQLAlchemy para SQLDatabase e to_sql
sql_db_utility = SQLDatabase(db_engine)

# --- Nós dos Agentes ---

def data_curator_and_loader_node(state: AgentState) -> AgentState:
    """
    Agente/Nó responsável por garantir que o esquema do BD esteja criado
    e os dados CSV carregados. Executado apenas uma vez por sessão ou se necessário.
    """
    if state.get("data_loaded", False):
        # print("Dados já carregados, pulando curadoria e carregamento.")
        return {"database_schema_info": get_table_info_for_prompt(db_engine), "data_loaded": True}

    # print("Iniciando curadoria de dados e carregamento...")
    all_schemas_created = True
    all_data_loaded = True
    
    # Usar conexão sqlite3 para CREATE TABLE, pois SQLAlchemy pode ter problemas com IF NOT EXISTS em algumas versões/dialetos
    conn_sqlite = sqlite3.connect(DB_PATH)

    for table_name, schema_info in EXPECTED_SCHEMA.items():
        try:
            create_table_from_schema(conn_sqlite, table_name, schema_info)
            
            # Carregar dados do CSV
            csv_path = schema_info["csv_file"]
            # Especificar colunas a serem lidas para evitar problemas com colunas extras/faltantes
            # e garantir que os nomes das colunas no DataFrame correspondam ao esquema
            df_cols_to_read = list(schema_info["columns"].keys())
            # Remover colunas autoincrementáveis da leitura do CSV se existirem
            df_cols_to_read =[col].upper()

            df = pd.read_csv(csv_path, usecols=lambda c: c in df_cols_to_read, low_memory=False)
            
            # Renomear colunas do DataFrame para corresponder exatamente ao esquema (case-sensitive)
            # Isso é importante porque os nomes das colunas no CSV podem ter variações
            rename_map = {csv_col: schema_col for csv_col in df.columns 
                          for schema_col in schema_info["columns"].keys() 
                          if csv_col.strip().upper() == schema_col.strip().upper()}
            df.rename(columns=rename_map, inplace=True)
            
            # Garantir que apenas as colunas definidas no esquema sejam passadas para to_sql
            df_final_cols = [col for col in schema_info["columns"].keys() if col in df.columns and "AUTOINCREMENT" not in schema_info["columns"][col].upper()]
            df_to_load = df[df_final_cols]

            load_df_to_table(df_to_load, table_name, db_engine, schema_info)

        except Exception as e:
            error_msg = f"Erro ao processar/carregar tabela {table_name}: {str(e)}"
            print(error_msg)
            all_schemas_created = False
            all_data_loaded = False
            # Retornar estado de erro imediatamente se algo falhar aqui
            return {"error_message": error_msg, "data_loaded": False}
    
    conn_sqlite.close()

    if all_schemas_created and all_data_loaded:
        # print("Curadoria e carregamento de dados concluídos.")
        return {"database_schema_info": get_table_info_for_prompt(db_engine), "data_loaded": True}
    else:
        return {"error_message": "Falha na curadoria ou carregamento de dados.", "data_loaded": False}


def db_specialist_query_node(state: AgentState) -> AgentState:
    """Agente/Nó que gera e executa a consulta SQL."""
    user_query = state["user_query"]
    db_schema = state.get("database_schema_info")

    if not db_schema:
        return {"error_message": "Esquema do banco de dados não disponível para gerar consulta."}

    # print(f"DB Specialist: Gerando SQL para: {user_query}")
    # print(f"DB Schema para prompt: {db_schema}")

    prompt_template_sql = ChatPromptTemplate.from_messages()

    sql_generation_chain = prompt_template_sql | llm | StrOutputParser()
    
    try:
        generated_sql = sql_generation_chain.invoke({
            "db_schema": db_schema,
            "user_question": user_query
        })
        # print(f"SQL Gerado (bruto): {generated_sql}")

        # Limpeza básica do SQL gerado (remover ```sql e ```)
        cleaned_sql = re.sub(r"```sql\n(.*)\n```", r"\1", generated_sql, flags=re.DOTALL).strip()
        cleaned_sql = cleaned_sql.replace("```", "").strip()
        # print(f"SQL Limpo: {cleaned_sql}")

        # Executar a consulta
        query_execution_tool = QuerySQLDatabaseTool(db=sql_db_utility)
        query_result = query_execution_tool.invoke(cleaned_sql)
        # print(f"Resultado da Consulta: {query_result}")
        return {"generated_sql_query": cleaned_sql, "sql_query_result": str(query_result)}
    except Exception as e:
        error_msg = f"Erro ao gerar ou executar SQL: {str(e)}\nSQL Tentado: {cleaned_sql if 'cleaned_sql' in locals() else 'N/A'}"
        print(error_msg)
        return {"error_message": error_msg, "generated_sql_query": cleaned_sql if 'cleaned_sql' in locals() else None}


def output_formatter_node(state: AgentState) -> AgentState:
    """Agente/Nó que formata o resultado da consulta em linguagem natural."""
    user_question = state["user_query"]
    generated_sql = state.get("generated_sql_query")
    sql_result = state.get("sql_query_result")
    error = state.get("error_message")

    if error:
        # print(f"Output Formatter: Formatando erro: {error}")
        # Tentar obter uma explicação mais amigável do erro do LLM
        error_prompt = ChatPromptTemplate.from_messages([
            ("system", "Você é um assistente de IA que explica erros de forma amigável. "
                       "O usuário fez uma pergunta e ocorreu um erro ao processá-la. "
                       "Explique o erro de forma simples e, se possível, sugira como o usuário pode reformular a pergunta ou qual pode ser o problema."),
            ("human", "Pergunta do Usuário: {user_question}\nErro ocorrido: {error_details}")
        ])
        error_formatting_chain = error_prompt | llm | StrOutputParser()
        formatted_error = error_formatting_chain.invoke({"user_question": user_question, "error_details": error})
        return {"formatted_answer": formatted_error}

    if sql_result is None: # Pode acontecer se o nó anterior falhar silenciosamente
        return {"formatted_answer": "Desculpe, não consegui obter um resultado para sua pergunta."}

    
    prompt_template_format = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente de IA que formata respostas de consultas SQL. "
                   "Se os resultados da consulta forem encontrados, formate-os de forma clara e amigável. "
                   "Se nenhum dado for encontrado, informe que nenhum dado foi encontrado. "
                   "Não repita a consulta SQL na sua resposta final ao usuário.")

    ])
    formatting_chain = prompt_template_format | llm | StrOutputParser()
    formatted_answer = formatting_chain.invoke({
        "user_question": user_question,
        "generated_sql_query": generated_sql,
        "sql_query_result": sql_result
    })
    # print(f"Resposta Formatada: {formatted_answer}")
    return {"formatted_answer": formatted_answer}

# --- Definição e Compilação do Grafo LangGraph ---
workflow = StateGraph(AgentState)

# Adicionar nós
workflow.add_node("data_loader_curator", data_curator_and_loader_node)
workflow.add_node("db_query_specialist", db_specialist_query_node)
workflow.add_node("output_formatter", output_formatter_node)

# Definir o ponto de entrada
workflow.set_entry_point("data_loader_curator")

# Definir arestas condicionais e normais
def should_proceed_after_loading(state: AgentState) -> str:
    if state.get("error_message"): # Erro no carregamento
        return "output_formatter" # Vai direto formatar o erro
    if state.get("data_loaded"):
        return "db_query_specialist"
    return "output_formatter" # Caso inesperado, formatar um erro genérico

workflow.add_conditional_edges(
    "data_loader_curator",
    should_proceed_after_loading,
    {
        "db_query_specialist": "db_query_specialist",
        "output_formatter": "output_formatter" # Para tratar erros de carregamento
    }
)
workflow.add_edge("db_query_specialist", "output_formatter")
workflow.add_edge("output_formatter", END) # Fim do fluxo

# Compilar o grafo
app_graph = workflow.compile()

# Função para invocar o sistema de agentes
def run_agent_system(user_input: str, current_state: Optional = None) -> str:
    """
    Executa o sistema de agentes com a entrada do usuário.
    Mantém o estado 'data_loaded' entre as chamadas.
    """
    initial_graph_state = {"user_query": user_input}
    if current_state and "data_loaded" in current_state:
        initial_graph_state["data_loaded"] = current_state["data_loaded"]
    
    final_state = app_graph.invoke(initial_graph_state)
    
    # Retornar o estado completo para que main_app possa atualizar st.session_state['agent_graph_internal_state']
    return final_state
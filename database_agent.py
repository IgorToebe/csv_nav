# -*- coding: utf-8 -*-
import sqlite3
import logging
import os
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
# Use the recommended create_sql_agent approach
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_FILE = "notas_fiscais.db"

def get_db_connection():
    """ Retorna um objeto SQLDatabase conectado ao banco SQLite. """
    if not os.path.exists(DB_FILE):
        logging.error(f"Arquivo do banco de dados não encontrado: {DB_FILE}")
        raise FileNotFoundError(f"Arquivo do banco de dados não encontrado: {DB_FILE}")
    
    db_uri = f"sqlite:///{DB_FILE}"
    try:
        db = SQLDatabase.from_uri(db_uri)
        logging.info(f"Conexão Langchain SQLDatabase estabelecida com {DB_FILE}")
        logging.info(f"Tabelas encontradas: {db.get_table_names()}")
        return db
    except Exception as e:
        logging.error(f"Erro ao criar SQLDatabase a partir da URI {db_uri}: {e}")
        raise

def execute_direct_sql(sql_query: str):
    """ Executa uma query SQL diretamente no banco e retorna os resultados. """
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        logging.info(f"Executando SQL direto: {sql_query}")
        cursor.execute(sql_query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description] if cursor.description else []
        conn.commit()
        logging.info(f"SQL direto executado com sucesso. {len(results)} linhas retornadas.")
        formatted_results = [dict(zip(column_names, row)) for row in results]
        return formatted_results
    except sqlite3.Error as e:
        logging.error(f"Erro ao executar SQL direto \n{sql_query}\n: {e}")
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()

def query_database_agent(question: str, google_api_key: str):
    """ 
    Usa um agente Langchain SQL para traduzir a pergunta em SQL, executar e retornar o resultado.
    """
    if not google_api_key:
        logging.error("Chave da API do Google não fornecida.")
        return {"error": "Chave da API do Google não fornecida."}

    try:
        db = get_db_connection()
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=google_api_key,
            temperature=0,
            convert_system_message_to_human=True
        )
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        # Criar o Agente SQL com handle_parsing_errors=True
        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True, 
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True # Adicionado para tratar erros de parsing
        )

        logging.info(f"Executando agente SQL com a pergunta: {question}")
        prompt_with_context = f"Responda em português. Analise as tabelas nfs_cabecalho (cabeçalho das notas fiscais) e nfs_itens (itens das notas fiscais) que estão relacionadas pela coluna CHAVE_DE_ACESSO. Questão: {question}"
        
        response = agent_executor.run(prompt_with_context)
        logging.info(f"Agente SQL retornou a resposta.")
        return {"result": response}

    except FileNotFoundError as e:
         logging.error(f"Erro no agente SQL: {e}")
         return {"error": str(e)}
    except Exception as e:
        logging.error(f"Erro inesperado no agente SQL: {e}", exc_info=True)
        # Retornar o erro específico para o usuário, se possível
        error_detail = str(e)
        # Verificar se é um erro de parsing que não foi tratado (apesar do handle_parsing_errors)
        if "Could not parse LLM output:" in error_detail:
             error_detail = f"Erro ao interpretar a resposta do modelo: {error_detail}"
        return {"error": f"Erro inesperado ao processar a consulta: {error_detail}"}

# Bloco para teste direto do script (opcional)
if __name__ == '__main__':
    print("--- Teste do Agente Especialista em Banco de Dados ---")
    if not os.path.exists(DB_FILE):
        print(f"Erro: Banco de dados {DB_FILE} não encontrado. Execute data_ingestion.py primeiro.")
    else:
        print("\nTeste 1: Execução SQL Direta (Contar cabeçalhos)")
        direct_result = execute_direct_sql("SELECT COUNT(*) as total FROM nfs_cabecalho;")
        print(f"Resultado SQL Direto: {direct_result}")

        print("\nTeste 2: Consulta com Agente SQL")
        google_key = os.environ.get("GOOGLE_API_KEY")
        if not google_key:
            print("AVISO: Chave GOOGLE_API_KEY não encontrada no ambiente. Pulando teste do agente SQL.")
            print("Defina a variável de ambiente GOOGLE_API_KEY para testar.")
        else:
            test_question = "Qual o valor total das notas fiscais emitidas para o destinatário com CNPJ 378257000181?"
            print(f"Pergunta: {test_question}")
            agent_result = query_database_agent(test_question, google_key)
            print(f"Resultado do Agente: {agent_result}")
            
            test_question_2 = "Liste os 3 produtos mais vendidos (em quantidade) e suas quantidades totais."
            print(f"\nPergunta 2: {test_question_2}")
            agent_result_2 = query_database_agent(test_question_2, google_key)
            print(f"Resultado do Agente 2: {agent_result_2}")

    print("\n--- Teste Concluído ---")


# -*- coding: utf-8 -*-
import streamlit as st
import os
import tempfile
import logging
import time

# Importar funções dos módulos dos agentes
from data_ingestion import create_connection, create_tables, ingest_data, DB_FILE
from database_agent import query_database_agent
from output_formatter import format_response

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Limpeza do Banco de Dados na Inicialização ---
# Garante que começamos com um banco de dados limpo a cada execução completa do script
try:
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        logging.info(f"Banco de dados anterior ({DB_FILE}) removido com sucesso na inicialização.")
    else:
        logging.info(f"Nenhum banco de dados anterior ({DB_FILE}) encontrado para remover na inicialização.")
except Exception as e:
    # Logar o erro mas não impedir a execução da app
    logging.error(f"Erro ao tentar remover o banco de dados {DB_FILE} na inicialização: {e}")

# --- Configuração da Página Streamlit ---
st.set_page_config(page_title="Chat com Notas Fiscais", page_icon="🧾", layout="wide")
st.title("📊 Chat com Notas Fiscais usando Gemini + SQLite")

# --- Estado da Sessão --- 
def initialize_session_state():
    # Resetar estados relacionados à ingestão/DB, pois o DB foi limpo
    if "history" not in st.session_state:
        st.session_state.history = []
    if "google_api_key" not in st.session_state:
        st.session_state.google_api_key = None
    # Sempre iniciar como não completo após a limpeza do DB
    st.session_state.ingestion_complete = False 
    st.session_state.ingestion_in_progress = False
    st.session_state.uploaded_files_paths = {"cabecalho": None, "itens": None}
    st.session_state.db_exists = False # DB foi removido, então não existe inicialmente

initialize_session_state()

# --- Barra Lateral (Sidebar) ---
st.sidebar.header("Configuração")

# Chave da API do Google
st.session_state.google_api_key = st.sidebar.text_input(
    "🔑 Google Gemini API Key", 
    type="password", 
    value=st.session_state.google_api_key or "",
    help="Insira sua chave da API do Google Gemini."
)

if not st.session_state.google_api_key:
    st.sidebar.warning("🔑 Por favor, insira sua chave da API do Google Gemini para habilitar o chat.")

st.sidebar.divider()

st.sidebar.header("Upload de Arquivos CSV")

# Upload do arquivo de Cabeçalho
uploaded_cabecalho = st.sidebar.file_uploader(
    "1. Envie o arquivo `*_NFs_Cabecalho.csv`", 
    type=["csv"],
    key="uploader_cabecalho"
)

# Upload do arquivo de Itens
uploaded_itens = st.sidebar.file_uploader(
    "2. Envie o arquivo `*_NFs_Itens.csv`", 
    type=["csv"],
    key="uploader_itens"
)

# Botão para iniciar ingestão
# Habilitar botão apenas se arquivos foram carregados E ingestão não está completa/em progresso
if uploaded_cabecalho and uploaded_itens and not st.session_state.ingestion_complete and not st.session_state.ingestion_in_progress:
    if st.sidebar.button("Processar Arquivos e Ingerir Dados", key="ingest_button"):
        st.session_state.ingestion_in_progress = True
        st.session_state.ingestion_complete = False
        st.rerun() # Reinicia para mostrar o status de progresso
elif st.session_state.ingestion_complete:
     st.sidebar.info("Dados já processados. Para reprocessar, reinicie a aplicação ou atualize a página.")

# --- Lógica de Ingestão --- 
if st.session_state.ingestion_in_progress:
    with st.spinner("Processando arquivos e ingerindo dados no banco de dados SQLite..."):
        try:
            # Salvar arquivos temporariamente para ingestão
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_cabecalho:
                tmp_cabecalho.write(uploaded_cabecalho.getvalue())
                st.session_state.uploaded_files_paths["cabecalho"] = tmp_cabecalho.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_itens:
                tmp_itens.write(uploaded_itens.getvalue())
                st.session_state.uploaded_files_paths["itens"] = tmp_itens.name

            logging.info("Iniciando processo de ingestão...")
            # Garantir que o DB seja criado/conectado aqui
            conn = create_connection() # Usa DB_FILE ('notas_fiscais.db')
            if conn:
                create_tables(conn) # Cria tabelas se não existirem
                success = ingest_data(conn, st.session_state.uploaded_files_paths["cabecalho"], st.session_state.uploaded_files_paths["itens"])
                conn.close()
                if success:
                    st.session_state.ingestion_complete = True
                    st.session_state.db_exists = True
                    st.sidebar.success("Dados ingeridos com sucesso! ✅")
                    logging.info("Ingestão concluída com sucesso.")
                else:
                    st.sidebar.error("Falha na ingestão dos dados. Verifique os logs.")
                    logging.error("Falha durante a ingestão de dados.")
                    # Se falhar, garantir que o estado reflita isso
                    st.session_state.ingestion_complete = False
                    st.session_state.db_exists = os.path.exists(DB_FILE) # Verificar se o arquivo foi criado mesmo com falha
            else:
                st.sidebar.error("Não foi possível conectar ao banco de dados.")
                logging.error("Falha ao criar conexão com o banco de dados para ingestão.")
                st.session_state.ingestion_complete = False
                st.session_state.db_exists = False
        except Exception as e:
            st.sidebar.error(f"Erro durante o processamento: {e}")
            logging.error(f"Erro excepcional durante ingestão: {e}", exc_info=True)
            st.session_state.ingestion_complete = False
            st.session_state.db_exists = os.path.exists(DB_FILE)
        finally:
            st.session_state.ingestion_in_progress = False
            # Limpar arquivos temporários
            if st.session_state.uploaded_files_paths["cabecalho"] and os.path.exists(st.session_state.uploaded_files_paths["cabecalho"]):
                 try: os.remove(st.session_state.uploaded_files_paths["cabecalho"]); logging.info("Arquivo temp cabecalho removido.")
                 except: pass
                 st.session_state.uploaded_files_paths["cabecalho"] = None
            if st.session_state.uploaded_files_paths["itens"] and os.path.exists(st.session_state.uploaded_files_paths["itens"]):
                 try: os.remove(st.session_state.uploaded_files_paths["itens"]); logging.info("Arquivo temp itens removido.")
                 except: pass
                 st.session_state.uploaded_files_paths["itens"] = None
            st.rerun() # Atualiza a interface após a ingestão (sucesso ou falha)

# Mensagem de status da ingestão
if st.session_state.ingestion_complete:
    st.sidebar.success(f"Banco de dados `{os.path.basename(DB_FILE)}` pronto para consulta. ✅")
elif not st.session_state.ingestion_in_progress and not (uploaded_cabecalho and uploaded_itens):
     st.sidebar.info("Aguardando o upload dos arquivos de Cabeçalho e Itens.")
elif not st.session_state.ingestion_in_progress and not st.session_state.ingestion_complete:
     # Verifica se os arquivos foram carregados para mostrar a msg correta
     if uploaded_cabecalho and uploaded_itens:
         st.sidebar.info("Arquivos carregados. Clique em \"Processar Arquivos\" para iniciar.")
     else:
         st.sidebar.info("Aguardando o upload dos arquivos de Cabeçalho e Itens.")


# --- Interface de Chat --- 
st.header("Chat com os Dados das Notas Fiscais")

# Exibir histórico de chat
for entry in st.session_state.history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

# Campo de entrada do usuário
chat_disabled = not st.session_state.ingestion_complete or not st.session_state.google_api_key
disabled_reason = "" 
if not st.session_state.ingestion_complete:
    disabled_reason += " Faça o upload e processe os arquivos CSV primeiro." 
if not st.session_state.google_api_key:
    disabled_reason += " Insira sua chave da API do Google na barra lateral." 

user_input = st.chat_input(
    "Faça sua pergunta sobre os dados...", 
    disabled=chat_disabled, 
    key="chat_input"
)

if chat_disabled and not st.session_state.ingestion_in_progress:
    st.info(f"O chat está desabilitado.{disabled_reason}")

# Processar pergunta do usuário
if user_input and not chat_disabled:
    # Adicionar pergunta do usuário ao histórico e exibir
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Chamar o agente especialista e formatador
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                logging.info(f"Enviando pergunta para o agente: {user_input}")
                agent_raw_response = query_database_agent(user_input, st.session_state.google_api_key)
                logging.info(f"Resposta bruta do agente: {agent_raw_response}")
                
                formatted_output = format_response(agent_raw_response, user_input)
                logging.info("Resposta formatada gerada.")
                
                st.markdown(formatted_output)
                st.session_state.history.append({"role": "assistant", "content": formatted_output})
            
            except FileNotFoundError as e:
                error_msg = f"Erro: O arquivo do banco de dados (`{DB_FILE}`) não foi encontrado. Verifique se a ingestão foi concluída com sucesso. Detalhes: {e}"
                st.error(error_msg)
                st.session_state.history.append({"role": "assistant", "content": error_msg})
                logging.error(error_msg)
            except Exception as e:
                error_msg = f"Ocorreu um erro inesperado ao processar sua pergunta: {e}"
                st.error(error_msg)
                st.session_state.history.append({"role": "assistant", "content": error_msg})
                logging.error(f"Erro excepcional no fluxo de chat: {e}", exc_info=True)

# Adicionar um rodapé ou informações adicionais, se necessário
st.sidebar.divider()
st.sidebar.markdown("Desenvolvido com Manus")


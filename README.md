# csv-nav: Chat com Notas Fiscais (NFe)

[//]: # (Add badges here for shields.io, e.g., Python version, license, build status)
<p align="center">
  <a href="#-português">Português</a> •
  <a href="#-english">English</a>
</p>

---

## 🇧🇷 Português

### Visão Geral

O **csv-nav** é uma ferramenta de chat conversacional que utiliza o poder da API Gemini do Google e a eficiência de um banco de dados SQLite para analisar arquivos CSV de Notas Fiscais Eletrônicas (NFe). Faça perguntas em linguagem natural e obtenha insights valiosos sobre seus dados fiscais.

### ✨ Funcionalidades

* **Chat Interativo:** Converse com seus dados de NFe como se estivesse falando com um analista.
* **Análise Inteligente:** Extraia informações como totais, produtos mais vendidos, principais clientes/fornecedores e muito mais.
* **Suporte a Múltiplos Arquivos:** Faça upload de arquivos `.csv` ou de um arquivo `.zip` contendo todos os seus CSVs.
* **Interface Simples:** Interface web amigável construída com Streamlit para fácil upload e visualização.
* **Setup Simplificado:** Execução rápida e isolada utilizando Docker e VS Code Dev Containers.

### 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **IA Generativa:** Google Gemini
* **Frameworks de IA:** LangChain, LangChain Google GenAI
* **Interface Web:** Streamlit
* **Manipulação de Dados:** Pandas
* **Banco de Dados:** SQLite

### 🚀 Começando

* Você pode experimentar as funcionalidades desse software diretamente em: [CSV_NAV_WEB](https://csvnav-dvjmgnhdbkphhishggyi6q.streamlit.app/)
* Ou então siga as instruções abaixo para executar o projeto em seu ambiente local.


### 🚀 Instalação local com Docker e VS Code (via Remote Containers)

Este é o método **recomendado** para executar a aplicação `csv-nav`, garantindo um ambiente isolado, reprodutível e com dependências corretamente configuradas.

#### ✅ Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:

* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/)
* [Visual Studio Code](https://code.visualstudio.com/)
* [Extensão Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) para o VS Code.

Além disso, deverá obter uma chave de API do Google Gemini que é solicitada durante a execução da aplicação.
* Você pode obter uma chave de API do Google Gemini em [Google AI Studio](https://aistudio.google.com/app/apikey).

#### ⚙️ Passo a Passo de Instalação

##### 1. Clone o repositório

Abra um terminal (cmd, PowerShell ou Git Bash) e execute:

```bash
git clone https://github.com/Marconiadsf/csv_nav.git
cd csv_nav
```

##### 2. Crie e acesse a pasta no Docker

Crie um container com a imagem oficial do Python, mapeando o diretório clonado:

```bash
docker run -it -v C:/Users/<SeuUsuario>/csv_nav:/app -p 8501:8501 python:latest bash
```

> 🧠 Substitua `<SeuUsuario>` pelo nome da sua conta de usuário no Windows.

##### 3. Conecte o VS Code ao container

1. Abra o **Visual Studio Code**.
2. Pressione `Ctrl+Shift+P` para abrir a paleta de comandos.
3. Digite `Remote: Show Remote Menu` e selecione a opção.
4. Localize o container recém-criado e clique em **"Attach in a New Window"**.
5. Crie o workspace apontando para a pasta `/app`.

##### 4. Instalação de Dependências 📦

No terminal dentro do VS Code (já conectado ao container), execute:

```bash
pip install -r requirements.txt
```

> 📁 Certifique-se de estar no diretório `/app` onde o arquivo `requirements.txt` está localizado.

#### 🚀 Execução da Aplicação

Para iniciar a aplicação, execute no terminal:

```bash
streamlit run app.py
```

Após a execução, o Streamlit exibirá um endereço local como:

```
http://0.0.0.0:8501
```

##### Acessando no Navegador

- Você pode abrir a aplicação diretamente acessando:
  - `http://localhost:8501`
  - ou, se necessário, substituir `0.0.0.0` pelo IP da sua máquina, por exemplo: `http://192.168.0.1:8501`
- Para descobrir seu IP local, utilize o comando `ipconfig` no terminal (Windows).

---

### ✅ Pronto!

A aplicação `csv-nav` estará disponível via navegador para você:

- Enviar arquivos `.csv` ou `.zip` com suas Notas Fiscais.
- Fazer perguntas em **linguagem natural** sobre os dados enviados.
- Obter insights fiscais diretamente com suporte da IA Gemini + LangChain.


#### Como Usar

A aplicação foi projetada para ser simples e intuitiva. Siga os passos abaixo após iniciá-la:

1.  **Carregue seus Arquivos:** Na interface da aplicação, utilize o seletor de arquivos para fazer o upload dos seus dados de NFe. **Você pode enviar múltiplos arquivos `.csv` ou um único arquivo `.zip` contendo os CSVs.**
2.  **Aguarde o Processamento:** A ferramenta irá ler, processar e indexar os dados dos seus arquivos em um banco de dados temporário para análise.
3.  **Faça suas Perguntas:** Utilize a caixa de chat principal para fazer **perguntas em linguagem natural sobre as informações contidas nos arquivos** que você enviou.

**Exemplos de perguntas:**
* *"Qual foi o valor total das notas fiscais no período?"*
* *"Liste os 5 produtos mais vendidos."*
* *"Quais foram os principais clientes e seus respectivos totais de compra?"*
* *"Mostre-me as notas fiscais emitidas no mês de maio."*

### 🔧 Solução de Problemas (Troubleshooting)

* **Erro de WSL no Windows:** Se o Docker apresentar um erro relacionado ao WSL (Windows Subsystem for Linux), pode ser necessário atualizar sua versão do WSL. Abra o PowerShell ou CMD como administrador e execute `wsl --update`, depois reinicie o computador.
* **Problemas no Container:** Se o Dev Container não iniciar corretamente, você pode tentar limpar containers antigos. Abra o Docker Desktop, vá para a seção "Containers", encontre o container associado a este projeto e remova-o. Depois, tente reabrir no VS Code.

---


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

Siga as instruções abaixo para executar o projeto em seu ambiente local.

#### Pré-requisitos

Antes de começar, garanta que você tenha os seguintes softwares instalados:

* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/)
* [Visual Studio Code](https://code.visualstudio.com/)
* [Extensão Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) para o VS Code.

#### Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Marconiadsf/csv_nav.git](https://github.com/Marconiadsf/csv_nav.git)
    cd csv-nav
    ```

2.  **Obtenha sua Chave de API do Google Gemini:**
   
    * Você pode obter sua chave da API do Google Gemini, no [Google AI Studio](https://aistudio.google.com/app/apikey).
    * Basta adicionar sua API ao acessar a página inicial da aplicação.

3.  **Abra no Dev Container:**
    * Abra a pasta do projeto no **Visual Studio Code**.
    * O VS Code detectará automaticamente a configuração (`.devcontainer/devcontainer.json`) e exibirá uma notificação no canto inferior direito. Clique em **"Reopen in Container"**.
    * Aguarde o Docker construir a imagem e iniciar o container. Este processo instalará todas as dependências do Python automaticamente.

4.  **Inicie a Aplicação:**
    * Com o projeto aberto no container, abra um novo terminal no VS Code (`Ctrl+'` ou `Terminal > New Terminal`).
    * Execute o seguinte comando para iniciar a aplicação Streamlit:
    ```bash
    streamlit run app.py
    ```

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

## 🇬🇧 English

### Overview

**csv-nav** is a conversational chat tool that leverages the power of Google's Gemini API and the efficiency of an SQLite database to analyze CSV files from Brazilian Electronic Invoices (NFe). Ask questions in natural language and get valuable insights from your fiscal data.

### ✨ Features

* **Interactive Chat:** Talk to your NFe data as if you were speaking to an analyst.
* **Intelligent Analysis:** Extract information like totals, best-selling products, top customers/suppliers, and more.
* **Multi-File Support:** Upload `.csv` files or a single `.zip` file containing all your CSVs.
* **Simple Interface:** User-friendly web UI built with Streamlit for easy uploads and visualization.
* **Simplified Setup:** Quick and isolated execution using Docker and VS Code Dev Containers.

### 🛠️ Tech Stack

* **Language:** Python
* **Generative AI:** Google Gemini
* **AI Frameworks:** LangChain, LangChain Google GenAI
* **Web Interface:** Streamlit
* **Data Manipulation:** Pandas
* **Database:** SQLite

### 🚀 Getting Started

Follow the instructions below to run the project in your local environment.

#### Prerequisites

Before you begin, ensure you have the following software installed:

* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/)
* [Visual Studio Code](https://code.visualstudio.com/)
* [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code.

#### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Marconiadsf/csv_nav.git](https://github.com/Marconiadsf/csv_nav.git)
    cd csv-nav
    ```

2.  **Set up your API Key:**
** TO DO **

3.  **Open in Dev Container:**
    * Open the project folder in **Visual Studio Code**.
    * VS Code will automatically detect the configuration (`.devcontainer/devcontainer.json`) and show a notification in the bottom-right corner. Click on **"Reopen in Container"**.
    * Wait for Docker to build the image and start the container. This process will automatically install all Python dependencies.

4.  **Start the Application:**
    * With the project open inside the container, open a new terminal in VS Code (`Ctrl+'` or `Terminal > New Terminal`).
    * Run the following command to start the Streamlit application:
    ```bash
    streamlit run app.py
    ```

#### How to Use

The application is designed to be simple and intuitive. Follow the steps below after launching it:

1.  **Upload Your Files:** In the application's UI, use the file selector to upload your NFe data. **You can upload multiple `.csv` files or a single `.zip` file containing the CSVs.**
2.  **Wait for Processing:** The tool will read, process, and index the data from your files into a temporary database for analysis.
3.  **Ask Your Questions:** Use the main chat box to ask **questions in natural language about the information contained in the files** you uploaded.

**Example Questions:**
* *"What was the total value of all invoices in the period?"*
* *"List the top 5 best-selling products."*
* *"Who were the main customers and what were their respective purchase totals?"*
* *"Show me the invoices issued in the month of May."*

### 🔧 Troubleshooting

* **WSL Error on Windows:** If Docker shows an error related to WSL (Windows Subsystem for Linux), you may need to update your WSL version. Open PowerShell or CMD as an administrator and run `wsl --update`, then reboot your computer.
* **Container Issues:** If the Dev Container fails to start correctly, you can try cleaning up old containers. Open Docker Desktop, go to the "Containers" section, find the container associated with this project, and remove it. Then, try reopening it in VS Code.

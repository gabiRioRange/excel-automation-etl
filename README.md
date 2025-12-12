# 📊 Excel Automation ETL & Dashboard

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker)
![Pandas](https://img.shields.io/badge/Pandas-ETL-150458?style=for-the-badge&logo=pandas)

Uma solução completa de **Engenharia de Dados** que integra Backend (API), Processamento de Dados (ETL) e Visualização (Dashboard). 

O sistema automatiza a ingestão de planilhas complexas, realiza tratamentos de dados, cálculos de negócio (margem de lucro), validações de integridade e identifica **Diferenças Incrementais (Diffs)** entre cargas de arquivos.

## 🖼️ Interface Visual

[Dashboard](Captura_de_tela.png)

## 🚀 Funcionalidades

### 🖥️ Dashboard de Monitoramento (Novo!)
- **Upload Drag & Drop**: Interface amigável para envio de arquivos Excel/CSV.
- **Métricas em Tempo Real**: Monitoramento de logs, contagem de erros e sucessos.
- **Download Center**: Baixe os arquivos processados (`.parquet`, `.csv`) e relatórios de Diffs diretamente pelo navegador.

### ⚙️ Backend & ETL
- **API RESTful**: Endpoints documentados via Swagger UI (`POST /processar/`).
- **Pipeline de Dados**:
  - **Limpeza**: Padronização de strings e remoção de espaços.
  - **Tipagem Forte**: Conversão segura de moedas e datas.
  - **Regras de Negócio**: Cálculo automático de margem e bloqueio de vendas negativas.
- **Detecção de Diffs**: O sistema compara o arquivo atual com a versão histórica e gera um relatório contendo **apenas os novos registros**.
- **Auditoria**: Logs detalhados de cada etapa do processamento.

## 🛠️ Tech Stack

- **Linguagem**: Python 3.10+
- **Frontend / Dash**: Streamlit + Plotly
- **Backend**: FastAPI + Uvicorn
- **Core ETL**: Pandas, Openpyxl, Pyarrow
- **Infraestrutura**: Docker

## ⚙️ Como executar localmente

### 1. Preparação
Clone o repositório e instale as dependências:

bash

    git clone [https://github.com/gabiRioRange/excel-automation-etl.git](https://github.com/gabiRioRange/excel-automation-etl.git)
    cd excel-automation-etl

# Criação do ambiente virtual

    python -m venv .venv
# Windows:

    .venv\Scripts\activate
# Linux/Mac:

    source .venv/bin/activate

    pip install -r requirements.txt

2. Rodando o Dashboard (Recomendado)

Para ver a interface visual e monitorar os jobs:
Bash

    streamlit run dashboard.py

O navegador abrirá automaticamente em http://localhost:8501
3. Rodando apenas a API (Modo Headless)

Se preferir usar apenas o Backend via Swagger:
Bash

    uvicorn src.api:app --reload

Acesse a documentação em http://127.0.0.1:8000/docs
## 🐳 Como executar com Docker

Para rodar a API isolada em um container:
Bash

# 1. Construir a imagem

    docker build -t excel-etl .

# 2. Rodar o container na porta 8000

    docker run -p 8000:8000 excel-etl

## 🧪 Estrutura do Projeto
Plaintext

    excel-automation-tool/
    │
    ├── data/                # Persistência de dados
    │   ├── input/           # Entrada de arquivos
    │   ├── output/          # Arquivos processados e Diffs
    │   └── logs/            # Logs de execução (lidos pelo Dashboard)
    │
    ├── src/
    │   ├── api.py           # API FastAPI
    │   └── pipeline.py      # Motor ETL (Pandas Logic)
    │
    ├── dashboard.py         # Interface Streamlit
    ├── Dockerfile           # Configuração de Container
    ├── main.py              # Script CLI legado
    └── requirements.txt     # Dependências

## 📋 Regras de Negócio Implementadas

    Validação: Bloqueia vendas com valores negativos e gera relatório de erros (erros_validacao.csv).

    Normalização: Mapeia colunas do Excel do cliente para o schema do banco de dados (Ex: "Vlr Venda" -> "valor_venda").

    Cálculo de Margem: (Valor Venda - Custo) / Valor Venda.

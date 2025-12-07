# 📊 Excel Automation ETL API

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker)
![Pandas](https://img.shields.io/badge/Pandas-ETL-150458?style=for-the-badge&logo=pandas)

Uma solução robusta de **Engenharia de Dados** para ingestão, processamento e validação de planilhas Excel via API REST. O sistema realiza limpeza de dados, cálculos de negócio e identifica diferenças incrementais (Diffs) entre cargas de arquivos.

## 🚀 Funcionalidades

- **API RESTful**: Upload de arquivos via `POST /processar/`.
- **ETL Automatizado**:
  - **Extração**: Suporte a múltiplos formatos (`.xlsx`, `.csv`).
  - **Transformação**: Limpeza de strings, tipagem forte, cálculo automático de margem de lucro.
  - **Carga**: Exportação otimizada em **Parquet** e CSV padronizado.
- **Detecção de Diffs**: Compara o arquivo atual com a versão anterior e gera um relatório contendo apenas os **novos registros**.
- **Log & Auditoria**: Rastreamento completo de cada etapa do processamento.
- **Docker Ready**: Arquitetura pronta para deploy em containers.

## 🛠️ Tech Stack

- **Linguagem**: Python 3.10+
- **Framework Web**: FastAPI + Uvicorn
- **Processamento de Dados**: Pandas, Openpyxl, Pyarrow
- **Infraestrutura**: Docker

## ⚙️ Como executar localmente

1. **Clone o repositório**
   ```bash
   git clone [https://github.com/SEU-USUARIO/excel-automation-etl.git](https://github.com/SEU-USUARIO/excel-automation-etl.git)
   cd excel-automation-etl
import streamlit as st
import os  # <--- FALTAVA ISSO AQUI
import pandas as pd
from pathlib import Path
import plotly.express as px
from src.pipeline import ExcelPipeline

# Configuração da Página
st.set_page_config(page_title="ETL Monitor", page_icon="📊", layout="wide")

# Caminhos
ROOT = Path(__file__).parent
LOG_FILE = ROOT / "data" / "logs" / "processamento.log"
OUTPUT_DIR = ROOT / "data" / "output"

# --- TÍTULO ---
st.title("📊 Excel Automation Dashboard")
st.markdown("Monitoramento de Jobs, Logs e Upload de Arquivos")

# --- SIDEBAR (Upload) ---
st.sidebar.header("📤 Upload de Arquivo")
uploaded_file = st.sidebar.file_uploader("Solte seu Excel aqui", type=["xlsx", "csv"])

if uploaded_file:
    if st.sidebar.button("Processar Arquivo"):
        with st.spinner("Processando..."):
            # Salva temporariamente
            temp_path = ROOT / "data" / "input" / uploaded_file.name
            # Garante que a pasta existe
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Roda o Pipeline diretamente
            try:
                pipeline = ExcelPipeline()
                raw = pipeline.ingest_files()
                
                if not raw.empty:
                    clean = pipeline.clean_and_normalize(raw)
                    final = pipeline.transform(clean)
                    pipeline.validate(final)
                    diff = pipeline.generate_diffs(final)
                    pipeline.export(final)
                    
                    st.sidebar.success("✅ Processado com Sucesso!")
                    if diff:
                        st.sidebar.warning(f"⚠️ Diff encontrado! {diff.name}")
                    
                    # Limpa o arquivo de input após processar para não duplicar depois
                    os.remove(temp_path)
                else:
                    st.sidebar.error("Arquivo vazio ou ilegível.")

            except Exception as e:
                st.sidebar.error(f"Erro: {e}")

# --- DASHBOARD (Logs e Métricas) ---

# 1. Leitura de Logs
if LOG_FILE.exists():
    # Lê o log bruto
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        logs = f.readlines()
    
    # Processa para criar um DataFrame de logs
    log_data = []
    for line in logs:
        try:
            # Ex: 2023-10-01 10:00:00,000 - INFO - Mensagem
            parts = line.split(" - ")
            if len(parts) >= 3:
                timestamp = parts[0]
                level = parts[1]
                message = " - ".join(parts[2:]).strip()
                log_data.append({"Time": timestamp, "Level": level, "Message": message})
        except:
            continue
            
    if log_data:
        df_logs = pd.DataFrame(log_data)
        
        # Métricas
        col1, col2, col3 = st.columns(3)
        
        erros = df_logs[df_logs["Level"] == "ERROR"].shape[0]
        # Conta linhas que indicam sucesso no export
        sucessos = df_logs[df_logs["Message"].str.contains("Arquivos salvos com sucesso", case=False)].shape[0]
        warnings = df_logs[df_logs["Level"] == "WARNING"].shape[0]

        col1.metric("Total de Exportações", sucessos)
        col2.metric("Erros Registrados", erros, delta_color="inverse")
        col3.metric("Alertas", warnings, delta_color="inverse")

        # Gráfico de Atividade
        st.subheader("📈 Atividade Recente")
        df_logs["Time"] = pd.to_datetime(df_logs["Time"].str.split(",").str[0], errors='coerce')
        # Remove linhas com data inválida
        df_logs = df_logs.dropna(subset=["Time"])
        
        if not df_logs.empty:
            activity = df_logs.groupby(df_logs["Time"].dt.hour)["Message"].count().reset_index()
            fig = px.bar(activity, x="Time", y="Message", title="Logs por Hora", labels={"Time": "Hora do Dia", "Message": "Volume de Logs"})
            st.plotly_chart(fig, use_container_width=True)

        # Tabela de Logs Recentes
        st.subheader("📜 Logs do Sistema")
        st.dataframe(df_logs.sort_index(ascending=False).head(100), use_container_width=True)
    else:
        st.info("O arquivo de log existe, mas está vazio ou fora do padrão.")

else:
    st.warning("Nenhum arquivo de log encontrado ainda.")

# --- AREA DE DOWNLOADS ---
st.subheader("📂 Arquivos Processados")
if OUTPUT_DIR.exists():
    # Lista arquivos e ordena por data de modificação (os mais novos primeiro)
    files = sorted(list(OUTPUT_DIR.glob("*.*")), key=os.path.getmtime, reverse=True)
    
    if not files:
        st.info("Nenhum arquivo processado encontrado.")
    
    for file in files[:5]: # Mostra os 5 últimos
        with open(file, "rb") as f:
            st.download_button(
                label=f"⬇️ Baixar {file.name}",
                data=f,
                file_name=file.name,
                mime="application/octet-stream"
            )
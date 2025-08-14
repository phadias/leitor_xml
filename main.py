import streamlit as st
import pandas as pd
from io import BytesIO
import etl
import time

# Configuração da página
st.set_page_config(page_title="Leitor de XMLs em Lote", layout="wide")
st.title("📦 Conversor XMLs → Arquivo Excel")
st.markdown(
    "Converte **XMLs** "
    "para um arquivo Excel contendo os códigos **JBS**."
)

# Cache para evitar reprocessamento desnecessário
@st.cache_data
def processar_xmls(files):
    return etl.concatenar_df(files)

# Upload dos arquivos
uploaded_files = st.file_uploader(
    "Selecione um ou mais arquivos XML",
    type="xml",
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("⏳ Processando arquivos..."):
        df = processar_xmls(uploaded_files)

    st.success(f"✅ {len(uploaded_files)} arquivos processados com sucesso! ({len(df)} linhas no total)")

    # Exibição do DataFrame
    st.subheader("📋 Pré-visualização dos Dados")
    st.dataframe(df, use_container_width=True)

    # Preparar arquivo para download
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="XMLs")
    output.seek(0)

    # Botão de download
    st.download_button(
        label="📥 Baixar Excel (.xlsx)",
        data=output,
        file_name="xmls_processados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📄 Envie um ou mais arquivos XML para iniciar o processamento.")

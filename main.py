import streamlit as st
import xmltodict
import pandas as pd
import os
from io import BytesIO
import etl


st.set_page_config(page_title="Leitor de XMLs em lote", layout="wide")
st.title("📦 Leitor de Múltiplos XMLs → DataFrame por Arquivo")

uploaded_files = st.file_uploader(
    "Selecione um ou mais arquivos XML",
    type="xml",
    accept_multiple_files=True
)

if uploaded_files:

    # Concatenar todos os DataFrames
    df = etl.concatenar_df(uploaded_files)

    st.success(f"{len(uploaded_files)} arquivos processados com sucesso!")

    # Mostrar o DataFrame completo
    st.subheader("📋 DataFrame Final")
    st.dataframe(df)

    # 🔽 Download como Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='XMLs')
    output.seek(0)

    st.download_button(
        label="📥 Baixar Excel (.xlsx)",
        data=output,
        file_name="xmls_processados.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

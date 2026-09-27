from datetime import datetime, timedelta
import google.genai as genai
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Autonomous Renewal & Sourcing Agent", page_icon="🤖", layout="wide"
)

# Seletor de idioma na barra lateral (Inglês como padrão por estar em primeiro)
lang = st.sidebar.selectbox("Language / Idioma", ["English", "Português"])

# Dicionário de traduções
t = {
    "English": {
        "title": "Autonomous Renewal & Sourcing Agent",
        "subtitle": (
            "Optimize your contract lifecycle, mitigate financial risks, and"
            " automate market benchmarking with AI."
        ),
        "control_panel": "Control Panel",
        "control_desc": (
            "Manage your vendor database and secure access credentials."
        ),
        "api_key_label": "Gemini API Key:",
        "data_source": "Data Source",
        "upload_label": "Upload your CSV file:",
        "upload_msg": (
            "👉 Please upload your contract CSV file via the sidebar to start."
        ),
        "table_header": "Loaded Contracts & Vendor Data",
        "status_header": "Contract Lifecycles & Kündigungsfrist Analysis",
        "error_msg": "Error processing file: ",
    },
    "Português": {
        "title": "Agente Autónomo de Renovação e Sourcing",
        "subtitle": (
            "Otimize o ciclo de vida dos contratos, mitigue riscos financeiros e"
            " automatize o benchmarking de mercado com IA."
        ),
        "control_panel": "Painel de Controlo",
        "control_desc": (
            "Gerencie a sua base de dados de fornecedores e credenciais de"
            " acesso."
        ),
        "api_key_label": "Chave da API Gemini:",
        "data_source": "Fonte de Dados",
        "upload_label": "Envie o seu ficheiro CSV:",
        "upload_msg": (
            "👉 Por favor, carregue o seu ficheiro CSV de contratos através da"
            " barra lateral para começar."
        ),
        "table_header": "Contratos Carregados e Dados de Fornecedores",
        "status_header": "Ciclos de Vida e Análise de Kündigungsfrist",
        "error_msg": "Erro ao processar o ficheiro: ",
    },
}

# Cabeçalho Principal
st.title(f"🤖 {t[lang]['title']}")
st.markdown(t[lang]["subtitle"])

# Barra Lateral - Controlo e Configurações
st.sidebar.header(t[lang]["control_panel"])
st.sidebar.markdown(t[lang]["control_desc"])

api_key = st.sidebar.text_input(
    t[lang]["api_key_label"], type="password", key="gemini_api_key"
)

st.sidebar.markdown(f"### {t[lang]['data_source']}")
uploaded_file = st.sidebar.file_uploader(
    t[lang]["upload_label"], type=["csv", "txt"]
)

# Corpo Principal da Aplicação
if uploaded_file is not None:
  try:
    # Leitura do CSV com delimitador ';' e limpeza de aspas e espaços
    df = pd.read_csv(uploaded_file, sep=";")
    df = df.apply(
        lambda x: x.str.strip('"').str.strip() if x.dtype == "object" else x
    )

    st.subheader(t[lang]["table_header"])
    st.dataframe(df, use_container_width=True)

    # Processamento de Prazos e Riscos (Kündigungsfrist)
    if "Renewal Date" in df.columns and "Notice Period Days" in df.columns:
      today = datetime.today()
      results = []

      for index, row in df.iterrows():
        try:
          r_date = datetime.strptime(str(row["Renewal Date"]), "%d/%m/%Y")
          notice_days = int(row["Notice Period Days"])
          deadline = r_date - timedelta(days=notice_days)
          days_left = (deadline - today).days

          if days_left < 0:
            risk = (
                "High Risk (Notice Expired)"
                if lang == "English"
                else "Risco Alto (Prazo Expirado)"
            )
          elif days_left < 30:
            risk = (
                "Medium Risk (Action Needed Soon)"
                if lang == "English"
                else "Risco Médio (Ação Necessária Breve)"
            )
          else:
            risk = "Safe" if lang == "English" else "Seguro"

          results.append({
              "Vendor Name": row.get("Vendor Name", "Unknown"),
              "Category": row.get("Category", ""),
              "Renewal Date": row["Renewal Date"],
              "Notice Deadline": deadline.strftime("%d/%m/%Y"),
              "Status": risk,
          })
        except Exception:
          continue

      if results:
        st.subheader(t[lang]["status_header"])
        st.dataframe(pd.DataFrame(results), use_container_width=True)

  except Exception as e:
    st.error(f"{t[lang]['error_msg']}{e}")
else:
  st.info(t[lang]["upload_msg"])

# Rodapé da Barra Lateral
st.sidebar.markdown("---")
st.sidebar.markdown("*Global IT Procurement Engine v2.0*")
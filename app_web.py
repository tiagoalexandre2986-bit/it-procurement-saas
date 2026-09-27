import streamlit as st
import pandas as pd
from datetime import datetime
import io
import time

try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Configuração da página com layout largo
st.set_page_config(
    page_title="Autonomous Procurement & Renewal SaaS",
    page_icon="🤖",
    layout="wide"
)

# Estilização CSS customizada
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ==================== BARRA LATERAL (SIDEBAR) ====================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=64)
    st.header("Control Panel")
    st.write("Manage your vendor database and secure access credentials.")
    
    st.divider()
    
    user_api_key = st.text_input("Gemini API Key:", type="password", help="Your key is secure and never stored.")
    
    st.divider()
    
    st.write("### Data Source")
    uploaded_file = st.file_uploader("Envie o seu ficheiro CSV:", type=["csv", "txt"], help="Carregue a planilha contendo os contratos.")
    
    st.divider()
    st.markdown("### 💡 SaaS Info")
    st.caption("Global IT Procurement Engine v2.0")

# ==================== TELA PRINCIPAL ====================
st.title("🤖 Autonomous Renewal & Sourcing Agent")
st.markdown("Optimize your contract lifecycle, mitigate financial risks, and automate market benchmarking with AI.")

df = None

if uploaded_file is not None:
    try:
        uploaded_file.seek(0)
        content_bytes = uploaded_file.read()
        try:
            content_str = content_bytes.decode('utf-8')
        except:
            content_str = content_bytes.decode('latin1')

        primeira_linha = content_str.strip().split('\n')[0]
        sep_char = ';' if ';' in primeira_linha else ','

        df = pd.read_csv(io.StringIO(content_str), sep=sep_char, engine='python', skipinitialspace=True)

        if len(df.columns) == 1:
            linhas = [linha.split(sep_char) for linha in content_str.strip().split('\n') if linha.strip()]
            if len(linhas) > 1:
                header = [h.strip().replace('"', '').replace("'", "") for h in linhas[0]]
                data = [[val.strip().replace('"', '').replace("'", "") for val in row] for row in linhas[1:]]
                df = pd.DataFrame(data, columns=header)
            
    except Exception as e:
        st.error(f"Erro ao ler o ficheiro. Detalhe: {e}")

if df is not None and not df.empty:
    cols = [c.strip().replace('"', '').replace("'", "") for c in df.columns.tolist()]
    df.columns = cols

    def get_column_data(possible_names, default_val=""):
        for name in possible_names:
            for col in cols:
                if name.lower() in col.lower():
                    return df[col]
        return pd.Series([default_val] * len(df))

    clean_df = pd.DataFrame()
    
    # Limpeza rigorosa de aspas em todas as colunas de texto
    clean_df['Vendor Name'] = get_column_data(['vendor name', 'empresa', 'name', 'fornecedor'], cols[0] if len(cols)>0 else "").astype(str).str.replace('"', '').str.replace("'", "").str.strip()
    clean_df['Category'] = get_column_data(['category', 'categoria', 'type', 'tipo'], cols[1] if len(cols)>1 else "").astype(str).str.replace('"', '').str.replace("'", "").str.strip()
    clean_df['Contact Email'] = get_column_data(['email', 'contact', 'contato'], cols[2] if len(cols)>2 else "contact@vendor.com").astype(str).str.replace('"', '').str.replace("'", "").str.strip()
    clean_df['Renewal Date Raw'] = get_column_data(['renewal date', 'vencimento', 'date', 'data'], cols[3] if len(cols)>3 else "").astype(str).str.replace('"', '').str.replace("'", "").str.strip()
    
    notice_series = get_column_data(['notice period', 'notice', 'kündigung', 'prazo', 'dias', 'days'], cols[4] if len(cols)>4 else 30)
    clean_df['Notice Period Days'] = pd.to_numeric(notice_series.astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(30).astype(int)

    today = datetime.now().date()
    critical_risks = 0
    clean_df['Status'] = ""
    clean_df['Renewal Date'] = ""
    clean_df['Cancellation Deadline'] = ""
    clean_df['Days Left'] = 0

    for index, row in clean_df.iterrows():
        raw_date_str = str(row['Renewal Date Raw']).strip()
        
        parsed_date = None
        for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d.%m.%Y', '%d-%m-%Y'):
            try:
                parsed_date = datetime.strptime(raw_date_str, fmt).date()
                break
            except ValueError:
                continue
                
        if not parsed_date:
            parsed_date = today

        days_to_notice = int(row['Notice Period Days'])
        deadline = parsed_date - pd.Timedelta(days=days_to_notice).to_pytimedelta()
        days_left = (deadline - today).days
        
        if days_left <= 2:
            clean_df.at[index, 'Status'] = "🚨 CRITICAL"
            critical_risks += 1
        elif days_left <= 15:
            clean_df.at[index, 'Status'] = "⚠️ WARNING"
            critical_risks += 1
        else:
            clean_df.at[index, 'Status'] = "✅ SAFE"
            
        clean_df.at[index, 'Renewal Date'] = parsed_date.strftime('%d/%m/%Y')
        clean_df.at[index, 'Cancellation Deadline'] = deadline.strftime('%d/%m/%Y')
        clean_df.at[index, 'Days Left'] = days_left

    # ==================== MÉTRICAS (KPIs) ====================
    total_contracts = len(clean_df)
    
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.metric(label="Total Contracts Analyzed", value=total_contracts)
    col_kpi2.metric(label="Contracts at Risk", value=critical_risks, delta="Action Needed" if critical_risks > 0 else "All Clear", delta_color="inverse")
    col_kpi3.metric(label="System Status", value="Active & Online")

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================== ABAS DE NAVEGAÇÃO ====================
    tab1, tab2 = st.tabs(["📊 Contract Portfolio & Risks", "🧠 On-Demand AI Sourcing"])

    with tab1:
        st.subheader("Vendor Contract Status Overview")
        st.markdown("Review all loaded records, calculated deadlines, and risk classifications based on individual Kündigungsfrist.")
        st.dataframe(
            clean_df[['Vendor Name', 'Category', 'Renewal Date', 'Notice Period Days', 'Cancellation Deadline', 'Days Left', 'Status']], 
            use_container_width=True,
            height=350
        )

    with tab2:
        st.subheader("On-Demand AI Market Intelligence")
        st.markdown("Select an individual vendor to instantly benchmark competitors and draft executive actions.")
        
        vendor_list = clean_df['Vendor Name'].tolist()
        selected_vendor_name = st.selectbox("Choose a contract to audit:", vendor_list)

        if st.button("🚀 Generate AI Strategy & Competitors", type="primary"):
            if not user_api_key:
                st.warning("⚠️ Please insert your Gemini API Key in the left sidebar first.")
            else:
                selected_row = clean_df[clean_df['Vendor Name'] == selected_vendor_name].iloc[0]
                
                with st.spinner(f"Analyzing market and drafting strategy for {selected_row['Vendor Name']}..."):
                    prompt = f"""
                    Act as an IT Procurement expert. The contract for vendor '{selected_row['Vendor Name']}' in category '{selected_row['Category']}' has a cancellation deadline on {selected_row['Cancellation Deadline']} (Notice period: {selected_row['Notice Period Days']} days before renewal).
                    
                    Tasks:
                    1. Identify 2 direct market competitors for this software/service.
                    2. Present a strong competitive advantage or estimated cost difference compared to {selected_row['Vendor Name']}.
                    3. Draft a short, direct executive message for the manager to decide whether to open renegotiations or send the cancellation notice to {selected_row['Contact Email']}.
                    """
                    
                    max_retries = 3
                    success = False
                    
                    for attempt in range(max_retries):
                        try:
                            client = genai.Client(api_key=user_api_key)
                            response = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
                            
                            with st.container():
                                st.success(f"Analysis successfully completed for {selected_row['Vendor Name']}")
                                st.markdown("### 📋 Executive Strategic Brief")
                                st.markdown(response.text)
                            success = True
                            break
                        except Exception as e:
                            error_msg = str(e)
                            if "503" in error_msg or "429" in error_msg:
                                if attempt < max_retries - 1:
                                    wait_time = 2 ** (attempt + 1)
                                    st.warning(f"AI server busy. Retrying in {wait_time} seconds...")
                                    time.sleep(wait_time)
                                else:
                                    st.error("AI servers are experiencing high demand. Please try again shortly.")
                            else:
                                st.error(f"API Error: {e}")
                                break
else:
    st.info("👈 Por favor, carregue o seu ficheiro CSV de contratos através da barra lateral para começar.")
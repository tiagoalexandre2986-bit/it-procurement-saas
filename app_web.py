from datetime import datetime, timedelta
import time
import google.genai as genai
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Autonomous Renewal & Sourcing Agent", page_icon="🤖", layout="wide"
)

# Main Title & Subtitle (English Only)
st.title("🤖 Autonomous Renewal & Sourcing Agent")
st.markdown(
    "Optimize your contract lifecycle, mitigate financial risks, and automate"
    " market benchmarking with AI."
)

# Sidebar - Control Panel & Settings
st.sidebar.header("Control Panel")
st.sidebar.markdown(
    "Manage your vendor database and secure access credentials."
)

api_key = st.sidebar.text_input(
    "Gemini API Key:", type="password", key="gemini_api_key"
)

st.sidebar.markdown("### Data Source")

# Instruções claras sobre o formato do CSV na barra lateral
with st.sidebar.expander("📋 CSV Format Guidelines"):
  st.markdown(
      "To ensure proper processing, your CSV file must follow these"
      " requirements:\n\n"
      "1. **Delimiter:** Use semicolon (`;`) to separate columns.\n"
      "2. **Required Columns:**\n"
      "   - `Vendor Name` (Text)\n"
      "   - `Category` (Text)\n"
      "   - `Email` (Text)\n"
      "   - `Renewal Date` (Format: `DD/MM/YYYY`)\n"
      "   - `Notice Period Days` (Integer, e.g., `30`, `90`)\n\n"
      "**Example row:**\n"
      "`Salesforce Brasil;CRM;support@salesforce.com.br;15/10/2026;30`"
  )

uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV file:", type=["csv", "txt"]
)

# Main Application Logic
if uploaded_file is not None:
  try:
    # Read CSV with semicolon delimiter and clean quotes/spaces
    df = pd.read_csv(uploaded_file, sep=";")
    df = df.apply(
        lambda x: x.str.strip('"'].str.strip() if x.dtype == "object" else x
    )

    st.subheader("Loaded Contracts & Vendor Data")
    st.dataframe(df, use_container_width=True)

    # Process Deadlines and Risks (Notice Period)
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
            risk = "High Risk (Notice Expired)"
          elif days_left < 30:
            risk = "Medium Risk (Action Needed Soon)"
          else:
            risk = "Safe"

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
        st.subheader("Contract Lifecycles & Notice Period Analysis")
        st.dataframe(pd.DataFrame(results), use_container_width=True)

        # AI-Powered Strategic Sourcing & Audit Module
        st.markdown("---")
        st.subheader("🤖 AI Strategic Sourcing & Risk Audit")
        st.markdown(
            "Select a vendor from your portfolio to generate an autonomous"
            " market benchmark and contract risk analysis."
        )

        vendor_names = [v["Vendor Name"] for v in results]
        selected_vendor = st.selectbox(
            "Select Vendor for AI Audit:", vendor_names
        )

        if "audit_cache" not in st.session_state:
          st.session_state.audit_cache = {}

        if st.button("Run AI Contract & Market Audit"):
          if not api_key:
            st.warning(
                "Please enter your Gemini API Key in the sidebar to run the AI"
                " audit."
            )
          else:
            if selected_vendor in st.session_state.audit_cache:
              st.success("Loaded from instant cache!")
              st.markdown("### AI Audit Report")
              st.write(st.session_state.audit_cache[selected_vendor])
            else:
              with st.spinner(
                  f"Analyzing contract risks for {selected_vendor}..."
              ):
                success = False
                response_text = ""
                for attempt in range(3):
                  try:
                    client = genai.Client(api_key=api_key)
                    prompt = (
                        f"As an IT procurement expert, provide a concise risk"
                        f" and market sourcing analysis for {selected_vendor}."
                        f" Cover key contract traps, negotiation levers, and top"
                        f" 2 market alternatives. Keep it professional and"
                        f" structured in English."
                    )
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt,
                        config={
                            "max_output_tokens": 600,
                            "temperature": 0.3,
                        },
                    )
                    response_text = response.text
                    success = True
                    break
                  except Exception:
                    time.sleep(2)

                if success:
                  st.session_state.audit_cache[selected_vendor] = response_text
                  st.markdown("### AI Audit Report")
                  st.write(response_text)
                else:
                  st.error(
                      "The server is experiencing high demand right now. Please"
                      " wait a few moments and try clicking the button again."
                  )

  except Exception as e:
    st.error(f"Error processing file: {e}")
else:
  st.info(
      "👉 Please upload your contract CSV file via the sidebar to start. Check"
      " the guidelines in the sidebar for column formatting details."
  )

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("*Global IT Procurement Engine v2.0*")
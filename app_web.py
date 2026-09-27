from datetime import datetime, timedelta
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
uploaded_file = st.sidebar.file_uploader(
    "Upload your CSV file:", type=["csv", "txt"]
)

# Main Application Logic
if uploaded_file is not None:
  try:
    # Read CSV with semicolon delimiter and clean quotes/spaces
    df = pd.read_csv(uploaded_file, sep=";")
    df = df.apply(
        lambda x: x.str.strip('"').str.strip() if x.dtype == "object" else x
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

        if st.button("Run AI Contract & Market Audit"):
          if not api_key:
            st.warning(
                "Please enter your Gemini API Key in the sidebar to run the AI"
                " audit."
            )
          else:
            with st.spinner(
                f"Analyzing contract risks and market alternatives for"
                f" {selected_vendor}..."
            ):
              try:
                # Initialize Gemini client
                client = genai.Client(api_key=api_key)

                prompt = (
                    f"Act as an expert IT Procurement Director and Financial"
                    f" Auditor. Provide a strategic risk and sourcing analysis"
                    f" for the software/IT vendor: {selected_vendor}. Include"
                    f" potential hidden traps in standard enterprise contracts"
                    f" (like automatic roll-over clauses, price inflation"
                    f" caps), negotiation levers for the upcoming renewal,"
                    f" and top 2 market alternatives or open-source equivalents"
                    f" to reduce costs. Keep it structured and professional"
                    f" in English."
                )

                response = client.models.generate_content(
                    model="gemini-3.8-flash", contents=prompt
                )

                st.markdown("### AI Audit Report")
                st.write(response.text)

              except Exception as ai_err:
                st.error(f"Error generating AI audit: {ai_err}")

  except Exception as e:
    st.error(f"Error processing file: {e}")
else:
  st.info("👉 Please upload your contract CSV file via the sidebar to start.")

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("*Global IT Procurement Engine v2.0*")
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

  except Exception as e:
    st.error(f"Error processing file: {e}")
else:
    st.info("👉 Please upload your contract CSV file via the sidebar to start.")

# Sidebar Footer
st.sidebar.markdown("---")
st.sidebar.markdown("*Global IT Procurement Engine v2.0*")
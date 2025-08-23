import streamlit as st
import pandas as pd
import numpy as np
from database import execute_many_insert, copy_via_csv

st.set_page_config(page_title="Bulk CSV Upload", page_icon="📤", layout="wide")
st.title("📤 Bulk Upload CSV to Supabase (Postgres)")

uploaded = st.file_uploader("Upload a CSV file", type=["csv"])

# Our table is 'students'
table = "students"

mode = st.radio(
    "Load mode",
    ["Fast (COPY)", "Safe (INSERT)"],
    index=0,
    help="COPY requires CSV headers match DB column names. INSERT lets you pick columns."
)

if uploaded:
    df = pd.read_csv(uploaded)
    st.subheader("Preview")
    st.dataframe(df.head(20), use_container_width=True)

    # Replace NaN with None for DB
    df = df.replace({np.nan: None})

    if mode == "Fast (COPY)":
        st.info("CSV headers must exactly match the 'students' table column names: id, name, course, year")
        if st.button("🚀 Bulk load with COPY"):
            try:
                copy_via_csv(table, df)
                st.success("✅ COPY completed!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ COPY failed: {e}")

    else:
        st.subheader("Select columns to insert (id is optional if SERIAL)")
        cols = st.multiselect(
            "Columns to insert:",
            options=list(df.columns),
            default=[c for c in df.columns if c != "id"],  # usually skip id
        )

        if st.button("⬇️ Bulk insert (INSERT)"):
            try:
                rows = [tuple(rec) for rec in df[cols].itertuples(index=False, name=None)]
                execute_many_insert(table, cols, rows)
                st.success("✅ INSERT completed!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ INSERT failed: {e}")


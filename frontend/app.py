import streamlit as st
import requests
import json
from typing import Dict, Any
import os

# Backend URL - configurable via environment
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("Autonomous Financial Research Agent")

st.sidebar.header("Analysis Configuration")
query = st.sidebar.text_input("Research Query", "Analyze Tesla stock")
mode = st.sidebar.selectbox("Analysis Mode", ["react", "plan_execute"])

if st.sidebar.button("Run Analysis"):
    with st.spinner("Running analysis..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/analyze",
                json={"query": query, "mode": mode},
                timeout=60  # Add timeout for long-running analyses
            )

            if response.status_code == 200:
                data = response.json()

                st.header("Analysis Result")
                st.write(data["result"])

                if data.get("report"):
                    report = data["report"]
                    st.header("Investment Report")

                    st.subheader("Executive Summary")
                    st.write(report["executive_summary"])

                    st.subheader("Company Overview")
                    st.write(report["company_overview"])

                    st.subheader("Financial Analysis")
                    st.write(report["financial_analysis"])

                    st.subheader("Risk Assessment")
                    st.write(report["risk_assessment"])

                    st.subheader("Competitive Analysis")
                    st.write(report["competitive_analysis"])

                    st.subheader("Final Insight")
                    st.write(report["final_insight"])
            else:
                st.error(f"Error: {response.text}")

        except requests.exceptions.Timeout:
            st.error("Analysis timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {e}")

st.header("Available Tools")
try:
    tools_response = requests.get(f"{BACKEND_URL}/tools", timeout=10)
    if tools_response.status_code == 200:
        tools = tools_response.json()["tools"]
        st.write("Available analysis tools:")
        for tool in tools:
            st.write(f"- {tool}")
    else:
        st.write("Backend not available")
except:
    st.write("Backend not available")

st.markdown("""
## How to use:
1. Enter your research query in the sidebar
2. Select analysis mode (ReAct or Plan-and-Execute)
3. Click "Run Analysis"
4. View the structured investment report

## Features:
- Multi-source data collection (SEC, financial APIs, news)
- AI-powered reasoning with tool use
- Memory system for context retention
- Structured investment reports
- Async processing for long analyses
""")
import streamlit as st
import pandas as pd
from ui.api_client import ask_question, get_anomalies, get_tickets


def render_health_badge(health: dict):
    
    if health.get("status") == "ok":
        st.sidebar.success(f"✅ API Online ({health.get('db_rows')} rows)")
    else:
        st.sidebar.error(f"❌ API Offline: {health.get('detail', 'unknown')}")


def render_query_tab():
    """Tab 1: Ask a question."""
    st.header("💬 Ask a Question")
    st.caption("Type any English question about the support tickets.")

    # Example chips
    st.write("**Try these:**")
    examples = [
        "How many tickets are currently open?",
        "Which agent has the lowest average customer rating?",
        "Show me all Critical tickets not resolved within 12 hours.",
        "What is the average customer rating for Technical tickets?",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        if cols[i % 2].button(ex, key=f"ex_{i}", width="stretch"):
            st.session_state["question"] = ex

    # Input
    question = st.text_input(
        "Your question:",
        value=st.session_state.get("question", ""),
        key="q_input",
        placeholder="e.g. How many critical tickets are unresolved?",
    )

    if st.button("🔍 Get Answer", type="primary", width="stretch"):
        if not question.strip():
            st.warning("Please type a question first.")
            return
        with st.spinner("Thinking..."):
            result = ask_question(question)

        if "error" in result:
            st.error(result["error"])
            return

        st.success(result.get("answer", "No answer"))

        with st.expander("📝 Generated SQL"):
            st.code(result.get("sql", ""), language="sql")

        if result.get("rows"):
            st.write(f"**Raw result ({result.get('row_count', 0)} rows):**")
            st.dataframe(pd.DataFrame(result["rows"]), width="stretch")

        st.caption(f"⏱ Latency: {result.get('latency_ms', 0)} ms")


def render_anomaly_tab():
   
    st.header("🚨 Anomaly Detection")
    st.caption("Automatically flagged suspicious tickets.")

    col1, col2 = st.columns(2)
    reason_filter = col1.selectbox(
        "Filter by reason:",
        ["(all)", "stale_high_priority", "slow_first_response",
         "long_resolution", "low_customer_rating", "escalated_unresolved",
         "zscore_outlier_resolution_time_hrs", "iqr_outlier_resolution_time_hrs",
         "isolation_forest_outlier"],
    )
    severity_filter = col2.selectbox("Filter by severity:", ["(all)", "high", "medium"])

    with st.spinner("Detecting anomalies..."):
        result = get_anomalies(
            reason=None if reason_filter == "(all)" else reason_filter,
            severity=None if severity_filter == "(all)" else severity_filter,
        )

    if "error" in result:
        st.error(result["error"])
        return

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Flags", result.get("total_anomalies", 0))
    c2.metric("Unique Tickets", result.get("unique_tickets_flagged", 0))
    c3.metric("Flag Types", len(result.get("by_reason", {})))

    # Chart
    if result.get("by_reason"):
        st.subheader("Flags by Reason")
        chart_df = pd.DataFrame(
            list(result["by_reason"].items()),
            columns=["Reason", "Count"],
        ).set_index("Reason")
        st.bar_chart(chart_df)

    # Table
    st.subheader("Flagged Tickets")
    if result.get("anomalies"):
        anomaly_df = pd.DataFrame(result["anomalies"])
        numeric_columns = [
            "response_time_hrs",
            "resolution_time_hrs",
            "customer_rating",
            "z_score",
            "score",
        ]
        for column in numeric_columns:
            if column in anomaly_df:
                anomaly_df[column] = pd.to_numeric(anomaly_df[column], errors="coerce")
        st.dataframe(anomaly_df, width="stretch")
    else:
        st.info("No anomalies match the current filters.")


def render_data_tab():
    """Tab 3: Raw data explorer."""
    st.header("📊 Data Explorer")
    st.caption("Browse the raw support tickets.")

    col1, col2, col3 = st.columns(3)
    status = col1.selectbox("Status:", ["(all)", "Open", "Resolved", "Escalated"])
    priority = col2.selectbox("Priority:", ["(all)", "Low", "Medium", "High", "Critical"])
    category = col3.selectbox("Category:", ["(all)", "Billing", "Technical", "General"])

    with st.spinner("Loading..."):
        result = get_tickets(
            status=None if status == "(all)" else status,
            priority=None if priority == "(all)" else priority,
            category=None if category == "(all)" else category,
            limit=500,
        )

    if "error" in result:
        st.error(result["error"])
        return

    st.metric("Tickets Found", result.get("total", 0))

    if result.get("tickets"):
        df = pd.DataFrame(result["tickets"])
        st.dataframe(df, width="stretch")

        # Quick charts
        st.subheader("Quick Insights")
        c1, c2 = st.columns(2)
        with c1:
            st.write("**By Priority**")
            st.bar_chart(df["priority"].value_counts())
        with c2:
            st.write("**By Status**")
            st.bar_chart(df["status"].value_counts())
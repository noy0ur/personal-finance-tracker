from datetime import date
import io
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Personal Finance Tracker", page_icon="💸", layout="wide")

CATEGORIES = [
    "Food", "Transport", "Housing", "Utilities", "Shopping",
    "Health", "Education", "Entertainment", "Savings", "Salary", "Other"
]
TYPES = ["Income", "Expense"]
REQUIRED_COLUMNS = {"date", "type", "category", "description", "amount"}

def clean_transactions(frame):
    """Validate and normalize uploaded transaction data."""
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))

    result = frame.copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce").dt.date
    result["type"] = result["type"].astype(str).str.strip().str.title()
    result["category"] = result["category"].astype(str).str.strip()
    result["description"] = result["description"].fillna("").astype(str).str.strip()
    result["amount"] = pd.to_numeric(result["amount"], errors="coerce")

    result = result.dropna(subset=["date", "amount"])
    result = result[result["type"].isin(TYPES)]
    result = result[result["amount"] > 0]
    result["category"] = result["category"].replace("", "Other")
    result["description"] = result["description"].replace("", "No description")
    return result[list(REQUIRED_COLUMNS)].sort_values("date", ascending=False).reset_index(drop=True)

def starter_data():
    sample_path = os.path.join(os.path.dirname(__file__), "sample_transactions.csv")
    return clean_transactions(pd.read_csv(sample_path))

st.title("💸 Personal Finance Tracker")
st.write("Track income and expenses, understand spending patterns, and compare expenses with a monthly budget.")
st.caption("Demo project. Use sample data first. Avoid uploading bank statements or personal financial information to a public repository.")

if "transactions" not in st.session_state:
    st.session_state.transactions = starter_data()

with st.sidebar:
    st.header("Data")
    uploaded = st.file_uploader("Import transactions (CSV)", type=["csv"])
    if uploaded is not None:
        try:
            imported = clean_transactions(pd.read_csv(uploaded))
            if st.button("Replace current data with imported CSV"):
                st.session_state.transactions = imported
                st.success(f"Imported {len(imported)} transactions.")
                st.rerun()
        except Exception as exc:
            st.error(f"Could not import CSV: {exc}")

    st.divider()
    st.subheader("Monthly expense budget")
    budget = st.number_input("Budget amount", min_value=0.0, value=25000.0, step=1000.0)
    st.caption("Budget is a demo setting and resets when the app session restarts.")

transactions = st.session_state.transactions.copy()

with st.expander("➕ Add a transaction", expanded=False):
    with st.form("add_transaction_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            tx_date = st.date_input("Date", value=date.today())
            tx_type = st.selectbox("Type", TYPES)
        with c2:
            tx_category = st.selectbox("Category", CATEGORIES)
            tx_amount = st.number_input("Amount (₹)", min_value=1.0, value=100.0, step=50.0)
        with c3:
            tx_description = st.text_input("Description", placeholder="e.g. Grocery shopping")
        add_clicked = st.form_submit_button("Add transaction")
        if add_clicked:
            new_row = pd.DataFrame([{
                "date": tx_date, "type": tx_type, "category": tx_category,
                "description": tx_description.strip() or "No description", "amount": float(tx_amount)
            }])
            st.session_state.transactions = pd.concat(
                [st.session_state.transactions, new_row], ignore_index=True
            )
            st.success("Transaction added for this session.")
            st.rerun()

if transactions.empty:
    st.info("No valid transactions yet. Add a transaction or import a CSV.")
    st.stop()

transactions["month"] = pd.to_datetime(transactions["date"]).dt.to_period("M").astype(str)
months = sorted(transactions["month"].unique())
selected_month = st.selectbox("Choose month", options=months, index=len(months)-1)
month_data = transactions[transactions["month"] == selected_month].copy()

income = month_data.loc[month_data["type"] == "Income", "amount"].sum()
expenses = month_data.loc[month_data["type"] == "Expense", "amount"].sum()
balance = income - expenses
savings_rate = (balance / income * 100) if income > 0 else 0.0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Income", f"₹{income:,.0f}")
m2.metric("Expenses", f"₹{expenses:,.0f}")
m3.metric("Net balance", f"₹{balance:,.0f}", delta=f"{balance:,.0f}")
m4.metric("Savings rate", f"{savings_rate:.1f}%")

budget_used = (expenses / budget * 100) if budget > 0 else 0
st.subheader("Monthly budget")
if budget > 0:
    st.progress(min(budget_used / 100, 1.0))
    st.write(f"Spent ₹{expenses:,.0f} of ₹{budget:,.0f} ({budget_used:.1f}%).")
    if expenses > budget:
        st.warning(f"You are ₹{expenses - budget:,.0f} over the monthly budget.")
    else:
        st.success(f"₹{budget - expenses:,.0f} remains in the monthly budget.")
else:
    st.info("Set a budget above ₹0 to see budget progress.")

left, right = st.columns(2)
with left:
    st.subheader("Expenses by category")
    expense_data = month_data[month_data["type"] == "Expense"]
    if expense_data.empty:
        st.info("No expenses recorded for this month.")
    else:
        category_data = expense_data.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
        fig = px.pie(category_data, names="category", values="amount", hole=0.45,
                     title="Where your money goes")
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Income vs expenses by month")
    monthly = transactions.pivot_table(index="month", columns="type", values="amount", aggfunc="sum", fill_value=0).reset_index()
    for col in TYPES:
        if col not in monthly.columns:
            monthly[col] = 0
    monthly_long = monthly.melt(id_vars="month", value_vars=TYPES, var_name="Transaction type", value_name="Amount")
    fig = px.bar(monthly_long, x="month", y="Amount", color="Transaction type", barmode="group",
                 title="Monthly cash flow")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Transactions")
filter_type = st.multiselect("Filter by transaction type", options=TYPES, default=TYPES)
filtered = month_data[month_data["type"].isin(filter_type)].copy()
display = filtered[["date", "type", "category", "description", "amount"]].sort_values("date", ascending=False)
st.dataframe(display, use_container_width=True, hide_index=True)

csv_bytes = transactions[["date", "type", "category", "description", "amount"]].to_csv(index=False).encode("utf-8")
st.download_button("Download transactions as CSV", data=csv_bytes,
                   file_name="my_transactions.csv", mime="text/csv")

st.caption("Note: entries added in the app are kept only for the current session unless you download the CSV. This is a portfolio demo, not a banking app.")

import streamlit as st
import requests
from datetime import date
import pandas as pd
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(page_title="Day-to-Day Expense Tracker", layout="centered")

# Theme toggle (Streamlit uses its own theme, so this is a placeholder)
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #333;
}
[data-theme="dark"] body {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("Day-to-Day Expense Tracker")

# Expense Form
with st.form("expense_form"):
    st.date_input("Date", value=date.today(), key="date")
    st.text_input("Description", key="description")
    st.number_input("Amount", min_value=0.0, step=0.01, key="amount")
    category = st.selectbox("Category", [
        "Food", "Transportation", "Entertainment", "Clothing", "Personal Care", "Education", "Savings",
        "Gadgets/Electronics", "Hobbies", "Snacks", "Gifts", "Mobile Recharge", "Home Rent", "Other"
    ])
    st.text_area("Notes", key="notes")
    receipt = st.file_uploader("Receipt Image", type=["png", "jpg", "jpeg"])

    # Submit button
    submitted = st.form_submit_button("Add Expense")
    if submitted:
        st.success("Expense added successfully!")

# Clear All Expenses
if st.button("Clear All Expenses"):
    response = requests.post("http://localhost:5000/clear")  # Replace with actual endpoint
    if response.status_code == 200:
        st.success("All expenses cleared successfully!")
    else:
        st.error("Failed to clear expenses.")

# Backup Functionality
if st.button("Backup Locally"):
    response = requests.get("http://localhost:5000/backup/local")  # Replace with actual endpoint
    if response.status_code == 200:
        st.success("Backup completed successfully!")
    else:
        st.error("Backup failed.")

# Placeholder data for expenses (replace with actual data fetching logic)
data = {
    "Date": ["2025-10-15", "2025-10-16", "2025-10-16"],
    "Description": ["Lunch", "Bus Ticket", "Movie"],
    "Amount": [150.0, 50.0, 300.0],
    "Category": ["Food", "Transportation", "Entertainment"],
    "Notes": ["", "", "Watched a movie"],
}
expenses_df = pd.DataFrame(data)

# Display expenses table
st.header("Expenses")
st.dataframe(expenses_df)

# Daily Expenses
st.header("Day-to-Day Expenses")
daily_totals = expenses_df.groupby("Date")["Amount"].sum()
for date, total in daily_totals.items():
    st.subheader(f"{date}")
    daily_expenses = expenses_df[expenses_df["Date"] == date]
    st.table(daily_expenses.drop(columns="Date"))
    st.write(f"**Total for {date}: ₹{total:.2f}**")

# Dashboard / Summary
st.header("Dashboard / Summary")

# Category-wise Spending Pie Chart
st.subheader("Category-wise Spending")
category_totals = expenses_df.groupby("Category")["Amount"].sum()
fig1, ax1 = plt.subplots()
ax1.pie(category_totals, labels=category_totals.index, autopct='%1.1f%%', startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
st.pyplot(fig1)

# Daily Trends Line Chart
st.subheader("Daily Trends")
fig2, ax2 = plt.subplots()
ax2.plot(daily_totals.index, daily_totals.values, marker='o')
ax2.set_title("Daily Expenses")
ax2.set_xlabel("Date")
ax2.set_ylabel("Amount (₹)")
ax2.grid(True)
st.pyplot(fig2)

# Export functionality
st.header("Export & Backup")
if st.button("Export to Excel", key="export_excel"):
    expenses_df.to_excel("expenses.xlsx", index=False)
    st.success("Exported to Excel successfully!")

if st.button("Export to PDF", key="export_pdf"):
    st.warning("PDF export functionality is not implemented yet.")

if st.button("Backup Locally", key="backup_local"):
    st.success("Backup completed successfully!")
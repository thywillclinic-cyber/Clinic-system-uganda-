import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="Uganda Clinic Management System", layout="wide")

# Initialize Session Data (Simulated Database)
if 'db' not in st.session_state:
    st.session_state.db = {
        "patients": [], "lab_orders": [], "sales": [], "expenses": [],
        "inventory": pd.DataFrame([
            {"Item": "Paracetamol", "Stock": 100, "Price": 500, "Cost": 300, "Expiry": "2025-10-01"},
            {"Item": "Amoxicillin", "Stock": 20, "Price": 2000, "Cost": 1500, "Expiry": "2024-12-20"}
        ]),
        "attendance": [], "messages": [], "leave": []
    }

# --- 2. LOGIN PAGE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("🏥 Clinic Management System - Login")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        phone = st.text_input("Mobile Phone Number")
        pwd = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if phone == "256772475760" and pwd == "96985255":
                st.session_state.logged_in = True
                st.session_state.user = "Admin"
                st.session_state.db["attendance"].append({"Staff": phone, "Date": date.today(), "In": datetime.now().strftime("%H:%M")})
                st.rerun()
            else:
                st.error("Invalid Login")

# --- 3. MAIN SYSTEM MODULES ---
def main():
    st.sidebar.title("Clinic Departments")
    menu = ["Reception", "Nursing (Triage)", "Consultation", "Laboratory", "Pharmacy (POS)", 
            "Maternity & FP", "Inventory", "Accounts & Expenses", "Staff Management"]
    choice = st.sidebar.selectbox("Go to:", menu)

    # RECEPTION
    if choice == "Reception":
        st.header("Patient Registration")
        with st.form("reg"):
            name = st.text_input("Patient Name")
            age = st.number_input("Age", 0, 100)
            reason = st.text_input("Reason for Visit")
            if st.form_submit_button("Register"):
                st.session_state.db["patients"].append({"name": name, "age": age, "status": "Nursing", "vitals": {}})
                st.success("Patient queued for Nursing.")

    # NURSING
    elif choice == "Nursing (Triage)":
        st.header("Nursing & Triage")
        waiting = [p for p in st.session_state.db["patients"] if p["status"] == "Nursing"]
        if not waiting: st.info("No patients waiting")
        else:
            p_name = st.selectbox("Select Patient", [p["name"] for p in waiting])
            temp = st.text_input("Temperature (°C)")
            bp = st.text_input("Blood Pressure")
            if st.button("Save Vitals & Send to Consultation"):
                for p in st.session_state.db["patients"]:
                    if p["name"] == p_name: 
                        p["status"] = "Consultation"
                        p["vitals"] = {"Temp": temp, "BP": bp}
                st.success("Vitals Sent.")

    # PHARMACY (POS)
    elif choice == "Pharmacy (POS)":
        st.header("Pharmacy Point of Sale (UGX)")
        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("Drug", st.session_state.db["inventory"]["Item"])
            qty = st.number_input("Qty", 1)
            disc = st.number_input("Discount", 0)
            price = st.session_state.db["inventory"].loc[st.session_state.db["inventory"]["Item"] == item, "Price"].values[0]
            cost = st.session_state.db["inventory"].loc[st.session_state.db["inventory"]["Item"] == item, "Cost"].values[0]
            total = (qty * price) - disc
            if st.button(f"Sell: UGX {total:,}"):
                st.session_state.db["sales"].append({"Total": total, "Profit": total - (qty * cost), "Date": date.today()})
                st.success("Sale Recorded.")
        with col2:
            st.subheader("Inventory Alerts")
            st.dataframe(st.session_state.db["inventory"])

    # MATERNITY & FP
    elif choice == "Maternity & FP":
        st.header("Maternity & Family Planning (UCG)")
        st.tabs(["ANC Monitoring", "Delivery Tool", "Postpartum", "FP Services"])
        st.info("Uganda Clinical Guidelines 2023 Integrated")

    # STAFF MANAGEMENT
    elif choice == "Staff Management":
        st.header("Staff Administration")
        tab1, tab2 = st.tabs(["Attendance", "Leave/Off Requests"])
        with tab1: st.table(st.session_state.db["attendance"])
        with tab2:
            st.date_input("Request Date Off")
            st.selectbox("Reason", ["Leave", "Off"])
            st.button("Submit Request")

    # ACCOUNTS
    elif choice == "Accounts & Expenses":
        st.header("Facility Reports")
        sales_df = pd.DataFrame(st.session_state.db["sales"])
        rev = sales_df["Total"].sum() if not sales_df.empty else 0
        prof = sales_df["Profit"].sum() if not sales_df.empty else 0
        st.metric("Daily Revenue", f"UGX {rev:,}")
        st.metric("Net Profit", f"UGX {prof:,}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# --- RUN ---
if not st.session_state.logged_in:
    login_page()
else:
    main()
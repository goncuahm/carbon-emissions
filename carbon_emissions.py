import streamlit as st
import pandas as pd
import numpy as np
from enum import Enum
from dataclasses import dataclass

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Carbon Emissions Calculator",
    layout="wide"
)

# ============================================================
# DATA MODELS
# ============================================================
class FuelType(Enum):
    NATURAL_GAS = "Natural Gas"
    DIESEL = "Diesel"
    GASOLINE = "Gasoline"
    LPG = "LPG"

@dataclass
class EmissionFactor:
    value: float
    unit: str
    source: str

# ============================================================
# EMISSION FACTORS
# ============================================================
FUEL_FACTORS = {
    FuelType.NATURAL_GAS: EmissionFactor(1.902, "kg CO₂ / m³", "EU MRR"),
    FuelType.DIESEL: EmissionFactor(2.676, "kg CO₂ / liter", "EU MRR"),
    FuelType.GASOLINE: EmissionFactor(2.296, "kg CO₂ / liter", "EU MRR"),
    FuelType.LPG: EmissionFactor(1.537, "kg CO₂ / liter", "EU MRR"),
}

ELECTRICITY_FACTORS = {
    "EU Average": 0.275,
    "Germany": 0.385,
    "France": 0.057,
    "Italy": 0.298,
    "Spain": 0.205,
    "Poland": 0.734,
    "Sweden": 0.013,
}

# ============================================================
# SCOPE 3 — PROCUREMENT FACTORS (EEIO-STYLE)
# ============================================================
PROCUREMENT_FACTORS = {
    "IT Equipment": 0.45,
    "Office Furniture": 0.32,
    "Construction Services": 0.28,
    "Steel Products": 1.90,
    "Chemicals": 1.25,
    "Textiles & Apparel": 0.55,
    "Food & Catering Services": 0.62,
    "Professional Services": 0.15,
    "Transportation Services": 0.41,
}

# ============================================================
# STATE
# ============================================================
if "results" not in st.session_state:
    st.session_state.results = []

# ============================================================
# UI
# ============================================================
st.title("🌍 Carbon Emissions Calculator")
st.caption("Scopes 1, 2, 3 — CSRD / GHG Protocol aligned")

# ============================================================
# SCOPE 1
# ============================================================
st.header("🔥 Scope 1 — Direct Emissions")

fuel = st.selectbox("Fuel Type", list(FuelType))
quantity = st.number_input("Fuel Quantity", min_value=0.0)

if st.button("Add Scope 1"):
    factor = FUEL_FACTORS[fuel]
    emissions = quantity * factor.value / 1000
    st.session_state.results.append({
        "Scope": "Scope 1",
        "Category": fuel.value,
        "Activity": quantity,
        "Unit": factor.unit,
        "Emission Factor": factor.value,
        "Emissions (tCO₂e)": emissions
    })
    st.success(f"{emissions:.2f} tCO₂ added")

# ============================================================
# SCOPE 2
# ============================================================
st.header("⚡ Scope 2 — Electricity")

country = st.selectbox("Electricity Country", list(ELECTRICITY_FACTORS.keys()))
kwh = st.number_input("Electricity Consumption (kWh)", min_value=0.0)

if st.button("Add Scope 2"):
    factor = ELECTRICITY_FACTORS[country]
    emissions = kwh * factor / 1000
    st.session_state.results.append({
        "Scope": "Scope 2",
        "Category": "Electricity",
        "Activity": kwh,
        "Unit": "kWh",
        "Emission Factor": factor,
        "Emissions (tCO₂e)": emissions
    })
    st.success(f"{emissions:.2f} tCO₂e added")

# ============================================================
# SCOPE 3
# ============================================================
st.header("🚚 Scope 3 — Purchased Goods & Services")

procurement = st.selectbox(
    "Procurement Category",
    list(PROCUREMENT_FACTORS.keys())
)

st.info(
    f"Emission factor: **{PROCUREMENT_FACTORS[procurement]} kg CO₂e / €** "
    f"(EEIO-based)"
)

spend = st.number_input("Annual Spend (€)", min_value=0.0)

if st.button("Add Scope 3"):
    factor = PROCUREMENT_FACTORS[procurement]
    emissions = spend * factor / 1000
    st.session_state.results.append({
        "Scope": "Scope 3",
        "Category": procurement,
        "Activity": spend,
        "Unit": "EUR",
        "Emission Factor": factor,
        "Emissions (tCO₂e)": emissions
    })
    st.success(f"{emissions:.2f} tCO₂e added")

# ============================================================
# RESULTS
# ============================================================
st.header("📊 Results")

df = pd.DataFrame(st.session_state.results)

if not df.empty:
    st.subheader("Detailed Emissions")
    st.dataframe(df, use_container_width=True)

    summary = df.groupby("Scope", as_index=False)["Emissions (tCO₂e)"].sum()

    st.subheader("Emissions by Scope")
    st.bar_chart(
        summary.set_index("Scope")["Emissions (tCO₂e)"]
    )

    total = summary["Emissions (tCO₂e)"].sum()
    st.metric("🌱 Total Carbon Footprint (tCO₂e)", f"{total:,.2f}")

else:
    st.info("No emissions recorded yet.")

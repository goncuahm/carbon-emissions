import streamlit as st
import pandas as pd
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="EU Carbon Emissions Calculator",
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
    COAL = "Coal"

@dataclass
class EmissionFactor:
    value: float
    unit: str
    source: str
    year: int

class EUEmissionFactors:
    FUEL_FACTORS = {
        FuelType.NATURAL_GAS: EmissionFactor(1.902, "kg CO₂ / m³", "EU MRR", 2023),
        FuelType.DIESEL: EmissionFactor(2.676, "kg CO₂ / liter", "EU MRR", 2023),
        FuelType.GASOLINE: EmissionFactor(2.296, "kg CO₂ / liter", "EU MRR", 2023),
        FuelType.LPG: EmissionFactor(1.537, "kg CO₂ / liter", "EU MRR", 2023),
        FuelType.COAL: EmissionFactor(2.35, "kg CO₂ / kg", "EU MRR", 2023),
    }

    ELECTRICITY_FACTORS = {
        "EU_AVERAGE": 0.275,
        "DE": 0.385,
        "FR": 0.057,
        "IT": 0.298,
        "ES": 0.205,
        "PL": 0.734,
        "NL": 0.395,
        "SE": 0.013,
    }

# ============================================================
# CALCULATORS
# ============================================================
class CarbonFootprintCalculator:
    def __init__(self):
        self.results = []

    def add(self, result: Dict):
        self.results.append(result)

    def dataframe(self):
        if not self.results:
            return pd.DataFrame()
        return pd.DataFrame(self.results)

    def summary(self):
        df = self.dataframe()
        if df.empty:
            return pd.DataFrame()
        return df.groupby("Scope")["Emissions (tCO₂e)"].sum().reset_index()

    def total(self):
        s = self.summary()
        return float(s["Emissions (tCO₂e)"].sum()) if not s.empty else 0.0


# ============================================================
# STREAMLIT UI
# ============================================================
st.title("🌍 EU-Compliant Carbon Emissions Calculator")
st.caption("Scopes 1, 2, 3 — EU ETS / CSRD / GHG Protocol aligned")

calculator = CarbonFootprintCalculator()
ef = EUEmissionFactors()

# ============================================================
# SCOPE 1
# ============================================================
st.header("🔥 Scope 1 — Direct Emissions")

fuel = st.selectbox("Fuel Type", list(FuelType))
quantity = st.number_input("Fuel Quantity", min_value=0.0)

if st.button("Add Scope 1 Emission"):
    factor = ef.FUEL_FACTORS[fuel]
    emissions = quantity * factor.value / 1000
    calculator.add({
        "Scope": "Scope 1",
        "Category": fuel.value,
        "Activity": quantity,
        "Unit": factor.unit,
        "Emission Factor": factor.value,
        "Emissions (tCO₂e)": emissions
    })
    st.success(f"Added {emissions:.2f} tCO₂")

# ============================================================
# SCOPE 2
# ============================================================
st.header("⚡ Scope 2 — Electricity")

country = st.selectbox("Country", list(ef.ELECTRICITY_FACTORS.keys()))
electricity = st.number_input("Electricity Consumption (kWh)", min_value=0.0)

if st.button("Add Scope 2 Emission"):
    factor = ef.ELECTRICITY_FACTORS[country]
    emissions = electricity * factor / 1000
    calculator.add({
        "Scope": "Scope 2",
        "Category": "Electricity",
        "Activity": electricity,
        "Unit": "kWh",
        "Emission Factor": factor,
        "Emissions (tCO₂e)": emissions
    })
    st.success(f"Added {emissions:.2f} tCO₂e")

# ============================================================
# SCOPE 3
# ============================================================
st.header("🚚 Scope 3 — Purchased Goods")

spend = st.number_input("Procurement Spend (€)", min_value=0.0)
factor_spend = st.number_input("Emission Factor (kg CO₂e / €)", value=0.45)

if st.button("Add Scope 3 Emission"):
    emissions = spend * factor_spend / 1000
    calculator.add({
        "Scope": "Scope 3",
        "Category": "Purchased Goods",
        "Activity": spend,
        "Unit": "EUR",
        "Emission Factor": factor_spend,
        "Emissions (tCO₂e)": emissions
    })
    st.success(f"Added {emissions:.2f} tCO₂e")

# ============================================================
# RESULTS
# ============================================================
st.header("📊 Results")

df = calculator.dataframe()
summary = calculator.summary()

if not df.empty:
    st.subheader("Detailed Emissions Table")
    st.dataframe(df, use_container_width=True)

    st.subheader("Emissions by Scope")
    st.bar_chart(summary.set_index("Scope"))

    st.subheader("Scope Share")
    st.pyplot(
        summary.set_index("Scope")
        .plot.pie(y="Emissions (tCO₂e)", autopct="%1.1f%%", legend=False)
        .get_figure()
    )

    st.metric("🌱 Total Carbon Footprint (tCO₂e)", f"{calculator.total():,.2f}")

else:
    st.info("No emissions added yet.")

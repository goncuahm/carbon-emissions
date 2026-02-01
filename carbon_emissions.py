import streamlit as st
import pandas as pd
import plotly.express as px

from carbon_calculator import (
    CarbonFootprintCalculator,
    FuelType
)

st.set_page_config(
    page_title="EU Carbon Emissions Calculator",
    layout="wide"
)

st.title("EU Carbon Emissions Calculator")
st.caption("EU ETS · CSRD · GHG Protocol aligned")

calc = CarbonFootprintCalculator()

# -------------------------
# Scope 1
# -------------------------
st.header("Scope 1 — Direct Emissions")

col1, col2 = st.columns(2)

with col1:
    fuel = st.selectbox("Fuel type", [f.name for f in FuelType])
    quantity = st.number_input("Fuel quantity", min_value=0.0)

with col2:
    if st.button("Add Scope 1 emission"):
        result = calc.scope1_calc.calculate_stationary_combustion(
            fuel_type=FuelType[fuel],
            quantity=quantity
        )
        calc.add_emission_source(result)
        st.success("Scope 1 emission added")

# -------------------------
# Scope 2
# -------------------------
st.header("Scope 2 — Electricity")

electricity = st.number_input("Electricity consumption (kWh)", min_value=0.0)
country = st.selectbox(
    "Country",
    ["EU_AVERAGE", "DE", "FR", "IT", "ES", "PL", "NL", "BE", "SE", "AT", "DK"]
)

if st.button("Add Scope 2 emission"):
    result = calc.scope2_calc.calculate_location_based(
        electricity_kwh=electricity,
        country_code=country
    )
    calc.add_emission_source(result)
    st.success("Scope 2 emission added")

# -------------------------
# Results
# -------------------------
st.header("Results")

summary = calc.get_summary()

if not summary.empty:
    summary_df = summary.reset_index()
    summary_df.columns = ["Scope", "Emissions (tCO₂e)"]

    st.subheader("Emissions by Scope")
    st.dataframe(summary_df, use_container_width=True)

    fig = px.bar(
        summary_df,
        x="Scope",
        y="Emissions (tCO₂e)",
        color="Scope",
        title="Carbon Footprint by Scope"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.metric(
        "Total Carbon Footprint",
        f"{calc.calculate_total_footprint():,.2f} tCO₂e"
    )
else:
    st.info("No emissions added yet.")

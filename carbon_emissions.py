import streamlit as st
import pandas as pd
import plotly.express as px

# Import your calculator classes
from carbon_calculator import (
    CarbonFootprintCalculator,
    FuelType
)

st.set_page_config(
    page_title="EU Carbon Footprint Calculator",
    layout="wide"
)

st.title("🌍 EU-Compliant Carbon Footprint Calculator")
st.caption("Scopes 1, 2 & 3 | EU ETS · CSRD · GHG Protocol")

calc = CarbonFootprintCalculator()

# ======================
# SIDEBAR INPUTS
# ======================
st.sidebar.header("Inputs")

scope = st.sidebar.selectbox(
    "Select Scope",
    ["Scope 1", "Scope 2", "Scope 3"]
)

# ======================
# SCOPE 1
# ======================
if scope == "Scope 1":
    st.subheader("Scope 1 — Direct Emissions")

    fuel = st.selectbox("Fuel Type", list(FuelType))
    quantity = st.number_input("Fuel Quantity", min_value=0.0)

    if st.button("Add Scope 1 Emissions"):
        res = calc.scope1_calc.calculate_stationary_combustion(
            fuel_type=fuel,
            quantity=quantity
        )
        calc.add_emission_source(res)
        st.success("Scope 1 emissions added.")

# ======================
# SCOPE 2
# ======================
elif scope == "Scope 2":
    st.subheader("Scope 2 — Purchased Electricity")

    electricity = st.number_input("Electricity Consumption (kWh)", min_value=0.0)
    country = st.selectbox(
        "Country",
        ["EU_AVERAGE", "DE", "FR", "IT", "ES", "PL", "NL", "SE", "AT", "DK"]
    )
    method = st.radio("Method", ["Location-based", "Market-based"])

    renewable = 0.0
    if method == "Market-based":
        renewable = st.number_input(
            "Renewable Electricity (kWh, with GOs)",
            min_value=0.0
        )

    if st.button("Add Scope 2 Emissions"):
        if method == "Location-based":
            res = calc.scope2_calc.calculate_location_based(
                electricity_kwh=electricity,
                country_code=country
            )
        else:
            res = calc.scope2_calc.calculate_market_based(
                electricity_kwh=electricity,
                renewable_kwh=renewable,
                country_code=country
            )

        calc.add_emission_source(res)
        st.success("Scope 2 emissions added.")

# ======================
# SCOPE 3
# ======================
elif scope == "Scope 3":
    st.subheader("Scope 3 — Value Chain")

    category = st.selectbox(
        "Category",
        ["Purchased Goods", "Business Travel"]
    )

    if category == "Purchased Goods":
        spend = st.number_input("Spend (€)", min_value=0.0)
        ef = st.number_input("Emission Factor (kg CO₂e / €)", min_value=0.0)

        if st.button("Add Scope 3 Emissions"):
            res = calc.scope3_calc.calculate_purchased_goods(
                spend_eur=spend,
                emission_factor_per_eur=ef
            )
            calc.add_emission_source(res)
            st.success("Scope 3 emissions added.")

    if category == "Business Travel":
        distance = st.number_input("Distance (km)", min_value=0.0)
        mode = st.selectbox(
            "Transport Mode",
            ["short_haul_flight", "medium_haul_flight", "long_haul_flight", "train"]
        )

        if st.button("Add Scope 3 Emissions"):
            res = calc.scope3_calc.calculate_business_travel(
                distance_km=distance,
                transport_mode=mode
            )
            calc.add_emission_source(res)
            st.success("Scope 3 emissions added.")

# ======================
# RESULTS
# ======================
st.divider()
st.header("📊 Results")

df = calc.get_detailed_report()

if not df.empty:
    st.subheader("Detailed Emissions Table")
    st.dataframe(df, use_container_width=True)

    summary = calc.get_summary().reset_index()
    summary.columns = ["Scope", "Emissions (tCO₂e)"]

    st.subheader("Summary by Scope")
    st.table(summary)

    col1, col2 = st.columns(2)

    with col1:
        fig_bar = px.bar(
            summary,
            x="Scope",
            y="Emissions (tCO₂e)",
            title="Emissions by Scope",
            text_auto=".2f"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        fig_pie = px.pie(
            summary,
            names="Scope",
            values="Emissions (tCO₂e)",
            title="Emissions Share by Scope"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    total = calc.calculate_total_footprint()
    st.metric("Total Carbon Footprint", f"{total:,.2f} tCO₂e")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Download Detailed CSV",
        csv,
        "carbon_footprint.csv",
        "text/csv"
    )

else:
    st.info("Add emission sources to see results.")

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

# Streamlit UI
st.title("Pressure Data Analysis Tool")

uploaded_file = st.file_uploader("Upload pressure data file (CSV or XLSX)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            df = pd.read_excel(uploaded_file, engine="openpyxl")
        else:
            df = pd.read_csv(uploaded_file)

        # Displaying the Distribution of the Columns
        st.subheader("Data Distribution")
        st.write(df.describe())

        # Displaying the Column in Dataset
        st.subheader("Columns in the Dataset")
        st.write(df.columns)

        # Selection of Specify Range
        st.sidebar.subheader("Region Selection")
        start = st.sidebar.slider("Select Start Index", 0, len(df) - 1, 0)
        end = st.sidebar.slider("Select End Index", 0, len(df) - 1, len(df) - 1)

        selected_data = df.iloc[start:end]
        st.subheader("Pressure Data Visualization")
        st.line_chart(selected_data)

        # 1. Mean Steady State Pressure
        mean_steady_state_pressure = selected_data["P2"].mean()

        # 2. Peak Pressure
        peak_pressure = selected_data["P2"].max()

        # 3. Pressure Standard Deviation
        pressure_std_deviation = selected_data["P2"].std()

        # 4. Pressure Roughness (STD. Nozzle Pressure / Mean Nozzle Pressure * 100)
        nozzle_pressure_std = selected_data["P2"].std()
        mean_nozzle_pressure = selected_data["P2"].mean()
        pressure_roughness = (nozzle_pressure_std / mean_nozzle_pressure) * 100

        # 5. T90 Pressure Rise
        threshold_t90 = 0.9 * mean_steady_state_pressure
        t90_index = (selected_data["P2"] >= threshold_t90).idxmax()
        t90_pressure_rise_time = selected_data["Time"].iloc[t90_index]

        # 6. T10 Pressure Fall Time
        threshold_t10 = 0.1 * mean_steady_state_pressure
        t10_index = (selected_data["P2"] <= threshold_t10).idxmax()
        t10_pressure_fall_time = selected_data["Time"].iloc[t10_index]

        # Displaying the calculated metrics
        st.subheader("Calculated Metrics")
        st.write(f"Mean Steady State Pressure: {mean_steady_state_pressure:.2f} Pa")
        st.write(f"Peak Pressure: {peak_pressure:.2f} Pa")
        st.write(f"Pressure Standard Deviation: {pressure_std_deviation:.2f} Pa")
        st.write(f"Pressure Roughness: {pressure_roughness:.2f}%")
        st.write(f"T90 Pressure Rise Time: {t90_pressure_rise_time} ")
        st.write(f"T10 Pressure Fall Time: {t10_pressure_fall_time} ")

        # Data Saving Code
        st.sidebar.subheader("Data Save")
        save_original_data = st.sidebar.checkbox("Save Original Data")
        save_analysis_results = st.sidebar.checkbox("Save Analysis Results")

        if save_original_data or save_analysis_results:
            with st.spinner("Saving Data..."):
                if save_original_data:
                    original_data_filename = "original_data.csv"
                    df.to_csv(original_data_filename, index=False)
                    st.success(f"Original data saved as {original_data_filename}")

                if save_analysis_results:
                    analysis_results = {
                        "Metric": ["Mean Steady State Pressure", "Peak Pressure",
                                    "Pressure Standard Deviation", "Pressure Roughness",
                                    "T90 Pressure Rise Time", "T10 Pressure Fall Time"],
                        "Value": [mean_steady_state_pressure, peak_pressure,
                                  pressure_std_deviation, pressure_roughness,
                                  t90_pressure_rise_time, t10_pressure_fall_time]
                    }

                    analysis_df = pd.DataFrame(analysis_results)
                    analysis_filename = "analysis_results.csv"
                    analysis_df.to_csv(analysis_filename, index=False)
                    st.success(f"Analysis results saved as {analysis_filename}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

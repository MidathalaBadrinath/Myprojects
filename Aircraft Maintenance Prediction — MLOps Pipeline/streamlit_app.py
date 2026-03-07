import streamlit as st
import pandas as pd
import random
from model.prediction import make_predictions
from model.data_cleaning import clean_data
from model.recommendation import generate_recommendation
#from mlflow.mlflow_logging import log_to_mlflow
#from mlflow_utils.mlflow_logging import log_to_mlflow

import joblib
import random
import time

# Load the pre-trained models
maintenance_model = joblib.load('models/maintenance_classifier_model.pkl')
lifespan_model = joblib.load('models/remaining_life_regressor_model.pkl')

# GitHub URL
github_url = "https://github.com/Yamini-Chittari/CI-CD-pipeline-MLOps-aircraft-Predictive-maintanence"

# MLflow Tracking URL (local)
mlflow_url = "http://localhost:5000"

# Function to generate predictions based on user input
def predict(user_data):
    X_user = user_data[['Temperature (°C)', 'Pressure (bar)', 'Vibration (mm/s)', 'Working_Hours']]
    predicted_maintenance = maintenance_model.predict(X_user)[0]
    predicted_lifespan = lifespan_model.predict(X_user)[0]

    # Recommendation generation based on predicted failure type
    failure_type = "None" if predicted_maintenance == 0 else random.choice(
        ['Turbine Overheat', 'Pressure Loss', 'Valve Stuck', 'Fuel Leakage'])
    flight_type = random.choice(['commercial', 'cargo', 'private', 'long-haul', 'short-haul'])
    flight_number = random.randint(1000, 9999)

    recommendation = generate_recommendation(failure_type, flight_type, flight_number, predicted_lifespan)

    return recommendation


# Streamlit UI setup
st.title("Aircraft Maintenance and Prediction System")

# Add GitHub URL and make it clickable
st.markdown(f"**Project Source Code**: [GitHub Repository]({github_url})")

# Add MLflow Tracking URL and make it clickable
st.markdown(f"**MLflow Tracking Server**: [Open MLflow](http://localhost:5000)")

user_input = st.radio("Select input method", ('Upload CSV', 'Manual Input', 'Simulated Data'))

if user_input == 'Upload CSV':
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        user_data = pd.read_csv(uploaded_file)
        if all(col in user_data.columns for col in
               ['Temperature (°C)', 'Pressure (bar)', 'Vibration (mm/s)', 'Working_Hours']):
            st.write("First row of the provided dataset:")
            st.write(user_data.head(1))  # Display first row
            recommendation = predict(user_data.head(1))  # Pass only the first row for prediction
            st.text_area("Generated Recommendation", recommendation, height=200)
        else:
            st.error("Dataset structure is incorrect. Please ensure it includes the required columns.")

elif user_input == 'Manual Input':
    st.write("Please input the parameters manually.")
    temperature = st.number_input("Temperature (°C)", min_value=-50, max_value=100)
    pressure = st.number_input("Pressure (bar)", min_value=0, max_value=50)
    vibration = st.number_input("Vibration (mm/s)", min_value=0, max_value=100)
    working_hours = st.number_input("Working Hours", min_value=0)

    if st.button("Submit"):
        user_data = pd.DataFrame({
            'Temperature (°C)': [temperature],
            'Pressure (bar)': [pressure],
            'Vibration (mm/s)': [vibration],
            'Working_Hours': [working_hours]
        })
        recommendation = predict(user_data)
        st.text_area("Generated Recommendation", recommendation, height=200)

elif user_input == 'Simulated Data':
    st.write("Starting simulation with random data...")
    while True:
        st.write("\nGenerating predictions for simulated inputs:")
        for i in range(4):  # Generate 4 predictions each cycle
            simulated_input = pd.DataFrame({
                'Temperature (°C)': [random.uniform(0, 100)],
                'Pressure (bar)': [random.uniform(5, 50)],
                'Vibration (mm/s)': [random.uniform(0, 100)],
                'Working_Hours': [random.randint(100, 5000)]
            })
            recommendation = predict(simulated_input)
            st.text_area("Simulated Prediction", recommendation, height=200)
            time.sleep(1)  # Short delay between each prediction
        st.write("\nWaiting for the next cycle...")
        time.sleep(random.randint(4, 8))  # Random sleep between cycles

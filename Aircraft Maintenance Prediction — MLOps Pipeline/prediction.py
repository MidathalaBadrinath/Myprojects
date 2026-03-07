# prediction.py
import random
import joblib
import pandas as pd
#from recommendation import generate_recommendation
from model.recommendation import generate_recommendation
from mlflow_utils.mlflow_logging import log_model, log_prediction
# Load the models
maintenance_model = joblib.load('models/maintenance_classifier_model.pkl')
lifespan_model = joblib.load('models/remaining_life_regressor_model.pkl')


def make_predictions(input_data):
    X_input = input_data[['Temperature (°C)', 'Pressure (bar)', 'Vibration (mm/s)', 'Working_Hours']]
    predicted_maintenance = maintenance_model.predict(X_input)[0]
    predicted_lifespan = lifespan_model.predict(X_input)[0]

    # Generate failure type and flight recommendation
    failure_type = "None" if predicted_maintenance == 0 else random.choice(
        ['Turbine Overheat', 'Pressure Loss', 'Valve Stuck'])
    flight_type = random.choice(['commercial', 'cargo', 'private', 'long-haul', 'short-haul'])
    flight_number = random.randint(1000, 9999)

    recommendation = generate_recommendation(failure_type, flight_type, flight_number, predicted_lifespan)

    return recommendation
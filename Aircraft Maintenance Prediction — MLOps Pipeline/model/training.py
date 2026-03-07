import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split

def train_models(df: pd.DataFrame):
    # Define features and targets
    X = df[['Temperature (°C)', 'Pressure (bar)', 'Vibration (mm/s)', 'Working_Hours']]
    y_maintenance = df['Maintenance_Required']  # Target for maintenance prediction
    y_lifespan = df['Remaining_Life (hours)']    # Target for lifespan prediction

    # Split dataset into training and testing sets
    X_train, X_test, y_train_maintenance, y_test_maintenance = train_test_split(X, y_maintenance, test_size=0.2, random_state=42)
    X_train_lifespan, X_test_lifespan, y_train_lifespan, y_test_lifespan = train_test_split(X, y_lifespan, test_size=0.2, random_state=42)

    # Train the models
    maintenance_model = RandomForestClassifier(n_estimators=100, random_state=42)
    maintenance_model.fit(X_train, y_train_maintenance)

    lifespan_model = RandomForestRegressor(n_estimators=100, random_state=42)
    lifespan_model.fit(X_train_lifespan, y_train_lifespan)

    # Save the models
    joblib.dump(maintenance_model, 'maintenance_classifier_model.pkl')
    joblib.dump(lifespan_model, 'remaining_life_regressor_model.pkl')

    print("Models have been trained and saved.")

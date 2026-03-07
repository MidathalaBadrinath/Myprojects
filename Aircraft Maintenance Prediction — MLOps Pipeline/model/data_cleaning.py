import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and preprocess the raw input data.
    """
    # Check for missing values
    df = df.dropna()

    # Ensure correct data types
    df['Temperature (°C)'] = df['Temperature (°C)'].astype(float)
    df['Pressure (bar)'] = df['Pressure (bar)'].astype(float)
    df['Vibration (mm/s)'] = df['Vibration (mm/s)'].astype(float)
    df['Working_Hours'] = df['Working_Hours'].astype(int)

    # Return cleaned dataframe
    return df

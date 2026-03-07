import mlflow
import mlflow.sklearn
import joblib
from sklearn.metrics import mean_squared_error, accuracy_score

def log_model(model, model_name, model_path):
    """
    Log the trained model to MLflow.
    """
    with mlflow.start_run(run_name=f"Logging {model_name}"):
        mlflow.sklearn.log_model(model, artifact_path=model_name)
        joblib.dump(model, model_path)
        print(f"Model '{model_name}' logged and saved successfully at '{model_path}'.")

def log_training_metrics(y_true, y_pred, model_name, task_type="classification"):
    """
    Log metrics like accuracy for classification and MSE for regression during training.
    """
    with mlflow.start_run(run_name=f"Metrics for {model_name}"):
        if task_type == "classification":
            accuracy = accuracy_score(y_true, y_pred)
            mlflow.log_metric("accuracy", accuracy)
            print(f"Accuracy logged: {accuracy}")
        elif task_type == "regression":
            mse = mean_squared_error(y_true, y_pred)
            mlflow.log_metric("mean_squared_error", mse)
            print(f"Mean Squared Error logged: {mse}")

def log_prediction(input_data, prediction, model_name):
    """
    Log prediction results to MLflow.
    """
    with mlflow.start_run(run_name=f"Prediction using {model_name}"):
        mlflow.log_param("Input Data", input_data.to_dict(orient="records"))
        mlflow.log_param("Prediction", prediction)
        print(f"Prediction logged successfully for '{model_name}'.")

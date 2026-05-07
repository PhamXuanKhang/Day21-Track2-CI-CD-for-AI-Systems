from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.storage.blob import BlobServiceClient
import joblib
import os

app = FastAPI()

AZURE_CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
AZURE_CONTAINER = os.environ["AZURE_CONTAINER"]
BLOB_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    """Tai file model.pkl tu Azure Blob Storage ve may khi server khoi dong."""
    blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    blob_client = blob_service.get_blob_client(container=AZURE_CONTAINER, blob=BLOB_MODEL_KEY)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        f.write(blob_client.download_blob().readall())
    print("Model da duoc tai xuong tu Azure Blob Storage.")


download_model()
model = joblib.load(MODEL_PATH)


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    """Endpoint kiem tra suc khoe server."""
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f12]}
    Dau ra  : JSON {"prediction": <0|1|2>, "label": <"thap"|"trung_binh"|"cao">}

    Thu tu 12 dac trung:
        fixed_acidity, volatile_acidity, citric_acid, residual_sugar,
        chlorides, free_sulfur_dioxide, total_sulfur_dioxide, density,
        pH, sulphates, alcohol, wine_type
    """
    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")

    pred = model.predict([req.features])[0]
    labels = {0: "thap", 1: "trung_binh", 2: "cao"}
    return {"prediction": int(pred), "label": labels[int(pred)]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

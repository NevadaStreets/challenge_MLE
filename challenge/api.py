from typing import List

import fastapi
import pandas as pd
from fastapi import HTTPException
from pydantic import BaseModel

from challenge.model import DelayModel

# Airlines (OPERA) present in the training dataset. A flight operated by an
# airline outside this set cannot be encoded into the model's feature space.
VALID_OPERA = {
    "Aerolineas Argentinas",
    "Aeromexico",
    "Air Canada",
    "Air France",
    "Alitalia",
    "American Airlines",
    "Austral",
    "Avianca",
    "British Airways",
    "Copa Air",
    "Delta Air",
    "Gol Trans",
    "Grupo LATAM",
    "Iberia",
    "JetSmart SPA",
    "K.L.M.",
    "Lacsa",
    "Latin American Wings",
    "Oceanair Linhas Aereas",
    "Plus Ultra Lineas Aereas",
    "Qantas Airways",
    "Sky Airline",
    "United Airlines",
}
VALID_TIPOVUELO = {"I", "N"}
VALID_MONTHS = set(range(1, 13))


class Flight(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int


class PredictRequest(BaseModel):
    flights: List[Flight]


app = fastapi.FastAPI()
model = DelayModel()


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }


@app.post("/predict", status_code=200)
async def post_predict(request: PredictRequest) -> dict:
    for flight in request.flights:
        if flight.MES not in VALID_MONTHS:
            raise HTTPException(status_code=400, detail=f"Invalid MES: {flight.MES}")
        if flight.TIPOVUELO not in VALID_TIPOVUELO:
            raise HTTPException(status_code=400, detail=f"Invalid TIPOVUELO: {flight.TIPOVUELO}")
        if flight.OPERA not in VALID_OPERA:
            raise HTTPException(status_code=400, detail=f"Invalid OPERA: {flight.OPERA}")

    data = pd.DataFrame([flight.dict() for flight in request.flights])
    features = model.preprocess(data)
    predictions = model.predict(features)

    return {
        "predict": predictions
    }

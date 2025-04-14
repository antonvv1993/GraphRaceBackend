from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

df = pd.read_csv("moex_candles.csv")
user_states = {}

@app.get("/game/start")
def start_game(user_id: str):
    index = random.randint(30, len(df) - 6)
    selection = df.iloc[index-30:index+6]
    user_states[user_id] = {
        "candles": selection.iloc[:30].to_dict(orient="records"),
        "target_close": selection.iloc[34].CLOSE,
        "current_close": selection.iloc[29].CLOSE
    }
    return {"candles": user_states[user_id]["candles"]}

@app.post("/game/submit")
async def submit_guess(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    prediction = data.get("prediction")
    state = user_states.get(user_id)
    if not state:
        return {"error": "No active game for this user."}
    
    result = (
        (prediction == "up" and state["target_close"] > state["current_close"]) or
        (prediction == "down" and state["target_close"] < state["current_close"])
    )
    return {
        "result": result,
        "correct_direction": "up" if state["target_close"] > state["current_close"] else "down"
    }

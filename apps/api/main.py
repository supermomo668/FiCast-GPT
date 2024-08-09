from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
from typing import List, Optional

app = FastAPI()

class Speaker(BaseModel):
    name: str
    description: str

class Dialogue(BaseModel):
    speaker: Speaker
    dialogue: str
    inner_thought: Optional[str] = None

class Script(BaseModel):
    title: str
    abstract: str
    dialogues: List[Dialogue]

@app.get("/")
async def home():
  return {"message": "Hello, FiCast!"}

@app.get("/script", response_model=Script)
async def get_script(include_inner_thought: bool = Query(True, description="Include inner thoughts in the response")):
    try:
        with open("../ficast-outputs/samples/scripts/script_20240805_074514.json", "r") as file:
            script_data = json.load(file)
        
        if not include_inner_thought:
            for dialogue in script_data["dialogues"]:
                dialogue.pop("inner_thought", None)

        return script_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Script not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=42110)

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
import glob, re
import json

from typing import List
from fastapi import FastAPI, Query

from gen_podcast import main as gen_podcast
app = FastAPI()

output_regex="outputs/conversations/*.txt"

@app.get("/conversation-raw", response_class=JSONResponse)
async def get_conversation_raw(
    topic: str = Query(..., description="Topic of the conversation"),
    speakers: List[str] = Query(..., description="List of speakers")
):
    try:
        conversation_output = gen_podcast(topic, speakers)
        return JSONResponse(content=conversation_output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
       
def parse_conversation(conversation_text):
    # Fix malformed speaker names and extract dialogues
    fixed_text = re.sub(r'\*\*(.*?)\*\*([a-zA-Z]*?):', r'**\1\2**:', conversation_text)
    
    # Split fixed text into potential dialogue blocks
    lines = re.split(r'\n\n', fixed_text)
    conversation_list = []

    for line in lines:
        # Match lines that start with "**" and contain ": "
        match = re.match(r'\*\*(.*?)\*\*:\s*(.*)', line)
        if match:
            speaker, message = match.groups()
            conversation_list.append({"speaker": speaker.strip(), "message": message.strip()})
        else:
            # Handle cases where the speaker's name might have trailing ** or other issues
            parts = line.split(':', 1)
            if len(parts) == 2:
                speaker = parts[0].strip(' *')
                message = parts[1].strip()
                conversation_list.append({"speaker": speaker, "message": message})

    print(f"Left with : {len(conversation_list)}")
    return conversation_list
 
@app.get("/conversation", response_class=JSONResponse)
async def get_latest_conversation():
    try:
        # Find all files matching the pattern
        files = glob.glob(output_regex)
        if not files:
            raise FileNotFoundError("No conversation files found.")
        
        # Get the latest file based on the timestamp in the filename
        latest_file = max(files, key=os.path.getctime)
        
        # Read the content of the latest file
        with open(latest_file, "r") as file:
            content = file.read()
        
        # Convert the content to JSON
        conversation_list = parse_conversation(content)
        return JSONResponse(content=conversation_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation-test", response_class=JSONResponse)
async def get_latest_conversation():
    try:
        # Find all files matching the pattern
        files = glob.glob(output_regex)
        if not files:
            raise FileNotFoundError("No conversation files found.")
        
        # Get the latest file based on the timestamp in the filename
        latest_file = max(files, key=os.path.getctime)
        
        # Read the content of the latest file
        with open(latest_file, "r") as file:
            content = file.read()
        
        # Convert the content to JSON
        conversation_list = parse_conversation(content)
        return JSONResponse(content=conversation_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

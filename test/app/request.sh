curl --location 'http://localhost:5008/api/start_chat' \
--header 'Content-Type: application/json' \
--data '{
    "message": "tell me a joke.", 
    "agents_info": [
        {
            "name": "Personal_Assistant",
            "type": "AssistantAgent",
            "llm": {
                "model": "gemini-1.5-pro"
            },
            "system_message": "You are a personal assistant who can answer questions.",
            "description": "This is a personal assistant who can answer questions."
        }
    ],
    "task_info": {
        "id": 0,
        "name": "Personal Assistant",
        "description": "This is a powerful personal assistant.",
        "maxMessages": 5,
        "speakSelMode": "auto"
    }
  }'
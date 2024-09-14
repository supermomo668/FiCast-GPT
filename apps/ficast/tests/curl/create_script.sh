response=$(curl -X POST "http://127.0.0.1:42110/podcast/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "topic": "world peace",
    "n_rounds": 20,
    "participants": [
      {
        "name": "Joe Rogan",
        "description": "Joe Rogan is a funny and popular podcast host",
        "model": "gemini-1.5-pro",
        "role": "host"
      },
      {
        "name": "Darth Vader",
        "description": "Sith Lord in Star Wars Universe",
        "model": null
      }
    ]
  }' \
)
TASK_ID=$(echo $response | jq -r ."task_id")
echo $TASK_ID
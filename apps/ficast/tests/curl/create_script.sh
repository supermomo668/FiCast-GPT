response=$(curl -X POST "http://127.0.0.1:42110/podcast/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "topic": "health & longevity",
    "n_rounds": 20,
    "participants": [
      {
        "name": "Joe Rogan",
        "description": "Joe Rogan is a funny and popular podcast host",
        "model": "gpt-3.5-turbo",
        "role": "host"
      },
      {
        "name": "David Sinclair",
        "description": "David Sinclair is a Harvard Medical Expert",
        "model": "gpt-3.5-turbo"
      }
    ]
  }' \
)
TASK_ID=$(echo $response | jq -r ."task_id")
echo $TASK_ID
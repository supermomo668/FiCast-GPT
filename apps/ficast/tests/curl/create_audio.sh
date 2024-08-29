response=$(curl -X POST "http://127.0.0.1:42110/podcast/$TASK_ID/audio" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
)
echo $response
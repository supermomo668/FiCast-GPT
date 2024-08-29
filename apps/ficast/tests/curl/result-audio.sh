response=$(curl -X GET "http://127.0.0.1:42110/podcast/$TASK_ID/audio" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -o data/curl-task-result.wav
)
echo data/curl-task-result.wav
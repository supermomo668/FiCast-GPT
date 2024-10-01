response=$(curl -X POST "http://127.0.0.1:42110/api/podcast/script" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d '{
    "task_id": "'$TASK_ID'"
  }' \
)
echo $response > data/curl-task-result.json

echo data/curl-task-result.json
curl -N -X POST "http://127.0.0.1:42110/api/podcast/stream/progress" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "task_id": "'$TASK_ID'",
    "event_type": "script"
  }'

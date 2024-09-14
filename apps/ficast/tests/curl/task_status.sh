curl -N "http://127.0.0.1:42110/podcast/$TASK_ID/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  | head -n 1 | sed 's/^data: //g'
response=$(curl -X GET "http://127.0.0.1:42110/podcast/${TASK_ID}TASK_ID/script" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
)
echo $response
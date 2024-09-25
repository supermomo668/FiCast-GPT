response=$(curl "http://127.0.0.1:42110/api/auth/check" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
)
echo $response
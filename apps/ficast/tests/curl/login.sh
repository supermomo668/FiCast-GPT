. .env
response=$(curl -X POST "http://127.0.0.1:42110/auth/login" \
  -d "username=${DEFAULT_USERNAME}&password=${DEFAULT_PASSWORD}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
)
ACCESS_TOKEN=$(echo $response | jq -r .access_token)
echo $ACCESS_TOKEN
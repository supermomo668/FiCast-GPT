# Helper function to generate HTML for curl examples
def generate_curl_example(description: str, command: str) -> str:
    return f"""
    <h3>{description}</h3>
    <pre><code>{command}</code></pre>
    """

# Helper function to generate the full HTML content
def generate_homepage_html() -> str:
    html_content = """
    <html>
        <head>
            <title>FiCast-TTS Documentation</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    line-height: 1.6;
                    color: #333;
                }}
                h1, h2 {{
                    color: #2c3e50;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <h1>Welcome to FiCast-TTS!</h1>
            <p>Explore the full self-generated API documentation at <a href="/docs">/docs</a>.</p>
            <h2>How to Use the FiCast-TTS API</h2>
            {generate_curl_example(
                "Create a Script",
                '''curl -X POST "http://127.0.0.1:42110/podcast/create" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer $ACCESS_TOKEN" \\
    -d '{
    "topic": "health & longevity",
    "n_rounds": 20,
    "participants": [
        {{
        "name": "Joe Rogan",
        "description": "Joe Rogan is a funny and popular podcast host",
        "model": "gpt-3.5-turbo",
        "role": "host"
        }},
        {{
        "name": "David Sinclair",
        "description": "David Sinclair is a Harvard Medical Expert",
        "model": "gpt-3.5-turbo"
        }}
    ]
    }}' '''
            )}
            <p>Save the response <code>task_id</code> as <code>$TASK_ID</code> for the next steps.</p>
            {generate_curl_example(
                "Retrieve Script Result",
                '''curl -X GET "http://127.0.0.1:42110/podcast/$TASK_ID/script" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}" '''
            )}
            {generate_curl_example(
                "Generate Audio from Script",
                '''response=$(curl -X POST "http://127.0.0.1:42110/podcast/$TASK_ID/audio" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}") \n
    echo $response'''
            )}
            {generate_curl_example(
                "Retrieve Generated Audio",
                '''response=$(curl -X GET "http://127.0.0.1:42110/podcast/$TASK_ID/audio" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \\
    -o data/curl-task-result.wav) \n
    echo data/curl-task-result.wav'''
            )}
        </body>
    </html>
    """
    return html_content
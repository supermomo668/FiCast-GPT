import html
from ..constants import API_DOC, API_REDOC, APP_ROOT

def generate_curl_example(description: str, command: str) -> str:
    # Escape special HTML characters to ensure correct rendering
    command_escaped = html.escape(command).replace("\\", "\\\\").replace("\n", "<br>").replace(" ", "&nbsp;")
    return f"""
    <div class="curl-example">
        <h3>{description}</h3>
        <pre><code>{command_escaped}</code></pre>
    </div>
    """

def generate_homepage_html() -> str:
    html_content = f"""
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FiCast-TTS API Documentation</title>
            <style>
                body {{{{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f8f9fa;
                    color: #343a40;
                    margin: 0;
                    padding: 0;
                }}}}
                .container {{{{
                    width: 90%;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }}}}
                h1, h2, h3 {{{{
                    color: #495057;
                }}}}
                h1 {{{{
                    font-size: 2.5em;
                    margin-bottom: 0.5em;
                }}}}
                h2 {{{{
                    font-size: 1.8em;
                    margin-bottom: 0.5em;
                    border-bottom: 2px solid #ced4da;
                    padding-bottom: 0.2em;
                }}}}
                h3 {{{{
                    font-size: 1.5em;
                    margin-top: 1.5em;
                }}}}
                p {{{{
                    font-size: 1.2em;
                    line-height: 1.6;
                }}}}
                a {{{{
                    color: #007bff;
                    text-decoration: none;
                }}}}
                a:hover {{{{
                    text-decoration: underline;
                }}}}
                pre {{{{
                    background-color: #e9ecef;
                    padding: 15px;
                    border-radius: 8px;
                    overflow-x: auto;
                    font-size: 1em;
                }}}}
                code {{{{
                    font-family: 'Courier New', Courier, monospace;
                    font-size: 0.95em;
                }}}}
                .curl-example {{{{
                    margin-bottom: 20px;
                }}}}
                .header {{{{
                    background-color: #343a40;
                    color: #fff;
                    padding: 20px 0;
                    text-align: center;
                }}}}
                .header h1 {{{{
                    margin: 0;
                    font-size: 3em;
                }}}}
                .footer {{{{
                    text-align: center;
                    padding: 20px 0;
                    margin-top: 40px;
                    background-color: #343a40;
                    color: #fff;
                }}}}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FiCast-TTS</h1>
                <p>Your gateway to text-to-speech podcast generation</p>
            </div>
            <div class="container">
                <h2>Explore the API Documentation</h2>
                <p><a href="{API_DOC}">Try-it-yourself API documentation</a>.</p>
                <p><a href="{API_REDOC}">Redoc API documentation</a>.</p>
                <h2>How to Use the FiCast-TTS API</h2>
    """

    # Appending the curl examples as individual string concatenations
    html_content += generate_curl_example(
                    "Create a Script",
                    '''curl -X POST "<this_url>/podcast/create" \\
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
                )

    html_content += """
                <p>Save the response <code>task_id</code> as <code>$TASK_ID</code> for the next steps.</p>
    """
    html_content += generate_curl_example(
                    "Retrieve Script Result",
                    '''curl -X GET "<this_url>/podcast/$TASK_ID/script" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}" '''
                )

    html_content += generate_curl_example(
                    "Generate Audio from Script",
                    '''response=$(curl -X POST "<this_url>/podcast/$TASK_ID/audio" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}") <br>
    echo $response'''
                )
    html_content += """
        <p><b>Note:</b> A schema-consistent JSON script created from the application is available at <a href="/samples/script">/samples/script</a>. However, more script formats is available by changing the input parameter `format`.</p>"""
    html_content += generate_curl_example(
                    "Retrieve Generated Audio",
                    '''response=$(curl -X GET "<this_url>/podcast/$TASK_ID/audio" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \\
    -o data/curl-task-result.wav) <br>
    echo data/curl-task-result.wav'''
                )

    # Adding the new Event Source endpoint example
    html_content += generate_curl_example(
                    "Stream Task Progress (Script or Audio)",
                    '''curl -N "<this_url>/podcast/$TASK_ID/progress?event_type=script" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}"'''
                )

    html_content += """
        <p><b>Note:</b> You can stream task progress for both script and audio by changing the <code>event_type</code> parameter in the URL. The event_type can either be <code>script</code> or <code>audio</code>.</p>"""

    html_content += """
            </div>
            <div class="footer">
                <p>&copy; 2024 FiCast-TTS. All rights reserved.</p>
            </div>
        </body>
    </html>
    """
    return html_content

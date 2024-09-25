
from ..services.usage_examples import *
from ..constants import API_DOC, API_REDOC, APP_ROOT

def get_style() -> str:
    """
    Return the CSS styles for the homepage.
    """
    return """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            color: #343a40;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #ffffff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }
        h1, h2, h3 {
            color: #495057;
        }
        h1 {
            font-size: 2.8em;
            margin-bottom: 0.5em;
            text-align: center;
        }
        h2 {
            font-size: 1.8em;
            margin-bottom: 0.5em;
            border-bottom: 2px solid #ced4da;
            padding-bottom: 0.2em;
        }
        h3 {
            font-size: 1.5em;
            margin-top: 1.5em;
        }
        p {
            font-size: 1.2em;
            line-height: 1.6;
        }
        a {
            color: #007bff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        pre {
            background-color: #f1f1f1;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 1em;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        code {
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.95em;
        }
        .curl-example {
            margin-bottom: 20px;
            border-left: 5px solid #007bff;
            padding-left: 15px;
        }
        .header {
            background-color: #343a40;
            color: #fff;
            padding: 20px 0;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 3.2em;
        }
        .footer {
            text-align: center;
            padding: 20px 0;
            margin-top: 40px;
            background-color: #343a40;
            color: #fff;
            font-size: 1.2em;
        }
    </style>
    """
def generate_homepage_html() -> str:
    """
    Assemble the homepage HTML by combining the style, header, and modular curl examples.
    """
    styles = get_style()

    html_content = f"""
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>FiCast-TTS API Documentation</title>
            {styles}
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
    # Append modular curl examples
    html_content += curl_example_create_script()
    html_content += curl_example_stream_task_progress()
    html_content += curl_example_retrieve_script()
    html_content += curl_example_create_audio()
    html_content += curl_example_retrieve_audio()

    # Footer and closing HTML
    html_content += """
        <p><b>Note:</b> You can stream task progress for both script and audio by changing the <code>event_type</code> parameter in the URL.</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 FiCast-TTS. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    return html_content
import html

def generate_curl_example(description: str, command: str) -> str:
    # Escape special HTML characters to ensure correct rendering
    command_escaped = html.escape(command).replace("\\", "\\\\").replace("\n", "<br>").replace(" ", "&nbsp;")
    return f"""
    <div class="curl-example">
        <h3>{description}</h3>
        <pre><code>{command_escaped}</code></pre>
    </div>
    """
    
def curl_example_create_script() -> str:
    return generate_curl_example(
        "Create Podcast Script",
        '''curl -X POST "<this_url>/podcast/create-script" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer $ACCESS_TOKEN" \\
    -d '{
    "topic": "health & longevity",
    "n_rounds": 20,
    "participants": [
        {
        "name": "Joe Rogan",
        "description": "Joe Rogan is a funny and popular podcast host",
        "model": "gpt-3.5-turbo",
        "role": "host"
        },
        {
        "name": "David Sinclair",
        "description": "David Sinclair is a Harvard Medical Expert",
        "model": "gpt-3.5-turbo"
        }
    ]
    }' '''
    )

def curl_example_stream_task_progress() -> str:
    return generate_curl_example(
        "Stream Task Progress (Script or Audio)",
        '''curl -N "<this_url>/podcast/stream/progress" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \\
    -d '{
    "task_id": "$TASK_ID",
    "event_type": "script"
    }' '''
    )

def curl_example_retrieve_script() -> str:
    return generate_curl_example(
        "Retrieve Podcast Script",
        '''curl -X POST "<this_url>/podcast/script" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \\
    -d '{
    "task_id": "$TASK_ID"
    }' '''
    )

def curl_example_create_audio() -> str:
    return generate_curl_example(
        "Create Podcast Audio",
        '''curl -X POST "<this_url>/podcast/create-audio" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \\
    -d '{
    "task_id": "$TASK_ID"
    }' '''
    )

def curl_example_retrieve_audio() -> str:
    return generate_curl_example(
        "Retrieve Podcast Audio",
        '''curl -X POST "<this_url>/podcast/audio" \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \\
    -d '{
    "task_id": "$TASK_ID"
    }' -o data/curl-task-result.wav \\
    echo "Audio saved to data/curl-task-result.wav"'''
    )
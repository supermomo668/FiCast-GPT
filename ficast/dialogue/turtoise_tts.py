import subprocess

def local_inference_docker(
  text, voice, 
  output_path="./results", preset="ultra_fast", container_name="tts-app", docker_image="tts"
  ):
  """
  Run the TTS Docker container with the specified arguments.

  Args:
  - text (str): The text to be converted to speech.
  - voice (str): The voice to use for the TTS.
  - output_path (str): The path to save the output.
  - container_name (str, optional): The name of the Docker container. Default is "tts-app".
  - docker_image (str, optional): The name of the Docker image. Default is "your-docker-image".
  - preset (str, optional): The preset for the TTS. Default is "ultra_fast".

  Returns:
  - None
  """
  # Define the Docker run command
  command = [
      'docker', 'run', '--rm',
      '--name', container_name, docker_image,
      '--output_path', output_path,
      '--preset', preset,
      '--voice', voice,
      '--text', text
  ]

  # Run the command
  result = subprocess.run(command, capture_output=True, text=True)

  # Print the output and errors (if any)
  print("Output:")
  print(result.stdout)
  print("Errors:")
  print(result.stderr)


def local_inference_factory(
  text, voice, output_path, option="docker",**kwargs
  ):
  """
  Factory wrapper for local inference.

  Args:
  - option (str): The option to choose the method ("docker" or others).
  - text (str): The text to be converted to speech.
  - voice (str): The voice to use for the TTS.
  - output_path (str): The path to save the output.
  - kwargs (dict): Additional keyword arguments for specific methods.

  Returns:
  - None
  """
  if option == "docker":
      local_inference_docker(text, voice, output_path, **kwargs)
  else:
      raise ValueError(f"Unknown option: {option}")

# Example usage
if __name__ == "__main__":
    local_inference_factory(
        option="docker",
        text="Time flies like an arrow; fruit flies like a banana.",
        voice="geralt",
        output_path="/results",
        container_name="tts-app",
        docker_image="your-docker-image",
        preset="ultra_fast"
    )

import React from "react";

const GettingStarted = () => {
  return (
    <section className="text-foreground">
      <h1 className="text-3xl font-bold mb-4">Getting Started</h1>

      <h2 className="text-2xl font-semibold mb-2">Overview</h2>
      <p className="mb-4">
        FiCast is a Python package that simplifies podcast creation by overlaying AI-generated content with ambient music. 
        Whether you’re building podcasts on technology, health, or lifestyle, FiCast provides a suite of tools to automate the 
        process. You can install FiCast from Test PyPI, set it up with an API key, and begin generating podcasts using the FiCast API.
      </p>

      <h2 className="text-2xl font-semibold mb-2">Installation via <code>pip</code></h2>
      <p className="mb-4">
        To install FiCast via <code>pip</code> from Test PyPI, use the following command:
      </p>
      <pre className="bg-background dark:bg-gray-900 text-foreground dark:text-gray-200 p-4 rounded-md mb-6">
        <code>pip install --index-url https://test.pypi.org/simple/ ficast-gpt</code>
      </pre>
      <p className="mb-4">
        This will install the FiCast package along with its dependencies, making it ready for use in your project. You can also 
        check for the latest updates on the official <a href="https://github.com/supermomo668/podcast-gpt" className="text-indigo-600" target="_blank" rel="noopener noreferrer">GitHub repository</a>.
      </p>

      <h2 className="text-2xl font-semibold mb-2">Installation via <code>poetry</code></h2>
      <p className="mb-4">
        If you are using <code>poetry</code> for package management, you can install FiCast by running the following command:
      </p>
      <pre className="bg-background dark:bg-gray-900 text-foreground dark:text-gray-200 p-4 rounded-md mb-6">
        <code>poetry add ficast-gpt --source https://test.pypi.org/simple/</code>
      </pre>
      <p className="mb-4">
        This will add FiCast to your project's dependencies and manage the environment using poetry's dependency resolver.
      </p>

      <h2 className="text-2xl font-semibold mb-2">Using the FiCast Python SDK</h2>
      <p className="mb-4">
        After installation, you can start working with the FiCast Python SDK. The SDK allows you to easily interact with 
        the FiCast API, including creating podcasts, managing participants, and retrieving generated content.
      </p>

      <p className="mb-4">
        Here’s a simple example of using the FiCast SDK to create a podcast programmatically:
      </p>
      <pre className="bg-background dark:bg-gray-900 text-foreground dark:text-gray-200 p-4 rounded-md mb-6">
        <code>
          {`from ficast import FiCastAPI

api = FiCastAPI(api_key='YOUR_API_KEY')

# Create a podcast
response = api.create_podcast(
    topic="The Future of AI",
    n_rounds=10,
    participants=[
        {
            "name": "AI Host",
            "description": "An AI host for podcast discussions",
            "model": "gpt-3.5-turbo",
            "role": "host"
        },
        {
            "name": "AI Expert",
            "description": "AI expert discussing future trends",
            "model": "gpt-3.5-turbo"
        }
    ]
)

# Print response
print(response)
`}
        </code>
      </pre>
      <p className="mb-4">
        This example demonstrates how easy it is to use FiCast for generating podcast content with AI participants. Be sure to 
        replace <code>'YOUR_API_KEY'</code> with your actual API key.
      </p>

      <h2 className="text-2xl font-semibold mb-2">Authentication</h2>
      <p className="mb-4">
        To use the FiCast API, you need to authenticate by providing an API key. You can obtain your API key by signing up 
        on the FiCast platform and accessing your dashboard. All API requests must include your API key as a Bearer token 
        in the request headers.
      </p>

      <pre className="bg-background dark:bg-gray-900 text-foreground dark:text-gray-200 p-4 rounded-md mb-6">
        <code>{`Authorization: Bearer YOUR_API_KEY`}</code>
      </pre>

      <h2 className="text-2xl font-semibold mb-2">Example API Call</h2>
      <p className="mb-4">
        Once authenticated, you can begin making requests to the FiCast API. Below is an example of creating a podcast 
        using the <code>curl</code> command:
      </p>
      <pre className="bg-background dark:bg-gray-900 text-foreground dark:text-gray-200 p-4 rounded-md mb-6">
        <code>
          {`curl -X POST "https://api.ficast.com/podcast/create" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "topic": "technology trends",
    "n_rounds": 5,
    "participants": [
      {
        "name": "Tech Host",
        "description": "An AI-generated expert in technology",
        "model": "gpt-3.5-turbo"
      }
    ]
  }'`}
        </code>
      </pre>

      <p className="mb-4">
        This example demonstrates how to create a podcast using FiCast's API. Once the API call is made, you will receive 
        a <code>task_id</code> to retrieve the generated script and audio content.
      </p>

      <h2 className="text-2xl font-semibold mb-2">Further Documentation</h2>
      <p className="mb-4">
        To learn more about the API, SDK, and advanced features, refer to the <a href="https://github.com/supermomo668/podcast-gpt" className="text-indigo-600" target="_blank" rel="noopener noreferrer">FiCast GitHub repository</a> 
        or visit the official <a href="/docs" className="text-indigo-600">documentation</a> for detailed guides and examples.
      </p>
    </section>
  );
};

export default GettingStarted;
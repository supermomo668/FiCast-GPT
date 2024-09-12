import React, { useState } from "react";

const UsingAPI = () => {
  const [token, setToken] = useState(""); // To hold the user's access token
  const placeholderToken = token || "<YOUR_ACCESS_TOKEN>"; // Default placeholder token

  const handleTokenChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setToken(e.target.value);
  };

  const handleCopy = (code: string) => {
    navigator.clipboard.writeText(code);
    alert("Copied to clipboard!");
  };

  const createPodcastRequest = `curl -X POST "<this_url>/podcast/create" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${placeholderToken}" \\
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
  }'`;

  const retrieveScriptRequest = `curl -X GET "<this_url>/podcast/$TASK_ID/script" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${placeholderToken}"`;

  const generateAudioRequest = `curl -X POST "<this_url>/podcast/$TASK_ID/audio" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer ${placeholderToken}"`;

  return (
    <section>
      <h1 className="text-3xl font-bold mb-4">Using the API</h1>
      <p className="mb-4">
        You can interact with the FiCast API by authenticating your requests with a Bearer token. Insert your token in the
        placeholder field below:
      </p>
      <div className="mb-4">
        <label htmlFor="token" className="block text-lg font-semibold mb-2">
          Bearer Token:
        </label>
        <input
          type="text"
          id="token"
          value={token}
          onChange={handleTokenChange}
          placeholder="Enter your Bearer token"
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        />
      </div>

      <h2 className="text-2xl font-semibold mb-4">1. Create a Podcast</h2>
      <p className="mb-2">Use the following request to create a podcast:</p>
      <div className="relative mb-6">
        <pre className="bg-gray-100 p-4 border rounded overflow-auto text-sm">
          <code>{createPodcastRequest}</code>
        </pre>
        <button
          onClick={() => handleCopy(createPodcastRequest)}
          className="absolute top-2 right-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-1 px-4 rounded-lg shadow"
        >
          Copy
        </button>
      </div>

      <h2 className="text-2xl font-semibold mb-4">2. Retrieve Script Result</h2>
      <p className="mb-2">Retrieve the script result using the following request:</p>
      <div className="relative mb-6">
        <pre className="bg-gray-100 p-4 border rounded overflow-auto text-sm">
          <code>{retrieveScriptRequest}</code>
        </pre>
        <button
          onClick={() => handleCopy(retrieveScriptRequest)}
          className="absolute top-2 right-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-1 px-4 rounded-lg shadow"
        >
          Copy
        </button>
      </div>

      <h2 className="text-2xl font-semibold mb-4">3. Generate and Retrieve Audio</h2>
      <p className="mb-2">Generate the podcast audio using the following request:</p>
      <div className="relative mb-6">
        <pre className="bg-gray-100 p-4 border rounded overflow-auto text-sm">
          <code>{generateAudioRequest}</code>
        </pre>
        <button
          onClick={() => handleCopy(generateAudioRequest)}
          className="absolute top-2 right-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-1 px-4 rounded-lg shadow"
        >
          Copy
        </button>
      </div>

      <h2 className="text-2xl font-semibold mb-4">Error Handling</h2>
      <p className="mb-4">
        If an error occurs, the API will return a JSON response with a status code and a message indicating the error. For example:
      </p>
      <pre className="bg-gray-100 p-4 border rounded overflow-auto text-sm">
        <code>{`{
  "error": "InvalidTokenError",
  "message": "The provided token is invalid or has expired."
}`}</code>
      </pre>

      <h2 className="text-2xl font-semibold mb-4">Additional API Endpoints</h2>
      <p className="mb-4">
        You can also explore additional endpoints such as updating a podcast, deleting a podcast, or retrieving a list of all podcasts.
        Check the official API documentation for more details.
      </p>
    </section>
  );
};

export default UsingAPI;

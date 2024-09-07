"use client";

import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import axios from 'axios';

const Profile = () => {
  const { user, authToken, loading, signOut } = useAuth();
  const router = useRouter();
  const [apiKey, setApiKey] = useState<string | null>(null);
  const [revealKey, setRevealKey] = useState(false);
  const [testResponse, setTestResponse] = useState<string | null>(null);
  const [testApiKey, setTestApiKey] = useState('');
  const [unauthorized, setUnauthorized] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      setUnauthorized(true);
      router.push('/login');
    }
  }, [loading, user, router]);

  const generateApiKey = async () => {
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_BACKEND_AUTH_URL}/issue-api-token`,
        {},
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        }
      );
      setApiKey(response.data.api_token);
    } catch (error) {
      console.error('Error issuing API key:', error);
    }
  };

  const testApiKeyRequest = async () => {
    try {
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_BACKEND_AUTH_URL}/test-api-token`,
        {},
        {
          headers: {
            Authorization: `Bearer ${testApiKey}`,
          },
        }
      );
      setTestResponse(JSON.stringify(response.data, null, 2));
      setShowModal(true);
    } catch (error) {
      setTestResponse('Invalid API Key or request failed');
      setShowModal(true);
    }
  };

  const copyToClipboard = () => {
    if (apiKey) {
      navigator.clipboard.writeText(apiKey);
      alert('API key copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background text-foreground">
        <div className="text-lg text-foreground animate-pulse">Loading...</div>
      </div>
    );
  }

  if (unauthorized) {
    return (
      <div className="text-center text-red-500 mt-10">
        Unauthorized: Please log in to access this page.
      </div>
    );
  }

  return (
    <div className="container mx-auto mt-10 p-6 bg-background text-foreground rounded-lg shadow-md">
      <h1 className="text-3xl font-bold mb-6">Welcome, {user?.displayName}</h1>

      <div className="mb-6">
        <button
          onClick={generateApiKey}
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg shadow-lg transition duration-300 ease-in-out"
        >
          Generate API Key
        </button>
        {apiKey && (
          <div className="mt-6 p-4 border border-border rounded-lg bg-background text-foreground relative shadow-md">
            <input
              type={revealKey ? 'text' : 'password'}
              value={apiKey}
              readOnly
              className="w-full p-2 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <button
              onClick={() => setRevealKey(!revealKey)}
              className="absolute top-4 right-36 text-sm text-indigo-600 hover:underline"
            >
              {revealKey ? 'Hide' : 'Reveal'}
            </button>
            <button
              onClick={copyToClipboard}
              className="absolute top-4 right-4 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-1 rounded-lg shadow"
            >
              Copy
            </button>
          </div>
        )}
      </div>

      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Test API Key</h2>
        <input
          type="text"
          value={testApiKey}
          onChange={(e) => setTestApiKey(e.target.value)}
          placeholder="Enter API Key"
          className="w-full p-2 border border-border rounded bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent mb-4"
        />
        <button
          onClick={testApiKeyRequest}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg shadow-lg transition duration-300 ease-in-out"
        >
          Test API Key
        </button>
      </div>

      <button
        onClick={() => signOut()}
        className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg shadow-lg transition duration-300 ease-in-out"
      >
        Sign Out
      </button>

      {/* Modal for displaying the pretty-printed JSON response */}
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
          <div className="bg-white dark:bg-background p-6 rounded shadow-lg max-w-lg w-full">
            <h2 className="text-xl font-bold mb-4">API Key Test Response</h2>
            <pre className="bg-gray-100 dark:bg-background p-4 border rounded overflow-auto text-sm">
              {testResponse}
            </pre>
            <button
              onClick={() => setShowModal(false)}
              className="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg shadow-lg transition duration-300 ease-in-out"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;

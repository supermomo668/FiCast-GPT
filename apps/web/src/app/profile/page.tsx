// src/pages/profile.tsx
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/router';
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
      console.log('User not authenticated, redirecting to login...'); // Log before redirection
      router.push('/login'); // Redirect to login if not authenticated
    }
  }, [loading, user, router]);

  const issueApiKey = async () => {
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
      const response = await axios.get(`${process.env.NEXT_PUBLIC_BACKEND_AUTH_URL}/test-api-token`, {
        headers: {
          Authorization: `Bearer ${testApiKey}`,
        },
      });
      setTestResponse(JSON.stringify(response.data, null, 2)); // Prettify the JSON response
      setShowModal(true); // Show the modal with the response
    } catch (error) {
      setTestResponse('Invalid API Key or request failed');
      setShowModal(true); // Show the modal even if there's an error
    }
  };

  if (loading) {
    return <div>Loading...</div>; // Show loading state while determining auth status
  }

  if (unauthorized) {
    return <div className="text-center text-red-500 mt-10">Unauthorized: Please log in to access this page.</div>;
  }

  return (
    <div className="container mx-auto mt-10">
      <h1 className="text-2xl mb-4">Welcome, {user?.displayName}</h1>
      <div className="mb-4">
        <button
          onClick={issueApiKey}
          className="bg-green-500 text-white px-4 py-2 rounded">
          Issue API Key
        </button>
        {apiKey && (
          <div className="mt-4">
            <input
              type={revealKey ? 'text' : 'password'}
              value={apiKey}
              readOnly
              className="border p-2 w-full"
            />
            <button onClick={() => setRevealKey(!revealKey)} className="text-blue-500 mt-2">
              {revealKey ? 'Hide' : 'Reveal'} Key
            </button>
          </div>
        )}
      </div>

      <div className="mb-4">
        <h2 className="text-xl">Test API Key</h2>
        <input
          type="text"
          value={testApiKey}
          onChange={(e) => setTestApiKey(e.target.value)}
          placeholder="Enter API Key"
          className="border p-2 w-full mb-2"
        />
        <button
          onClick={testApiKeyRequest}
          className="bg-blue-500 text-white px-4 py-2 rounded">
          Test API Key
        </button>
      </div>

      <button onClick={() => signOut()} className="bg-red-500 text-white px-4 py-2 rounded">
        Sign Out
      </button>

      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
          <div className="bg-white p-6 rounded shadow-lg w-1/2 max-h-full overflow-auto">
            <h2 className="text-xl mb-4">API Key Test Response</h2>
            <pre className="bg-gray-100 p-4 border rounded overflow-auto">{testResponse}</pre>
            <button
              onClick={() => setShowModal(false)}
              className="mt-4 bg-blue-500 text-white px-4 py-2 rounded">
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;

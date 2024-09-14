import { useEffect, useState } from 'react';
import { auth, provider } from '@/lib/firebase';
import { signInWithPopup, signOut as firebaseSignOut, onAuthStateChanged } from 'firebase/auth';
import { FicastAPIClient } from '@/lib/ficast_client'; // Import your Axios client
import { AxiosError, InternalAxiosRequestConfig } from 'axios';

export const useAuth = () => {
  const [user, setUser] = useState<any>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [authResponse, setAuthResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      console.log('Auth state changed:', currentUser);

      if (currentUser) {
        const token = await currentUser.getIdToken();
        console.log('Token obtained:', token);
        setAuthToken(token);

        // Dynamically inject the token into FicastAPIClient headers
        FicastAPIClient.interceptors.request.use(
          (config: InternalAxiosRequestConfig<any>) => {
            config.headers.Authorization = `Bearer ${authToken}`;
            return config;
          },
          (error: AxiosError) => Promise.reject(error)
        );

        // Make API request to verify authentication
        try {
          const response = await FicastAPIClient.get('/check');
          console.log('Auth response:', response.data);
          setAuthResponse(response.data.message || 'Authentication successful!');
          setUser(currentUser);
        } catch (error) {
          console.error('Error during authentication:', (error as Error).message);
          setAuthResponse(
            'Authentication failed. Error: ' + (error as Error).message + ' with the endpoint: /check'
          );
          setUser(null);
        }
      } else {
        setUser(null);
        setAuthToken(null);
      }
      setLoading(false);
      console.log('Loading state set to false');
    });

    return () => unsubscribe();
  }, []);

  // Google Sign-in using Firebase Popup
  const signIn = async () => {
    try {
      console.log('Authenticating with Google...');
      const result = await signInWithPopup(auth, provider);
      // Handle post-authentication logic here if needed
    } catch (error) {
      console.error('Error during sign-in:', (error as Error).message);
    }
  };

  // Google Sign-out using Firebase
  const signOut = async () => {
    try {
      await firebaseSignOut(auth);
      setUser(null);
      setAuthToken(null);
      setAuthResponse(null);
    } catch (error) {
      console.error('Error during sign-out:', (error as Error).message);
    }
  };

  return { user, authToken, authResponse, loading, signIn, signOut };
};

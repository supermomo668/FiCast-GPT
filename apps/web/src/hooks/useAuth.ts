// src/hooks/useAuth.ts
import { useEffect, useState } from 'react';
import { auth, provider } from '@/lib/firebase';
import { signInWithPopup, signOut as firebaseSignOut, onAuthStateChanged } from 'firebase/auth';
import axios from 'axios';

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

        try {
          const response = await axios.get(
            `${process.env.NEXT_PUBLIC_BACKEND_AUTH_URL}/check`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );
          console.log('Auth response:', response.data);
          setAuthResponse(response.data.message || 'Authentication successful!');
          setUser(currentUser);
        } catch (error) {
          console.error('Error during authentication:', (error as Error).message);
          setAuthResponse('Authentication failed. Error: ' + (error as Error).message + ' with the endpoint: ' + `${process.env.NEXT_PUBLIC_BACKEND_AUTH_URL}/check`);
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

  const signIn = async () => {
    try {
      console.log("Authenticating with Google...");
      const result = await signInWithPopup(auth, provider);
    } catch (error) {
      console.error('Error during sign-in:', (error as Error).message);
    }
  };

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

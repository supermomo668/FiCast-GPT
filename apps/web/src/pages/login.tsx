import React from "react";
import { signInWithGoogle } from "../app/firebase";
import { useRouter } from "next/router";

const LoginPage: React.FC = () => {
  const router = useRouter();  // Use the router instance

  const handleSignIn = async () => {
    try {
      await signInWithGoogle();
      router.push("/"); // Redirect to the home page after login
    } catch (error) {
      console.error("Error during sign-in:", error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
      <h1 className="text-4xl font-bold mb-8">Welcome to FiCast</h1>
      <p className="text-lg mb-12">Knowledgeable Music in Your Ears</p>
      <button
        onClick={handleSignIn}
        className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-md text-lg"
      >
        Sign in with Google
      </button>
    </div>
  );
};

export default LoginPage;

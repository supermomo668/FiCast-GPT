import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import { FirestoreAdapter } from "@auth/firebase-adapter";
import { cert } from "firebase-admin/app";
import fs from "fs";
import path from "path";

// Get the path to the service account JSON key file from an environment variable
const serviceAccountPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;

if (!serviceAccountPath) {
  throw new Error("The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.");
}

// Load and parse the service account JSON file
let serviceAccount;
try {
  serviceAccount = JSON.parse(fs.readFileSync(path.resolve(serviceAccountPath), "utf8"));
} catch (error) {
  throw new Error(`Failed to load service account key file: ${error.message}`);
}

export default NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  adapter: FirestoreAdapter({
    credential: cert({
      projectId: serviceAccount.project_id,
      clientEmail: serviceAccount.client_email,
      privateKey: serviceAccount.private_key, // Use the private key directly from the JSON file
    }),
  }),
});

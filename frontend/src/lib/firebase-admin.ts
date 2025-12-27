import 'server-only';

import { initializeApp, getApps, cert, type ServiceAccount } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';

function getServiceAccount(): ServiceAccount {
  const projectId = process.env.FIREBASE_PROJECT_ID;
  const clientEmail = process.env.FIREBASE_CLIENT_EMAIL;
  const privateKey = process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n');

  if (!projectId || !clientEmail || !privateKey) {
    throw new Error(
      'Missing Firebase Admin credentials. Ensure FIREBASE_PROJECT_ID, FIREBASE_CLIENT_EMAIL, and FIREBASE_PRIVATE_KEY are set.'
    );
  }

  return {
    projectId,
    clientEmail,
    privateKey,
  };
}

const app = getApps().length === 0
  ? initializeApp({ credential: cert(getServiceAccount()) })
  : getApps()[0];

export const adminDb = getFirestore(app);

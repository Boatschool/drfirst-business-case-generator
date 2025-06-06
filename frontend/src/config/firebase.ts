// Firebase configuration for DrFirst Business Case Generator
import { initializeApp, FirebaseApp, getApps } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import Logger from '../utils/logger';

// Firebase configuration object
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

// Create logger for Firebase configuration
const logger = Logger.create('Firebase');

// Debug Firebase configuration (only in development)
if (import.meta.env.VITE_ENVIRONMENT === 'development') {
  logger.debug('Firebase Config Debug:', {
    apiKey: firebaseConfig.apiKey
      ? `${firebaseConfig.apiKey.substring(0, 10)}...`
      : 'MISSING',
    authDomain: firebaseConfig.authDomain || 'MISSING',
    projectId: firebaseConfig.projectId || 'MISSING',
    envVars: {
      apiKey: import.meta.env.VITE_FIREBASE_API_KEY ? 'SET' : 'MISSING',
      authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN ? 'SET' : 'MISSING',
      projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID ? 'SET' : 'MISSING',
    },
  });
}

// Validate required environment variables
const requiredEnvVars = {
  VITE_FIREBASE_API_KEY: import.meta.env.VITE_FIREBASE_API_KEY,
  VITE_FIREBASE_AUTH_DOMAIN: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  VITE_FIREBASE_PROJECT_ID: import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

const missingEnvVars = Object.entries(requiredEnvVars)
  .filter(([, value]) => !value)
  .map(([key]) => key);

if (missingEnvVars.length > 0) {
  const errorMsg = `Missing required Firebase environment variables: ${missingEnvVars.join(
    ', '
  )}`;
  logger.error('Firebase Configuration Error:', errorMsg);
  throw new Error(errorMsg);
}

// Initialize Firebase app (only once)
let app: FirebaseApp;
const existingApps = getApps();

if (existingApps.length > 0) {
  app = existingApps[0];
  logger.debug('Using existing Firebase app:', app.name);
} else {
  app = initializeApp(firebaseConfig);
  logger.debug('Firebase app initialized:', app.name);
}

// Initialize Firebase Auth
export const auth = getAuth(app);
export const firebaseApp = app;

// Set up auth state persistence
if (typeof window !== 'undefined') {
  import('firebase/auth').then(
    ({ browserLocalPersistence, setPersistence }) => {
      setPersistence(auth, browserLocalPersistence).catch((error) => {
        logger.warn('Failed to set auth persistence:', error);
      });
    }
  );
}

export { firebaseConfig };

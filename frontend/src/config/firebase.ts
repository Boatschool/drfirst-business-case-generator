// Firebase configuration for DrFirst Business Case Generator
import { initializeApp, FirebaseApp, getApps } from 'firebase/app';
import { getAuth, Auth } from 'firebase/auth';

// Firebase configuration object
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

// Debug Firebase configuration (only in development)
if (import.meta.env.VITE_ENVIRONMENT === 'development') {
  console.log('🔧 Firebase Config Debug:', {
    apiKey: firebaseConfig.apiKey ? `${firebaseConfig.apiKey.substring(0, 10)}...` : 'MISSING',
    authDomain: firebaseConfig.authDomain || 'MISSING',
    projectId: firebaseConfig.projectId || 'MISSING',
    envVars: {
      apiKey: import.meta.env.VITE_FIREBASE_API_KEY ? 'SET' : 'MISSING',
      authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN ? 'SET' : 'MISSING',
      projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID ? 'SET' : 'MISSING',
    }
  });
}

// Validate required environment variables
const requiredEnvVars = {
  'VITE_FIREBASE_API_KEY': import.meta.env.VITE_FIREBASE_API_KEY,
  'VITE_FIREBASE_AUTH_DOMAIN': import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  'VITE_FIREBASE_PROJECT_ID': import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

const missingEnvVars = Object.entries(requiredEnvVars)
  .filter(([key, value]) => !value)
  .map(([key]) => key);

if (missingEnvVars.length > 0) {
  const errorMsg = `Missing required Firebase environment variables: ${missingEnvVars.join(', ')}`;
  console.error('❌ Firebase Configuration Error:', errorMsg);
  throw new Error(errorMsg);
}

// Initialize Firebase app (only once)
let app: FirebaseApp;
const existingApps = getApps();

if (existingApps.length > 0) {
  app = existingApps[0];
  console.log('📱 Using existing Firebase app:', app.name);
} else {
  app = initializeApp(firebaseConfig);
  console.log('✅ Firebase app initialized:', app.name);
}

// Initialize Firebase Auth
export const auth = getAuth(app);
export const firebaseApp = app;

// Set up auth state persistence
if (typeof window !== 'undefined') {
  import('firebase/auth').then(({ browserLocalPersistence, setPersistence }) => {
    setPersistence(auth, browserLocalPersistence).catch((error) => {
      console.warn('Failed to set auth persistence:', error);
    });
  });
}

export { firebaseConfig }; 
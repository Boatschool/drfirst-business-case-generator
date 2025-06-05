import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock environment variables for testing
Object.defineProperty(window, 'ENV', {
  writable: true,
  value: {
    VITE_API_BASE_URL: 'http://localhost:8000',
    VITE_FIREBASE_API_KEY: 'test-api-key',
    VITE_FIREBASE_AUTH_DOMAIN: 'test-project.firebaseapp.com',
    VITE_FIREBASE_PROJECT_ID: 'test-project',
    VITE_FIREBASE_STORAGE_BUCKET: 'test-project.appspot.com',
    VITE_FIREBASE_MESSAGING_SENDER_ID: '123456789',
    VITE_FIREBASE_APP_ID: '1:123456789:web:abcdef123456',
  },
});

// Mock Firebase Auth
const mockAuth = {
  currentUser: null,
  onAuthStateChanged: vi.fn(),
  signInWithEmailAndPassword: vi.fn(),
  signOut: vi.fn(),
  createUserWithEmailAndPassword: vi.fn(),
};

const mockUser = {
  uid: 'test-uid',
  email: 'test@example.com',
  displayName: 'Test User',
  photoURL: null,
  emailVerified: true,
};

const mockIdTokenResult = {
  token: 'mock-token',
  authTime: new Date().toISOString(),
  issuedAtTime: new Date().toISOString(),
  expirationTime: new Date(Date.now() + 3600000).toISOString(),
  signInProvider: 'password',
  signInSecondFactor: null,
  claims: {
    iss: 'test-issuer',
    aud: 'test-audience',
    auth_time: Math.floor(Date.now() / 1000),
    user_id: 'test-uid',
    sub: 'test-uid',
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 3600,
    email: 'test@example.com',
    email_verified: true,
    firebase: {
      identities: {
        email: ['test@example.com']
      },
      sign_in_provider: 'password'
    }
  }
};

vi.mock('firebase/auth', () => ({
  getAuth: () => mockAuth,
  onAuthStateChanged: mockAuth.onAuthStateChanged,
  signInWithEmailAndPassword: mockAuth.signInWithEmailAndPassword,
  signOut: mockAuth.signOut,
  createUserWithEmailAndPassword: mockAuth.createUserWithEmailAndPassword,
  signInWithPopup: vi.fn().mockResolvedValue({ user: mockUser }),
  getIdToken: vi.fn().mockResolvedValue('mock-token'),
  getIdTokenResult: vi.fn().mockResolvedValue(mockIdTokenResult),
  GoogleAuthProvider: vi.fn().mockImplementation(() => ({
    addScope: vi.fn(),
  })),
  browserLocalPersistence: {
    type: 'LOCAL'
  },
  setPersistence: vi.fn().mockResolvedValue(undefined),
}));

// Mock Firebase Firestore
vi.mock('firebase/firestore', () => ({
  getFirestore: vi.fn(),
  collection: vi.fn(),
  doc: vi.fn(),
  getDoc: vi.fn(),
  setDoc: vi.fn(),
  updateDoc: vi.fn(),
  deleteDoc: vi.fn(),
  query: vi.fn(),
  where: vi.fn(),
  orderBy: vi.fn(),
  getDocs: vi.fn(),
}));

// Mock useAgentContext hook
vi.mock('./hooks/useAgentContext', () => ({
  useAgentContext: () => ({
    currentCaseDetails: null,
    cases: [],
    loading: false,
    error: null,
    generateCase: vi.fn(),
    streamCase: vi.fn(),
    stopGeneration: vi.fn(),
    saveCase: vi.fn(),
    loadCase: vi.fn(),
    deleteCase: vi.fn(),
    loadCases: vi.fn(),
    updateCaseSection: vi.fn(),
    regenerateSection: vi.fn(),
    clearError: vi.fn(),
  }),
}));

// Global test utilities
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

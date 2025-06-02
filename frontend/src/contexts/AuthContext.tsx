import React, { createContext, useState, useEffect, ReactNode } from 'react';
// FirebaseUser is used by Firebase SDK, AuthUser is our simplified version from authService
import { User as FirebaseUser } from 'firebase/auth'; 
import { authService, AuthUser } from '../services/auth/authService'; // Corrected import

interface AuthContextType {
  currentUser: AuthUser | null;
  loading: boolean;
  error: Error | null;
  signUp: typeof authService.signUp;
  signIn: typeof authService.signIn; // For email/password
  signInWithGoogle: typeof authService.signInWithGoogle; // Explicitly add Google Sign-In
  signOut: typeof authService.signOut;
  // Add other auth methods as needed, e.g., sendPasswordResetEmail
}

// Create the context with a default undefined value to catch consumers not wrapped in a provider
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setLoading(true);
    const unsubscribe = authService.onAuthStateChanged((user: AuthUser | null) => {
      setCurrentUser(user);
      setLoading(false);
      setError(null); 
      // Note: The authService.onAuthStateChanged itself doesn't directly provide an error callback.
      // Errors during auth operations (signUp, signIn, etc.) are caught by their respective promises.
    });
    return unsubscribe; 
  }, []);

  // Sign up, sign in, sign out methods from the authService
  const signUp = authService.signUp;
  const signIn = authService.signIn;
  const signOut = authService.signOut;
  const signInWithGoogle = authService.signInWithGoogle;

  const value = {
    currentUser,
    loading,
    error,
    signUp,
    signIn,
    signInWithGoogle,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 
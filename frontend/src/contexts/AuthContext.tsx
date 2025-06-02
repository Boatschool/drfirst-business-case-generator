import React, { createContext, useState, useEffect, ReactNode, useContext } from 'react';
// FirebaseUser is used by Firebase SDK, AuthUser is our simplified version from authService
import { User as FirebaseUser } from 'firebase/auth'; 
import { authService, AuthUser } from '../services/auth/authService'; // Corrected import

interface AuthContextType {
  currentUser: AuthUser | null;
  loading: boolean;
  error: string | null;
  signUp: typeof authService.signUp;
  signIn: typeof authService.signIn;
  signInWithGoogle: typeof authService.signInWithGoogle;
  signOut: typeof authService.signOut;
  getIdToken: typeof authService.getIdToken;
  isDrFirstUser: boolean;
  isValidUser: boolean;
}

// Create the context with a default undefined value to catch consumers not wrapped in a provider
const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('🔄 Setting up auth state listener...');
    setLoading(true);
    
    const unsubscribe = authService.onAuthStateChanged((user: AuthUser | null) => {
      console.log('📱 Auth state changed in context:', user ? user.email : 'null');
      setCurrentUser(user);
      setLoading(false);
      setError(null);
    });

    return () => {
      console.log('🧹 Cleaning up auth state listener');
      unsubscribe();
    };
  }, []);

  // Computed values
  const isDrFirstUser = authService.isDrFirstUser(currentUser);
  const validationResult = authService.validateUserAccess(currentUser);
  const isValidUser = validationResult.isValid;

  // If validation fails and we have a user, set the error
  useEffect(() => {
    if (currentUser && !isValidUser) {
      setError(validationResult.reason || 'Access validation failed');
    } else if (currentUser && isValidUser) {
      setError(null);
    }
  }, [currentUser, isValidUser, validationResult.reason]);

  const value: AuthContextType = {
    currentUser,
    loading,
    error,
    signUp: authService.signUp,
    signIn: authService.signIn,
    signInWithGoogle: authService.signInWithGoogle,
    signOut: authService.signOut,
    getIdToken: authService.getIdToken,
    isDrFirstUser,
    isValidUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}; 

// Custom hook to use the auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 

export { AuthContext }; 
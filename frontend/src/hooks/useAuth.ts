import { useState, useEffect, useCallback } from 'react';
import { authService, AuthUser, AuthState } from '../services/auth/authService';

export function useAuth(): AuthState & {
  signInWithGoogle: () => Promise<void>;
  signOut: () => Promise<void>;
  getIdToken: () => Promise<string | null>;
  isDrFirstUser: boolean;
  isValidUser: boolean;
} {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
  });

  // Authentication methods
  const signInWithGoogle = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      await authService.signInWithGoogle();
      // User state will be updated via onAuthStateChanged
    } catch (error) {
      console.error('Sign-in error:', error);
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Sign-in failed' 
      }));
    }
  }, []);

  const signOut = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      await authService.signOut();
      // User state will be updated via onAuthStateChanged
    } catch (error) {
      console.error('Sign-out error:', error);
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error instanceof Error ? error.message : 'Sign-out failed' 
      }));
    }
  }, []);

  const getIdToken = useCallback(async () => {
    return await authService.getIdToken();
  }, []);

  // Computed values
  const isDrFirstUser = authService.isDrFirstUser(state.user);
  const validationResult = authService.validateUserAccess(state.user);
  const isValidUser = validationResult.isValid;

  // Set up auth state listener
  useEffect(() => {
    const unsubscribe = authService.onAuthStateChanged((user: AuthUser | null) => {
      setState(prev => ({
        ...prev,
        user,
        loading: false,
        error: null,
      }));
    });

    return unsubscribe;
  }, []);

  // Update error if user access is invalid
  useEffect(() => {
    if (state.user && !isValidUser) {
      setState(prev => ({ 
        ...prev, 
        error: validationResult.error || 'Access denied' 
      }));
    } else if (state.user && isValidUser && state.error) {
      setState(prev => ({ ...prev, error: null }));
    }
  }, [state.user, isValidUser, validationResult.error]);

  return {
    ...state,
    signInWithGoogle,
    signOut,
    getIdToken,
    isDrFirstUser,
    isValidUser,
  };
} 
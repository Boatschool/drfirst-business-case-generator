import React, {
  createContext,
  useState,
  useEffect,
  ReactNode,
  useContext,
  useMemo,
} from 'react';
// FirebaseUser is used by Firebase SDK, AuthUser is our simplified version from authService

import { authService, AuthUser } from '../services/auth/authService'; // Corrected import

// Generate unique provider ID for debugging
const AUTH_PROVIDER_ID = Math.random().toString(36).substring(2, 15);
console.log(`🆔 AuthProvider Instance Created: ${AUTH_PROVIDER_ID}`);

interface AuthContextType {
  currentUser: AuthUser | null;
  loading: boolean;
  error: string | null;
  signUp: typeof authService.signUp;
  signIn: typeof authService.signIn;
  signInWithGoogle: typeof authService.signInWithGoogle;
  signOut: typeof authService.signOut;
  getIdToken: typeof authService.getIdToken;
  getIdTokenResult: typeof authService.getIdTokenResult;
  refreshIdToken: typeof authService.refreshIdToken;
  isDrFirstUser: boolean;
  isValidUser: boolean;
  systemRole: string | null;
  isAdmin: boolean;
  isDeveloper: boolean;
  isSalesManager: boolean;
  isFinanceApprover: boolean;
  isProductOwner: boolean;
  isFinalApprover: boolean;
}

// Create the context with a default undefined value to catch consumers not wrapped in a provider
const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  console.log(
    `🟢 [${AUTH_PROVIDER_ID}] AuthProvider: Component mounted/rendering`
  );

  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Debug: Log component mount/unmount
  useEffect(() => {
    console.log(`🟢 [${AUTH_PROVIDER_ID}] AuthProvider: Mounted`);
    return () => {
      console.log(`🔴 [${AUTH_PROVIDER_ID}] AuthProvider: Unmounted`);
    };
  }, []);

  useEffect(() => {
    console.log(`🔄 [${AUTH_PROVIDER_ID}] Setting up auth state listener...`);
    setLoading(true);

    const unsubscribe = authService.onAuthStateChanged(
      (user: AuthUser | null) => {
        console.log(
          '📱 Auth state changed in context:',
          user ? user.email : 'null'
        );
        setCurrentUser(user);
        setLoading(false);
        setError(null);
      }
    );

    return () => {
      console.log(`🧹 [${AUTH_PROVIDER_ID}] Cleaning up auth state listener`);
      unsubscribe();
    };
  }, []);

  // Computed values
  const isDrFirstUser = authService.isDrFirstUser(currentUser);
  const validationResult = authService.validateUserAccess(currentUser);
  const isValidUser = validationResult.isValid;
  const systemRole = currentUser?.systemRole || null;
  const isAdmin = systemRole === 'ADMIN';

  // Additional role checks for commonly used roles
  const isDeveloper = systemRole === 'DEVELOPER';
  const isSalesManager = systemRole === 'SALES_MANAGER';
  const isFinanceApprover = systemRole === 'FINANCE_APPROVER';
  const isProductOwner = systemRole === 'PRODUCT_OWNER';
  const isFinalApprover = systemRole === 'FINAL_APPROVER';

  // If validation fails and we have a user, set the error
  useEffect(() => {
    if (currentUser && !isValidUser) {
      setError(validationResult.reason || 'Access validation failed');
    } else if (currentUser && isValidUser) {
      setError(null);
    }
  }, [currentUser, isValidUser, validationResult.reason]);

  const value: AuthContextType = useMemo(
    () => ({
      currentUser,
      loading,
      error,
      signUp: authService.signUp,
      signIn: authService.signIn,
      signInWithGoogle: authService.signInWithGoogle,
      signOut: authService.signOut,
      getIdToken: authService.getIdToken,
      getIdTokenResult: authService.getIdTokenResult,
      refreshIdToken: authService.refreshIdToken,
      isDrFirstUser,
      isValidUser,
      systemRole,
      isAdmin,
      isDeveloper,
      isSalesManager,
      isFinanceApprover,
      isProductOwner,
      isFinalApprover,
    }),
    [
      currentUser,
      loading,
      error,
      isDrFirstUser,
      isValidUser,
      systemRole,
      isAdmin,
      isDeveloper,
      isSalesManager,
      isFinanceApprover,
      isProductOwner,
      isFinalApprover,
    ]
  );

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

import {
  User,
  UserCredential,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  onAuthStateChanged,
  signOut,
  getIdToken,
  getIdTokenResult,
  IdTokenResult,
} from 'firebase/auth';
import { auth } from '../../config/firebase';
import Logger from '../../utils/logger';

// User type for our application
export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
  systemRole?: string | null;
}

// Auth state type
export interface AuthState {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
}

class AuthService {
  private googleProvider: GoogleAuthProvider;
  private logger = Logger.create('AuthService');

  constructor() {
    // Initialize Google provider
    this.googleProvider = new GoogleAuthProvider();
    this.googleProvider.addScope('email');
    this.googleProvider.addScope('profile');

    this.logger.debug('AuthService initialized');
  }

  /**
   * Sign up with email and password
   */
  signUp = async (email: string, password: string): Promise<UserCredential> => {
    try {
      this.logger.debug('Attempting email sign-up for:', email);
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        email,
        password
      );
      this.logger.debug('Email sign-up successful:', userCredential.user.email);
      return userCredential;
    } catch (error) {
      this.logger.error('Email sign-up error:', error);
      throw error;
    }
  };

  /**
   * Sign in with email and password
   */
  signIn = async (email: string, password: string): Promise<UserCredential> => {
    try {
      this.logger.debug('Attempting email sign-in for:', email);
      const userCredential = await signInWithEmailAndPassword(
        auth,
        email,
        password
      );
      this.logger.debug('Email sign-in successful:', userCredential.user.email);
      return userCredential;
    } catch (error) {
      this.logger.error('Email sign-in error:', error);
      throw error;
    }
  };

  /**
   * Sign in with Google using popup
   */
  signInWithGoogle = async (): Promise<UserCredential> => {
    try {
      this.logger.debug('Attempting Google sign-in...');
      const result = await signInWithPopup(auth, this.googleProvider);
      this.logger.debug('Google sign-in successful:', result.user.email);
      return result;
    } catch (error) {
      this.logger.error('Google sign-in error:', error);
      throw error;
    }
  };

  /**
   * Sign out current user
   */
  signOut = async (): Promise<void> => {
    try {
      this.logger.debug('Signing out...');
      await signOut(auth);
      this.logger.debug('Sign-out successful');
    } catch (error) {
      this.logger.error('Sign-out error:', error);
      throw error;
    }
  };

  /**
   * Get current user
   */
  getCurrentUser(): AuthUser | null {
    const user = auth.currentUser;
    return user ? this.convertFirebaseUser(user) : null;
  }

  /**
   * Get ID token for authenticated requests
   */
  getIdToken = async (): Promise<string | null> => {
    try {
      const user = auth.currentUser;
      if (!user) {
        this.logger.debug('No authenticated user for token');
        return null;
      }

      this.logger.debug('Getting ID token for user:', user.email);
      const token = await getIdToken(user);
      this.logger.debug('ID token retrieved successfully');
      return token;
    } catch (error) {
      this.logger.error('Error getting ID token:', error);
      throw error;
    }
  };

  /**
   * Get ID token result with custom claims for authenticated requests
   */
  getIdTokenResult = async (): Promise<IdTokenResult | null> => {
    try {
      const user = auth.currentUser;
      if (!user) {
        this.logger.debug('No authenticated user for token result');
        return null;
      }

      this.logger.debug(
        'Getting ID token result with custom claims for user:',
        user.email
      );
      const tokenResult = await getIdTokenResult(user);
      this.logger.debug('ID token result retrieved successfully');
      return tokenResult;
    } catch (error) {
      this.logger.error('Error getting ID token result:', error);
      throw error;
    }
  };

  /**
   * Force refresh ID token to get a new token with current project configuration
   */
  refreshIdToken = async (): Promise<string | null> => {
    try {
      const user = auth.currentUser;
      if (!user) {
        this.logger.debug('No authenticated user for token refresh');
        return null;
      }

      this.logger.debug('Force refreshing ID token for user:', user.email);
      const token = await getIdToken(user, true); // Force refresh
      this.logger.debug('ID token refreshed successfully');
      return token;
    } catch (error) {
      this.logger.error('Error refreshing ID token:', error);
      throw error;
    }
  };

  /**
   * Listen to auth state changes
   */
  onAuthStateChanged = (
    callback: (user: AuthUser | null) => void
  ): (() => void) => {
    this.logger.debug('Setting up auth state listener');
    return onAuthStateChanged(auth, async (user: User | null) => {
      this.logger.debug(
        'Auth state changed:',
        user ? `${user.email} (${user.uid})` : 'null'
      );

      if (user) {
        // Get user with custom claims
        const authUser = await this.convertFirebaseUserWithClaims(user);
        callback(authUser);
      } else {
        callback(null);
      }
    });
  };

  /**
   * Convert Firebase User to AuthUser with custom claims
   */
  private async convertFirebaseUserWithClaims(user: User): Promise<AuthUser> {
    try {
      const tokenResult = await getIdTokenResult(user);
      const systemRole = tokenResult.claims.systemRole || null;

      this.logger.debug('User claims:', {
        email: user.email,
        systemRole,
        hasCustomClaims: Object.keys(tokenResult.claims).length > 0,
      });

      return {
        uid: user.uid,
        email: user.email,
        displayName: user.displayName,
        photoURL: user.photoURL,
        emailVerified: user.emailVerified,
        systemRole: systemRole,
      };
    } catch (error) {
      this.logger.error('Error getting custom claims:', error);
      // Fallback to user without custom claims
      return this.convertFirebaseUser(user);
    }
  }

  /**
   * Convert Firebase User to AuthUser
   */
  private convertFirebaseUser(user: User): AuthUser {
    return {
      uid: user.uid,
      email: user.email,
      displayName: user.displayName,
      photoURL: user.photoURL,
      emailVerified: user.emailVerified,
      systemRole: null,
    };
  }

  /**
   * Check if user has DrFirst email domain
   */
  isDrFirstUser(user: AuthUser | null): boolean {
    if (!user?.email) return false;
    return user.email.endsWith('@drfirst.com');
  }

  /**
   * Validate user access based on business rules
   */
  validateUserAccess(user: AuthUser | null): {
    isValid: boolean;
    reason?: string;
  } {
    if (!user) {
      return { isValid: false, reason: 'No user authenticated' };
    }

    if (!user.emailVerified) {
      return { isValid: false, reason: 'Email not verified' };
    }

    // For now, allow all verified users
    // In the future, you might want to restrict to DrFirst emails only:
    // if (!this.isDrFirstUser(user)) {
    //   return { isValid: false, reason: 'Access restricted to DrFirst employees' };
    // }

    return { isValid: true };
  }
}

// Export singleton instance
export const authService = new AuthService();

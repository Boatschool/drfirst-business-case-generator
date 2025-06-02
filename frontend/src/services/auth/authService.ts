import { 
  initializeApp, 
  FirebaseApp, 
  getApps 
} from 'firebase/app';
import { 
  getAuth, 
  Auth, 
  GoogleAuthProvider, 
  signInWithPopup, 
  signOut as firebaseSignOut,
  onAuthStateChanged,
  User,
  UserCredential,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword
} from 'firebase/auth';

// Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
};

export interface AuthUser {
  uid: string;
  email: string | null;
  displayName: string | null;
  photoURL: string | null;
  emailVerified: boolean;
}

export interface AuthState {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
}

class AuthService {
  private app: FirebaseApp;
  private auth: Auth;
  private googleProvider: GoogleAuthProvider;

  constructor() {
    // Initialize Firebase (only if not already initialized)
    this.app = getApps().length > 0 ? getApps()[0] : initializeApp(firebaseConfig);
    this.auth = getAuth(this.app);
    
    // Configure Google provider
    this.googleProvider = new GoogleAuthProvider();
    this.googleProvider.addScope('email');
    this.googleProvider.addScope('profile');
    
    // Force account selection for cleaner UX
    this.googleProvider.setCustomParameters({
      prompt: 'select_account'
    });
  }

  /**
   * Sign in with Google using popup
   */
  async signInWithGoogle(): Promise<UserCredential | null> {
    try {
      const result = await signInWithPopup(this.auth, this.googleProvider);
      console.log('✅ Google sign-in successful:', result.user.email);
      return result;
    } catch (error) {
      console.error('❌ Google sign-in error:', error);
      throw error;
    }
  }

  /**
   * Sign out current user
   */
  async signOut(): Promise<void> {
    try {
      await firebaseSignOut(this.auth);
      console.log('✅ Sign-out successful');
    } catch (error) {
      console.error('❌ Sign-out error:', error);
      throw error;
    }
  }

  /**
   * Get current user
   */
  getCurrentUser(): User | null {
    return this.auth.currentUser;
  }

  /**
   * Get current user's ID token
   */
  async getIdToken(): Promise<string | null> {
    const user = this.getCurrentUser();
    if (user) {
      try {
        return await user.getIdToken();
      } catch (error) {
        console.error('❌ Error getting ID token:', error);
        return null;
      }
    }
    return null;
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
    };
  }

  /**
   * Subscribe to authentication state changes
   */
  onAuthStateChanged(callback: (user: AuthUser | null) => void): () => void {
    return onAuthStateChanged(this.auth, (user) => {
      callback(user ? this.convertFirebaseUser(user) : null);
    });
  }

  /**
   * Check if user email is from DrFirst domain
   */
  isDrFirstUser(user: AuthUser | null): boolean {
    return user?.email?.endsWith('@drfirst.com') ?? false;
  }

  /**
   * Validate user access (DrFirst domain only)
   */
  validateUserAccess(user: AuthUser | null): { isValid: boolean; error?: string } {
    if (!user) {
      return { isValid: false, error: 'No user authenticated' };
    }

    if (!user.emailVerified) {
      return { isValid: false, error: 'Email not verified' };
    }

    if (!this.isDrFirstUser(user)) {
      return { 
        isValid: false, 
        error: 'Access restricted to DrFirst employees. Please use your @drfirst.com email.' 
      };
    }

    return { isValid: true };
  }

  /**
   * Sign up with email and password
   */
  async signUp(email: string, password: string): Promise<UserCredential> {
    try {
      const userCredential = await createUserWithEmailAndPassword(this.auth, email, password);
      console.log('✅ Email sign-up successful:', userCredential.user.email);
      // You might want to send a verification email here
      return userCredential;
    } catch (error) {
      console.error('❌ Email sign-up error:', error);
      throw error;
    }
  }

  /**
   * Sign in with email and password
   */
  async signIn(email: string, password: string): Promise<UserCredential> {
    try {
      const userCredential = await signInWithEmailAndPassword(this.auth, email, password);
      console.log('✅ Email sign-in successful:', userCredential.user.email);
      return userCredential;
    } catch (error) {
      console.error('❌ Email sign-in error:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const authService = new AuthService();
export default authService; 
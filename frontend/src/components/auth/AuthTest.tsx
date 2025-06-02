import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './AuthTest.css';

export const AuthTest: React.FC = () => {
  const { 
    currentUser, 
    loading, 
    error, 
    signInWithGoogle, 
    signOut, 
    isDrFirstUser, 
    isValidUser 
  } = useAuth();

  if (loading) {
    return (
      <div className="auth-test">
        <div className="loading">
          <h2>🔄 Loading...</h2>
          <p>Checking authentication status...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="auth-test">
        <div className="error">
          <h2>❌ Authentication Error</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!currentUser) {
    return (
      <div className="auth-test">
        <div className="sign-in">
          <h1>🔐 DrFirst Business Case Generator</h1>
          <p>Please sign in with your DrFirst Google account to continue.</p>
          <button 
            onClick={signInWithGoogle}
            className="google-sign-in-btn"
          >
            <img 
              src="https://developers.google.com/identity/images/g-logo.png" 
              alt="Google"
              width="20"
              height="20"
            />
            Sign in with Google
          </button>
          <p className="note">
            <strong>Note:</strong> Only @drfirst.com email addresses are allowed.
          </p>
        </div>
      </div>
    );
  }

  // User is signed in
  return (
    <div className="auth-test">
      <div className="user-info">
        <h2>✅ Authentication Successful</h2>
        <div className="user-details">
          <p><strong>Email:</strong> {currentUser.email}</p>
          <p><strong>Name:</strong> {currentUser.displayName || 'Not provided'}</p>
          <p><strong>UID:</strong> {currentUser.uid}</p>
          <p><strong>Email Verified:</strong> {currentUser.emailVerified ? '✅ Yes' : '❌ No'}</p>
          <p><strong>DrFirst User:</strong> {isDrFirstUser ? '✅ Yes' : '❌ No'}</p>
          <p><strong>Valid Access:</strong> {isValidUser ? '✅ Yes' : '❌ No'}</p>
        </div>
        
        {currentUser.photoURL && (
          <div className="user-avatar">
            <img 
              src={currentUser.photoURL} 
              alt="User Avatar" 
              width="60" 
              height="60" 
              style={{ borderRadius: '50%' }}
            />
          </div>
        )}
        
        <div className="actions">
          <button onClick={signOut} className="sign-out-btn">
            Sign Out
          </button>
        </div>
        
        {!isValidUser && (
          <div className="warning">
            <p>⚠️ Your account doesn't have valid access. Please contact an administrator.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuthTest; 
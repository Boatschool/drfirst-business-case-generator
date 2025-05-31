import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import './AuthTest.css';

export const AuthTest: React.FC = () => {
  const { 
    user, 
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

  if (!user) {
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

  return (
    <div className="auth-test">
      <div className="user-profile">
        <h1>✅ Authentication Successful!</h1>
        
        <div className="user-info">
          {user.photoURL && (
            <img 
              src={user.photoURL} 
              alt="Profile" 
              className="profile-picture"
            />
          )}
          
          <div className="user-details">
            <h2>Welcome, {user.displayName || user.email}!</h2>
            <p><strong>Email:</strong> {user.email}</p>
            <p><strong>UID:</strong> {user.uid}</p>
            <p><strong>Email Verified:</strong> {user.emailVerified ? '✅' : '❌'}</p>
            <p><strong>DrFirst User:</strong> {isDrFirstUser ? '✅' : '❌'}</p>
            <p><strong>Access Granted:</strong> {isValidUser ? '✅' : '❌'}</p>
          </div>
        </div>

        <div className="actions">
          <button onClick={signOut} className="sign-out-btn">
            Sign Out
          </button>
        </div>

        <div className="status">
          <h3>🎉 Identity Platform Status</h3>
          <ul>
            <li>✅ Firebase SDK initialized</li>
            <li>✅ Google authentication working</li>
            <li>✅ DrFirst domain validation active</li>
            <li>✅ User session management ready</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AuthTest; 
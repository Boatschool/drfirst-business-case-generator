import React, { useState } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  TextField, 
  Button, 
  Alert,
  CircularProgress 
} from '@mui/material';
import { EmailAuthProvider, linkWithCredential, getAuth } from 'firebase/auth';
import { useAuth } from '../../hooks/useAuth';
import Logger from '../../utils/logger';

interface LinkEmailPasswordProps {
  onSuccess?: () => void;
}

const logger = Logger.create('LinkEmailPassword');

export const LinkEmailPassword: React.FC<LinkEmailPasswordProps> = ({ onSuccess }) => {
  const { currentUser } = useAuth();
  const [email, setEmail] = useState(currentUser?.email || '');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleLinkEmailPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!currentUser) {
      setError('No user signed in');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create email/password credential
      const credential = EmailAuthProvider.credential(email, password);
      
      // Link it to the current user
      const auth = getAuth();
      if (!auth.currentUser) {
        throw new Error('No Firebase user available');
      }
      await linkWithCredential(auth.currentUser, credential);
      
      setSuccess(true);
      logger.debug('Email/password successfully linked to account');
      
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      logger.error('Error linking email/password:', error);
      
      const errorObj = error && typeof error === 'object' ? error as Record<string, unknown> : {};
      const code = String(errorObj.code || '');
      const message = String(errorObj.message || '');
      
      if (code === 'auth/credential-already-in-use') {
        setError('This email is already associated with another account.');
      } else if (code === 'auth/email-already-in-use') {
        setError('This email is already in use by another account.');
      } else if (code === 'auth/provider-already-linked') {
        setError('Email/password is already linked to this account.');
      } else {
        setError(message || 'Failed to link email/password');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <Card>
        <CardContent>
          <Alert severity="success">
            <Typography variant="h6" gutterBottom>
              Email/Password Successfully Linked! 🎉
            </Typography>
            <Typography variant="body2">
              You can now sign in using either Google or your email/password.
            </Typography>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Link Email/Password to Your Account
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Add email/password sign-in to your existing Google account.
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleLinkEmailPassword}>
          <TextField
            fullWidth
            label="Email Address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            margin="normal"
            required
            disabled={!!currentUser?.email}
            helperText={currentUser?.email ? "Using your current email address" : ""}
          />
          
          <TextField
            fullWidth
            label="New Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
            helperText="Minimum 6 characters"
          />
          
          <TextField
            fullWidth
            label="Confirm Password"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            margin="normal"
            required
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            disabled={loading || !password || !confirmPassword}
            sx={{ mt: 3, mb: 2 }}
          >
            {loading ? (
              <CircularProgress size={24} />
            ) : (
              'Link Email/Password'
            )}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
}; 
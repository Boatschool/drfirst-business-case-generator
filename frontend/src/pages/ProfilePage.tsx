import React from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Card, 
  CardContent, 
  Chip,
  Divider,
  Alert
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { LinkEmailPassword } from '../components/auth/LinkEmailPassword';
import useDocumentTitle from '../hooks/useDocumentTitle';

export const ProfilePage: React.FC = () => {
  // Set document title
  useDocumentTitle('Profile');

  const { currentUser, systemRole, isAdmin } = useAuth();

  if (!currentUser) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          Please sign in to view your profile.
        </Alert>
      </Container>
    );
  }

  // Check if user has email/password linked
  // Note: This is a simplified check - in a real implementation you'd need to check Firebase User.providerData
  const hasEmailPassword = false; // Simplified for now

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Profile & Account Settings
      </Typography>

      {/* User Info Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Account Information
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Email Address
            </Typography>
            <Typography variant="body1">
              {currentUser.email}
            </Typography>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Display Name
            </Typography>
            <Typography variant="body1">
              {currentUser.displayName || 'Not set'}
            </Typography>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Role
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Chip 
                label={systemRole} 
                color={isAdmin ? "primary" : "default"}
                variant="outlined"
              />
            </Box>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Sign-in Methods
            </Typography>
            <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip 
                label="Google"
                size="small"
                color="success"
              />
              {hasEmailPassword && (
                <Chip 
                  label="Email/Password"
                  size="small"
                  color="success"
                />
              )}
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Account Linking Section */}
      {!hasEmailPassword && (
        <>
          <Divider sx={{ my: 3 }} />
          <Typography variant="h6" gutterBottom>
            Add Sign-in Method
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Link email/password sign-in to your account so you can sign in with either Google or email/password.
          </Typography>
          <LinkEmailPassword 
            onSuccess={() => {
              // Could show a success message or refresh the page
              window.location.reload();
            }}
          />
        </>
      )}

      {hasEmailPassword && (
        <Alert severity="success" sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Email/Password Already Linked ✅
          </Typography>
          <Typography variant="body2">
            You can sign in using either Google or your email/password.
          </Typography>
        </Alert>
      )}
    </Container>
  );
}; 
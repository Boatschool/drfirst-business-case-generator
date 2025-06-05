import React, { useContext, useState, useCallback } from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import {
  Link as RouterLink,
  Outlet,
  useNavigate,
  useLocation,
} from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { useAgentContext } from '../contexts/AgentContext';
import FloatingChat from '../components/common/FloatingChat';
import Breadcrumbs from '../components/common/Breadcrumbs';

const AppLayout: React.FC = () => {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  const {
    messages,
    sendFeedbackToAgent,
    currentCaseDetails,
    isLoading,
    error: agentContextError,
  } = useAgentContext();

  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const [isSendingFeedback, setIsSendingFeedback] = useState(false);

  const handleSignOut = async () => {
    if (authContext) {
      try {
        await authContext.signOut();
        navigate('/login');
      } catch (error) {
        console.error('Sign out failed:', error);
        // Optionally show an error message to the user
      }
    }
  };

  const handleSendMessage = useCallback(
    async (message: string) => {
      if (!currentCaseDetails?.case_id) {
        setFeedbackError(
          'No active case selected. Please navigate to a specific business case or create a new one to use the chat.'
        );
        return;
      }

      setIsSendingFeedback(true);
      setFeedbackError(null);

      try {
        await sendFeedbackToAgent({
          caseId: currentCaseDetails.case_id,
          message: message,
        });
      } catch (err: any) {
        setFeedbackError(
          err.message || 'Failed to send message. Please try again.'
        );
      } finally {
        setIsSendingFeedback(false);
      }
    },
    [currentCaseDetails, sendFeedbackToAgent]
  );

  // Helper function to determine if a navigation link is active
  const isActivePath = (path: string): boolean => {
    return location.pathname === path;
  };

  // Style for active navigation buttons
  const getNavButtonStyle = (path: string) => ({
    color: 'inherit',
    fontWeight: isActivePath(path) ? 'bold' : 'normal',
    textDecoration: 'none',
    borderBottom: isActivePath(path) ? '2px solid currentColor' : 'none',
    borderRadius: 0,
  });

  // Only show chat on protected pages where user is authenticated
  const showChat =
    authContext?.currentUser &&
    !['/login', '/signup', '/'].includes(location.pathname);

  // Filter out PRD_DRAFT messages for the chat display
  const displayMessages = (messages || []).filter(
    (msg) => msg.messageType !== 'PRD_DRAFT'
  );

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{ flexGrow: 1, color: 'inherit', textDecoration: 'none' }}
          >
            DrFirst Business Case Gen
          </Typography>
          {authContext?.currentUser ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {/* Primary Navigation Links */}
              <Button 
                color="inherit" 
                component={RouterLink} 
                to="/dashboard"
                sx={getNavButtonStyle('/dashboard')}
              >
                Dashboard
              </Button>
              <Button 
                color="inherit" 
                component={RouterLink} 
                to="/new-case"
                sx={getNavButtonStyle('/new-case')}
              >
                Create New Case
              </Button>
              
              {/* Conditional Admin Link - Only show for admin users */}
              {authContext.isAdmin && (
                <Button 
                  color="inherit" 
                  component={RouterLink} 
                  to="/admin"
                  sx={getNavButtonStyle('/admin')}
                >
                  Admin
                </Button>
              )}
              
              {/* User Profile and Sign Out */}
              <Button 
                color="inherit" 
                onClick={handleSignOut}
                sx={{ ml: 2 }}
              >
                Sign Out ({authContext.currentUser.email})
              </Button>
            </Box>
          ) : (
            <Button color="inherit" component={RouterLink} to="/login">
              Sign In
            </Button>
          )}
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Breadcrumbs />
        <Outlet /> {/* Child routes will render here */}
      </Box>
      <Box
        component="footer"
        sx={{
          p: 2,
          mt: 'auto',
          backgroundColor: 'grey.200',
          textAlign: 'center',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} DrFirst
        </Typography>
      </Box>

      {/* Persistent Floating Chat */}
      {showChat && (
        <FloatingChat
          messages={displayMessages}
          onSendMessage={handleSendMessage}
          isSending={isSendingFeedback}
          isLoading={isLoading}
          error={feedbackError || agentContextError?.message || undefined}
          disabled={!currentCaseDetails}
          currentCaseTitle={currentCaseDetails?.title}
        />
      )}
    </Box>
  );
};

export default AppLayout;

import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink, Outlet, useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

const AppLayout: React.FC = () => {
  const authContext = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSignOut = async () => {
    if (authContext) {
      try {
        await authContext.signOut();
        navigate('/login');
      } catch (error) {
        console.error("Sign out failed:", error);
        // Optionally show an error message to the user
      }
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component={RouterLink} to="/" sx={{ flexGrow: 1, color: 'inherit', textDecoration: 'none' }}>
            DrFirst Business Case Gen
          </Typography>
          {authContext?.currentUser ? (
            <Button color="inherit" onClick={handleSignOut}>
              Sign Out ({authContext.currentUser.email})
            </Button>
          ) : (
            <Button color="inherit" component={RouterLink} to="/login">
              Sign In
            </Button>
          )}
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Outlet /> {/* Child routes will render here */}
      </Box>
      <Box component="footer" sx={{ p: 2, mt: 'auto', backgroundColor: 'grey.200', textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          © {new Date().getFullYear()} DrFirst
        </Typography>
      </Box>
    </Box>
  );
};

export default AppLayout; 
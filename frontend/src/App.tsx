import React, { useContext } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Outlet,
  useLocation,
} from 'react-router-dom';
import { AuthProvider, AuthContext } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import SignUpPage from './pages/SignUpPage';
import DashboardPage from './pages/DashboardPage';
import NewCasePage from './pages/NewCasePage';
import BusinessCaseDetailPage from './pages/BusinessCaseDetailPage';
import AppLayout from './layouts/AppLayout';
import { Container, Typography, Box, Alert } from '@mui/material';

// Placeholder for a simple Home Page component
const HomePage: React.FC = () => (
  <Container>
    <Box sx={{ my: 4, textAlign: 'center' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome to DrFirst Business Case Generator
      </Typography>
      <Typography variant="body1">
        Please log in or sign up to continue.
      </Typography>
    </Box>
  </Container>
);

// ProtectedRoute component
interface ProtectedRouteProps {
  // children?: React.ReactNode; // Outlet handles children now
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = () => {
  const authContext = useContext(AuthContext);
  const location = useLocation();

  if (!authContext) {
    return <Alert severity="error">Auth context not available in ProtectedRoute.</Alert>;
  }

  if (authContext.loading) {
    return (
      <Container sx={{display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh'}}>
        <Typography>Loading authentication status...</Typography>
      </Container>
    );
  }

  if (!authContext.currentUser) {
    // Redirect them to the /login page, but save the current location they were
    // trying to go to when they were redirected. This allows us to send them
    // along to that page after they login, which is a nicer user experience
    // than dropping them off on the home page.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />; // Renders the child route's element (e.g., DashboardPage)
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route element={<AppLayout />}> {/* AppLayout wraps all pages */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="/" element={<HomePage />} />
            
            {/* Protected Routes */}
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/new-case" element={<NewCasePage />} />
              <Route path="/cases/:caseId" element={<BusinessCaseDetailPage />} />
              {/* Add other protected routes here */}
            </Route>
            
            {/* Catch-all for unmatched routes (optional) */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App; 
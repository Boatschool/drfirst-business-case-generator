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
import { AgentProvider } from './contexts/AgentContext';
import LoginPage from './pages/LoginPage';
import SignUpPage from './pages/SignUpPage';
import MainPage from './pages/MainPage';
import DashboardPage from './pages/DashboardPage';
import NewCasePage from './pages/NewCasePage';
import { ProfilePage } from './pages/ProfilePage';

import BusinessCaseDetailPageSimplified from './pages/BusinessCaseDetailPage_Simplified';
import ReadOnlyCaseViewPage from './pages/ReadOnlyCaseViewPage';
import AdminPage from './pages/AdminPage';
import ErrorDemoPage from './pages/ErrorDemoPage';
import AppLayout from './layouts/AppLayout';
import ErrorBoundary from './components/common/ErrorBoundary';
import {
  Container,
  Typography,
  Box,
  Alert,
  Button,
  Stack,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

// Smart Home Page component that redirects based on auth status
const HomePage: React.FC = () => {
  const authContext = useContext(AuthContext);

  if (!authContext) {
    return <Alert severity="error">Auth context not available.</Alert>;
  }

  if (authContext.loading) {
    return (
      <Container
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <Typography>Loading authentication status...</Typography>
      </Container>
    );
  }

  // If user is authenticated, redirect to main page
  if (authContext.currentUser) {
    return <Navigate to="/main" replace />;
  }

  // If not authenticated, show welcome screen
  return (
    <Container>
      <Box sx={{ my: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to DrFirst Business Case Generator
        </Typography>
        <Typography variant="body1" sx={{ mb: 4 }}>
          Please log in or sign up to continue.
        </Typography>
        <Stack direction="row" spacing={2} justifyContent="center">
          <Button
            component={RouterLink}
            to="/login"
            variant="contained"
            size="large"
          >
            Sign In
          </Button>
          <Button
            component={RouterLink}
            to="/signup"
            variant="outlined"
            size="large"
          >
            Sign Up
          </Button>
        </Stack>
      </Box>
    </Container>
  );
};

// ProtectedRoute component
interface ProtectedRouteProps {
  // children?: React.ReactNode; // Outlet handles children now
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = () => {
  const authContext = useContext(AuthContext);
  const location = useLocation();

  if (!authContext) {
    return (
      <Alert severity="error">
        Auth context not available in ProtectedRoute.
      </Alert>
    );
  }

  if (authContext.loading) {
    return (
      <Container
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
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

// AdminProtectedRoute component - requires ADMIN role
interface AdminProtectedRouteProps {
  // children?: React.ReactNode; // Outlet handles children now
}

const AdminProtectedRoute: React.FC<AdminProtectedRouteProps> = () => {
  const authContext = useContext(AuthContext);
  const location = useLocation();

  if (!authContext) {
    return (
      <Alert severity="error">
        Auth context not available in AdminProtectedRoute.
      </Alert>
    );
  }

  if (authContext.loading) {
    return (
      <Container
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <Typography>Loading authentication status...</Typography>
      </Container>
    );
  }

  if (!authContext.currentUser) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!authContext.isAdmin) {
    // Show access denied for non-admin users
    return (
      <Container
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Access Denied
            </Typography>
            <Typography variant="body1" sx={{ mb: 2 }}>
              You do not have administrator privileges to access this page.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Current role: {authContext.systemRole || 'USER'}
            </Typography>
          </Alert>
          <Button
            component={RouterLink}
            to="/dashboard"
            variant="contained"
            sx={{ mt: 2 }}
          >
            Return to Dashboard
          </Button>
        </Box>
      </Container>
    );
  }

  return <Outlet />; // Renders the child route's element (e.g., AdminPage)
};

function App() {
  return (
    <ErrorBoundary title="Application Error">
      <AuthProvider>
        <AgentProvider>
          <Router>
            <Routes>
              <Route element={<AppLayout />}>
                {' '}
                {/* AppLayout wraps all pages */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/signup" element={<SignUpPage />} />
                <Route path="/" element={<HomePage />} />
                {/* Protected Routes */}
                <Route element={<ProtectedRoute />}>
                                  <Route path="/main" element={<MainPage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/new-case" element={<NewCasePage />} />
                <Route path="/profile" element={<ProfilePage />} />
                <Route path="/error-demo" element={<ErrorDemoPage />} />
                  <Route
                    path="/cases/:caseId"
                    element={<BusinessCaseDetailPageSimplified />}
                  />
                  <Route
                    path="/cases/:caseId/view"
                    element={<ReadOnlyCaseViewPage />}
                  />
                  <Route path="/admin" element={<AdminProtectedRoute />}>
                    <Route index element={<AdminPage />} />
                    <Route path=":adminAction" element={<AdminPage />} />
                  </Route>
                  {/* Add other protected routes here */}
                </Route>
                {/* Catch-all for unmatched routes (optional) */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Route>
            </Routes>
          </Router>
        </AgentProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;

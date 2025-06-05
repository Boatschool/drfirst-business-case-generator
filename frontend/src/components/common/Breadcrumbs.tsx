import React from 'react';
import {
  Breadcrumbs as MUIBreadcrumbs,
  Link,
  Typography,
  Box,
} from '@mui/material';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { useAgentContext } from '../../contexts/AgentContext';

interface BreadcrumbItem {
  label: string;
  path?: string;
  isCurrentPage?: boolean;
}

// Path-to-label mapping for static routes
const STATIC_ROUTE_LABELS: Record<string, string> = {
  '': 'Home',
  'dashboard': 'Dashboard',
  'new-case': 'New Case',
  'admin': 'Admin',
  'profile': 'Profile',
  'main': 'Main',
  'cases': 'Cases',
};

// Helper function to get case title from AgentContext
const useCaseTitle = (caseId?: string): string | null => {
  const { currentCaseDetails, cases } = useAgentContext();
  
  if (!caseId) return null;
  
  // First try to get from current case details if it matches
  if (currentCaseDetails?.case_id === caseId) {
    return currentCaseDetails.title || null;
  }
  
  // Fallback to cases list
  const caseFromList = cases.find(c => c.case_id === caseId);
  return caseFromList?.title || null;
};

const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  
  // Split pathname into segments and filter out empty strings
  const pathSegments = location.pathname.split('/').filter(Boolean);
  
  // Generate breadcrumb items
  const breadcrumbItems = React.useMemo((): BreadcrumbItem[] => {
    const items: BreadcrumbItem[] = [];
    
    // Always start with Home/Dashboard for authenticated pages
    items.push({
      label: 'Dashboard',
      path: '/dashboard',
    });
    
    // Build breadcrumbs for each path segment
    for (let i = 0; i < pathSegments.length; i++) {
      const segment = pathSegments[i];
      const isLast = i === pathSegments.length - 1;
      const pathUpToSegment = '/' + pathSegments.slice(0, i + 1).join('/');
      
      // Handle special cases for dynamic routes
      if (segment === 'cases' && pathSegments[i + 1]) {
        // For /cases/:caseId routes
        const caseId = pathSegments[i + 1];
        const caseTitle = useCaseTitle(caseId);
        
        // Add "Cases" if not already there
        if (!items.some(item => item.label === 'Cases')) {
          items.push({
            label: 'Cases',
            path: i === pathSegments.length - 2 ? undefined : '/dashboard', // Link to dashboard if not the final segment
          });
        }
        
        // Add the case title or ID
        const label = caseTitle || `Case ${caseId.substring(0, 8)}...`;
        const casePath = `/cases/${caseId}`;
        
        // Check if there's a "view" sub-path
        if (pathSegments[i + 2] === 'view') {
          // For /cases/:caseId/view
          items.push({
            label: label,
            path: casePath,
          });
          items.push({
            label: 'View',
            isCurrentPage: true,
          });
          break;
        } else {
          // For /cases/:caseId
          items.push({
            label: label,
            isCurrentPage: isLast,
            path: isLast ? undefined : casePath,
          });
          // Skip the caseId segment in next iteration
          i++;
        }
      } else if (segment === 'admin' && pathSegments[i + 1]) {
        // For /admin/:adminAction routes
        items.push({
          label: 'Admin',
          path: '/admin',
        });
        
        const adminAction = pathSegments[i + 1];
        const actionLabel = adminAction
          .split('-')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
        
        items.push({
          label: actionLabel,
          isCurrentPage: true,
        });
        break;
      } else {
        // Handle standard static routes
        const label = STATIC_ROUTE_LABELS[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
        
        // Skip adding Dashboard if it's already there and we're on dashboard route
        if (segment === 'dashboard' && items.some(item => item.label === 'Dashboard')) {
          continue;
        }
        
        items.push({
          label: label,
          path: isLast ? undefined : pathUpToSegment,
          isCurrentPage: isLast,
        });
      }
    }
    
    return items;
  }, [location.pathname, pathSegments]);
  
  // Get case title for current route if applicable
  const currentCaseId = React.useMemo(() => {
    const caseMatch = location.pathname.match(/\/cases\/([^\/]+)/);
    return caseMatch ? caseMatch[1] : undefined;
  }, [location.pathname]);
  
  const caseTitle = useCaseTitle(currentCaseId);
  
  // Update breadcrumb items with case title if available
  const finalBreadcrumbItems = React.useMemo(() => {
    if (!caseTitle || !currentCaseId) return breadcrumbItems;
    
    return breadcrumbItems.map(item => {
      if (item.label.startsWith('Case ') && item.label.includes('...')) {
        return { ...item, label: caseTitle };
      }
      return item;
    });
  }, [breadcrumbItems, caseTitle, currentCaseId]);
  
  // Don't show breadcrumbs on login, signup, or home pages
  if (['/login', '/signup', '/', '/main'].includes(location.pathname)) {
    return null;
  }
  
  // Don't show if no meaningful breadcrumbs
  if (finalBreadcrumbItems.length <= 1) {
    return null;
  }
  
  return (
    <Box sx={{ mb: 2 }}>
      <MUIBreadcrumbs aria-label="breadcrumb">
        {finalBreadcrumbItems.map((item, index) => {
          if (item.isCurrentPage || !item.path) {
            return (
              <Typography key={index} color="text.primary">
                {item.label}
              </Typography>
            );
          }
          
          return (
            <Link
              key={index}
              component={RouterLink}
              to={item.path}
              underline="hover"
              color="inherit"
            >
              {item.label}
            </Link>
          );
        })}
      </MUIBreadcrumbs>
    </Box>
  );
};

export default Breadcrumbs; 
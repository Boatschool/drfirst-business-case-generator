/**
 * AdminPage component for managing rate cards and pricing templates
 * Currently provides read-only access to view existing data
 */

import React, { useState, useEffect, useContext } from 'react';
import { Navigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Alert,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Divider,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import { AdminPanelSettings, AccountBalanceWallet, PriceCheck } from '@mui/icons-material';
import { AuthContext } from '../contexts/AuthContext';
import { RateCard, PricingTemplate } from '../services/admin/AdminService';
import { HttpAdminAdapter } from '../services/admin/HttpAdminAdapter';

const AdminPage: React.FC = () => {
  const authContext = useContext(AuthContext);
  
  // Admin service instance
  const [adminService] = useState(() => new HttpAdminAdapter());
  
  // Rate Cards state
  const [rateCards, setRateCards] = useState<RateCard[]>([]);
  const [isLoadingRateCards, setIsLoadingRateCards] = useState(false);
  const [rateCardsError, setRateCardsError] = useState<string | null>(null);
  
  // Pricing Templates state
  const [pricingTemplates, setPricingTemplates] = useState<PricingTemplate[]>([]);
  const [isLoadingPricingTemplates, setIsLoadingPricingTemplates] = useState(false);
  const [pricingTemplatesError, setPricingTemplatesError] = useState<string | null>(null);

  // Simple admin check (placeholder for full RBAC in Task 7.3)
  // For now, allow any authenticated user to access admin page
  // TODO: Replace with proper role-based access control
  if (!authContext?.currentUser) {
    return <Navigate to="/login" replace />;
  }

  // Fetch rate cards
  const fetchRateCards = async () => {
    setIsLoadingRateCards(true);
    setRateCardsError(null);
    
    try {
      const cards = await adminService.listRateCards();
      setRateCards(cards);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch rate cards';
      setRateCardsError(errorMessage);
      console.error('Error fetching rate cards:', error);
    } finally {
      setIsLoadingRateCards(false);
    }
  };

  // Fetch pricing templates
  const fetchPricingTemplates = async () => {
    setIsLoadingPricingTemplates(true);
    setPricingTemplatesError(null);
    
    try {
      const templates = await adminService.listPricingTemplates();
      setPricingTemplates(templates);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch pricing templates';
      setPricingTemplatesError(errorMessage);
      console.error('Error fetching pricing templates:', error);
    } finally {
      setIsLoadingPricingTemplates(false);
    }
  };

  // Load data on component mount
  useEffect(() => {
    fetchRateCards();
    fetchPricingTemplates();
  }, []);

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
          <AdminPanelSettings sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Admin Dashboard
          </Typography>
        </Box>

        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Manage rate cards and pricing templates for business case financial calculations.
        </Typography>

        <Grid container spacing={4}>
          {/* Rate Cards Section */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <AccountBalanceWallet sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h5" component="h2">
                  Rate Cards
                </Typography>
              </Box>

              {isLoadingRateCards && (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              )}

              {rateCardsError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {rateCardsError}
                </Alert>
              )}

              {!isLoadingRateCards && !rateCardsError && rateCards.length === 0 && (
                <Alert severity="info">
                  No rate cards found. Rate cards are used to calculate project costs based on role-specific hourly rates.
                </Alert>
              )}

              {!isLoadingRateCards && !rateCardsError && rateCards.length > 0 && (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Default Rate</TableCell>
                        <TableCell>Roles</TableCell>
                        <TableCell>Last Updated</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {rateCards.map((rateCard) => (
                        <TableRow key={rateCard.id}>
                          <TableCell>
                            <Typography variant="subtitle2" fontWeight="bold">
                              {rateCard.name}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {rateCard.description}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={rateCard.isActive ? 'Active' : 'Inactive'}
                              color={rateCard.isActive ? 'success' : 'default'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              ${rateCard.defaultOverallRate}/hour
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {rateCard.roles.length} role{rateCard.roles.length !== 1 ? 's' : ''}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {new Date(rateCard.updated_at).toLocaleDateString()}
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Paper>
          </Grid>

          {/* Pricing Templates Section */}
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <PriceCheck sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h5" component="h2">
                  Pricing Templates
                </Typography>
              </Box>

              {isLoadingPricingTemplates && (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                  <CircularProgress />
                </Box>
              )}

              {pricingTemplatesError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {pricingTemplatesError}
                </Alert>
              )}

              {!isLoadingPricingTemplates && !pricingTemplatesError && pricingTemplates.length === 0 && (
                <Alert severity="info">
                  No pricing templates found. Pricing templates are used to estimate business value and revenue projections.
                </Alert>
              )}

              {!isLoadingPricingTemplates && !pricingTemplatesError && pricingTemplates.length > 0 && (
                <Grid container spacing={2}>
                  {pricingTemplates.map((template) => (
                    <Grid item xs={12} md={6} key={template.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" component="h3" gutterBottom>
                            {template.name}
                          </Typography>
                          <Typography variant="body2" color="text.secondary" paragraph>
                            {template.description}
                          </Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="body2" color="text.secondary">
                              Version: {template.version}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Type: {template.structureDefinition.type}
                            </Typography>
                          </Box>
                          {template.structureDefinition.scenarios && (
                            <Box sx={{ mt: 2 }}>
                              <Typography variant="body2" fontWeight="bold" gutterBottom>
                                Scenarios: {template.structureDefinition.scenarios.length}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                {template.structureDefinition.scenarios.map((scenario, index) => (
                                  <Chip
                                    key={index}
                                    label={`${scenario.case}: $${scenario.value.toLocaleString()}`}
                                    size="small"
                                    variant="outlined"
                                  />
                                ))}
                              </Box>
                            </Box>
                          )}
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                            Last updated: {new Date(template.updated_at).toLocaleDateString()}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default AdminPage; 
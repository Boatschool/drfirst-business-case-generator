/**
 * AdminPage component for managing rate cards and pricing templates
 * Provides full CRUD operations for rate cards and read-only access to pricing templates
 */

import React, { useState, useEffect, useContext, useCallback } from 'react';
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
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,
  Stack,
  Tooltip,
  Snackbar,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  AdminPanelSettings,
  AccountBalanceWallet,
  PriceCheck,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { AuthContext } from '../contexts/AuthContext';
import { RateCard, PricingTemplate, CreateRateCardRequest, UpdateRateCardRequest } from '../services/admin/AdminService';
import { HttpAdminAdapter } from '../services/admin/HttpAdminAdapter';

interface RoleFormData {
  roleName: string;
  hourlyRate: number;
}

interface RateCardFormData {
  name: string;
  description: string;
  isActive: boolean;
  defaultOverallRate: number;
  roles: RoleFormData[];
}

interface RateCardFormErrors {
  name?: string;
  description?: string;
  defaultOverallRate?: string;
  roles?: string;
}

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

  // Modal states
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedRateCard, setSelectedRateCard] = useState<RateCard | null>(null);

  // Form states
  const [formData, setFormData] = useState<RateCardFormData>({
    name: '',
    description: '',
    isActive: true,
    defaultOverallRate: 100,
    roles: []
  });
  const [formErrors, setFormErrors] = useState<RateCardFormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Notification states
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'success'
  });

  // Simple admin check (placeholder for full RBAC in Task 7.3)
  // For now, allow any authenticated user to access admin page
  // TODO: Replace with proper role-based access control
  if (!authContext?.currentUser) {
    return <Navigate to="/login" replace />;
  }

  // Fetch rate cards
  const fetchRateCards = useCallback(async () => {
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
  }, [adminService]);

  // Fetch pricing templates
  const fetchPricingTemplates = useCallback(async () => {
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
  }, [adminService]);

  // Load data on component mount
  useEffect(() => {
    fetchRateCards();
    fetchPricingTemplates();
  }, [fetchRateCards, fetchPricingTemplates]);

  // Show notification
  const showNotification = (message: string, severity: 'success' | 'error' | 'info' | 'warning' = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  // Close notification
  const closeNotification = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  // Reset form data
  const resetFormData = () => {
    setFormData({
      name: '',
      description: '',
      isActive: true,
      defaultOverallRate: 100,
      roles: []
    });
    setFormErrors({});
  };

  // Validate form data
  const validateFormData = (data: RateCardFormData): RateCardFormErrors => {
    const errors: RateCardFormErrors = {};

    if (!data.name.trim()) {
      errors.name = 'Name is required';
    } else if (data.name.length > 100) {
      errors.name = 'Name must be 100 characters or less';
    }

    if (!data.description.trim()) {
      errors.description = 'Description is required';
    } else if (data.description.length > 500) {
      errors.description = 'Description must be 500 characters or less';
    }

    if (data.defaultOverallRate <= 0) {
      errors.defaultOverallRate = 'Default rate must be greater than 0';
    }

    // Validate roles
    const roleNames = new Set<string>();
    for (const role of data.roles) {
      if (!role.roleName.trim()) {
        errors.roles = 'Role name is required';
        break;
      }
      if (roleNames.has(role.roleName)) {
        errors.roles = 'Duplicate role names are not allowed';
        break;
      }
      if (role.hourlyRate <= 0) {
        errors.roles = 'Hourly rates must be greater than 0';
        break;
      }
      roleNames.add(role.roleName);
    }

    return errors;
  };

  // Handle create rate card
  const handleCreateRateCard = () => {
    resetFormData();
    setCreateModalOpen(true);
  };

  // Handle edit rate card
  const handleEditRateCard = (rateCard: RateCard) => {
    setSelectedRateCard(rateCard);
    setFormData({
      name: rateCard.name,
      description: rateCard.description,
      isActive: rateCard.isActive,
      defaultOverallRate: rateCard.defaultOverallRate,
      roles: rateCard.roles.map(role => ({ ...role }))
    });
    setFormErrors({});
    setEditModalOpen(true);
  };

  // Handle delete rate card
  const handleDeleteRateCard = (rateCard: RateCard) => {
    setSelectedRateCard(rateCard);
    setDeleteDialogOpen(true);
  };

  // Submit create form
  const handleSubmitCreate = async () => {
    const errors = validateFormData(formData);
    setFormErrors(errors);

    if (Object.keys(errors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      const createData: CreateRateCardRequest = {
        name: formData.name,
        description: formData.description,
        isActive: formData.isActive,
        defaultOverallRate: formData.defaultOverallRate,
        roles: formData.roles
      };

      await adminService.createRateCard(createData);
      showNotification('Rate card created successfully!');
      setCreateModalOpen(false);
      resetFormData();
      await fetchRateCards(); // Refresh the list
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create rate card';
      showNotification(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Submit edit form
  const handleSubmitEdit = async () => {
    if (!selectedRateCard) return;

    const errors = validateFormData(formData);
    setFormErrors(errors);

    if (Object.keys(errors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      const updateData: UpdateRateCardRequest = {
        name: formData.name,
        description: formData.description,
        isActive: formData.isActive,
        defaultOverallRate: formData.defaultOverallRate,
        roles: formData.roles
      };

      await adminService.updateRateCard(selectedRateCard.id, updateData);
      showNotification('Rate card updated successfully!');
      setEditModalOpen(false);
      setSelectedRateCard(null);
      resetFormData();
      await fetchRateCards(); // Refresh the list
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update rate card';
      showNotification(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Confirm delete
  const handleConfirmDelete = async () => {
    if (!selectedRateCard) return;

    setIsSubmitting(true);
    try {
      await adminService.deleteRateCard(selectedRateCard.id);
      showNotification(`Rate card "${selectedRateCard.name}" deleted successfully!`);
      setDeleteDialogOpen(false);
      setSelectedRateCard(null);
      await fetchRateCards(); // Refresh the list
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete rate card';
      showNotification(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle role changes
  const handleAddRole = () => {
    setFormData(prev => ({
      ...prev,
      roles: [...prev.roles, { roleName: '', hourlyRate: 100 }]
    }));
  };

  const handleRemoveRole = (index: number) => {
    setFormData(prev => ({
      ...prev,
      roles: prev.roles.filter((_, i) => i !== index)
    }));
  };

  const handleRoleChange = (index: number, field: keyof RoleFormData, value: string | number) => {
    setFormData(prev => ({
      ...prev,
      roles: prev.roles.map((role, i) => 
        i === index ? { ...role, [field]: value } : role
      )
    }));
  };

  // Close modals
  const handleCloseCreateModal = () => {
    setCreateModalOpen(false);
    resetFormData();
  };

  const handleCloseEditModal = () => {
    setEditModalOpen(false);
    setSelectedRateCard(null);
    resetFormData();
  };

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setSelectedRateCard(null);
  };

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
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <AccountBalanceWallet sx={{ mr: 2, color: 'primary.main' }} />
                  <Typography variant="h5" component="h2">
                    Rate Cards
                  </Typography>
                </Box>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleCreateRateCard}
                  disabled={isLoadingRateCards}
                >
                  Create New Rate Card
                </Button>
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
                  No rate cards found. Create your first rate card to get started with project cost calculations.
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
                        <TableCell align="center">Actions</TableCell>
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
                          <TableCell align="center">
                            <Stack direction="row" spacing={1}>
                              <Tooltip title="Edit rate card">
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditRateCard(rateCard)}
                                  disabled={isSubmitting}
                                >
                                  <EditIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Delete rate card">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteRateCard(rateCard)}
                                  disabled={isSubmitting}
                                  color="error"
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </Tooltip>
                            </Stack>
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

      {/* Create Rate Card Modal */}
      <Dialog
        open={createModalOpen}
        onClose={handleCloseCreateModal}
        maxWidth="md"
        fullWidth
        disableEscapeKeyDown={isSubmitting}
      >
        <DialogTitle>Create New Rate Card</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              error={!!formErrors.name}
              helperText={formErrors.name}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              error={!!formErrors.description}
              helperText={formErrors.description}
              fullWidth
              required
              multiline
              rows={3}
            />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Default Overall Rate"
                type="number"
                value={formData.defaultOverallRate}
                onChange={(e) => setFormData(prev => ({ ...prev, defaultOverallRate: parseFloat(e.target.value) || 0 }))}
                error={!!formErrors.defaultOverallRate}
                helperText={formErrors.defaultOverallRate}
                InputProps={{ inputProps: { min: 0.01, step: 0.01 } }}
                required
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.isActive}
                    onChange={(e) => setFormData(prev => ({ ...prev, isActive: e.target.checked }))}
                  />
                }
                label="Active"
              />
            </Box>
            
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Roles</Typography>
                <Button variant="outlined" size="small" onClick={handleAddRole}>
                  Add Role
                </Button>
              </Box>
              
              {formData.roles.length === 0 && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  No roles defined. Add roles to specify different hourly rates for different team members.
                </Typography>
              )}
              
              <List dense>
                {formData.roles.map((role, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <Box sx={{ display: 'flex', gap: 2, width: '100%', alignItems: 'flex-start' }}>
                      <TextField
                        label="Role Name"
                        value={role.roleName}
                        onChange={(e) => handleRoleChange(index, 'roleName', e.target.value)}
                        size="small"
                        sx={{ flex: 1 }}
                      />
                      <TextField
                        label="Hourly Rate"
                        type="number"
                        value={role.hourlyRate}
                        onChange={(e) => handleRoleChange(index, 'hourlyRate', parseFloat(e.target.value) || 0)}
                        InputProps={{ inputProps: { min: 0.01, step: 0.01 } }}
                        size="small"
                        sx={{ width: 120 }}
                      />
                      <IconButton
                        onClick={() => handleRemoveRole(index)}
                        size="small"
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </ListItem>
                ))}
              </List>
              
              {formErrors.roles && (
                <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                  Please check role data for errors
                </Typography>
              )}
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleCloseCreateModal}
            disabled={isSubmitting}
            startIcon={<CancelIcon />}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmitCreate}
            variant="contained"
            disabled={isSubmitting}
            startIcon={isSubmitting ? <CircularProgress size={20} /> : <SaveIcon />}
          >
            {isSubmitting ? 'Creating...' : 'Create Rate Card'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Rate Card Modal */}
      <Dialog
        open={editModalOpen}
        onClose={handleCloseEditModal}
        maxWidth="md"
        fullWidth
        disableEscapeKeyDown={isSubmitting}
      >
        <DialogTitle>Edit Rate Card</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              error={!!formErrors.name}
              helperText={formErrors.name}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              error={!!formErrors.description}
              helperText={formErrors.description}
              fullWidth
              required
              multiline
              rows={3}
            />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Default Overall Rate"
                type="number"
                value={formData.defaultOverallRate}
                onChange={(e) => setFormData(prev => ({ ...prev, defaultOverallRate: parseFloat(e.target.value) || 0 }))}
                error={!!formErrors.defaultOverallRate}
                helperText={formErrors.defaultOverallRate}
                InputProps={{ inputProps: { min: 0.01, step: 0.01 } }}
                required
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.isActive}
                    onChange={(e) => setFormData(prev => ({ ...prev, isActive: e.target.checked }))}
                  />
                }
                label="Active"
              />
            </Box>
            
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6">Roles</Typography>
                <Button variant="outlined" size="small" onClick={handleAddRole}>
                  Add Role
                </Button>
              </Box>
              
              {formData.roles.length === 0 && (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  No roles defined. Add roles to specify different hourly rates for different team members.
                </Typography>
              )}
              
              <List dense>
                {formData.roles.map((role, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <Box sx={{ display: 'flex', gap: 2, width: '100%', alignItems: 'flex-start' }}>
                      <TextField
                        label="Role Name"
                        value={role.roleName}
                        onChange={(e) => handleRoleChange(index, 'roleName', e.target.value)}
                        size="small"
                        sx={{ flex: 1 }}
                      />
                      <TextField
                        label="Hourly Rate"
                        type="number"
                        value={role.hourlyRate}
                        onChange={(e) => handleRoleChange(index, 'hourlyRate', parseFloat(e.target.value) || 0)}
                        InputProps={{ inputProps: { min: 0.01, step: 0.01 } }}
                        size="small"
                        sx={{ width: 120 }}
                      />
                      <IconButton
                        onClick={() => handleRemoveRole(index)}
                        size="small"
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </ListItem>
                ))}
              </List>
              
              {formErrors.roles && (
                <Typography variant="body2" color="error" sx={{ mt: 1 }}>
                  Please check role data for errors
                </Typography>
              )}
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleCloseEditModal}
            disabled={isSubmitting}
            startIcon={<CancelIcon />}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmitEdit}
            variant="contained"
            disabled={isSubmitting}
            startIcon={isSubmitting ? <CircularProgress size={20} /> : <SaveIcon />}
          >
            {isSubmitting ? 'Updating...' : 'Update Rate Card'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        disableEscapeKeyDown={isSubmitting}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the rate card "{selectedRateCard?.name}"?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This action cannot be undone. The rate card will be permanently removed from the system.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleCloseDeleteDialog}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDelete}
            variant="contained"
            color="error"
            disabled={isSubmitting}
            startIcon={isSubmitting ? <CircularProgress size={20} /> : <DeleteIcon />}
          >
            {isSubmitting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={closeNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={closeNotification} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default AdminPage; 
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  AdminPanelSettings,
  AccountBalanceWallet,
  PriceCheck,
  People as PeopleIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { AuthContext } from '../contexts/AuthContext';
import {
  RateCard,
  PricingTemplate,
  CreateRateCardRequest,
  UpdateRateCardRequest,
  CreatePricingTemplateRequest,
  UpdatePricingTemplateRequest,
  User,
} from '../services/admin/AdminService';
import { HttpAdminAdapter } from '../services/admin/HttpAdminAdapter';
import { TableSkeleton, LoadingButton, InlineLoading } from '../components/common/LoadingIndicators';
import useDocumentTitle from '../hooks/useDocumentTitle';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../styles/constants';
import Logger from '../utils/logger';

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

interface PricingTemplateFormData {
  name: string;
  description: string;
  version: string;
  structureDefinition: string; // JSON string for the form
}

interface PricingTemplateFormErrors {
  name?: string;
  description?: string;
  version?: string;
  structureDefinition?: string;
}

const logger = Logger.create('AdminPage');

const AdminPage: React.FC = () => {
  // Set document title
  useDocumentTitle('Admin');

  const authContext = useContext(AuthContext);

  // Admin service instance
  const [adminService] = useState(() => new HttpAdminAdapter());

  // Rate Cards state
  const [rateCards, setRateCards] = useState<RateCard[]>([]);
  const [isLoadingRateCards, setIsLoadingRateCards] = useState(false);
  const [rateCardsError, setRateCardsError] = useState<string | null>(null);

  // Pricing Templates state
  const [pricingTemplates, setPricingTemplates] = useState<PricingTemplate[]>(
    []
  );
  const [isLoadingPricingTemplates, setIsLoadingPricingTemplates] =
    useState(false);
  const [pricingTemplatesError, setPricingTemplatesError] = useState<
    string | null
  >(null);

  // Users state
  const [users, setUsers] = useState<User[]>([]);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [usersError, setUsersError] = useState<string | null>(null);

  // Modal states for Rate Cards
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedRateCard, setSelectedRateCard] = useState<RateCard | null>(
    null
  );

  // Modal states for Pricing Templates
  const [createTemplateModalOpen, setCreateTemplateModalOpen] = useState(false);
  const [editTemplateModalOpen, setEditTemplateModalOpen] = useState(false);
  const [deleteTemplateDialogOpen, setDeleteTemplateDialogOpen] =
    useState(false);
  const [selectedPricingTemplate, setSelectedPricingTemplate] =
    useState<PricingTemplate | null>(null);

  // Form states for Rate Cards
  const [formData, setFormData] = useState<RateCardFormData>({
    name: '',
    description: '',
    isActive: true,
    defaultOverallRate: 100,
    roles: [],
  });
  const [formErrors, setFormErrors] = useState<RateCardFormErrors>({});

  // Form states for Pricing Templates
  const [templateFormData, setTemplateFormData] =
    useState<PricingTemplateFormData>({
      name: '',
      description: '',
      version: '1.0',
      structureDefinition: JSON.stringify(
        {
          type: 'LowBaseHigh',
          scenarios: [
            { case: 'low', value: 5000, description: 'Conservative estimate' },
            { case: 'base', value: 15000, description: 'Most likely scenario' },
            { case: 'high', value: 30000, description: 'Optimistic scenario' },
          ],
        },
        null,
        2
      ),
    });
  const [templateFormErrors, setTemplateFormErrors] =
    useState<PricingTemplateFormErrors>({});

  const [isSubmitting, setIsSubmitting] = useState(false);

  // Notification states
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info' | 'warning';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Global Approver Configuration state
  const [finalApproverRoleName, setFinalApproverRoleName] = useState<string>('FINAL_APPROVER');
  const [isLoadingApproverConfig, setIsLoadingApproverConfig] = useState(false);
  const [approverConfigError, setApproverConfigError] = useState<string | null>(null);
  const [selectedApproverRole, setSelectedApproverRole] = useState<string>('FINAL_APPROVER');
  const [isSavingApproverConfig, setIsSavingApproverConfig] = useState(false);

  // Fetch rate cards
  const fetchRateCards = useCallback(async () => {
    setIsLoadingRateCards(true);
    setRateCardsError(null);

    try {
      const cards = await adminService.listRateCards();
      setRateCards(cards);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to fetch rate cards';
      setRateCardsError(errorMessage);
      logger.error('Error fetching rate cards:', error);
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
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Failed to fetch pricing templates';
      setPricingTemplatesError(errorMessage);
      logger.error('Error fetching pricing templates:', error);
    } finally {
      setIsLoadingPricingTemplates(false);
    }
  }, [adminService]);

  // Fetch users
  const fetchUsers = useCallback(async () => {
    setIsLoadingUsers(true);
    setUsersError(null);

    try {
      const usersList = await adminService.listUsers();
      setUsers(usersList);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to fetch users';
      setUsersError(errorMessage);
      logger.error('Error fetching users:', error);
    } finally {
      setIsLoadingUsers(false);
    }
  }, [adminService]);

  // Fetch global approver configuration
  const fetchApproverConfig = useCallback(async () => {
    setIsLoadingApproverConfig(true);
    setApproverConfigError(null);

    try {
      const config = await adminService.getFinalApproverRoleSetting();
      setFinalApproverRoleName(config.finalApproverRoleName);
      setSelectedApproverRole(config.finalApproverRoleName);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to fetch approver configuration';
      setApproverConfigError(errorMessage);
      logger.error('Error fetching approver configuration:', error);
    } finally {
      setIsLoadingApproverConfig(false);
    }
  }, [adminService]);

  // Load data on component mount
  useEffect(() => {
    fetchRateCards();
    fetchPricingTemplates();
    fetchUsers();
    fetchApproverConfig();
  }, [fetchRateCards, fetchPricingTemplates, fetchUsers, fetchApproverConfig]);

  // Simple admin check (placeholder for full RBAC in Task 7.3)
  // For now, allow any authenticated user to access admin page
  // TODO: Replace with proper role-based access control
  if (!authContext?.currentUser) {
    return <Navigate to="/login" replace />;
  }

  // Show admin role information and access status
  const userRole = authContext.systemRole || 'USER';
  const isAdminUser = authContext.isAdmin;

  logger.debug('AdminPage - User role info:', {
    email: authContext.currentUser?.email,
    systemRole: authContext.systemRole,
    isAdmin: authContext.isAdmin,
    hasAdminAccess: isAdminUser,
  });

  // Show notification
  const showNotification = (
    message: string,
    severity: 'success' | 'error' | 'info' | 'warning' = 'success'
  ) => {
    setSnackbar({ open: true, message, severity });
  };

  // Close notification
  const closeNotification = () => {
    setSnackbar((prev) => ({ ...prev, open: false }));
  };

  // Reset form data for Rate Cards
  const resetFormData = () => {
    setFormData({
      name: '',
      description: '',
      isActive: true,
      defaultOverallRate: 100,
      roles: [],
    });
    setFormErrors({});
  };

  // Reset form data for Pricing Templates
  const resetTemplateFormData = () => {
    setTemplateFormData({
      name: '',
      description: '',
      version: '1.0',
      structureDefinition: JSON.stringify(
        {
          type: 'LowBaseHigh',
          scenarios: [
            { case: 'low', value: 5000, description: 'Conservative estimate' },
            { case: 'base', value: 15000, description: 'Most likely scenario' },
            { case: 'high', value: 30000, description: 'Optimistic scenario' },
          ],
        },
        null,
        2
      ),
    });
    setTemplateFormErrors({});
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
      roles: rateCard.roles.map((role) => ({ ...role })),
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
        roles: formData.roles,
      };

      await adminService.createRateCard(createData);
      showNotification('Rate card created successfully!');
      setCreateModalOpen(false);
      resetFormData();
      await fetchRateCards(); // Refresh the list
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to create rate card';
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
        roles: formData.roles,
      };

      await adminService.updateRateCard(selectedRateCard.id, updateData);
      showNotification('Rate card updated successfully!');
      setEditModalOpen(false);
      setSelectedRateCard(null);
      resetFormData();
      await fetchRateCards(); // Refresh the list
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update rate card';
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
      showNotification(
        `Rate card "${selectedRateCard.name}" deleted successfully!`
      );
      setDeleteDialogOpen(false);
      setSelectedRateCard(null);
      await fetchRateCards(); // Refresh the list
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to delete rate card';
      showNotification(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle role changes
  const handleAddRole = () => {
    setFormData((prev) => ({
      ...prev,
      roles: [...prev.roles, { roleName: '', hourlyRate: 100 }],
    }));
  };

  const handleRemoveRole = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      roles: prev.roles.filter((_, i) => i !== index),
    }));
  };

  const handleRoleChange = (
    index: number,
    field: keyof RoleFormData,
    value: string | number
  ) => {
    setFormData((prev) => ({
      ...prev,
      roles: prev.roles.map((role, i) =>
        i === index ? { ...role, [field]: value } : role
      ),
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

  // Validate form data for Pricing Templates
  const validateTemplateFormData = (
    data: PricingTemplateFormData
  ): PricingTemplateFormErrors => {
    const errors: PricingTemplateFormErrors = {};

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

    if (!data.version.trim()) {
      errors.version = 'Version is required';
    } else if (data.version.length > 20) {
      errors.version = 'Version must be 20 characters or less';
    }

    if (!data.structureDefinition.trim()) {
      errors.structureDefinition = 'Structure definition is required';
    } else {
      try {
        JSON.parse(data.structureDefinition);
      } catch (e) {
        errors.structureDefinition = 'Structure definition must be valid JSON';
      }
    }

    return errors;
  };

  // Pricing Template Handlers
  const handleCreatePricingTemplate = () => {
    resetTemplateFormData();
    setCreateTemplateModalOpen(true);
  };

  const handleEditPricingTemplate = (template: PricingTemplate) => {
    setSelectedPricingTemplate(template);
    setTemplateFormData({
      name: template.name,
      description: template.description,
      version: template.version,
      structureDefinition: JSON.stringify(
        template.structureDefinition,
        null,
        2
      ),
    });
    setTemplateFormErrors({});
    setEditTemplateModalOpen(true);
  };

  const handleDeletePricingTemplate = (template: PricingTemplate) => {
    setSelectedPricingTemplate(template);
    setDeleteTemplateDialogOpen(true);
  };

  const handleSubmitCreateTemplate = async () => {
    const errors = validateTemplateFormData(templateFormData);
    setTemplateFormErrors(errors);

    if (Object.keys(errors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      const createData: CreatePricingTemplateRequest = {
        name: templateFormData.name,
        description: templateFormData.description,
        version: templateFormData.version,
        structureDefinition: JSON.parse(templateFormData.structureDefinition),
      };

      await adminService.createPricingTemplate(createData);
      showNotification('Pricing template created successfully!');
      setCreateTemplateModalOpen(false);
      resetTemplateFormData();
      await fetchPricingTemplates(); // Refresh the list
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Failed to create pricing template';
      showNotification(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitEditTemplate = async () => {
    if (!selectedPricingTemplate) return;

    const errors = validateTemplateFormData(templateFormData);
    setTemplateFormErrors(errors);

    if (Object.keys(errors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      const updateData: UpdatePricingTemplateRequest = {
        name: templateFormData.name,
        description: templateFormData.description,
        version: templateFormData.version,
        structureDefinition: JSON.parse(templateFormData.structureDefinition),
      };

      await adminService.updatePricingTemplate(
        selectedPricingTemplate.id,
        updateData
      );
      showNotification('Pricing template updated successfully!');
      setEditTemplateModalOpen(false);
      setSelectedPricingTemplate(null);
      resetTemplateFormData();
      await fetchPricingTemplates(); // Refresh the list
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Failed to update pricing template';
      showNotification(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirmDeleteTemplate = async () => {
    if (!selectedPricingTemplate) return;

    setIsSubmitting(true);
    try {
      await adminService.deletePricingTemplate(selectedPricingTemplate.id);
      showNotification(
        `Pricing template "${selectedPricingTemplate.name}" deleted successfully!`
      );
      setDeleteTemplateDialogOpen(false);
      setSelectedPricingTemplate(null);
      await fetchPricingTemplates(); // Refresh the list
    } catch (error) {
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Failed to delete pricing template';
      showNotification(errorMessage, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCloseCreateTemplateModal = () => {
    setCreateTemplateModalOpen(false);
    resetTemplateFormData();
  };

  const handleCloseEditTemplateModal = () => {
    setEditTemplateModalOpen(false);
    setSelectedPricingTemplate(null);
    resetTemplateFormData();
  };

  const handleCloseDeleteTemplateDialog = () => {
    setDeleteTemplateDialogOpen(false);
    setSelectedPricingTemplate(null);
  };

  // Global Approver Configuration handlers
  const handleSaveApproverConfig = async () => {
    if (selectedApproverRole === finalApproverRoleName) {
      showNotification('No changes to save', 'info');
      return;
    }

    setIsSavingApproverConfig(true);
    setApproverConfigError(null);

    try {
      await adminService.setFinalApproverRoleSetting(selectedApproverRole);
      setFinalApproverRoleName(selectedApproverRole);
      showNotification(`Final approver role updated to '${selectedApproverRole}' successfully`, 'success');
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to update final approver role';
      setApproverConfigError(errorMessage);
      showNotification(errorMessage, 'error');
    } finally {
      setIsSavingApproverConfig(false);
    }
  };



  return (
    <Container maxWidth="lg" sx={STANDARD_STYLES.pageContainer}>
      <Box>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
          <AdminPanelSettings sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Admin Dashboard
          </Typography>
        </Box>

        {/* Admin Role Status */}
        <Alert severity={isAdminUser ? 'success' : 'warning'} sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Access Status:</strong>{' '}
            {isAdminUser ? '✅ Admin Access Granted' : '⚠️ Limited Access'}
            &nbsp;|&nbsp;
            <strong>Role:</strong> {userRole}
            &nbsp;|&nbsp;
            <strong>User:</strong> {authContext.currentUser?.email}
          </Typography>
          {!isAdminUser && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Note: Some admin features may be restricted. Contact an
              administrator to request ADMIN role assignment.
            </Typography>
          )}
        </Alert>

        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Manage rate cards and pricing templates for business case financial
          calculations.
        </Typography>

        <Grid container spacing={4}>
          {/* Global Approval Settings Section */}
          <Grid item xs={12}>
            <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <SettingsIcon sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h5" component="h2">
                  Global Approval Settings
                </Typography>
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Configure which system role is used for final business case approvals across the application.
              </Typography>

              {isLoadingApproverConfig && (
                <InlineLoading message="Loading approver configuration..." size={24} />
              )}

              {approverConfigError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {approverConfigError}
                </Alert>
              )}

              {!isLoadingApproverConfig && (
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Typography variant="body2">
                      <strong>Current Final Approver Role:</strong>
                    </Typography>
                    <Chip
                      label={finalApproverRoleName}
                      color="primary"
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  </Box>

                  <Stack direction="row" spacing={2} alignItems="center" sx={{ mt: 2 }}>
                    <FormControl sx={{ minWidth: 200 }}>
                      <InputLabel id="approver-role-select-label">Final Approver Role</InputLabel>
                      <Select
                        labelId="approver-role-select-label"
                        value={selectedApproverRole}
                        label="Final Approver Role"
                        onChange={(e) => setSelectedApproverRole(e.target.value as string)}
                        disabled={isSavingApproverConfig}
                      >
                        <MenuItem value="ADMIN">ADMIN</MenuItem>
                        <MenuItem value="DEVELOPER">DEVELOPER</MenuItem>
                        <MenuItem value="SALES_MANAGER_APPROVER">SALES_MANAGER_APPROVER</MenuItem>
                        <MenuItem value="FINAL_APPROVER">FINAL_APPROVER</MenuItem>
                        <MenuItem value="CASE_INITIATOR">CASE_INITIATOR</MenuItem>
                      </Select>
                    </FormControl>

                    <LoadingButton
                      variant="contained"
                      onClick={handleSaveApproverConfig}
                      disabled={selectedApproverRole === finalApproverRoleName}
                      loading={isSavingApproverConfig}
                      loadingText="Saving..."
                      startIcon={<SaveIcon />}
                    >
                      Save Setting
                    </LoadingButton>
                  </Stack>

                  <Alert severity="warning" sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      <strong>Important:</strong> Changing this setting affects ALL business case final approvals.
                      Only users with the selected role will be able to approve or reject final business cases.
                    </Typography>
                  </Alert>
                </Box>
              )}
            </Paper>
          </Grid>
          {/* Rate Cards Section */}
          <Grid item xs={12}>
            <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 3,
                }}
              >
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
                <TableSkeleton rows={5} columns={7} />
              )}

              {rateCardsError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {rateCardsError}
                </Alert>
              )}

              {!isLoadingRateCards &&
                !rateCardsError &&
                rateCards.length === 0 && (
                  <Alert severity="info">
                    No rate cards found. Create your first rate card to get
                    started with project cost calculations.
                  </Alert>
                )}

              {!isLoadingRateCards &&
                !rateCardsError &&
                rateCards.length > 0 && (
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
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                {rateCard.description}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Chip
                                label={
                                  rateCard.isActive ? 'Active' : 'Inactive'
                                }
                                color={
                                  rateCard.isActive ? 'success' : 'default'
                                }
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
                                {rateCard.roles.length} role
                                {rateCard.roles.length !== 1 ? 's' : ''}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                {new Date(
                                  rateCard.updated_at
                                ).toLocaleDateString()}
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
                                    onClick={() =>
                                      handleDeleteRateCard(rateCard)
                                    }
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
            <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 3,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PriceCheck sx={{ mr: 2, color: 'primary.main' }} />
                  <Typography variant="h5" component="h2">
                    Pricing Templates
                  </Typography>
                </Box>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={handleCreatePricingTemplate}
                  disabled={isLoadingPricingTemplates}
                >
                  Create New Pricing Template
                </Button>
              </Box>

              {isLoadingPricingTemplates && (
                <Box sx={{ p: 2 }}>
                  <InlineLoading message="Loading pricing templates..." />
                </Box>
              )}

              {pricingTemplatesError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {pricingTemplatesError}
                </Alert>
              )}

              {!isLoadingPricingTemplates &&
                !pricingTemplatesError &&
                pricingTemplates.length === 0 && (
                  <Alert severity="info">
                    No pricing templates found. Pricing templates are used to
                    estimate business value and revenue projections.
                  </Alert>
                )}

              {!isLoadingPricingTemplates &&
                !pricingTemplatesError &&
                pricingTemplates.length > 0 && (
                  <Grid container spacing={2}>
                    {pricingTemplates.map((template) => (
                      <Grid item xs={12} md={6} key={template.id}>
                        <Card variant="outlined">
                          <CardContent>
                            <Box
                              sx={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'flex-start',
                                mb: 2,
                              }}
                            >
                              <Typography
                                variant="h6"
                                component="h3"
                                gutterBottom
                              >
                                {template.name}
                              </Typography>
                              <Stack direction="row" spacing={1}>
                                <Tooltip title="Edit pricing template">
                                  <IconButton
                                    size="small"
                                    onClick={() =>
                                      handleEditPricingTemplate(template)
                                    }
                                    disabled={isSubmitting}
                                  >
                                    <EditIcon />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Delete pricing template">
                                  <IconButton
                                    size="small"
                                    onClick={() =>
                                      handleDeletePricingTemplate(template)
                                    }
                                    disabled={isSubmitting}
                                    color="error"
                                  >
                                    <DeleteIcon />
                                  </IconButton>
                                </Tooltip>
                              </Stack>
                            </Box>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              paragraph
                            >
                              {template.description}
                            </Typography>
                            <Box
                              sx={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                mb: 1,
                              }}
                            >
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                Version: {template.version}
                              </Typography>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                Type: {template.structureDefinition.type}
                              </Typography>
                            </Box>
                            {template.structureDefinition.scenarios && (
                              <Box sx={{ mt: 2 }}>
                                <Typography
                                  variant="body2"
                                  fontWeight="bold"
                                  gutterBottom
                                >
                                  Scenarios:{' '}
                                  {
                                    template.structureDefinition.scenarios
                                      .length
                                  }
                                </Typography>
                                <Box
                                  sx={{
                                    display: 'flex',
                                    gap: 1,
                                    flexWrap: 'wrap',
                                  }}
                                >
                                  {template.structureDefinition.scenarios.map(
                                    (scenario, index) => (
                                      <Chip
                                        key={index}
                                        label={`${
                                          scenario.case
                                        }: $${scenario.value.toLocaleString()}`}
                                        size="small"
                                        variant="outlined"
                                      />
                                    )
                                  )}
                                </Box>
                              </Box>
                            )}
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ display: 'block', mt: 2 }}
                            >
                              Last updated:{' '}
                              {new Date(
                                template.updated_at
                              ).toLocaleDateString()}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                )}
            </Paper>
          </Grid>

          {/* Users Section */}
          <Grid item xs={12}>
            <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PeopleIcon sx={{ mr: 2, color: 'primary.main' }} />
                  <Typography variant="h5" component="h2">
                    User Management
                  </Typography>
                </Box>
              </Box>

              {isLoadingUsers && (
                <TableSkeleton rows={6} columns={6} />
              )}

              {usersError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {usersError}
                </Alert>
              )}

              {!isLoadingUsers && !usersError && users.length === 0 && (
                <Alert severity="info">No users found in the system.</Alert>
              )}

              {!isLoadingUsers && !usersError && users.length > 0 && (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>User ID</TableCell>
                        <TableCell>Email</TableCell>
                        <TableCell>Display Name</TableCell>
                        <TableCell>System Role</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Last Login</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {users.map((user) => (
                        <TableRow key={user.uid}>
                          <TableCell>
                            <Typography
                              variant="body2"
                              sx={{ fontFamily: 'monospace' }}
                            >
                              {user.uid}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="subtitle2" fontWeight="bold">
                              {user.email}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {user.display_name || 'N/A'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            {user.systemRole ? (
                              <Chip
                                label={user.systemRole}
                                color={
                                  user.systemRole === 'ADMIN'
                                    ? 'primary'
                                    : 'default'
                                }
                                size="small"
                              />
                            ) : (
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                No Role Assigned
                              </Typography>
                            )}
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={
                                user.is_active !== false ? 'Active' : 'Inactive'
                              }
                              color={
                                user.is_active !== false ? 'success' : 'default'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" color="text.secondary">
                              {user.last_login
                                ? new Date(user.last_login).toLocaleDateString()
                                : 'Never'}
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
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, name: e.target.value }))
              }
              error={!!formErrors.name}
              helperText={formErrors.name}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={formData.description}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
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
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    defaultOverallRate: parseFloat(e.target.value) || 0,
                  }))
                }
                error={!!formErrors.defaultOverallRate}
                helperText={formErrors.defaultOverallRate}
                InputProps={{ inputProps: { min: 0.01, step: 0.01 } }}
                required
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.isActive}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        isActive: e.target.checked,
                      }))
                    }
                  />
                }
                label="Active"
              />
            </Box>

            <Box>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 2,
                }}
              >
                <Typography variant="h6" component="h3">Roles</Typography>
                <Button variant="outlined" size="small" onClick={handleAddRole}>
                  Add Role
                </Button>
              </Box>

              {formData.roles.length === 0 && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  No roles defined. Add roles to specify different hourly rates
                  for different team members.
                </Typography>
              )}

              <List dense>
                {formData.roles.map((role, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        gap: 2,
                        width: '100%',
                        alignItems: 'flex-start',
                      }}
                    >
                      <TextField
                        label="Role Name"
                        value={role.roleName}
                        onChange={(e) =>
                          handleRoleChange(index, 'roleName', e.target.value)
                        }
                        size="small"
                        sx={{ flex: 1 }}
                      />
                      <TextField
                        label="Hourly Rate"
                        type="number"
                        value={role.hourlyRate}
                        onChange={(e) =>
                          handleRoleChange(
                            index,
                            'hourlyRate',
                            parseFloat(e.target.value) || 0
                          )
                        }
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
          <LoadingButton
            onClick={handleSubmitCreate}
            variant="contained"
            loading={isSubmitting}
            loadingText="Creating..."
            startIcon={<SaveIcon />}
          >
            Create Rate Card
          </LoadingButton>
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
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, name: e.target.value }))
              }
              error={!!formErrors.name}
              helperText={formErrors.name}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={formData.description}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
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
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    defaultOverallRate: parseFloat(e.target.value) || 0,
                  }))
                }
                error={!!formErrors.defaultOverallRate}
                helperText={formErrors.defaultOverallRate}
                InputProps={{ inputProps: { min: 0.01, step: 0.01 } }}
                required
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.isActive}
                    onChange={(e) =>
                      setFormData((prev) => ({
                        ...prev,
                        isActive: e.target.checked,
                      }))
                    }
                  />
                }
                label="Active"
              />
            </Box>

            <Box>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mb: 2,
                }}
              >
                <Typography variant="h6" component="h3">Roles</Typography>
                <Button variant="outlined" size="small" onClick={handleAddRole}>
                  Add Role
                </Button>
              </Box>

              {formData.roles.length === 0 && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  No roles defined. Add roles to specify different hourly rates
                  for different team members.
                </Typography>
              )}

              <List dense>
                {formData.roles.map((role, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        gap: 2,
                        width: '100%',
                        alignItems: 'flex-start',
                      }}
                    >
                      <TextField
                        label="Role Name"
                        value={role.roleName}
                        onChange={(e) =>
                          handleRoleChange(index, 'roleName', e.target.value)
                        }
                        size="small"
                        sx={{ flex: 1 }}
                      />
                      <TextField
                        label="Hourly Rate"
                        type="number"
                        value={role.hourlyRate}
                        onChange={(e) =>
                          handleRoleChange(
                            index,
                            'hourlyRate',
                            parseFloat(e.target.value) || 0
                          )
                        }
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
          <LoadingButton
            onClick={handleSubmitEdit}
            variant="contained"
            loading={isSubmitting}
            loadingText="Saving..."
            startIcon={<SaveIcon />}
          >
            Save Changes
          </LoadingButton>
        </DialogActions>
      </Dialog>

      {/* Delete Rate Card Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        disableEscapeKeyDown={isSubmitting}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the rate card "
            {selectedRateCard?.name}"?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This action cannot be undone. The rate card will be permanently
            removed from the system.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} disabled={isSubmitting}>
            Cancel
          </Button>
          <LoadingButton
            onClick={handleConfirmDelete}
            variant="contained"
            color="error"
            loading={isSubmitting}
            loadingText="Deleting..."
            startIcon={<DeleteIcon />}
          >
            Delete
          </LoadingButton>
        </DialogActions>
      </Dialog>

      {/* Create Pricing Template Modal */}
      <Dialog
        open={createTemplateModalOpen}
        onClose={handleCloseCreateTemplateModal}
        maxWidth="md"
        fullWidth
        disableEscapeKeyDown={isSubmitting}
      >
        <DialogTitle>Create New Pricing Template</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={templateFormData.name}
              onChange={(e) =>
                setTemplateFormData((prev) => ({
                  ...prev,
                  name: e.target.value,
                }))
              }
              error={!!templateFormErrors.name}
              helperText={templateFormErrors.name}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={templateFormData.description}
              onChange={(e) =>
                setTemplateFormData((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
              error={!!templateFormErrors.description}
              helperText={templateFormErrors.description}
              fullWidth
              required
              multiline
              rows={3}
            />
            <TextField
              label="Version"
              value={templateFormData.version}
              onChange={(e) =>
                setTemplateFormData((prev) => ({
                  ...prev,
                  version: e.target.value,
                }))
              }
              error={!!templateFormErrors.version}
              helperText={templateFormErrors.version}
              fullWidth
              required
            />
            <TextField
              label="Structure Definition (JSON)"
              value={templateFormData.structureDefinition}
              onChange={(e) =>
                setTemplateFormData((prev) => ({
                  ...prev,
                  structureDefinition: e.target.value,
                }))
              }
              error={!!templateFormErrors.structureDefinition}
              helperText={
                templateFormErrors.structureDefinition ||
                'Enter a valid JSON structure definition for the pricing template'
              }
              fullWidth
              required
              multiline
              rows={8}
              sx={{ fontFamily: 'monospace' }}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleCloseCreateTemplateModal}
            disabled={isSubmitting}
            startIcon={<CancelIcon />}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmitCreateTemplate}
            variant="contained"
            disabled={isSubmitting}
            startIcon={
              isSubmitting ? <CircularProgress size={20} /> : <SaveIcon />
            }
          >
            {isSubmitting ? 'Creating...' : 'Create Pricing Template'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Pricing Template Modal */}
      <Dialog
        open={editTemplateModalOpen}
        onClose={handleCloseEditTemplateModal}
        maxWidth="md"
        fullWidth
        disableEscapeKeyDown={isSubmitting}
      >
        <DialogTitle>Edit Pricing Template</DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={templateFormData.name}
              onChange={(e) =>
                setTemplateFormData((prev) => ({
                  ...prev,
                  name: e.target.value,
                }))
              }
              error={!!templateFormErrors.name}
              helperText={templateFormErrors.name}
              fullWidth
              required
            />
            <TextField
              label="Description"
              value={templateFormData.description}
              onChange={(e) =>
                setTemplateFormData((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
              error={!!templateFormErrors.description}
              helperText={templateFormErrors.description}
              fullWidth
              required
              multiline
              rows={3}
            />
            <TextField
              label="Version"
              value={templateFormData.version}
              onChange={(e) =>
                setTemplateFormData((prev) => ({
                  ...prev,
                  version: e.target.value,
                }))
              }
              error={!!templateFormErrors.version}
              helperText={templateFormErrors.version}
              fullWidth
              required
            />
            <TextField
              label="Structure Definition (JSON)"
              value={templateFormData.structureDefinition}
              onChange={(e) =>
                setTemplateFormData((prev) => ({
                  ...prev,
                  structureDefinition: e.target.value,
                }))
              }
              error={!!templateFormErrors.structureDefinition}
              helperText={
                templateFormErrors.structureDefinition ||
                'Enter a valid JSON structure definition for the pricing template'
              }
              fullWidth
              required
              multiline
              rows={8}
              sx={{ fontFamily: 'monospace' }}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleCloseEditTemplateModal}
            disabled={isSubmitting}
            startIcon={<CancelIcon />}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmitEditTemplate}
            variant="contained"
            disabled={isSubmitting}
            startIcon={
              isSubmitting ? <CircularProgress size={20} /> : <SaveIcon />
            }
          >
            {isSubmitting ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Pricing Template Confirmation Dialog */}
      <Dialog
        open={deleteTemplateDialogOpen}
        onClose={handleCloseDeleteTemplateDialog}
        disableEscapeKeyDown={isSubmitting}
      >
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the pricing template "
            {selectedPricingTemplate?.name}"?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This action cannot be undone. The pricing template will be
            permanently removed from the system.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleCloseDeleteTemplateDialog}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <LoadingButton
            onClick={handleConfirmDeleteTemplate}
            variant="contained"
            color="error"
            loading={isSubmitting}
            loadingText="Deleting..."
            startIcon={<DeleteIcon />}
          >
            Delete
          </LoadingButton>
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

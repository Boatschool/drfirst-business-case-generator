/**
 * PromptManagementPage component for managing agent prompts
 * Provides full CRUD operations for prompts and versions
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

  Chip,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControlLabel,
  Switch,

  Tooltip,
  Snackbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,

} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,

  ExpandMore as ExpandMoreIcon,

  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as InactiveIcon,

} from '@mui/icons-material';
import { AuthContext } from '../../contexts/AuthContext';
import {
  AgentPrompt,

  AgentPromptCreatePayload,
  AgentPromptUpdatePayload,
  AgentPromptVersionCreatePayload,
  HttpPromptServiceAdmin,
} from '../../services/admin/PromptServiceAdmin';
import { TableSkeleton, LoadingButton } from '../../components/common/LoadingIndicators';
import useDocumentTitle from '../../hooks/useDocumentTitle';
import { PAPER_ELEVATION } from '../../styles/constants';
import Logger from '../../utils/logger';

interface PromptFormData {
  agent_name: string;
  agent_function: string;
  title: string;
  description: string;
  prompt_template: string;
  category: string;
  placeholders: string[];
  version_description: string;
}

interface PromptFormErrors {
  agent_name?: string;
  agent_function?: string;
  title?: string;
  description?: string;
  prompt_template?: string;
  category?: string;
}

interface VersionFormData {
  prompt_template: string;
  description: string;
  placeholders: string[];
  make_active: boolean;
}

interface VersionFormErrors {
  prompt_template?: string;
  description?: string;
}

const logger = Logger.create('PromptManagementPage');

const PromptManagementPage: React.FC = () => {
  // Set document title
  useDocumentTitle('Prompt Management');

  const authContext = useContext(AuthContext);

  // Service instance
  const [promptService] = useState(() => new HttpPromptServiceAdmin());

  // Main data state
  const [prompts, setPrompts] = useState<AgentPrompt[]>([]);
  const [isLoadingPrompts, setIsLoadingPrompts] = useState(false);
  const [promptsError, setPromptsError] = useState<string | null>(null);

  // Filter state
  const [agentNameFilter, setAgentNameFilter] = useState<string>('');
  const [filteredPrompts, setFilteredPrompts] = useState<AgentPrompt[]>([]);

  // Modal states for Prompts
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [selectedPrompt, setSelectedPrompt] = useState<AgentPrompt | null>(null);

  // Modal states for Versions
  const [versionModalOpen, setVersionModalOpen] = useState(false);
  const [selectedPromptForVersion, setSelectedPromptForVersion] = useState<AgentPrompt | null>(null);

  // Form states for Prompts
  const [formData, setFormData] = useState<PromptFormData>({
    agent_name: '',
    agent_function: '',
    title: '',
    description: '',
    prompt_template: '',
    category: 'general',
    placeholders: [],
    version_description: 'Initial version',
  });
  const [formErrors, setFormErrors] = useState<PromptFormErrors>({});

  // Form states for Versions
  const [versionFormData, setVersionFormData] = useState<VersionFormData>({
    prompt_template: '',
    description: '',
    placeholders: [],
    make_active: false,
  });
  const [versionFormErrors, setVersionFormErrors] = useState<VersionFormErrors>({});

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

  // Helper functions
  const showNotification = useCallback((
    message: string,
    severity: 'success' | 'error' | 'info' | 'warning' = 'success'
  ) => {
    setSnackbar({
      open: true,
      message,
      severity,
    });
  }, []);

  const loadPrompts = useCallback(async () => {
    setIsLoadingPrompts(true);
    setPromptsError(null);
    try {
      const promptsData = await promptService.listPrompts();
      setPrompts(promptsData);
      logger.info('Loaded prompts successfully', { count: promptsData.length });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load prompts';
      setPromptsError(errorMessage);
      logger.error('Failed to load prompts', { error });
      showNotification(errorMessage, 'error');
    } finally {
      setIsLoadingPrompts(false);
    }
  }, [promptService, showNotification]);

  // Load prompts on component mount
  useEffect(() => {
    loadPrompts();
  }, [loadPrompts]);

  // Filter prompts when filter changes
  useEffect(() => {
    if (agentNameFilter) {
      setFilteredPrompts(prompts.filter(p => 
        p.agent_name.toLowerCase().includes(agentNameFilter.toLowerCase())
      ));
    } else {
      setFilteredPrompts(prompts);
    }
  }, [prompts, agentNameFilter]);

  // Check if user is authorized (admin role)
  if (!authContext?.currentUser || authContext.loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (!authContext.isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  const closeNotification = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  const resetFormData = () => {
    setFormData({
      agent_name: '',
      agent_function: '',
      title: '',
      description: '',
      prompt_template: '',
      category: 'general',
      placeholders: [],
      version_description: 'Initial version',
    });
    setFormErrors({});
  };

  const resetVersionFormData = () => {
    setVersionFormData({
      prompt_template: '',
      description: '',
      placeholders: [],
      make_active: false,
    });
    setVersionFormErrors({});
  };

  const validateFormData = (data: PromptFormData): PromptFormErrors => {
    const errors: PromptFormErrors = {};

    if (!data.agent_name.trim()) {
      errors.agent_name = 'Agent name is required';
    }

    if (!data.agent_function.trim()) {
      errors.agent_function = 'Agent function is required';
    }

    if (!data.title.trim()) {
      errors.title = 'Title is required';
    }

    if (!data.description.trim()) {
      errors.description = 'Description is required';
    }

    if (!data.prompt_template.trim()) {
      errors.prompt_template = 'Prompt template is required';
    }

    return errors;
  };

  const validateVersionFormData = (data: VersionFormData): VersionFormErrors => {
    const errors: VersionFormErrors = {};

    if (!data.prompt_template.trim()) {
      errors.prompt_template = 'Prompt template is required';
    }

    if (!data.description.trim()) {
      errors.description = 'Description is required';
    }

    return errors;
  };

  const handleCreatePrompt = () => {
    resetFormData();
    setCreateModalOpen(true);
  };

  const handleEditPrompt = (prompt: AgentPrompt) => {
    setSelectedPrompt(prompt);
    setEditModalOpen(true);
  };

  const handleAddVersion = (prompt: AgentPrompt) => {
    setSelectedPromptForVersion(prompt);
    resetVersionFormData();
    setVersionModalOpen(true);
  };

  const handleSubmitCreate = async () => {
    const errors = validateFormData(formData);
    setFormErrors(errors);

    if (Object.keys(errors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      const createData: AgentPromptCreatePayload = {
        agent_name: formData.agent_name,
        agent_function: formData.agent_function,
        title: formData.title,
        description: formData.description,
        prompt_template: formData.prompt_template,
        category: formData.category,
        placeholders: formData.placeholders,
        version_description: formData.version_description,
      };

      await promptService.createPrompt(createData);
      await loadPrompts();
      setCreateModalOpen(false);
      resetFormData();
      showNotification('Prompt created successfully');
      logger.info('Created prompt successfully', { agent_name: formData.agent_name });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create prompt';
      showNotification(errorMessage, 'error');
      logger.error('Failed to create prompt', { error });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitEdit = async () => {
    if (!selectedPrompt) return;

    setIsSubmitting(true);
    try {
      const updateData: AgentPromptUpdatePayload = {
        title: selectedPrompt.title,
        description: selectedPrompt.description,
        category: selectedPrompt.category,
        is_enabled: selectedPrompt.is_enabled,
      };

      await promptService.updatePrompt(selectedPrompt.prompt_id, updateData);
      await loadPrompts();
      setEditModalOpen(false);
      setSelectedPrompt(null);
      showNotification('Prompt updated successfully');
      logger.info('Updated prompt successfully', { prompt_id: selectedPrompt.prompt_id });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update prompt';
      showNotification(errorMessage, 'error');
      logger.error('Failed to update prompt', { error });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitVersion = async () => {
    if (!selectedPromptForVersion) return;

    const errors = validateVersionFormData(versionFormData);
    setVersionFormErrors(errors);

    if (Object.keys(errors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      const versionData: AgentPromptVersionCreatePayload = {
        prompt_template: versionFormData.prompt_template,
        description: versionFormData.description,
        placeholders: versionFormData.placeholders,
        make_active: versionFormData.make_active,
      };

      await promptService.addPromptVersion(selectedPromptForVersion.prompt_id, versionData);
      await loadPrompts();
      setVersionModalOpen(false);
      setSelectedPromptForVersion(null);
      resetVersionFormData();
      showNotification('Version added successfully');
      logger.info('Added version successfully', { 
        prompt_id: selectedPromptForVersion.prompt_id 
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to add version';
      showNotification(errorMessage, 'error');
      logger.error('Failed to add version', { error });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSetActiveVersion = async (prompt: AgentPrompt, version: string) => {
    try {
      await promptService.setActivePromptVersion(prompt.prompt_id, version);
      await loadPrompts();
      showNotification(`Version ${version} set as active`);
      logger.info('Set active version successfully', { 
        prompt_id: prompt.prompt_id, 
        version 
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to set active version';
      showNotification(errorMessage, 'error');
      logger.error('Failed to set active version', { error });
    }
  };

  const handleCloseCreateModal = () => {
    setCreateModalOpen(false);
    resetFormData();
  };

  const handleCloseEditModal = () => {
    setEditModalOpen(false);
    setSelectedPrompt(null);
  };

  const handleCloseVersionModal = () => {
    setVersionModalOpen(false);
    setSelectedPromptForVersion(null);
    resetVersionFormData();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getAvailableAgentNames = () => {
    const names = Array.from(new Set(prompts.map(p => p.agent_name))).sort();
    return names;
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Agent Prompt Management
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Manage AI agent prompts and their versions
        </Typography>
      </Box>

      {/* Filter and Action Bar */}
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Filter by Agent Name</InputLabel>
              <Select
                value={agentNameFilter}
                label="Filter by Agent Name"
                onChange={(e) => setAgentNameFilter(e.target.value)}
              >
                <MenuItem value="">All Agents</MenuItem>
                {getAvailableAgentNames().map((name) => (
                  <MenuItem key={name} value={name}>
                    {name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={8}>
            <Box display="flex" justifyContent="flex-end">
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleCreatePrompt}
              >
                Create New Prompt
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Main Content */}
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT}>
        {promptsError && (
          <Alert severity="error" sx={{ m: 2 }}>
            {promptsError}
          </Alert>
        )}

        {isLoadingPrompts ? (
          <TableSkeleton rows={5} columns={6} />
        ) : (
          <Box sx={{ p: 2 }}>
            {filteredPrompts.length === 0 ? (
              <Box textAlign="center" py={4}>
                <Typography variant="body1" color="text.secondary">
                  {agentNameFilter 
                    ? `No prompts found for agent "${agentNameFilter}"`
                    : 'No prompts found. Create your first prompt to get started.'
                  }
                </Typography>
              </Box>
            ) : (
              filteredPrompts.map((prompt) => (
                <Accordion key={prompt.prompt_id} sx={{ mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', pr: 2 }}>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6">{prompt.title}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {prompt.agent_name}.{prompt.agent_function} • {prompt.category}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Chip
                          size="small"
                          label={`v${prompt.current_version}`}
                          color="primary"
                        />
                        <Chip
                          size="small"
                          label={prompt.is_enabled ? 'Enabled' : 'Disabled'}
                          color={prompt.is_enabled ? 'success' : 'default'}
                        />
                        <Chip
                          size="small"
                          label={`${prompt.usage_count} uses`}
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={3}>
                      {/* Prompt Details */}
                      <Grid item xs={12} md={6}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Prompt Details
                            </Typography>
                            <Typography variant="body2" paragraph>
                              <strong>Description:</strong> {prompt.description}
                            </Typography>
                            <Typography variant="body2" paragraph>
                              <strong>Created:</strong> {formatDate(prompt.created_at)}
                            </Typography>
                            <Typography variant="body2" paragraph>
                              <strong>Last Updated:</strong> {formatDate(prompt.updated_at)}
                            </Typography>
                            {prompt.placeholders.length > 0 && (
                              <Typography variant="body2" paragraph>
                                <strong>Placeholders:</strong> {prompt.placeholders.join(', ')}
                              </Typography>
                            )}
                            <Box sx={{ mt: 2 }}>
                              <Button
                                size="small"
                                startIcon={<EditIcon />}
                                onClick={() => handleEditPrompt(prompt)}
                                sx={{ mr: 1 }}
                              >
                                Edit Metadata
                              </Button>
                              <Button
                                size="small"
                                startIcon={<AddIcon />}
                                onClick={() => handleAddVersion(prompt)}
                              >
                                Add Version
                              </Button>
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>

                      {/* Versions List */}
                      <Grid item xs={12} md={6}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Versions ({prompt.versions.length})
                            </Typography>
                            <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                              {prompt.versions
                                .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                                .map((version) => (
                                <Box key={version.version} sx={{ mb: 2, pb: 2, borderBottom: '1px solid #eee' }}>
                                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="subtitle2">
                                      Version {version.version}
                                    </Typography>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                      {version.is_active ? (
                                        <Tooltip title="Active Version">
                                          <CheckCircleIcon color="success" fontSize="small" />
                                        </Tooltip>
                                      ) : (
                                        <Tooltip title="Set as Active">
                                          <IconButton
                                            size="small"
                                            onClick={() => handleSetActiveVersion(prompt, version.version)}
                                          >
                                            <InactiveIcon fontSize="small" />
                                          </IconButton>
                                        </Tooltip>
                                      )}
                                    </Box>
                                  </Box>
                                  <Typography variant="body2" color="text.secondary" paragraph>
                                    {version.description}
                                  </Typography>
                                  <Typography variant="caption" color="text.secondary">
                                    Created: {formatDate(version.created_at)}
                                  </Typography>
                                </Box>
                              ))}
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))
            )}
          </Box>
        )}
      </Paper>

      {/* Create Prompt Modal */}
      <Dialog 
        open={createModalOpen} 
        onClose={handleCloseCreateModal}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create New Prompt</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Agent Name"
                value={formData.agent_name}
                onChange={(e) => setFormData({ ...formData, agent_name: e.target.value })}
                error={!!formErrors.agent_name}
                helperText={formErrors.agent_name}
                placeholder="e.g., BusinessCaseAgent"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Agent Function"
                value={formData.agent_function}
                onChange={(e) => setFormData({ ...formData, agent_function: e.target.value })}
                error={!!formErrors.agent_function}
                helperText={formErrors.agent_function}
                placeholder="e.g., generatePRD"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                error={!!formErrors.title}
                helperText={formErrors.title}
                placeholder="Human-readable title for this prompt"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                error={!!formErrors.description}
                helperText={formErrors.description}
                placeholder="What does this prompt do?"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category}
                  label="Category"
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                >
                  <MenuItem value="general">General</MenuItem>
                  <MenuItem value="prd_generation">PRD Generation</MenuItem>
                  <MenuItem value="system_design">System Design</MenuItem>
                  <MenuItem value="analysis">Analysis</MenuItem>
                  <MenuItem value="validation">Validation</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Version Description"
                value={formData.version_description}
                onChange={(e) => setFormData({ ...formData, version_description: e.target.value })}
                placeholder="Initial version"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Prompt Template"
                multiline
                rows={8}
                value={formData.prompt_template}
                onChange={(e) => setFormData({ ...formData, prompt_template: e.target.value })}
                error={!!formErrors.prompt_template}
                helperText={formErrors.prompt_template || "Use {{variable}} for placeholders"}
                placeholder="Enter your prompt template with {{placeholders}}"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCreateModal}>Cancel</Button>
          <LoadingButton
            onClick={handleSubmitCreate}
            loading={isSubmitting}
            variant="contained"
          >
            Create Prompt
          </LoadingButton>
        </DialogActions>
      </Dialog>

      {/* Edit Prompt Modal */}
      <Dialog 
        open={editModalOpen} 
        onClose={handleCloseEditModal}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Edit Prompt Metadata</DialogTitle>
        <DialogContent>
          {selectedPrompt && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Title"
                  value={selectedPrompt.title}
                  onChange={(e) => setSelectedPrompt({ 
                    ...selectedPrompt, 
                    title: e.target.value 
                  })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  multiline
                  rows={3}
                  value={selectedPrompt.description}
                  onChange={(e) => setSelectedPrompt({ 
                    ...selectedPrompt, 
                    description: e.target.value 
                  })}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={selectedPrompt.category}
                    label="Category"
                    onChange={(e) => setSelectedPrompt({ 
                      ...selectedPrompt, 
                      category: e.target.value 
                    })}
                  >
                    <MenuItem value="general">General</MenuItem>
                    <MenuItem value="prd_generation">PRD Generation</MenuItem>
                    <MenuItem value="system_design">System Design</MenuItem>
                    <MenuItem value="analysis">Analysis</MenuItem>
                    <MenuItem value="validation">Validation</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={selectedPrompt.is_enabled}
                      onChange={(e) => setSelectedPrompt({ 
                        ...selectedPrompt, 
                        is_enabled: e.target.checked 
                      })}
                    />
                  }
                  label="Enabled"
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditModal}>Cancel</Button>
          <LoadingButton
            onClick={handleSubmitEdit}
            loading={isSubmitting}
            variant="contained"
          >
            Update Prompt
          </LoadingButton>
        </DialogActions>
      </Dialog>

      {/* Add Version Modal */}
      <Dialog 
        open={versionModalOpen} 
        onClose={handleCloseVersionModal}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Add New Version</DialogTitle>
        <DialogContent>
          {selectedPromptForVersion && (
            <>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Adding version to: <strong>{selectedPromptForVersion.title}</strong>
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Version Description"
                    value={versionFormData.description}
                    onChange={(e) => setVersionFormData({ 
                      ...versionFormData, 
                      description: e.target.value 
                    })}
                    error={!!versionFormErrors.description}
                    helperText={versionFormErrors.description}
                    placeholder="What's new in this version?"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Prompt Template"
                    multiline
                    rows={10}
                    value={versionFormData.prompt_template}
                    onChange={(e) => setVersionFormData({ 
                      ...versionFormData, 
                      prompt_template: e.target.value 
                    })}
                    error={!!versionFormErrors.prompt_template}
                    helperText={versionFormErrors.prompt_template || "Use {{variable}} for placeholders"}
                    placeholder="Enter your prompt template with {{placeholders}}"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={versionFormData.make_active}
                        onChange={(e) => setVersionFormData({ 
                          ...versionFormData, 
                          make_active: e.target.checked 
                        })}
                      />
                    }
                    label="Make this version active immediately"
                  />
                </Grid>
              </Grid>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseVersionModal}>Cancel</Button>
          <LoadingButton
            onClick={handleSubmitVersion}
            loading={isSubmitting}
            variant="contained"
          >
            Add Version
          </LoadingButton>
        </DialogActions>
      </Dialog>

      {/* Notification Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={closeNotification}
      >
        <Alert onClose={closeNotification} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default PromptManagementPage; 
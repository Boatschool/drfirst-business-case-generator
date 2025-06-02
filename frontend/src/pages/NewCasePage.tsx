import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  TextField,
  Button,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Grid,
  IconButton,
  Paper,
} from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline';
import { useAgentContext } from '../contexts/AgentContext';
import { InitiateCasePayload } from '../services/agent/AgentService';

const NewCasePage: React.FC = () => {
  const [projectTitle, setProjectTitle] = useState('');
  const [problemStatement, setProblemStatement] = useState('');
  const [relevantLinks, setRelevantLinks] = useState<Array<{ name: string; url: string }>>([{ name: '', url: '' }]);
  const { initiateBusinessCase, isLoading, error } = useAgentContext();
  const navigate = useNavigate();

  const handleAddLink = () => {
    setRelevantLinks([...relevantLinks, { name: '', url: '' }]);
  };

  const handleRemoveLink = (index: number) => {
    const newLinks = relevantLinks.filter((_, i) => i !== index);
    setRelevantLinks(newLinks);
  };

  const handleLinkChange = (index: number, field: 'name' | 'url', value: string) => {
    const newLinks = relevantLinks.map((link, i) => 
      i === index ? { ...link, [field]: value } : link
    );
    setRelevantLinks(newLinks);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!projectTitle.trim() || !problemStatement.trim()) {
      // Basic validation, can be enhanced
      alert('Project Title and Problem Statement are required.');
      return;
    }

    const payload: InitiateCasePayload = {
      projectTitle,
      problemStatement,
      relevantLinks: relevantLinks.filter(link => link.name.trim() && link.url.trim()),
    };

    const response = await initiateBusinessCase(payload);
    if (response && response.caseId) {
      // Navigate to the dashboard or the new case detail page
      navigate('/dashboard'); // Or navigate(`/cases/${response.caseId}`);
    }
  };

  return (
    <Container component="main" maxWidth="md">
      <Paper elevation={3} sx={{ mt: 4, p: 3 }}>
        <Typography component="h1" variant="h4" gutterBottom align="center">
          Initiate New Business Case
        </Typography>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error.message || 'Failed to initiate business case.'}
          </Alert>
        )}
        <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="projectTitle"
            label="Project Title"
            name="projectTitle"
            autoFocus
            value={projectTitle}
            onChange={(e) => setProjectTitle(e.target.value)}
            disabled={isLoading}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="problemStatement"
            label="Problem Statement"
            name="problemStatement"
            multiline
            rows={4}
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
            disabled={isLoading}
          />

          <Typography variant="h6" sx={{ mt: 3, mb: 1 }}>
            Relevant Links (Optional)
          </Typography>
          {relevantLinks.map((link, index) => (
            <Grid container spacing={2} key={index} alignItems="center" sx={{ mb: 1 }}>
              <Grid item xs={12} sm={5}>
                <TextField
                  fullWidth
                  label="Link Name"
                  value={link.name}
                  onChange={(e) => handleLinkChange(index, 'name', e.target.value)}
                  disabled={isLoading}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Link URL"
                  value={link.url}
                  onChange={(e) => handleLinkChange(index, 'url', e.target.value)}
                  disabled={isLoading}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={1}>
                <IconButton onClick={() => handleRemoveLink(index)} disabled={isLoading || relevantLinks.length === 1 && index === 0 && !link.name && !link.url}>
                  <RemoveCircleOutlineIcon />
                </IconButton>
              </Grid>
            </Grid>
          ))}
          <Button
            startIcon={<AddCircleOutlineIcon />}
            onClick={handleAddLink}
            disabled={isLoading}
            sx={{ mt: 1 }}
          >
            Add Link
          </Button>

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2, py: 1.5 }}
            disabled={isLoading}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Initiate Case'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NewCasePage; 
import React, { useState, useMemo } from 'react';
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
  Tooltip,
  FormHelperText,
} from '@mui/material';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { useAgentContext } from '../contexts/AgentContext';
import { InitiateCasePayload } from '../services/agent/AgentService';
import { isNotEmpty, validateRelevantLink } from '../utils/validation';
import useDocumentTitle from '../hooks/useDocumentTitle';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../styles/constants';

interface FormErrors {
  projectTitle: string;
  problemStatement: string;
  relevantLinks: Array<{ name: string; url: string }>;
}

const NewCasePage: React.FC = () => {
  // Set document title
  useDocumentTitle('New Business Case');

  const [projectTitle, setProjectTitle] = useState('');
  const [problemStatement, setProblemStatement] = useState('');
  const [relevantLinks, setRelevantLinks] = useState<
    Array<{ name: string; url: string }>
  >([{ name: '', url: '' }]);
  const [touched, setTouched] = useState({
    projectTitle: false,
    problemStatement: false,
    relevantLinks: [false],
  });
  
  const { initiateBusinessCase, isLoading, error } = useAgentContext();
  const navigate = useNavigate();

  // Form validation logic
  const formErrors = useMemo((): FormErrors => {
    const errors: FormErrors = {
      projectTitle: '',
      problemStatement: '',
      relevantLinks: [],
    };

    // Validate project title
    if (touched.projectTitle && !isNotEmpty(projectTitle)) {
      errors.projectTitle = 'Project title is required';
    }

    // Validate problem statement
    if (touched.problemStatement && !isNotEmpty(problemStatement)) {
      errors.problemStatement = 'Problem statement is required';
    }

    // Validate relevant links
    relevantLinks.forEach((link, index) => {
      const hasAnyContent = link.name.trim() || link.url.trim();
      if (hasAnyContent && touched.relevantLinks[index]) {
        const validation = validateRelevantLink(link);
        errors.relevantLinks[index] = validation.errors;
      } else {
        errors.relevantLinks[index] = { name: '', url: '' };
      }
    });

    return errors;
  }, [projectTitle, problemStatement, relevantLinks, touched]);

  // Check if form is valid
  const isFormValid = useMemo(() => {
    // Check required fields
    if (!isNotEmpty(projectTitle) || !isNotEmpty(problemStatement)) {
      return false;
    }

    // Check relevant links - only validate if they have content
    for (let i = 0; i < relevantLinks.length; i++) {
      const link = relevantLinks[i];
      const hasAnyContent = link.name.trim() || link.url.trim();
      
      if (hasAnyContent) {
        const validation = validateRelevantLink(link);
        if (!validation.isValid) {
          return false;
        }
      }
    }

    return true;
  }, [projectTitle, problemStatement, relevantLinks]);

  const handleProjectTitleChange = (value: string) => {
    setProjectTitle(value);
    if (!touched.projectTitle) {
      setTouched(prev => ({ ...prev, projectTitle: true }));
    }
  };

  const handleProblemStatementChange = (value: string) => {
    setProblemStatement(value);
    if (!touched.problemStatement) {
      setTouched(prev => ({ ...prev, problemStatement: true }));
    }
  };

  const handleAddLink = () => {
    setRelevantLinks([...relevantLinks, { name: '', url: '' }]);
    setTouched(prev => ({
      ...prev,
      relevantLinks: [...prev.relevantLinks, false],
    }));
  };

  const handleRemoveLink = (index: number) => {
    const newLinks = relevantLinks.filter((_, i) => i !== index);
    const newTouched = touched.relevantLinks.filter((_, i) => i !== index);
    setRelevantLinks(newLinks);
    setTouched(prev => ({
      ...prev,
      relevantLinks: newTouched,
    }));
  };

  const handleLinkChange = (
    index: number,
    field: 'name' | 'url',
    value: string
  ) => {
    const newLinks = relevantLinks.map((link, i) =>
      i === index ? { ...link, [field]: value } : link
    );
    setRelevantLinks(newLinks);

    // Mark this link as touched
    if (!touched.relevantLinks[index]) {
      const newTouched = [...touched.relevantLinks];
      newTouched[index] = true;
      setTouched(prev => ({
        ...prev,
        relevantLinks: newTouched,
      }));
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    
    // Mark all fields as touched for validation display
    setTouched({
      projectTitle: true,
      problemStatement: true,
      relevantLinks: relevantLinks.map(() => true),
    });

    if (!isFormValid) {
      return;
    }

    const payload: InitiateCasePayload = {
      projectTitle,
      problemStatement,
      relevantLinks: relevantLinks.filter(
        (link) => link.name.trim() && link.url.trim()
      ),
    };

    const response = await initiateBusinessCase(payload);
    if (response && response.caseId) {
      // Navigate directly to the newly created case detail page
      navigate(`/cases/${response.caseId}`);
    }
  };

  return (
    <Container component="main" maxWidth="md" sx={STANDARD_STYLES.pageContainer}>
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
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
            placeholder="Enter a concise and descriptive title for your business case"
            value={projectTitle}
            onChange={(e) => handleProjectTitleChange(e.target.value)}
            onBlur={() => setTouched(prev => ({ ...prev, projectTitle: true }))}
            disabled={isLoading}
            error={touched.projectTitle && !!formErrors.projectTitle}
            helperText={touched.projectTitle ? formErrors.projectTitle : ''}
          />
          
          <Box sx={{ position: 'relative', mt: 2 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="problemStatement"
              label="Problem Statement"
              name="problemStatement"
              multiline
              rows={4}
              placeholder="Clearly describe the problem you are trying to solve, the opportunity, or the core idea. What pain points does this address? Who is affected?"
              value={problemStatement}
              onChange={(e) => handleProblemStatementChange(e.target.value)}
              onBlur={() => setTouched(prev => ({ ...prev, problemStatement: true }))}
              disabled={isLoading}
              error={touched.problemStatement && !!formErrors.problemStatement}
              helperText={touched.problemStatement ? formErrors.problemStatement : ''}
            />
            <Tooltip title="Provide a detailed description of the business problem or opportunity. Include background context, current pain points, target users or stakeholders, and the expected impact of solving this problem.">
              <IconButton
                size="small"
                sx={{
                  position: 'absolute',
                  top: 16,
                  right: 8,
                }}
              >
                <HelpOutlineIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>

          <Typography variant="h5" component="h2" sx={{ mt: 3, mb: 1 }}>
            Relevant Links (Optional)
          </Typography>
          <FormHelperText sx={{ mb: 2 }}>
            Add links to related documentation, Confluence pages, Jira tickets, or other resources that provide context for this business case.
          </FormHelperText>
          
          {relevantLinks.map((link, index) => (
            <Grid
              container
              spacing={2}
              key={index}
              alignItems="flex-start"
              sx={{ mb: 1 }}
            >
              <Grid item xs={12} sm={5}>
                <TextField
                  fullWidth
                  label="Link Name"
                  placeholder="e.g., Confluence Page, Jira Epic, Requirements Doc"
                  value={link.name}
                  onChange={(e) =>
                    handleLinkChange(index, 'name', e.target.value)
                  }
                  onBlur={() => {
                    if (!touched.relevantLinks[index]) {
                      const newTouched = [...touched.relevantLinks];
                      newTouched[index] = true;
                      setTouched(prev => ({
                        ...prev,
                        relevantLinks: newTouched,
                      }));
                    }
                  }}
                  disabled={isLoading}
                  size="small"
                  error={touched.relevantLinks[index] && !!formErrors.relevantLinks[index]?.name}
                  helperText={touched.relevantLinks[index] ? formErrors.relevantLinks[index]?.name : ''}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Link URL"
                  placeholder="https://your.confluence.link/..."
                  value={link.url}
                  onChange={(e) =>
                    handleLinkChange(index, 'url', e.target.value)
                  }
                  onBlur={() => {
                    if (!touched.relevantLinks[index]) {
                      const newTouched = [...touched.relevantLinks];
                      newTouched[index] = true;
                      setTouched(prev => ({
                        ...prev,
                        relevantLinks: newTouched,
                      }));
                    }
                  }}
                  disabled={isLoading}
                  size="small"
                  error={touched.relevantLinks[index] && !!formErrors.relevantLinks[index]?.url}
                  helperText={touched.relevantLinks[index] ? formErrors.relevantLinks[index]?.url : ''}
                />
              </Grid>
              <Grid item xs={12} sm={1}>
                <IconButton
                  onClick={() => handleRemoveLink(index)}
                  disabled={
                    isLoading ||
                    (relevantLinks.length === 1 &&
                      index === 0 &&
                      !link.name &&
                      !link.url)
                  }
                  sx={{ mt: 1 }}
                >
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
            disabled={isLoading || !isFormValid}
          >
            {isLoading ? <CircularProgress size={24} /> : 'Initiate Case'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default NewCasePage;

import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepButton,
  useTheme,
  useMediaQuery,
  Typography,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  RadioButtonUnchecked as RadioButtonUncheckedIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import {
  getWorkflowStageState,
  isStageAccessible,
  WorkflowStage,
} from '../../types/workflow';

interface ProgressStepperProps {
  currentCaseStatus: string;
  enableNavigation?: boolean;
}

const ProgressStepper: React.FC<ProgressStepperProps> = ({ 
  currentCaseStatus, 
  enableNavigation = true 
}) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const { caseId } = useParams<{ caseId: string }>();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const { activeStage, completedStages, allStages } = getWorkflowStageState(currentCaseStatus);
  
  const activeStepIndex = activeStage 
    ? allStages.findIndex(stage => stage.id === activeStage.id)
    : -1;

  const handleStepClick = (stage: WorkflowStage) => {
    if (!enableNavigation || !caseId || !isStageAccessible(stage, currentCaseStatus)) {
      return;
    }
    
    if (stage.routePath) {
      navigate(`/cases/${caseId}${stage.routePath}`);
    }
  };

  const getStepIcon = (stage: WorkflowStage) => {
    const isCompleted = completedStages.includes(stage);
    const isActive = activeStage?.id === stage.id;
    const isRejected = currentCaseStatus.includes('REJECTED') && isActive;
    
    if (isCompleted) {
      return <CheckCircleIcon color="primary" />;
    }
    
    if (isRejected) {
      return <CancelIcon color="error" />;
    }
    
    if (isActive) {
      return <RadioButtonUncheckedIcon color="primary" />;
    }
    
    return <RadioButtonUncheckedIcon color="disabled" />;
  };

  const getTooltipTitle = (stage: WorkflowStage) => {
    const isCompleted = completedStages.includes(stage);
    const isActive = activeStage?.id === stage.id;
    const isAccessible = isStageAccessible(stage, currentCaseStatus);
    const isRejected = currentCaseStatus.includes('REJECTED') && isActive;
    
    if (isRejected) {
      return `${stage.label} - Stage rejected. Click to review and make necessary changes.`;
    }
    
    if (isCompleted) {
      return `${stage.label} - Completed. Click to view details or make revisions.`;
    }
    
    if (isActive) {
      return `${stage.label} - Currently active. Click to continue working on this stage.`;
    }
    
    if (isAccessible) {
      return `${stage.label} - Available. Click to navigate to this stage.`;
    }
    
    return `${stage.label} - Not yet available. Complete previous stages first.`;
  };

  const getStepContent = (stage: WorkflowStage) => {
    const isCompleted = completedStages.includes(stage);
    const isActive = activeStage?.id === stage.id;
    const isAccessible = isStageAccessible(stage, currentCaseStatus);
    const isClickable = enableNavigation && isAccessible && stage.routePath;

    const stepContent = (
      <StepLabel
        StepIconComponent={() => getStepIcon(stage)}
        sx={{
          '& .MuiStepLabel-label': {
            fontSize: isMobile ? '0.75rem' : '0.875rem',
            fontWeight: 500,
            color: isCompleted || isActive 
              ? theme.palette.text.primary 
              : theme.palette.text.disabled,
            textAlign: 'center',
          },
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <Typography 
            variant={isMobile ? 'caption' : 'body2'} 
            component="span"
            sx={{ 
              display: 'block',
              fontWeight: 500,
              fontSize: isMobile ? '0.75rem' : '0.875rem',
              textAlign: 'center',
              lineHeight: 1.2,
            }}
          >
            {stage.label}
          </Typography>
          {!isMobile && (
            <Typography 
              variant="caption" 
              color="text.secondary"
              sx={{ 
                display: 'block', 
                mt: 0.5,
                fontSize: '0.75rem',
                fontWeight: 400,
                textAlign: 'center',
                lineHeight: 1.1,
              }}
            >
              {stage.description}
            </Typography>
          )}
        </Box>
      </StepLabel>
    );

    // Always wrap in tooltip for better user experience
    return (
      <Tooltip title={getTooltipTitle(stage)} arrow placement="top">
        {isClickable ? (
          <StepButton
            onClick={() => handleStepClick(stage)}
            sx={{
              '&:hover': {
                backgroundColor: 'action.hover',
              },
              cursor: 'pointer',
              textAlign: 'center',
            }}
          >
            {stepContent}
          </StepButton>
        ) : (
          <Box sx={{ cursor: isAccessible ? 'default' : 'not-allowed', textAlign: 'center' }}>
            {stepContent}
          </Box>
        )}
      </Tooltip>
    );
  };

  return (
    <Box sx={{ 
      width: '100%', 
      mb: 3,
      p: 2,
      backgroundColor: 'background.paper',
      borderRadius: 1,
      border: '1px solid',
      borderColor: 'divider',
    }}>
      <Typography 
        variant="h6" 
        component="h2" 
        gutterBottom 
        sx={{ 
          mb: 2,
          fontSize: isMobile ? '1rem' : '1.25rem',
          fontWeight: 600,
        }}
      >
        Business Case Progress
      </Typography>
      
      <Stepper
        activeStep={activeStepIndex}
        orientation={isMobile ? 'vertical' : 'horizontal'}
        sx={{
          '& .MuiStepConnector-root': {
            '& .MuiStepConnector-line': {
              borderColor: theme.palette.divider,
            },
          },
          '& .MuiStepConnector-active .MuiStepConnector-line': {
            borderColor: theme.palette.primary.main,
          },
          '& .MuiStepConnector-completed .MuiStepConnector-line': {
            borderColor: theme.palette.primary.main,
          },
        }}
      >
        {allStages.map((stage) => (
          <Step 
            key={stage.id}
            completed={completedStages.includes(stage)}
            active={activeStage?.id === stage.id}
          >
            {getStepContent(stage)}
          </Step>
        ))}
      </Stepper>
      
      {activeStage && (
        <Box sx={{ mt: 2, p: 2, backgroundColor: 'action.hover', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            <strong>Current Stage:</strong> {activeStage.label}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            <strong>Status:</strong> {currentCaseStatus.replace(/_/g, ' ')}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            <strong>Description:</strong> {activeStage.description}
          </Typography>
          {activeStage.routePath && caseId && (
            <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Action:</strong>
              </Typography>
              <Button
                size="small"
                variant="outlined"
                onClick={() => handleStepClick(activeStage)}
                sx={{ minHeight: 'auto', py: 0.5, px: 1 }}
              >
                Continue Work
              </Button>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default ProgressStepper; 
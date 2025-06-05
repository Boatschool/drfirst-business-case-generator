import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Box,
  Button,
  Divider,
  Stack,
  TextField,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as RejectIcon,
  AccessTime as TimeIcon,
  AttachMoney as MoneyIcon,
  TrendingUp as ValueIcon,
  PictureAsPdf as PdfIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useAgentContext } from '../contexts/AgentContext';
import {
  EffortEstimate,
  CostEstimate,
  ValueProjection,
} from '../services/agent/AgentService';

import { useAuth } from '../contexts/AuthContext';
import { PAPER_ELEVATION, STANDARD_STYLES } from '../styles/constants';

// Helper function to improve text formatting for better readability
const formatPrdContent = (content: string): string => {
  if (!content) return content;

  // Ensure proper line breaks after headings and before new sections
  let formatted = content
    // Add line breaks after markdown headings
    .replace(/^(#{1,6}\s.+)$/gm, '$1\n')
    // Add line breaks before new headings if not already present
    .replace(/([^\n])\n(#{1,6}\s)/g, '$1\n\n$2')
    // Ensure bullet points have proper spacing
    .replace(/^(\s*[-*+]\s.+)$/gm, '$1')
    // Add spacing after bullet point groups
    .replace(/^(\s*[-*+]\s.+)(\n(?!\s*[-*+]))/gm, '$1\n$2')
    // Clean up multiple consecutive line breaks (max 2)
    .replace(/\n{3,}/g, '\n\n');

  return formatted;
};

// Enhanced markdown styles for better PRD formatting
const markdownStyles = {
  '& h1': {
    fontSize: '1.8rem',
    fontWeight: 600,
    color: '#1976d2',
    marginTop: '2rem',
    marginBottom: '1rem',
    borderBottom: '2px solid #e3f2fd',
    paddingBottom: '0.5rem',
  },
  '& h2': {
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#333',
    marginTop: '1.5rem',
    marginBottom: '0.8rem',
  },
  '& h3': {
    fontSize: '1.3rem',
    fontWeight: 500,
    color: '#444',
    marginTop: '1.2rem',
    marginBottom: '0.6rem',
  },
  '& p': {
    marginBottom: '1rem',
    lineHeight: 1.6,
    color: '#333',
  },
  '& ul, & ol': {
    marginBottom: '1rem',
    paddingLeft: '1.5rem',
  },
  '& li': {
    marginBottom: '0.5rem',
    lineHeight: 1.5,
  },
  '& strong': {
    fontWeight: 600,
    color: '#1976d2',
  },
  '& em': {
    fontStyle: 'italic',
    color: '#666',
  },
  '& blockquote': {
    borderLeft: '4px solid #1976d2',
    paddingLeft: '1rem',
    margin: '1rem 0',
    fontStyle: 'italic',
    backgroundColor: '#f8f9fa',
    padding: '0.5rem 1rem',
  },
  '& code': {
    backgroundColor: '#f5f5f5',
    padding: '0.2rem 0.4rem',
    borderRadius: '3px',
    fontSize: '0.9em',
    fontFamily: 'monospace',
  },
  '& pre': {
    backgroundColor: '#f5f5f5',
    padding: '1rem',
    borderRadius: '5px',
    overflow: 'auto',
    margin: '1rem 0',
  },
};

const BusinessCaseDetailPage: React.FC = () => {
  const { caseId } = useParams<{ caseId: string }>();
  const navigate = useNavigate();
  const {
    currentCaseDetails,
    isLoadingCaseDetails,
    caseDetailsError,
    fetchCaseDetails,

    updatePrdDraft,
    submitPrdForReview,
    approvePrd,
    rejectPrd,
    updateSystemDesign,
    submitSystemDesignForReview,
    approveSystemDesign,
    rejectSystemDesign,
    updateEffortEstimate,
    submitEffortEstimateForReview,
    updateCostEstimate,
    submitCostEstimateForReview,
    updateValueProjection,
    submitValueProjectionForReview,
    approveEffortEstimate,
    rejectEffortEstimate,
    approveCostEstimate,
    rejectCostEstimate,
    approveValueProjection,
    rejectValueProjection,
    submitCaseForFinalApproval,
    approveFinalCase,
    rejectFinalCase,
    exportCaseToPdf,
    isLoading,
    error: agentContextError,
    clearCurrentCaseDetails,
  } = useAgentContext();
  const { currentUser, systemRole, isFinalApprover } = useAuth();

  const [isEditingPrd, setIsEditingPrd] = useState(false);
  const [editablePrdContent, setEditablePrdContent] = useState('');
  const [isEditingSystemDesign, setIsEditingSystemDesign] = useState(false);
  const [editableSystemDesignContent, setEditableSystemDesignContent] =
    useState('');

  const [prdUpdateError, setPrdUpdateError] = useState<string | null>(null);
  const [prdUpdateSuccess, setPrdUpdateSuccess] = useState<string | null>(null);
  const [systemDesignUpdateError, setSystemDesignUpdateError] = useState<
    string | null
  >(null);
  const [systemDesignUpdateSuccess, setSystemDesignUpdateSuccess] = useState<
    string | null
  >(null);
  const [statusUpdateSuccess, setStatusUpdateSuccess] = useState<string | null>(
    null
  );
  const [statusUpdateError, setStatusUpdateError] = useState<string | null>(
    null
  );
  const [approvalSuccess, setApprovalSuccess] = useState<string | null>(null);
  const [approvalError, setApprovalError] = useState<string | null>(null);
  const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false);
  const [isSystemDesignRejectDialogOpen, setIsSystemDesignRejectDialogOpen] =
    useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [systemDesignRejectionReason, setSystemDesignRejectionReason] =
    useState('');

  // Financial estimate rejection dialogs
  const [isEffortRejectDialogOpen, setIsEffortRejectDialogOpen] =
    useState(false);
  const [isCostRejectDialogOpen, setIsCostRejectDialogOpen] = useState(false);
  const [isValueRejectDialogOpen, setIsValueRejectDialogOpen] = useState(false);
  const [effortRejectionReason, setEffortRejectionReason] = useState('');
  const [costRejectionReason, setCostRejectionReason] = useState('');
  const [valueRejectionReason, setValueRejectionReason] = useState('');

  // Final approval states
  const [isFinalRejectDialogOpen, setIsFinalRejectDialogOpen] = useState(false);
  const [finalRejectionReason, setFinalRejectionReason] = useState('');

  // PDF export states
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);
  const [exportSuccess, setExportSuccess] = useState<string | null>(null);

  // Financial estimate editing states
  const [isEditingEffortEstimate, setIsEditingEffortEstimate] = useState(false);
  const [editableEffortEstimate, setEditableEffortEstimate] =
    useState<EffortEstimate | null>(null);
  const [isEditingCostEstimate, setIsEditingCostEstimate] = useState(false);
  const [editableCostEstimate, setEditableCostEstimate] =
    useState<CostEstimate | null>(null);
  const [isEditingValueProjection, setIsEditingValueProjection] =
    useState(false);
  const [editableValueProjection, setEditableValueProjection] =
    useState<ValueProjection | null>(null);

  // Success/error states for financial estimates
  const [effortEstimateUpdateSuccess, setEffortEstimateUpdateSuccess] =
    useState<string | null>(null);
  const [effortEstimateUpdateError, setEffortEstimateUpdateError] = useState<
    string | null
  >(null);
  const [costEstimateUpdateSuccess, setCostEstimateUpdateSuccess] = useState<
    string | null
  >(null);
  const [costEstimateUpdateError, setCostEstimateUpdateError] = useState<
    string | null
  >(null);
  const [valueProjectionUpdateSuccess, setValueProjectionUpdateSuccess] =
    useState<string | null>(null);
  const [valueProjectionUpdateError, setValueProjectionUpdateError] = useState<
    string | null
  >(null);

  const loadDetails = useCallback(() => {
    if (caseId) {
      fetchCaseDetails(caseId);
    }
  }, [caseId, fetchCaseDetails]);

  useEffect(() => {
    loadDetails();
    return () => {
      clearCurrentCaseDetails();
    };
  }, [loadDetails, clearCurrentCaseDetails]);

  useEffect(() => {
    if (currentCaseDetails?.prd_draft?.content_markdown && !isEditingPrd) {
      setEditablePrdContent(currentCaseDetails.prd_draft.content_markdown);
    }
  }, [currentCaseDetails, isEditingPrd]);

  useEffect(() => {
    if (
      currentCaseDetails?.system_design_v1_draft?.content_markdown &&
      !isEditingSystemDesign
    ) {
      setEditableSystemDesignContent(
        currentCaseDetails.system_design_v1_draft.content_markdown
      );
    }
  }, [currentCaseDetails, isEditingSystemDesign]);

  const handleEditPrd = () => {
    setEditablePrdContent(
      currentCaseDetails?.prd_draft?.content_markdown || ''
    );
    setIsEditingPrd(true);
    setPrdUpdateError(null);
    setPrdUpdateSuccess(null);
  };

  const handleCancelEditPrd = () => {
    setEditablePrdContent(
      currentCaseDetails?.prd_draft?.content_markdown || ''
    );
    setIsEditingPrd(false);
    setPrdUpdateError(null);
    setPrdUpdateSuccess(null);
  };

  const handleSavePrd = async () => {
    if (!caseId || !currentCaseDetails) return;
    setPrdUpdateError(null);
    setPrdUpdateSuccess(null);

    const success = await updatePrdDraft({
      caseId,
      content_markdown: editablePrdContent,
    });

    if (success) {
      setIsEditingPrd(false);
      setPrdUpdateSuccess('PRD updated successfully!');
      // Clear success message after 5 seconds
      setTimeout(() => setPrdUpdateSuccess(null), 5000);
    } else {
      setPrdUpdateError(
        agentContextError?.message || 'Failed to save PRD. Please try again.'
      );
    }
  };

  const handleSubmitPrdForReview = async () => {
    if (!caseId || !currentCaseDetails) return;
    setStatusUpdateError(null);
    setStatusUpdateSuccess(null);

    const success = await submitPrdForReview(caseId);

    if (success) {
      setStatusUpdateSuccess('PRD submitted for review successfully!');
      // Clear success message after 5 seconds
      setTimeout(() => setStatusUpdateSuccess(null), 5000);
    } else {
      setStatusUpdateError(
        agentContextError?.message ||
          'Failed to submit PRD for review. Please try again.'
      );
    }
  };

  const handleApprovePrd = async () => {
    if (!caseId || !currentCaseDetails) return;
    setApprovalError(null);
    setApprovalSuccess(null);

    const success = await approvePrd(caseId);

    if (success) {
      setApprovalSuccess('PRD approved successfully!');
      // Clear success message after 5 seconds
      setTimeout(() => setApprovalSuccess(null), 5000);
    } else {
      setApprovalError(
        agentContextError?.message || 'Failed to approve PRD. Please try again.'
      );
    }
  };

  const handleRejectPrd = async () => {
    if (!caseId || !currentCaseDetails) return;
    setApprovalError(null);
    setApprovalSuccess(null);

    const success = await rejectPrd(
      caseId,
      rejectionReason.trim() || undefined
    );

    if (success) {
      setApprovalSuccess('PRD rejected successfully.');
      setIsRejectDialogOpen(false);
      setRejectionReason('');
      // Clear success message after 5 seconds
      setTimeout(() => setApprovalSuccess(null), 5000);
    } else {
      setApprovalError(
        agentContextError?.message || 'Failed to reject PRD. Please try again.'
      );
    }
  };

  const handleOpenRejectDialog = () => {
    setIsRejectDialogOpen(true);
    setRejectionReason('');
    setApprovalError(null);
    setApprovalSuccess(null);
  };

  const handleCloseRejectDialog = () => {
    setIsRejectDialogOpen(false);
    setRejectionReason('');
  };

  // System Design Handlers
  const handleEditSystemDesign = () => {
    setEditableSystemDesignContent(
      currentCaseDetails?.system_design_v1_draft?.content_markdown || ''
    );
    setIsEditingSystemDesign(true);
    setSystemDesignUpdateError(null);
    setSystemDesignUpdateSuccess(null);
  };

  const handleCancelEditSystemDesign = () => {
    setIsEditingSystemDesign(false);
    setEditableSystemDesignContent(
      currentCaseDetails?.system_design_v1_draft?.content_markdown || ''
    );
    setSystemDesignUpdateError(null);
    setSystemDesignUpdateSuccess(null);
  };

  const handleSaveSystemDesign = async () => {
    if (!caseId) return;

    try {
      const success = await updateSystemDesign(
        caseId,
        editableSystemDesignContent
      );
      if (success) {
        setIsEditingSystemDesign(false);
        setSystemDesignUpdateSuccess('System Design saved successfully.');
        setSystemDesignUpdateError(null);
      }
    } catch (error: any) {
      setSystemDesignUpdateError(
        error.message || 'Failed to save System Design.'
      );
      setSystemDesignUpdateSuccess(null);
    }
  };

  const handleSubmitSystemDesignForReview = async () => {
    if (!caseId) return;

    try {
      const success = await submitSystemDesignForReview(caseId);
      if (success) {
        setStatusUpdateSuccess(
          'System Design submitted for review successfully.'
        );
        setStatusUpdateError(null);
      }
    } catch (error: any) {
      setStatusUpdateError(
        error.message || 'Failed to submit System Design for review.'
      );
      setStatusUpdateSuccess(null);
    }
  };

  const handleApproveSystemDesign = async () => {
    if (!caseId) return;

    try {
      const success = await approveSystemDesign(caseId);
      if (success) {
        setApprovalSuccess('System Design approved successfully.');
        setApprovalError(null);
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to approve System Design.');
      setApprovalSuccess(null);
    }
  };

  const handleRejectSystemDesign = async () => {
    if (!caseId) return;

    try {
      const success = await rejectSystemDesign(
        caseId,
        systemDesignRejectionReason
      );
      if (success) {
        setApprovalSuccess('System Design rejected successfully.');
        setApprovalError(null);
        setIsSystemDesignRejectDialogOpen(false);
        setSystemDesignRejectionReason('');
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to reject System Design.');
      setApprovalSuccess(null);
    }
  };

  const handleOpenSystemDesignRejectDialog = () => {
    setIsSystemDesignRejectDialogOpen(true);
    setSystemDesignRejectionReason('');
  };

  const handleCloseSystemDesignRejectDialog = () => {
    setIsSystemDesignRejectDialogOpen(false);
    setSystemDesignRejectionReason('');
  };

  // Effort Estimate handlers
  const handleEditEffortEstimate = () => {
    if (currentCaseDetails?.effort_estimate_v1) {
      setEditableEffortEstimate({ ...currentCaseDetails.effort_estimate_v1 });
      setIsEditingEffortEstimate(true);
      setEffortEstimateUpdateSuccess(null);
      setEffortEstimateUpdateError(null);
    }
  };

  const handleCancelEditEffortEstimate = () => {
    setIsEditingEffortEstimate(false);
    setEditableEffortEstimate(null);
    setEffortEstimateUpdateSuccess(null);
    setEffortEstimateUpdateError(null);
  };

  const handleSaveEffortEstimate = async () => {
    if (!caseId || !editableEffortEstimate) return;

    setEffortEstimateUpdateSuccess(null);
    setEffortEstimateUpdateError(null);

    try {
      const success = await updateEffortEstimate(
        caseId,
        editableEffortEstimate
      );
      if (success) {
        setEffortEstimateUpdateSuccess('Effort Estimate updated successfully!');
        setIsEditingEffortEstimate(false);
        setEditableEffortEstimate(null);
      } else {
        setEffortEstimateUpdateError(
          'Failed to update effort estimate. Please try again.'
        );
      }
    } catch (error: any) {
      setEffortEstimateUpdateError(
        error.message || 'Failed to update effort estimate.'
      );
    }
  };

  const handleSubmitEffortEstimateForReview = async () => {
    if (!caseId) return;

    try {
      const success = await submitEffortEstimateForReview(caseId);
      if (success) {
        setEffortEstimateUpdateSuccess(
          'Effort Estimate submitted for review successfully!'
        );
      } else {
        setEffortEstimateUpdateError(
          'Failed to submit effort estimate for review. Please try again.'
        );
      }
    } catch (error: any) {
      setEffortEstimateUpdateError(
        error.message || 'Failed to submit effort estimate for review.'
      );
    }
  };

  // Cost Estimate handlers
  const handleEditCostEstimate = () => {
    if (currentCaseDetails?.cost_estimate_v1) {
      setEditableCostEstimate({ ...currentCaseDetails.cost_estimate_v1 });
      setIsEditingCostEstimate(true);
      setCostEstimateUpdateSuccess(null);
      setCostEstimateUpdateError(null);
    }
  };

  const handleCancelEditCostEstimate = () => {
    setIsEditingCostEstimate(false);
    setEditableCostEstimate(null);
    setCostEstimateUpdateSuccess(null);
    setCostEstimateUpdateError(null);
  };

  const handleSaveCostEstimate = async () => {
    if (!caseId || !editableCostEstimate) return;

    setCostEstimateUpdateSuccess(null);
    setCostEstimateUpdateError(null);

    try {
      const success = await updateCostEstimate(caseId, editableCostEstimate);
      if (success) {
        setCostEstimateUpdateSuccess('Cost Estimate updated successfully!');
        setIsEditingCostEstimate(false);
        setEditableCostEstimate(null);
      } else {
        setCostEstimateUpdateError(
          'Failed to update cost estimate. Please try again.'
        );
      }
    } catch (error: any) {
      setCostEstimateUpdateError(
        error.message || 'Failed to update cost estimate.'
      );
    }
  };

  const handleSubmitCostEstimateForReview = async () => {
    if (!caseId) return;

    try {
      const success = await submitCostEstimateForReview(caseId);
      if (success) {
        setCostEstimateUpdateSuccess(
          'Cost Estimate submitted for review successfully!'
        );
      } else {
        setCostEstimateUpdateError(
          'Failed to submit cost estimate for review. Please try again.'
        );
      }
    } catch (error: any) {
      setCostEstimateUpdateError(
        error.message || 'Failed to submit cost estimate for review.'
      );
    }
  };

  // Value Projection handlers
  const handleEditValueProjection = () => {
    if (currentCaseDetails?.value_projection_v1) {
      setEditableValueProjection({ ...currentCaseDetails.value_projection_v1 });
      setIsEditingValueProjection(true);
      setValueProjectionUpdateSuccess(null);
      setValueProjectionUpdateError(null);
    }
  };

  const handleCancelEditValueProjection = () => {
    setIsEditingValueProjection(false);
    setEditableValueProjection(null);
    setValueProjectionUpdateSuccess(null);
    setValueProjectionUpdateError(null);
  };

  const handleSaveValueProjection = async () => {
    if (!caseId || !editableValueProjection) return;

    setValueProjectionUpdateSuccess(null);
    setValueProjectionUpdateError(null);

    try {
      const success = await updateValueProjection(
        caseId,
        editableValueProjection
      );
      if (success) {
        setValueProjectionUpdateSuccess(
          'Value Projection updated successfully!'
        );
        setIsEditingValueProjection(false);
        setEditableValueProjection(null);
      } else {
        setValueProjectionUpdateError(
          'Failed to update value projection. Please try again.'
        );
      }
    } catch (error: any) {
      setValueProjectionUpdateError(
        error.message || 'Failed to update value projection.'
      );
    }
  };

  const handleSubmitValueProjectionForReview = async () => {
    if (!caseId) return;

    try {
      const success = await submitValueProjectionForReview(caseId);
      if (success) {
        setValueProjectionUpdateSuccess(
          'Value Projection submitted for review successfully!'
        );
      } else {
        setValueProjectionUpdateError(
          'Failed to submit value projection for review. Please try again.'
        );
      }
    } catch (error: any) {
      setValueProjectionUpdateError(
        error.message || 'Failed to submit value projection for review.'
      );
    }
  };

  // Financial estimate approval/rejection handlers
  const handleApproveEffortEstimate = async () => {
    if (!caseId) return;
    try {
      const success = await approveEffortEstimate(caseId);
      if (success) {
        setApprovalSuccess('Effort Estimate approved successfully!');
      } else {
        setApprovalError(
          'Failed to approve effort estimate. Please try again.'
        );
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to approve effort estimate.');
    }
  };

  const handleRejectEffortEstimate = async () => {
    if (!caseId) return;
    try {
      const success = await rejectEffortEstimate(
        caseId,
        effortRejectionReason || undefined
      );
      if (success) {
        setApprovalSuccess('Effort Estimate rejected successfully!');
        setIsEffortRejectDialogOpen(false);
        setEffortRejectionReason('');
      } else {
        setApprovalError('Failed to reject effort estimate. Please try again.');
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to reject effort estimate.');
    }
  };

  const handleApproveCostEstimate = async () => {
    if (!caseId) return;
    try {
      const success = await approveCostEstimate(caseId);
      if (success) {
        setApprovalSuccess('Cost Estimate approved successfully!');
      } else {
        setApprovalError('Failed to approve cost estimate. Please try again.');
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to approve cost estimate.');
    }
  };

  const handleRejectCostEstimate = async () => {
    if (!caseId) return;
    try {
      const success = await rejectCostEstimate(
        caseId,
        costRejectionReason || undefined
      );
      if (success) {
        setApprovalSuccess('Cost Estimate rejected successfully!');
        setIsCostRejectDialogOpen(false);
        setCostRejectionReason('');
      } else {
        setApprovalError('Failed to reject cost estimate. Please try again.');
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to reject cost estimate.');
    }
  };

  const handleApproveValueProjection = async () => {
    if (!caseId) return;
    try {
      const success = await approveValueProjection(caseId);
      if (success) {
        setApprovalSuccess('Value Projection approved successfully!');
      } else {
        setApprovalError(
          'Failed to approve value projection. Please try again.'
        );
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to approve value projection.');
    }
  };

  const handleRejectValueProjection = async () => {
    if (!caseId) return;
    try {
      const success = await rejectValueProjection(
        caseId,
        valueRejectionReason || undefined
      );
      if (success) {
        setApprovalSuccess('Value Projection rejected successfully!');
        setIsValueRejectDialogOpen(false);
        setValueRejectionReason('');
      } else {
        setApprovalError(
          'Failed to reject value projection. Please try again.'
        );
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to reject value projection.');
    }
  };

  // Dialog handlers for financial estimates
  const handleOpenEffortRejectDialog = () => {
    setIsEffortRejectDialogOpen(true);
    setEffortRejectionReason('');
  };

  const handleCloseEffortRejectDialog = () => {
    setIsEffortRejectDialogOpen(false);
    setEffortRejectionReason('');
  };

  const handleOpenCostRejectDialog = () => {
    setIsCostRejectDialogOpen(true);
    setCostRejectionReason('');
  };

  const handleCloseCostRejectDialog = () => {
    setIsCostRejectDialogOpen(false);
    setCostRejectionReason('');
  };

  const handleOpenValueRejectDialog = () => {
    setIsValueRejectDialogOpen(true);
    setValueRejectionReason('');
  };

  const handleCloseValueRejectDialog = () => {
    setIsValueRejectDialogOpen(false);
    setValueRejectionReason('');
  };

  // Final approval handlers
  const handleSubmitForFinalApproval = async () => {
    if (!caseId) return;

    try {
      const success = await submitCaseForFinalApproval(caseId);
      if (success) {
        setStatusUpdateSuccess(
          'Business case submitted for final approval successfully.'
        );
        setStatusUpdateError(null);
      }
    } catch (error: any) {
      setStatusUpdateError(
        error.message || 'Failed to submit for final approval.'
      );
      setStatusUpdateSuccess(null);
    }
  };

  const handleApproveFinalCase = async () => {
    if (!caseId) return;

    try {
      const success = await approveFinalCase(caseId);
      if (success) {
        setApprovalSuccess('Business case approved successfully.');
        setApprovalError(null);
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to approve business case.');
      setApprovalSuccess(null);
    }
  };

  const handleRejectFinalCase = async () => {
    if (!caseId) return;

    try {
      const success = await rejectFinalCase(caseId, finalRejectionReason);
      if (success) {
        setApprovalSuccess('Business case rejected successfully.');
        setApprovalError(null);
        setIsFinalRejectDialogOpen(false);
        setFinalRejectionReason('');
      }
    } catch (error: any) {
      setApprovalError(error.message || 'Failed to reject business case.');
      setApprovalSuccess(null);
    }
  };

  const handleOpenFinalRejectDialog = () => {
    setIsFinalRejectDialogOpen(true);
    setFinalRejectionReason('');
  };

  const handleCloseFinalRejectDialog = () => {
    setIsFinalRejectDialogOpen(false);
    setFinalRejectionReason('');
  };

  // PDF Export Handler
  const handleExportToPdf = async () => {
    if (!caseId || !currentCaseDetails) return;

    setIsExportingPdf(true);
    setExportError(null);
    setExportSuccess(null);

    try {
      await exportCaseToPdf(caseId);
      setExportSuccess('PDF exported successfully!');
      // Clear success message after 5 seconds
      setTimeout(() => setExportSuccess(null), 5000);
    } catch (error: any) {
      setExportError(
        error.message || 'Failed to export PDF. Please try again.'
      );
    } finally {
      setIsExportingPdf(false);
    }
  };

  // Helper functions to check permissions and status
  const canEditEffortEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = [
      'PLANNING_COMPLETE',
      'EFFORT_PENDING_REVIEW',
      'EFFORT_REJECTED',
    ];
    return isInitiator && allowedStatuses.includes(currentCaseDetails.status);
  };

  const canSubmitEffortEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['PLANNING_COMPLETE', 'EFFORT_REJECTED'];
    return (
      isInitiator &&
      allowedStatuses.includes(currentCaseDetails.status) &&
      currentCaseDetails.effort_estimate_v1
    );
  };

  const canEditCostEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = [
      'COSTING_COMPLETE',
      'COSTING_PENDING_REVIEW',
      'COSTING_REJECTED',
    ];
    return isInitiator && allowedStatuses.includes(currentCaseDetails.status);
  };

  const canSubmitCostEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['COSTING_COMPLETE', 'COSTING_REJECTED'];
    return (
      isInitiator &&
      allowedStatuses.includes(currentCaseDetails.status) &&
      currentCaseDetails.cost_estimate_v1
    );
  };

  const canEditValueProjection = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = [
      'VALUE_ANALYSIS_COMPLETE',
      'VALUE_PENDING_REVIEW',
      'VALUE_REJECTED',
    ];
    return isInitiator && allowedStatuses.includes(currentCaseDetails.status);
  };

  const canSubmitValueProjection = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const allowedStatuses = ['VALUE_ANALYSIS_COMPLETE', 'VALUE_REJECTED'];
    return (
      isInitiator &&
      allowedStatuses.includes(currentCaseDetails.status) &&
      currentCaseDetails.value_projection_v1
    );
  };

  // Financial estimate approval/rejection permission helpers
  const canApproveRejectEffortEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    return isInitiator && currentCaseDetails.status === 'EFFORT_PENDING_REVIEW';
  };

  const canApproveRejectCostEstimate = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    return (
      isInitiator && currentCaseDetails.status === 'COSTING_PENDING_REVIEW'
    );
  };

  const canApproveRejectValueProjection = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    const isSalesManagerApprover = systemRole === 'SALES_MANAGER_APPROVER';
    return (
      (isInitiator || isSalesManagerApprover) &&
      currentCaseDetails.status === 'VALUE_PENDING_REVIEW'
    );
  };

  // Final approval permission helpers
  const canSubmitForFinalApproval = () => {
    if (!currentCaseDetails || !currentUser) return false;
    const isInitiator = currentCaseDetails.user_id === currentUser.uid;
    return (
      isInitiator && currentCaseDetails.status === 'FINANCIAL_MODEL_COMPLETE'
    );
  };

  const canApproveRejectFinalCase = () => {
    if (!currentCaseDetails || !currentUser) return false;
    return (
      isFinalApprover && currentCaseDetails.status === 'PENDING_FINAL_APPROVAL'
    );
  };

  if (isLoadingCaseDetails && !currentCaseDetails) {
    return (
      <CircularProgress sx={{ display: 'block', margin: 'auto', mt: 5 }} />
    );
  }

  if (caseDetailsError) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          Error loading case details: {caseDetailsError.message}
        </Alert>
        <Button onClick={() => navigate('/dashboard')} sx={{ mt: 2 }}>
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  if (!currentCaseDetails) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Typography variant="h6">
          Case not found or no details available.
        </Typography>
        <Button onClick={() => navigate('/dashboard')} sx={{ mt: 2 }}>
          Back to Dashboard
        </Button>
      </Container>
    );
  }

  const {
    title,
    status,
    problem_statement,
    relevant_links,
    prd_draft,
    system_design_v1_draft,
    effort_estimate_v1,
    cost_estimate_v1,
    value_projection_v1,
  } = currentCaseDetails;

  // Note: displayMessages is currently unused but may be needed for future chat functionality
  // const displayMessages = (messages || []).filter(msg => msg.messageType !== 'PRD_DRAFT');

  return (
    <Container maxWidth="lg" sx={STANDARD_STYLES.pageContainer}>
      <Paper elevation={PAPER_ELEVATION.MAIN_CONTENT} sx={STANDARD_STYLES.mainContentPaper}>
        <Stack
          direction="row"
          justifyContent="space-between"
          alignItems="center"
          mb={3}
        >
          <Stack direction="row" alignItems="center" spacing={2}>
            <Tooltip title="Back to Dashboard">
              <IconButton
                onClick={() => navigate('/dashboard')}
                disabled={isLoading}
              >
                <ArrowBackIcon />
              </IconButton>
            </Tooltip>
            <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 0 }}>
              {title || 'Business Case Details'}
            </Typography>
          </Stack>
          <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              startIcon={<PdfIcon />}
              onClick={handleExportToPdf}
              disabled={isExportingPdf}
              sx={{ mr: 1 }}
            >
              {isExportingPdf ? 'Exporting...' : 'Export PDF'}
            </Button>
            <Tooltip title="Refresh Case Details">
              <IconButton
                onClick={loadDetails}
                disabled={isLoading || isLoadingCaseDetails}
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>

        <Typography variant="overline" display="block" gutterBottom>
          Status: {status}
        </Typography>

        {/* Export Success/Error Messages */}
        {exportSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {exportSuccess}
          </Alert>
        )}
        {exportError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {exportError}
          </Alert>
        )}

        <Box mb={3}>
          <Typography variant="h5" component="h2" gutterBottom>
            Problem Statement
          </Typography>
          <Typography paragraph sx={{ whiteSpace: 'pre-wrap' }}>
            {problem_statement || 'Not provided'}
          </Typography>
        </Box>

        {relevant_links && relevant_links.length > 0 && (
          <Box mb={3}>
            <Typography variant="h5" component="h2" gutterBottom>
              Relevant Links
            </Typography>
            <Stack spacing={1}>
              {relevant_links.map(
                (link: { name: string; url: string }, index: number) => (
                  <Typography
                    key={index}
                    component="a"
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {link.name || link.url}
                  </Typography>
                )
              )}
            </Stack>
          </Box>
        )}

        <Divider sx={{ my: 3 }} />

        <Box mb={3}>
          <Stack
            direction="row"
            justifyContent="space-between"
            alignItems="center"
            mb={1}
          >
            <Typography variant="h5" component="h2" gutterBottom>
              PRD Draft
            </Typography>
            {!isEditingPrd && (
              <Button
                startIcon={<EditIcon />}
                onClick={handleEditPrd}
                disabled={isLoading}
              >
                Edit PRD
              </Button>
            )}
          </Stack>

          {isEditingPrd ? (
            <Box>
              <TextField
                fullWidth
                multiline
                rows={15}
                value={editablePrdContent}
                onChange={(e) => setEditablePrdContent(e.target.value)}
                variant="outlined"
                sx={{ mb: 1 }}
              />
              <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
                <Button
                  variant="contained"
                  onClick={handleSavePrd}
                  startIcon={<SaveIcon />}
                  disabled={isLoading}
                >
                  {isLoading ? 'Saving...' : 'Save Changes'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleCancelEditPrd}
                  startIcon={<CancelIcon />}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              </Stack>
            </Box>
          ) : prd_draft?.content_markdown ? (
            <Paper
              elevation={0}
              sx={{
                p: 3,
                mt: 1,
                border: '1px solid #eee',
                backgroundColor: '#ffffff',
                ...markdownStyles,
              }}
            >
              <ReactMarkdown>
                {formatPrdContent(prd_draft.content_markdown)}
              </ReactMarkdown>
            </Paper>
          ) : (
            <Typography color="textSecondary" sx={{ mt: 1 }}>
              PRD content not yet generated or available.
            </Typography>
          )}
          {prdUpdateError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {prdUpdateError}
            </Alert>
          )}
          {prdUpdateSuccess && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {prdUpdateSuccess}
            </Alert>
          )}

          {/* Submit PRD for Review Section */}
          {!isEditingPrd &&
            prd_draft?.content_markdown &&
            (status === 'INTAKE' ||
              status === 'PRD_DRAFTING' ||
              status === 'PRD_REVIEW') && (
              <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #eee' }}>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={handleSubmitPrdForReview}
                    disabled={isLoading}
                    startIcon={<SendIcon />}
                  >
                    {status === 'PRD_REVIEW'
                      ? 'Resubmit PRD for Review'
                      : 'Submit PRD for Review'}
                  </Button>
                  <Typography variant="body2" color="text.secondary">
                    {status === 'PRD_REVIEW'
                      ? 'PRD is currently under review. You can resubmit if changes were made.'
                      : status === 'INTAKE'
                      ? 'Submit your PRD content for review by stakeholders.'
                      : 'Submit your PRD draft for review by stakeholders.'}
                  </Typography>
                </Stack>
                {statusUpdateError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {statusUpdateError}
                  </Alert>
                )}
                {statusUpdateSuccess && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    {statusUpdateSuccess}
                  </Alert>
                )}
              </Box>
            )}

          {/* PRD Approval/Rejection Section */}
          {!isEditingPrd &&
            status === 'PRD_REVIEW' &&
            currentUser?.uid === currentCaseDetails.user_id && (
              <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #eee' }}>
                <Typography variant="h6" gutterBottom>
                  PRD Review Actions
                </Typography>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2 }}
                >
                  As the case initiator, you can approve or reject this PRD.
                </Typography>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Button
                    variant="contained"
                    color="success"
                    onClick={handleApprovePrd}
                    disabled={isLoading}
                    startIcon={<CheckCircleIcon />}
                  >
                    Approve PRD
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={handleOpenRejectDialog}
                    disabled={isLoading}
                    startIcon={<RejectIcon />}
                  >
                    Reject PRD
                  </Button>
                </Stack>
                {approvalError && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {approvalError}
                  </Alert>
                )}
                {approvalSuccess && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    {approvalSuccess}
                  </Alert>
                )}
              </Box>
            )}
        </Box>

        {/* System Design Section */}
        {system_design_v1_draft?.content_markdown && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                mb={2}
              >
                <Typography variant="h5" component="h2">System Design (v1)</Typography>
                <Stack direction="row" spacing={1}>
                  {/* Edit System Design Button - Show for owner or DEVELOPER role in appropriate statuses */}
                  {!isEditingSystemDesign &&
                    (status === 'SYSTEM_DESIGN_DRAFTED' ||
                      status === 'SYSTEM_DESIGN_PENDING_REVIEW') &&
                    (currentCaseDetails?.user_id === currentUser?.uid ||
                      systemRole === 'DEVELOPER') && (
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<EditIcon />}
                        onClick={handleEditSystemDesign}
                        disabled={isLoading}
                      >
                        Edit System Design
                      </Button>
                    )}

                  {/* Submit for Review Button - Show for owner or DEVELOPER role when status is SYSTEM_DESIGN_DRAFTED */}
                  {!isEditingSystemDesign &&
                    status === 'SYSTEM_DESIGN_DRAFTED' &&
                    (currentCaseDetails?.user_id === currentUser?.uid ||
                      systemRole === 'DEVELOPER') && (
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<SendIcon />}
                        onClick={handleSubmitSystemDesignForReview}
                        disabled={isLoading}
                      >
                        Submit for Review
                      </Button>
                    )}

                  {/* Approve System Design Button - Show only for DEVELOPER role when status is SYSTEM_DESIGN_PENDING_REVIEW */}
                  {!isEditingSystemDesign &&
                    status === 'SYSTEM_DESIGN_PENDING_REVIEW' &&
                    systemRole === 'DEVELOPER' && (
                      <Button
                        variant="contained"
                        size="small"
                        color="success"
                        startIcon={<CheckCircleIcon />}
                        onClick={handleApproveSystemDesign}
                        disabled={isLoading}
                      >
                        Approve System Design
                      </Button>
                    )}

                  {/* Reject System Design Button - Show only for DEVELOPER role when status is SYSTEM_DESIGN_PENDING_REVIEW */}
                  {!isEditingSystemDesign &&
                    status === 'SYSTEM_DESIGN_PENDING_REVIEW' &&
                    systemRole === 'DEVELOPER' && (
                      <Button
                        variant="outlined"
                        size="small"
                        color="error"
                        startIcon={<RejectIcon />}
                        onClick={handleOpenSystemDesignRejectDialog}
                        disabled={isLoading}
                      >
                        Reject System Design
                      </Button>
                    )}
                </Stack>
              </Stack>

              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Generated by: {system_design_v1_draft.generated_by} • Version:{' '}
                {system_design_v1_draft.version}
                {system_design_v1_draft.last_edited_by && (
                  <>
                    {' '}
                    • Last edited by: {system_design_v1_draft.last_edited_by}
                  </>
                )}
              </Typography>

              {/* System Design Update Success/Error Messages */}
              {systemDesignUpdateSuccess && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  {systemDesignUpdateSuccess}
                </Alert>
              )}
              {systemDesignUpdateError && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {systemDesignUpdateError}
                </Alert>
              )}

              {/* System Design Content - Editable or Read-only */}
              {isEditingSystemDesign ? (
                <Box>
                  <TextField
                    multiline
                    fullWidth
                    rows={20}
                    value={editableSystemDesignContent}
                    onChange={(e) =>
                      setEditableSystemDesignContent(e.target.value)
                    }
                    variant="outlined"
                    placeholder="Edit the system design content..."
                    sx={{ mb: 2, fontFamily: 'monospace' }}
                  />
                  <Stack direction="row" spacing={1}>
                    <Button
                      variant="contained"
                      startIcon={<SaveIcon />}
                      onClick={handleSaveSystemDesign}
                      disabled={isLoading}
                    >
                      Save Changes
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<CancelIcon />}
                      onClick={handleCancelEditSystemDesign}
                      disabled={isLoading}
                    >
                      Cancel
                    </Button>
                  </Stack>
                </Box>
              ) : (
                <Paper
                  elevation={0}
                  sx={{
                    p: 3,
                    mt: 1,
                    border: '1px solid #eee',
                    backgroundColor: '#fafafa',
                    ...markdownStyles,
                  }}
                >
                  <ReactMarkdown>
                    {formatPrdContent(system_design_v1_draft.content_markdown)}
                  </ReactMarkdown>
                </Paper>
              )}
            </Box>
          </>
        )}

        {/* Effort Estimate Section */}
        {effort_estimate_v1 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                mb={2}
              >
                <Stack direction="row" alignItems="center" spacing={1}>
                  <TimeIcon color="primary" />
                  <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 0 }}>
                    Effort Estimate
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1}>
                  {canEditEffortEstimate() && !isEditingEffortEstimate && (
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<EditIcon />}
                      onClick={handleEditEffortEstimate}
                      disabled={isLoading}
                    >
                      Edit Effort Estimate
                    </Button>
                  )}
                  {canSubmitEffortEstimate() && !isEditingEffortEstimate && (
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<SendIcon />}
                      onClick={handleSubmitEffortEstimateForReview}
                      disabled={isLoading}
                    >
                      Submit for Review
                    </Button>
                  )}
                  {canApproveRejectEffortEstimate() &&
                    !isEditingEffortEstimate && (
                      <>
                        <Button
                          variant="contained"
                          size="small"
                          color="success"
                          startIcon={<CheckCircleIcon />}
                          onClick={handleApproveEffortEstimate}
                          disabled={isLoading}
                        >
                          Approve Effort
                        </Button>
                        <Button
                          variant="outlined"
                          size="small"
                          color="error"
                          startIcon={<RejectIcon />}
                          onClick={handleOpenEffortRejectDialog}
                          disabled={isLoading}
                        >
                          Reject Effort
                        </Button>
                      </>
                    )}
                </Stack>
              </Stack>

              {effortEstimateUpdateSuccess && (
                <Alert
                  severity="success"
                  sx={{ mb: 2 }}
                  onClose={() => setEffortEstimateUpdateSuccess(null)}
                >
                  {effortEstimateUpdateSuccess}
                </Alert>
              )}
              {effortEstimateUpdateError && (
                <Alert
                  severity="error"
                  sx={{ mb: 2 }}
                  onClose={() => setEffortEstimateUpdateError(null)}
                >
                  {effortEstimateUpdateError}
                </Alert>
              )}

              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  {!isEditingEffortEstimate ? (
                    <>
                      <Stack direction="row" spacing={4} mb={3}>
                        <Box>
                          <Typography variant="h6" color="primary">
                            {effort_estimate_v1.total_hours}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Total Hours
                          </Typography>
                        </Box>
                        <Box>
                          <Typography variant="h6" color="primary">
                            {effort_estimate_v1.estimated_duration_weeks}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Weeks Duration
                          </Typography>
                        </Box>
                        <Box>
                          <Chip
                            label={effort_estimate_v1.complexity_assessment}
                            color="info"
                            variant="outlined"
                          />
                        </Box>
                      </Stack>

                      <Typography variant="h6" gutterBottom>
                        Role Breakdown
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>
                                <strong>Role</strong>
                              </TableCell>
                              <TableCell align="right">
                                <strong>Hours</strong>
                              </TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {effort_estimate_v1.roles?.map((role, index) => (
                              <TableRow key={index}>
                                <TableCell>{role.role}</TableCell>
                                <TableCell align="right">
                                  {role.hours}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>

                      {effort_estimate_v1.notes && (
                        <Box mt={2}>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ fontStyle: 'italic' }}
                          >
                            {effort_estimate_v1.notes}
                          </Typography>
                        </Box>
                      )}
                    </>
                  ) : (
                    <>
                      <Stack direction="row" spacing={2} mb={3}>
                        <TextField
                          label="Total Hours"
                          type="number"
                          value={editableEffortEstimate?.total_hours || 0}
                          onChange={(e) =>
                            editableEffortEstimate &&
                            setEditableEffortEstimate({
                              ...editableEffortEstimate,
                              total_hours: parseInt(e.target.value) || 0,
                            })
                          }
                          size="small"
                          sx={{ minWidth: 150 }}
                        />
                        <TextField
                          label="Duration (Weeks)"
                          type="number"
                          value={
                            editableEffortEstimate?.estimated_duration_weeks ||
                            0
                          }
                          onChange={(e) =>
                            editableEffortEstimate &&
                            setEditableEffortEstimate({
                              ...editableEffortEstimate,
                              estimated_duration_weeks:
                                parseInt(e.target.value) || 0,
                            })
                          }
                          size="small"
                          sx={{ minWidth: 150 }}
                        />
                        <TextField
                          label="Complexity Assessment"
                          value={
                            editableEffortEstimate?.complexity_assessment || ''
                          }
                          onChange={(e) =>
                            editableEffortEstimate &&
                            setEditableEffortEstimate({
                              ...editableEffortEstimate,
                              complexity_assessment: e.target.value,
                            })
                          }
                          size="small"
                          sx={{ minWidth: 200 }}
                        />
                      </Stack>

                      <TextField
                        label="Notes"
                        multiline
                        rows={3}
                        fullWidth
                        value={editableEffortEstimate?.notes || ''}
                        onChange={(e) =>
                          editableEffortEstimate &&
                          setEditableEffortEstimate({
                            ...editableEffortEstimate,
                            notes: e.target.value,
                          })
                        }
                        sx={{ mb: 3 }}
                      />

                      <Stack
                        direction="row"
                        spacing={2}
                        justifyContent="flex-end"
                      >
                        <Button
                          variant="outlined"
                          startIcon={<CancelIcon />}
                          onClick={handleCancelEditEffortEstimate}
                          disabled={isLoading}
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="contained"
                          startIcon={<SaveIcon />}
                          onClick={handleSaveEffortEstimate}
                          disabled={isLoading}
                        >
                          {isLoading ? 'Saving...' : 'Save Changes'}
                        </Button>
                      </Stack>
                    </>
                  )}
                </CardContent>
              </Card>
            </Box>
          </>
        )}

        {/* Cost Estimate Section */}
        {cost_estimate_v1 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                mb={2}
              >
                <Stack direction="row" alignItems="center" spacing={1}>
                  <MoneyIcon color="primary" />
                  <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 0 }}>
                    Cost Estimate
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1}>
                  {canEditCostEstimate() && !isEditingCostEstimate && (
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<EditIcon />}
                      onClick={handleEditCostEstimate}
                      disabled={isLoading}
                    >
                      Edit Cost Estimate
                    </Button>
                  )}
                  {canSubmitCostEstimate() && !isEditingCostEstimate && (
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<SendIcon />}
                      onClick={handleSubmitCostEstimateForReview}
                      disabled={isLoading}
                    >
                      Submit for Review
                    </Button>
                  )}
                  {canApproveRejectCostEstimate() && !isEditingCostEstimate && (
                    <>
                      <Button
                        variant="contained"
                        size="small"
                        color="success"
                        startIcon={<CheckCircleIcon />}
                        onClick={handleApproveCostEstimate}
                        disabled={isLoading}
                      >
                        Approve Cost
                      </Button>
                      <Button
                        variant="outlined"
                        size="small"
                        color="error"
                        startIcon={<RejectIcon />}
                        onClick={handleOpenCostRejectDialog}
                        disabled={isLoading}
                      >
                        Reject Cost
                      </Button>
                    </>
                  )}
                </Stack>
              </Stack>

              {costEstimateUpdateSuccess && (
                <Alert
                  severity="success"
                  sx={{ mb: 2 }}
                  onClose={() => setCostEstimateUpdateSuccess(null)}
                >
                  {costEstimateUpdateSuccess}
                </Alert>
              )}
              {costEstimateUpdateError && (
                <Alert
                  severity="error"
                  sx={{ mb: 2 }}
                  onClose={() => setCostEstimateUpdateError(null)}
                >
                  {costEstimateUpdateError}
                </Alert>
              )}

              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  {!isEditingCostEstimate ? (
                    <>
                      <Stack direction="row" spacing={4} mb={3}>
                        <Box>
                          <Typography variant="h4" color="primary">
                            ${cost_estimate_v1.estimated_cost.toLocaleString()}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Total Cost ({cost_estimate_v1.currency})
                          </Typography>
                        </Box>
                        {cost_estimate_v1.rate_card_used && (
                          <Box>
                            <Typography variant="body1" fontWeight="medium">
                              {cost_estimate_v1.rate_card_used}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Rate Card Used
                            </Typography>
                          </Box>
                        )}
                      </Stack>

                      <Typography variant="h6" component="h3" gutterBottom>
                        Cost Breakdown by Role
                      </Typography>
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>
                                <strong>Role</strong>
                              </TableCell>
                              <TableCell align="right">
                                <strong>Hours</strong>
                              </TableCell>
                              <TableCell align="right">
                                <strong>Rate</strong>
                              </TableCell>
                              <TableCell align="right">
                                <strong>Total Cost</strong>
                              </TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {cost_estimate_v1.breakdown_by_role?.map(
                              (role, index) => (
                                <TableRow key={index}>
                                  <TableCell>{role.role}</TableCell>
                                  <TableCell align="right">
                                    {role.hours}
                                  </TableCell>
                                  <TableCell align="right">
                                    ${role.hourly_rate}/hr
                                  </TableCell>
                                  <TableCell align="right">
                                    ${role.total_cost.toLocaleString()}
                                  </TableCell>
                                </TableRow>
                              )
                            )}
                          </TableBody>
                        </Table>
                      </TableContainer>

                      {cost_estimate_v1.notes && (
                        <Box mt={2}>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ fontStyle: 'italic' }}
                          >
                            {cost_estimate_v1.notes}
                          </Typography>
                        </Box>
                      )}
                    </>
                  ) : (
                    <>
                      <Stack direction="row" spacing={2} mb={3}>
                        <TextField
                          label="Total Cost"
                          type="number"
                          value={editableCostEstimate?.estimated_cost || 0}
                          onChange={(e) =>
                            editableCostEstimate &&
                            setEditableCostEstimate({
                              ...editableCostEstimate,
                              estimated_cost: parseFloat(e.target.value) || 0,
                            })
                          }
                          size="small"
                          sx={{ minWidth: 150 }}
                          InputProps={{ startAdornment: '$' }}
                        />
                        <TextField
                          label="Currency"
                          value={editableCostEstimate?.currency || 'USD'}
                          onChange={(e) =>
                            editableCostEstimate &&
                            setEditableCostEstimate({
                              ...editableCostEstimate,
                              currency: e.target.value,
                            })
                          }
                          size="small"
                          sx={{ minWidth: 100 }}
                        />
                        <TextField
                          label="Rate Card Used"
                          value={editableCostEstimate?.rate_card_used || ''}
                          onChange={(e) =>
                            editableCostEstimate &&
                            setEditableCostEstimate({
                              ...editableCostEstimate,
                              rate_card_used: e.target.value,
                            })
                          }
                          size="small"
                          sx={{ minWidth: 200 }}
                        />
                      </Stack>

                      <TextField
                        label="Calculation Method"
                        value={editableCostEstimate?.calculation_method || ''}
                        onChange={(e) =>
                          editableCostEstimate &&
                          setEditableCostEstimate({
                            ...editableCostEstimate,
                            calculation_method: e.target.value,
                          })
                        }
                        fullWidth
                        sx={{ mb: 2 }}
                      />

                      <TextField
                        label="Notes"
                        multiline
                        rows={3}
                        fullWidth
                        value={editableCostEstimate?.notes || ''}
                        onChange={(e) =>
                          editableCostEstimate &&
                          setEditableCostEstimate({
                            ...editableCostEstimate,
                            notes: e.target.value,
                          })
                        }
                        sx={{ mb: 3 }}
                      />

                      <Stack
                        direction="row"
                        spacing={2}
                        justifyContent="flex-end"
                      >
                        <Button
                          variant="outlined"
                          startIcon={<CancelIcon />}
                          onClick={handleCancelEditCostEstimate}
                          disabled={isLoading}
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="contained"
                          startIcon={<SaveIcon />}
                          onClick={handleSaveCostEstimate}
                          disabled={isLoading}
                        >
                          {isLoading ? 'Saving...' : 'Save Changes'}
                        </Button>
                      </Stack>
                    </>
                  )}
                </CardContent>
              </Card>
            </Box>
          </>
        )}

        {/* Value Projection Section */}
        {value_projection_v1 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                mb={2}
              >
                <Stack direction="row" alignItems="center" spacing={1}>
                  <ValueIcon color="primary" />
                  <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 0 }}>
                    Value/Revenue Projection
                  </Typography>
                </Stack>
                <Stack direction="row" spacing={1}>
                  {canEditValueProjection() && !isEditingValueProjection && (
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<EditIcon />}
                      onClick={handleEditValueProjection}
                      disabled={isLoading}
                    >
                      Edit Value Projection
                    </Button>
                  )}
                  {canSubmitValueProjection() && !isEditingValueProjection && (
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<SendIcon />}
                      onClick={handleSubmitValueProjectionForReview}
                      disabled={isLoading}
                    >
                      Submit for Review
                    </Button>
                  )}
                  {canApproveRejectValueProjection() &&
                    !isEditingValueProjection && (
                      <>
                        <Button
                          variant="contained"
                          size="small"
                          color="success"
                          startIcon={<CheckCircleIcon />}
                          onClick={handleApproveValueProjection}
                          disabled={isLoading}
                        >
                          Approve Value
                        </Button>
                        <Button
                          variant="outlined"
                          size="small"
                          color="error"
                          startIcon={<RejectIcon />}
                          onClick={handleOpenValueRejectDialog}
                          disabled={isLoading}
                        >
                          Reject Value
                        </Button>
                      </>
                    )}
                </Stack>
              </Stack>

              {valueProjectionUpdateSuccess && (
                <Alert
                  severity="success"
                  sx={{ mb: 2 }}
                  onClose={() => setValueProjectionUpdateSuccess(null)}
                >
                  {valueProjectionUpdateSuccess}
                </Alert>
              )}
              {valueProjectionUpdateError && (
                <Alert
                  severity="error"
                  sx={{ mb: 2 }}
                  onClose={() => setValueProjectionUpdateError(null)}
                >
                  {valueProjectionUpdateError}
                </Alert>
              )}

              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  {!isEditingValueProjection ? (
                    <>
                      <Stack direction="row" spacing={4} mb={3}>
                        {value_projection_v1.template_used && (
                          <Box>
                            <Typography variant="body1" fontWeight="medium">
                              {value_projection_v1.template_used}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Template Used
                            </Typography>
                          </Box>
                        )}
                        {value_projection_v1.methodology && (
                          <Box>
                            <Typography variant="body1" fontWeight="medium">
                              {value_projection_v1.methodology}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Methodology
                            </Typography>
                          </Box>
                        )}
                      </Stack>

                      <Typography variant="h6" component="h3" gutterBottom>
                        Value Scenarios
                      </Typography>
                      <Stack spacing={2} mb={3}>
                        {value_projection_v1.scenarios?.map(
                          (scenario, index) => (
                            <Card
                              key={index}
                              variant="outlined"
                              sx={{ backgroundColor: '#f8f9fa' }}
                            >
                              <CardContent sx={{ py: 2 }}>
                                <Stack
                                  direction="row"
                                  justifyContent="space-between"
                                  alignItems="center"
                                >
                                  <Box>
                                    <Typography variant="h6" color="primary">
                                      {scenario.case} Scenario
                                    </Typography>
                                    {scenario.description && (
                                      <Typography
                                        variant="body2"
                                        color="text.secondary"
                                      >
                                        {scenario.description}
                                      </Typography>
                                    )}
                                  </Box>
                                  <Typography
                                    variant="h5"
                                    fontWeight="bold"
                                    color="success.main"
                                  >
                                    ${scenario.value.toLocaleString()}{' '}
                                    {value_projection_v1.currency}
                                  </Typography>
                                </Stack>
                              </CardContent>
                            </Card>
                          )
                        )}
                      </Stack>

                      {value_projection_v1.assumptions &&
                        value_projection_v1.assumptions.length > 0 && (
                          <Box mb={2}>
                            <Typography variant="h6" component="h3" gutterBottom>
                              Key Assumptions
                            </Typography>
                            <List dense>
                              {value_projection_v1.assumptions.map(
                                (assumption, index) => (
                                  <ListItem key={index} sx={{ py: 0.5 }}>
                                    <ListItemText
                                      primary={assumption}
                                      primaryTypographyProps={{
                                        variant: 'body2',
                                      }}
                                    />
                                  </ListItem>
                                )
                              )}
                            </List>
                          </Box>
                        )}

                      {value_projection_v1.notes && (
                        <Box mt={2}>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ fontStyle: 'italic' }}
                          >
                            {value_projection_v1.notes}
                          </Typography>
                        </Box>
                      )}
                    </>
                  ) : (
                    <>
                      <Stack direction="row" spacing={2} mb={3}>
                        <TextField
                          label="Currency"
                          value={editableValueProjection?.currency || 'USD'}
                          onChange={(e) =>
                            editableValueProjection &&
                            setEditableValueProjection({
                              ...editableValueProjection,
                              currency: e.target.value,
                            })
                          }
                          size="small"
                          sx={{ minWidth: 100 }}
                        />
                        <TextField
                          label="Template Used"
                          value={editableValueProjection?.template_used || ''}
                          onChange={(e) =>
                            editableValueProjection &&
                            setEditableValueProjection({
                              ...editableValueProjection,
                              template_used: e.target.value,
                            })
                          }
                          size="small"
                          sx={{ minWidth: 200 }}
                        />
                        <TextField
                          label="Methodology"
                          value={editableValueProjection?.methodology || ''}
                          onChange={(e) =>
                            editableValueProjection &&
                            setEditableValueProjection({
                              ...editableValueProjection,
                              methodology: e.target.value,
                            })
                          }
                          size="small"
                          sx={{ minWidth: 200 }}
                        />
                      </Stack>

                      <TextField
                        label="Key Assumptions (one per line)"
                        multiline
                        rows={4}
                        fullWidth
                        value={
                          editableValueProjection?.assumptions?.join('\n') || ''
                        }
                        onChange={(e) =>
                          editableValueProjection &&
                          setEditableValueProjection({
                            ...editableValueProjection,
                            assumptions: e.target.value
                              .split('\n')
                              .filter((line) => line.trim()),
                          })
                        }
                        sx={{ mb: 2 }}
                      />

                      <TextField
                        label="Notes"
                        multiline
                        rows={3}
                        fullWidth
                        value={editableValueProjection?.notes || ''}
                        onChange={(e) =>
                          editableValueProjection &&
                          setEditableValueProjection({
                            ...editableValueProjection,
                            notes: e.target.value,
                          })
                        }
                        sx={{ mb: 3 }}
                      />

                      <Stack
                        direction="row"
                        spacing={2}
                        justifyContent="flex-end"
                      >
                        <Button
                          variant="outlined"
                          startIcon={<CancelIcon />}
                          onClick={handleCancelEditValueProjection}
                          disabled={isLoading}
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="contained"
                          startIcon={<SaveIcon />}
                          onClick={handleSaveValueProjection}
                          disabled={isLoading}
                        >
                          {isLoading ? 'Saving...' : 'Save Changes'}
                        </Button>
                      </Stack>
                    </>
                  )}
                </CardContent>
              </Card>
            </Box>
          </>
        )}

        {/* Financial Summary Section */}
        {currentCaseDetails?.financial_summary_v1 && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Stack direction="row" alignItems="center" spacing={1} mb={2}>
                <MoneyIcon color="primary" />
                <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 0 }}>
                  Financial Model Summary
                </Typography>
              </Stack>

              <Card
                variant="outlined"
                sx={{ mb: 2, backgroundColor: '#f8f9fa' }}
              >
                <CardContent>
                  <Stack spacing={3}>
                    {/* Key Financial Metrics */}
                    <Box>
                      <Typography variant="h6" component="h3" gutterBottom color="primary">
                        Key Financial Metrics
                      </Typography>
                      <Stack direction="row" spacing={4} mb={2}>
                        <Box>
                          <Typography
                            variant="h4"
                            color="primary"
                            fontWeight="bold"
                          >
                            $
                            {currentCaseDetails.financial_summary_v1.total_estimated_cost.toLocaleString()}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Total Estimated Cost (
                            {currentCaseDetails.financial_summary_v1.currency})
                          </Typography>
                        </Box>
                        <Box>
                          <Typography
                            variant="h4"
                            color="success.main"
                            fontWeight="bold"
                          >
                            $
                            {currentCaseDetails.financial_summary_v1.financial_metrics.primary_net_value.toLocaleString()}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Net Value (Base Case)
                          </Typography>
                        </Box>
                        <Box>
                          <Typography
                            variant="h4"
                            color="info.main"
                            fontWeight="bold"
                          >
                            {typeof currentCaseDetails.financial_summary_v1
                              .financial_metrics.primary_roi_percentage ===
                            'number'
                              ? `${currentCaseDetails.financial_summary_v1.financial_metrics.primary_roi_percentage.toFixed(
                                  1
                                )}%`
                              : currentCaseDetails.financial_summary_v1
                                  .financial_metrics.primary_roi_percentage}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Return on Investment (ROI)
                          </Typography>
                        </Box>
                        <Box>
                          <Typography
                            variant="h4"
                            color="warning.main"
                            fontWeight="bold"
                          >
                            {typeof currentCaseDetails.financial_summary_v1
                              .financial_metrics.simple_payback_period_years ===
                            'number'
                              ? `${currentCaseDetails.financial_summary_v1.financial_metrics.simple_payback_period_years.toFixed(
                                  1
                                )} years`
                              : currentCaseDetails.financial_summary_v1
                                  .financial_metrics
                                  .simple_payback_period_years}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Estimated Payback Period
                          </Typography>
                        </Box>
                      </Stack>
                    </Box>

                    {/* Value Scenarios */}
                    {Object.keys(
                      currentCaseDetails.financial_summary_v1.value_scenarios
                    ).length > 0 && (
                      <Box>
                        <Typography variant="h6" component="h3" gutterBottom>
                          Value Scenarios Analysis
                        </Typography>
                        <Stack direction="row" spacing={2}>
                          {Object.entries(
                            currentCaseDetails.financial_summary_v1
                              .value_scenarios
                          ).map(([scenario, value]) => {
                            const scenarioKey = scenario
                              .toLowerCase()
                              .replace(' ', '_');
                            const netValue =
                              currentCaseDetails.financial_summary_v1
                                ?.financial_metrics[`net_value_${scenarioKey}`];
                            const roi =
                              currentCaseDetails.financial_summary_v1
                                ?.financial_metrics[
                                `roi_${scenarioKey}_percentage`
                              ];

                            return (
                              <Card
                                key={scenario}
                                variant="outlined"
                                sx={{ flex: 1 }}
                              >
                                <CardContent sx={{ textAlign: 'center' }}>
                                  <Typography
                                    variant="h6"
                                    color="primary"
                                    gutterBottom
                                  >
                                    {scenario} Case
                                  </Typography>
                                  <Typography
                                    variant="h5"
                                    fontWeight="bold"
                                    color="success.main"
                                    gutterBottom
                                  >
                                    ${value.toLocaleString()}
                                  </Typography>
                                  <Typography
                                    variant="body2"
                                    color="text.secondary"
                                    gutterBottom
                                  >
                                    Projected Value
                                  </Typography>
                                  {netValue !== undefined && (
                                    <>
                                      <Typography
                                        variant="body1"
                                        fontWeight="medium"
                                      >
                                        Net: $
                                        {typeof netValue === 'number'
                                          ? netValue.toLocaleString()
                                          : netValue}
                                      </Typography>
                                      <Typography
                                        variant="body2"
                                        color="text.secondary"
                                      >
                                        ROI:{' '}
                                        {typeof roi === 'number'
                                          ? `${roi.toFixed(1)}%`
                                          : roi}
                                      </Typography>
                                    </>
                                  )}
                                </CardContent>
                              </Card>
                            );
                          })}
                        </Stack>
                      </Box>
                    )}

                    {/* Methodology and Sources */}
                    <Box>
                      <Typography variant="h6" component="h3" gutterBottom>
                        Analysis Methodology
                      </Typography>
                      <Stack spacing={1}>
                        {currentCaseDetails.financial_summary_v1
                          .cost_breakdown_source && (
                          <Typography variant="body2">
                            <strong>Cost Analysis:</strong>{' '}
                            {
                              currentCaseDetails.financial_summary_v1
                                .cost_breakdown_source
                            }
                          </Typography>
                        )}
                        {currentCaseDetails.financial_summary_v1
                          .value_methodology && (
                          <Typography variant="body2">
                            <strong>Value Methodology:</strong>{' '}
                            {
                              currentCaseDetails.financial_summary_v1
                                .value_methodology
                            }
                          </Typography>
                        )}
                        {currentCaseDetails.financial_summary_v1
                          .financial_metrics.payback_period_note && (
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{ fontStyle: 'italic' }}
                          >
                            <strong>Payback Note:</strong>{' '}
                            {
                              currentCaseDetails.financial_summary_v1
                                .financial_metrics.payback_period_note
                            }
                          </Typography>
                        )}
                      </Stack>
                    </Box>

                    {/* Additional Notes */}
                    {currentCaseDetails.financial_summary_v1.notes && (
                      <Box>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{ fontStyle: 'italic' }}
                        >
                          <strong>Notes:</strong>{' '}
                          {currentCaseDetails.financial_summary_v1.notes}
                        </Typography>
                      </Box>
                    )}

                    {/* Generation Timestamp */}
                    {currentCaseDetails.financial_summary_v1
                      .generated_timestamp && (
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Financial summary generated on:{' '}
                          {new Date(
                            currentCaseDetails.financial_summary_v1.generated_timestamp
                          ).toLocaleString()}
                        </Typography>
                      </Box>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Box>
          </>
        )}

        {/* Final Business Case Approval Section */}
        {(canSubmitForFinalApproval() ||
          canApproveRejectFinalCase() ||
          status === 'PENDING_FINAL_APPROVAL' ||
          status === 'APPROVED' ||
          status === 'REJECTED') && (
          <>
            <Divider sx={{ my: 3 }} />
            <Box mb={3}>
              <Typography
                variant="h5"
                gutterBottom
                sx={{ display: 'flex', alignItems: 'center', mb: 3 }}
              >
                <CheckCircleIcon
                  sx={{
                    mr: 1,
                    color:
                      status === 'APPROVED'
                        ? 'success.main'
                        : status === 'REJECTED'
                        ? 'error.main'
                        : 'primary.main',
                  }}
                />
                Final Business Case Approval
              </Typography>

              {/* Status Display */}
              {(status === 'PENDING_FINAL_APPROVAL' ||
                status === 'APPROVED' ||
                status === 'REJECTED') && (
                <Card sx={{ mb: 3 }}>
                  <CardContent>
                    <Stack spacing={2}>
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          Current Status:
                          <Chip
                            label={
                              status === 'PENDING_FINAL_APPROVAL'
                                ? 'Pending Final Approval'
                                : status === 'APPROVED'
                                ? 'Approved'
                                : status === 'REJECTED'
                                ? 'Rejected'
                                : status
                            }
                            color={
                              status === 'APPROVED'
                                ? 'success'
                                : status === 'REJECTED'
                                ? 'error'
                                : 'warning'
                            }
                            sx={{ ml: 1 }}
                          />
                        </Typography>
                      </Box>

                      {status === 'APPROVED' && (
                        <Alert severity="success">
                          <Typography variant="body1">
                            🎉 <strong>Congratulations!</strong> This business
                            case has been approved and is ready for
                            implementation.
                          </Typography>
                        </Alert>
                      )}

                      {status === 'REJECTED' && (
                        <Alert severity="error">
                          <Typography variant="body1">
                            ❌ This business case has been rejected. Please
                            review the feedback and consider revisions.
                          </Typography>
                        </Alert>
                      )}

                      {status === 'PENDING_FINAL_APPROVAL' && (
                        <Alert severity="info">
                          <Typography variant="body1">
                            ⏳ This business case is awaiting final approval
                            from authorized reviewers.
                          </Typography>
                        </Alert>
                      )}
                    </Stack>
                  </CardContent>
                </Card>
              )}

              {/* Submit for Final Approval */}
              {canSubmitForFinalApproval() && (
                <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #eee' }}>
                  <Typography variant="h6" gutterBottom>
                    Ready for Final Approval
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    All prerequisite components (PRD, System Design, and
                    Financial Model) have been completed. You can now submit
                    this business case for final approval.
                  </Typography>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleSubmitForFinalApproval}
                      disabled={isLoading}
                      startIcon={<SendIcon />}
                      size="large"
                    >
                      Submit for Final Approval
                    </Button>
                  </Stack>
                  {statusUpdateError && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {statusUpdateError}
                    </Alert>
                  )}
                  {statusUpdateSuccess && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      {statusUpdateSuccess}
                    </Alert>
                  )}
                </Box>
              )}

              {/* Final Approval Actions (for FINAL_APPROVER role) */}
              {canApproveRejectFinalCase() && (
                <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #eee' }}>
                  <Typography variant="h6" gutterBottom>
                    Final Approval Actions
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    As a final approver, you can approve or reject this complete
                    business case.
                  </Typography>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Button
                      variant="contained"
                      color="success"
                      onClick={handleApproveFinalCase}
                      disabled={isLoading}
                      startIcon={<CheckCircleIcon />}
                      size="large"
                    >
                      Approve Final Business Case
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      onClick={handleOpenFinalRejectDialog}
                      disabled={isLoading}
                      startIcon={<RejectIcon />}
                      size="large"
                    >
                      Reject Final Business Case
                    </Button>
                  </Stack>
                  {approvalError && (
                    <Alert severity="error" sx={{ mt: 2 }}>
                      {approvalError}
                    </Alert>
                  )}
                  {approvalSuccess && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      {approvalSuccess}
                    </Alert>
                  )}
                </Box>
              )}
            </Box>
          </>
        )}

        {isLoading && !isLoadingCaseDetails && !isEditingPrd && (
          <CircularProgress sx={{ display: 'block', margin: '20px auto' }} />
        )}
      </Paper>

      {/* PRD Rejection Dialog */}
      <Dialog
        open={isRejectDialogOpen}
        onClose={handleCloseRejectDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject PRD</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this PRD (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={rejectionReason}
            onChange={(e) => setRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseRejectDialog} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleRejectPrd}
            color="error"
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? 'Rejecting...' : 'Reject PRD'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* System Design Rejection Dialog */}
      <Dialog
        open={isSystemDesignRejectDialogOpen}
        onClose={handleCloseSystemDesignRejectDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject System Design</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this System Design (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={systemDesignRejectionReason}
            onChange={(e) => setSystemDesignRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={handleCloseSystemDesignRejectDialog}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleRejectSystemDesign}
            color="error"
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? 'Rejecting...' : 'Reject System Design'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Financial Estimate Rejection Dialogs */}

      {/* Effort Estimate Rejection Dialog */}
      <Dialog
        open={isEffortRejectDialogOpen}
        onClose={handleCloseEffortRejectDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject Effort Estimate</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this Effort Estimate
            (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={effortRejectionReason}
            onChange={(e) => setEffortRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEffortRejectDialog} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleRejectEffortEstimate}
            color="error"
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? 'Rejecting...' : 'Reject Effort Estimate'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Cost Estimate Rejection Dialog */}
      <Dialog
        open={isCostRejectDialogOpen}
        onClose={handleCloseCostRejectDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject Cost Estimate</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this Cost Estimate (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={costRejectionReason}
            onChange={(e) => setCostRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCostRejectDialog} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleRejectCostEstimate}
            color="error"
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? 'Rejecting...' : 'Reject Cost Estimate'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Value Projection Rejection Dialog */}
      <Dialog
        open={isValueRejectDialogOpen}
        onClose={handleCloseValueRejectDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject Value Projection</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this Value Projection
            (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={valueRejectionReason}
            onChange={(e) => setValueRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseValueRejectDialog} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleRejectValueProjection}
            color="error"
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? 'Rejecting...' : 'Reject Value Projection'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Final Business Case Rejection Dialog */}
      <Dialog
        open={isFinalRejectDialogOpen}
        onClose={handleCloseFinalRejectDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Reject Final Business Case</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Please provide a reason for rejecting this business case (optional):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            value={finalRejectionReason}
            onChange={(e) => setFinalRejectionReason(e.target.value)}
            placeholder="Enter reason for rejection..."
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseFinalRejectDialog} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleRejectFinalCase}
            color="error"
            variant="contained"
            disabled={isLoading}
          >
            {isLoading ? 'Rejecting...' : 'Reject Business Case'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default BusinessCaseDetailPage;

import { useState, useEffect } from 'react';
import { HttpAdminAdapter } from '../services/admin/HttpAdminAdapter';
import { useAuth } from './useAuth';
import Logger from '../utils/logger';

const logger = Logger.create('useStageApproverConfig');

export interface StageApproverRoles {
  PRD?: string;
  SystemDesign?: string;
  EffortEstimate?: string;
  CostEstimate?: string;
  ValueProjection?: string;
  FinancialModel?: string;
  FinalApproval?: string;
}

const DEFAULT_STAGE_APPROVER_ROLES: StageApproverRoles = {
  PRD: 'PRODUCT_OWNER',
  SystemDesign: 'DEVELOPER', 
  EffortEstimate: 'DEVELOPER',
  CostEstimate: 'FINANCE_APPROVER',
  ValueProjection: 'SALES_MANAGER',
  FinancialModel: 'FINANCE_APPROVER',
  FinalApproval: 'FINAL_APPROVER'
};

/**
 * Hook to fetch and cache stage approver role configuration.
 * Falls back to sensible defaults if configuration cannot be fetched.
 */
export const useStageApproverConfig = () => {
  const [stageApproverRoles, setStageApproverRoles] = useState<StageApproverRoles>(DEFAULT_STAGE_APPROVER_ROLES);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { currentUser, isAdmin } = useAuth();

  useEffect(() => {
    const fetchStageApproverConfig = async () => {
      // Only fetch if user is authenticated
      if (!currentUser) {
        return;
      }

      setIsLoading(true);
      setError(null);
      
      try {
        // Create admin service instance to try to fetch the configuration
        const adminService = new HttpAdminAdapter();
        const config = await adminService.getStageApproverRoleSettings();
        setStageApproverRoles(config.stageApproverRoles || DEFAULT_STAGE_APPROVER_ROLES);
        logger.debug('Stage approver configuration fetched successfully', config.stageApproverRoles);
      } catch (err) {
        // If user is not admin or there's an error, fall back to defaults
        logger.debug('Failed to fetch stage approver configuration, using defaults:', err);
        setStageApproverRoles(DEFAULT_STAGE_APPROVER_ROLES);
        setError(null); // Don't show error to user, just use defaults
      } finally {
        setIsLoading(false);
      }
    };

    fetchStageApproverConfig();
  }, [currentUser, isAdmin]);

  /**
   * Check if the current user can approve/reject a specific stage
   */
  const canApproveStage = (stageName: keyof StageApproverRoles, userRole: string | null): boolean => {
    // Admin can always approve any stage
    if (userRole === 'ADMIN') {
      return true;
    }

    // Check if user has the configured role for this stage
    const requiredRole = stageApproverRoles[stageName];
    return requiredRole ? userRole === requiredRole : false;
  };

  return {
    stageApproverRoles,
    isLoading,
    error,
    canApproveStage,
  };
}; 
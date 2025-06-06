import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StatusBadge from '../StatusBadge';

describe('StatusBadge Component', () => {
  describe('Status Display', () => {
    it('should render status text correctly', () => {
      render(<StatusBadge status="INTAKE" />);
      expect(screen.getByText('INTAKE')).toBeInTheDocument();
    });

    it('should handle empty status gracefully', () => {
      render(<StatusBadge status="" />);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should handle undefined status', () => {
      render(<StatusBadge status={undefined as any} />);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });
  });

  describe('Color Mapping', () => {
    const statusColorTests = [
      // Initial stages
      { status: 'INTAKE', expectedColor: 'info', description: 'intake stage' },
      { status: 'PRD_DRAFTING', expectedColor: 'warning', description: 'PRD drafting' },
      { status: 'PRD_REVIEW', expectedColor: 'secondary', description: 'PRD review' },
      { status: 'PRD_APPROVED', expectedColor: 'success', description: 'PRD approved' },
      { status: 'PRD_REJECTED', expectedColor: 'error', description: 'PRD rejected' },
      
      // System Design stages
      { status: 'SYSTEM_DESIGN_DRAFTING', expectedColor: 'warning', description: 'system design drafting' },
      { status: 'SYSTEM_DESIGN_DRAFTED', expectedColor: 'info', description: 'system design drafted' },
      { status: 'SYSTEM_DESIGN_PENDING_REVIEW', expectedColor: 'secondary', description: 'system design pending review' },
      { status: 'SYSTEM_DESIGN_APPROVED', expectedColor: 'success', description: 'system design approved' },
      { status: 'SYSTEM_DESIGN_REJECTED', expectedColor: 'error', description: 'system design rejected' },
      
      // Planning stages
      { status: 'PLANNING_IN_PROGRESS', expectedColor: 'warning', description: 'planning in progress' },
      { status: 'PLANNING_COMPLETE', expectedColor: 'primary', description: 'planning complete' },
      
      // Effort estimation stages
      { status: 'EFFORT_PENDING_REVIEW', expectedColor: 'secondary', description: 'effort pending review' },
      { status: 'EFFORT_APPROVED', expectedColor: 'success', description: 'effort approved' },
      { status: 'EFFORT_REJECTED', expectedColor: 'error', description: 'effort rejected' },
      
      // Cost estimation stages
      { status: 'COSTING_IN_PROGRESS', expectedColor: 'warning', description: 'costing in progress' },
      { status: 'COSTING_COMPLETE', expectedColor: 'primary', description: 'costing complete' },
      { status: 'COSTING_PENDING_REVIEW', expectedColor: 'secondary', description: 'costing pending review' },
      { status: 'COSTING_APPROVED', expectedColor: 'success', description: 'costing approved' },
      { status: 'COSTING_REJECTED', expectedColor: 'error', description: 'costing rejected' },
      
      // Value analysis stages
      { status: 'VALUE_ANALYSIS_IN_PROGRESS', expectedColor: 'warning', description: 'value analysis in progress' },
      { status: 'VALUE_ANALYSIS_COMPLETE', expectedColor: 'primary', description: 'value analysis complete' },
      { status: 'VALUE_PENDING_REVIEW', expectedColor: 'secondary', description: 'value pending review' },
      { status: 'VALUE_APPROVED', expectedColor: 'success', description: 'value approved' },
      { status: 'VALUE_REJECTED', expectedColor: 'error', description: 'value rejected' },
      
      // Financial model stages
      { status: 'FINANCIAL_MODEL_IN_PROGRESS', expectedColor: 'warning', description: 'financial model in progress' },
      { status: 'FINANCIAL_MODEL_COMPLETE', expectedColor: 'primary', description: 'financial model complete' },
      { status: 'FINANCIAL_ANALYSIS', expectedColor: 'primary', description: 'financial analysis' },
      
      // Final approval stages
      { status: 'FINAL_REVIEW', expectedColor: 'secondary', description: 'final review' },
      { status: 'PENDING_FINAL_APPROVAL', expectedColor: 'warning', description: 'pending final approval' },
      { status: 'APPROVED', expectedColor: 'success', description: 'approved' },
      { status: 'REJECTED', expectedColor: 'error', description: 'rejected' },
    ];

    statusColorTests.forEach(({ status, expectedColor, description }) => {
      it(`should apply ${expectedColor} color for ${description}`, () => {
        const { container } = render(<StatusBadge status={status} />);
        const chip = container.querySelector('.MuiChip-root');
        expect(chip).toHaveClass(`MuiChip-color${expectedColor.charAt(0).toUpperCase() + expectedColor.slice(1)}`);
      });
    });

    it('should use default color for unknown status', () => {
      const { container } = render(<StatusBadge status="UNKNOWN_STATUS" />);
      const chip = container.querySelector('.MuiChip-root');
      expect(chip).toHaveClass('MuiChip-colorDefault');
    });
  });

  describe('Component Props', () => {
    it('should apply custom size prop', () => {
      const { container } = render(<StatusBadge status="INTAKE" size="medium" />);
      const chip = container.querySelector('.MuiChip-root');
      expect(chip).toHaveClass('MuiChip-sizeMedium');
    });

    it('should apply small size by default', () => {
      const { container } = render(<StatusBadge status="INTAKE" />);
      const chip = container.querySelector('.MuiChip-root');
      expect(chip).toHaveClass('MuiChip-sizeSmall');
    });

    it('should apply custom variant prop', () => {
      const { container } = render(<StatusBadge status="INTAKE" variant="outlined" />);
      const chip = container.querySelector('.MuiChip-root');
      expect(chip).toHaveClass('MuiChip-outlined');
    });

    it('should apply filled variant by default', () => {
      const { container } = render(<StatusBadge status="INTAKE" />);
      const chip = container.querySelector('.MuiChip-root');
      expect(chip).toHaveClass('MuiChip-filled');
    });
  });

  describe('Accessibility', () => {
    it('should have proper role for screen readers', () => {
      render(<StatusBadge status="APPROVED" />);
      expect(screen.getByRole('button')).toBeInTheDocument();
    });

    it('should be readable by screen readers', () => {
      render(<StatusBadge status="PENDING_FINAL_APPROVAL" />);
      const chip = screen.getByRole('button');
      expect(chip).toHaveAccessibleName('PENDING_FINAL_APPROVAL');
    });
  });

  describe('Visual States', () => {
    it('should render success states with green color', () => {
      const successStatuses = ['PRD_APPROVED', 'SYSTEM_DESIGN_APPROVED', 'EFFORT_APPROVED', 'COSTING_APPROVED', 'VALUE_APPROVED', 'APPROVED'];
      
      successStatuses.forEach(status => {
        const { container } = render(<StatusBadge status={status} />);
        const chip = container.querySelector('.MuiChip-root');
        expect(chip).toHaveClass('MuiChip-colorSuccess');
      });
    });

    it('should render error states with red color', () => {
      const errorStatuses = ['PRD_REJECTED', 'SYSTEM_DESIGN_REJECTED', 'EFFORT_REJECTED', 'COSTING_REJECTED', 'VALUE_REJECTED', 'REJECTED'];
      
      errorStatuses.forEach(status => {
        const { container } = render(<StatusBadge status={status} />);
        const chip = container.querySelector('.MuiChip-root');
        expect(chip).toHaveClass('MuiChip-colorError');
      });
    });

    it('should render warning states with yellow color', () => {
      const warningStatuses = ['PRD_DRAFTING', 'SYSTEM_DESIGN_DRAFTING', 'PLANNING_IN_PROGRESS', 'COSTING_IN_PROGRESS', 'VALUE_ANALYSIS_IN_PROGRESS', 'FINANCIAL_MODEL_IN_PROGRESS', 'PENDING_FINAL_APPROVAL'];
      
      warningStatuses.forEach(status => {
        const { container } = render(<StatusBadge status={status} />);
        const chip = container.querySelector('.MuiChip-root');
        expect(chip).toHaveClass('MuiChip-colorWarning');
      });
    });
  });
}); 
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import StatusFilter from '../StatusFilter';

describe('StatusFilter Component', () => {
  const mockOnStatusChange = vi.fn();
  const defaultProps = {
    allStatuses: ['INTAKE', 'PRD_DRAFTING', 'APPROVED', 'REJECTED'],
    selectedStatus: '',
    onStatusChange: mockOnStatusChange,
  };

  beforeEach(() => {
    mockOnStatusChange.mockClear();
  });

  describe('Basic Rendering', () => {
    it('should render filter icon button', () => {
      render(<StatusFilter {...defaultProps} />);
      expect(screen.getByRole('button')).toBeInTheDocument();
      expect(screen.getByLabelText(/filter by status/i)).toBeInTheDocument();
    });

    it('should show default tooltip text when no status selected', () => {
      render(<StatusFilter {...defaultProps} />);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Filter by status. Current filter: All Statuses');
    });

    it('should show selected status in tooltip when status is selected', () => {
      render(<StatusFilter {...defaultProps} selectedStatus="INTAKE" />);
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Filter by status. Current filter: Intake');
    });

    it('should apply small size by default', () => {
      const { container } = render(<StatusFilter {...defaultProps} />);
      const button = container.querySelector('.MuiIconButton-sizeSmall');
      expect(button).toBeInTheDocument();
    });

    it('should apply custom size prop', () => {
      const { container } = render(<StatusFilter {...defaultProps} size="medium" />);
      const button = container.querySelector('.MuiIconButton-sizeMedium');
      expect(button).toBeInTheDocument();
    });
  });

  describe('Visual States', () => {
    it('should have primary color when status is selected', () => {
      const { container } = render(<StatusFilter {...defaultProps} selectedStatus="INTAKE" />);
      const button = container.querySelector('.MuiIconButton-root');
      expect(button).toHaveStyle({ color: 'rgb(25, 118, 210)' }); // MUI primary color
    });

    it('should have secondary color when no status is selected', () => {
      const { container } = render(<StatusFilter {...defaultProps} />);
      const button = container.querySelector('.MuiIconButton-root');
      expect(button).toHaveStyle({ color: 'rgba(0, 0, 0, 0.6)' }); // MUI text.secondary color
    });
  });

  describe('Menu Interaction', () => {
    it('should open menu when button is clicked', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      expect(screen.getByRole('menu')).toBeInTheDocument();
    });

    it('should show all statuses in menu', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      expect(screen.getByRole('menuitem', { name: 'All Statuses' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'Intake' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'Prd Drafting' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'Approved' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'Rejected' })).toBeInTheDocument();
    });

    it('should mark selected status as selected in menu', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} selectedStatus="INTAKE" />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      const selectedItem = screen.getByRole('menuitem', { name: 'Intake' });
      expect(selectedItem).toHaveAttribute('aria-selected', 'true');
    });

    it('should mark "All Statuses" as selected when no status is selected', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      const allStatusesItem = screen.getByRole('menuitem', { name: 'All Statuses' });
      expect(allStatusesItem).toHaveAttribute('aria-selected', 'true');
    });

    it('should close menu when clicking outside', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      expect(screen.getByRole('menu')).toBeInTheDocument();

      // Click outside
      await user.click(document.body);
      await waitFor(() => {
        expect(screen.queryByRole('menu')).not.toBeInTheDocument();
      });
    });

    it('should close menu when escape key is pressed', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      expect(screen.getByRole('menu')).toBeInTheDocument();

      await user.keyboard('{Escape}');
      await waitFor(() => {
        expect(screen.queryByRole('menu')).not.toBeInTheDocument();
      });
    });
  });

  describe('Status Selection', () => {
    it('should call onStatusChange with empty string when "All Statuses" is selected', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} selectedStatus="INTAKE" />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      const allStatusesItem = screen.getByRole('menuitem', { name: 'All Statuses' });
      await user.click(allStatusesItem);

      expect(mockOnStatusChange).toHaveBeenCalledWith('');
    });

    it('should call onStatusChange with status value when status is selected', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      const intakeItem = screen.getByRole('menuitem', { name: 'Intake' });
      await user.click(intakeItem);

      expect(mockOnStatusChange).toHaveBeenCalledWith('INTAKE');
    });

    it('should close menu after status selection', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      const intakeItem = screen.getByRole('menuitem', { name: 'Intake' });
      await user.click(intakeItem);

      await waitFor(() => {
        expect(screen.queryByRole('menu')).not.toBeInTheDocument();
      });
    });

    it('should handle complex status names correctly', async () => {
      const user = userEvent.setup();
      const complexProps = {
        ...defaultProps,
        allStatuses: ['SYSTEM_DESIGN_PENDING_REVIEW', 'VALUE_ANALYSIS_IN_PROGRESS', 'PENDING_FINAL_APPROVAL']
      };
      
      render(<StatusFilter {...complexProps} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      expect(screen.getByRole('menuitem', { name: 'System Design Pending Review' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'Value Analysis In Progress' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'Pending Final Approval' })).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes when closed', () => {
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-expanded', 'false');
      expect(button).toHaveAttribute('aria-haspopup', 'menu');
      expect(button).not.toHaveAttribute('aria-controls');
    });

    it('should have proper ARIA attributes when open', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      expect(button).toHaveAttribute('aria-expanded', 'true');
      expect(button).toHaveAttribute('aria-controls', 'status-filter-menu');
    });

    it('should support keyboard navigation in menu', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} />);
      
      const button = screen.getByRole('button');
      button.focus();
      await user.keyboard('{Enter}');

      const menu = screen.getByRole('menu');
      expect(menu).toBeInTheDocument();

      // Navigate with arrow keys
      await user.keyboard('{ArrowDown}');
      const intakeItem = screen.getByRole('menuitem', { name: 'Intake' });
      expect(intakeItem).toHaveFocus();

      // Select with Enter
      await user.keyboard('{Enter}');
      expect(mockOnStatusChange).toHaveBeenCalledWith('INTAKE');
    });
  });

  describe('Status Text Formatting', () => {
    it('should format snake_case status to title case', async () => {
      const user = userEvent.setup();
      const props = {
        ...defaultProps,
        allStatuses: ['PRD_DRAFTING', 'SYSTEM_DESIGN_APPROVED', 'VALUE_ANALYSIS_IN_PROGRESS']
      };
      
      render(<StatusFilter {...props} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      expect(screen.getByRole('menuitem', { name: 'Prd Drafting' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'System Design Approved' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'Value Analysis In Progress' })).toBeInTheDocument();
    });

    it('should handle single word status correctly', async () => {
      const user = userEvent.setup();
      const props = {
        ...defaultProps,
        allStatuses: ['APPROVED', 'REJECTED', 'INTAKE']
      };
      
      render(<StatusFilter {...props} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      expect(screen.getByRole('menuitem', { name: 'Approved' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'Rejected' })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: 'Intake' })).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty status array', async () => {
      const user = userEvent.setup();
      render(<StatusFilter {...defaultProps} allStatuses={[]} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      // Should only show "All Statuses" option
      expect(screen.getByRole('menuitem', { name: 'All Statuses' })).toBeInTheDocument();
      expect(screen.getAllByRole('menuitem')).toHaveLength(1);
    });

    it('should handle duplicate statuses in array', async () => {
      const user = userEvent.setup();
      const props = {
        ...defaultProps,
        allStatuses: ['INTAKE', 'INTAKE', 'APPROVED', 'APPROVED']
      };
      
      render(<StatusFilter {...props} />);
      
      const button = screen.getByRole('button');
      await user.click(button);

      // Should deduplicate and show each status only once (plus "All Statuses")
      const menuItems = screen.getAllByRole('menuitem');
      expect(menuItems).toHaveLength(3); // All Statuses + 2 unique statuses
    });

    it('should handle invalid selected status', () => {
      render(<StatusFilter {...defaultProps} selectedStatus="INVALID_STATUS" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Filter by status. Current filter: Invalid Status');
    });
  });
}); 
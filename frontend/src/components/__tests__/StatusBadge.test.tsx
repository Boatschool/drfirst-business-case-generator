// import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import StatusBadge from '../common/StatusBadge';

describe('StatusBadge', () => {
  it('should render status text correctly', () => {
    render(<StatusBadge status="APPROVED" />);
    
    expect(screen.getByText('Approved')).toBeInTheDocument();
  });

  it('should format status text with proper case', () => {
    render(<StatusBadge status="PRD_PENDING_REVIEW" />);
    
    expect(screen.getByText('Prd Pending Review')).toBeInTheDocument();
  });

  it('should render as a chip component', () => {
    render(<StatusBadge status="APPROVED" />);
    
    // Material-UI Chip renders as a div with specific classes
    const chipElement = screen.getByText('Approved').closest('div');
    expect(chipElement).toHaveClass('MuiChip-root');
  });

  it('should apply different colors based on status', () => {
    const { rerender } = render(<StatusBadge status="APPROVED" />);
    
    let chipElement = screen.getByText('Approved').closest('div');
    expect(chipElement).toHaveClass('MuiChip-colorSuccess');
    
    rerender(<StatusBadge status="REJECTED" />);
    chipElement = screen.getByText('Rejected').closest('div');
    expect(chipElement).toHaveClass('MuiChip-colorError');
    
    rerender(<StatusBadge status="PRD_DRAFTING" />);
    chipElement = screen.getByText('Prd Drafting').closest('div');
    expect(chipElement).toHaveClass('MuiChip-colorWarning');
  });

  it('should use default color for unknown status', () => {
    render(<StatusBadge status="UNKNOWN_STATUS" />);
    
    const chipElement = screen.getByText('Unknown Status').closest('div');
    expect(chipElement).toHaveClass('MuiChip-colorDefault');
  });

  it('should support different sizes', () => {
    render(<StatusBadge status="APPROVED" size="medium" />);
    
    const chipElement = screen.getByText('Approved').closest('div');
    expect(chipElement).toHaveClass('MuiChip-sizeMedium');
  });

  it('should support different variants', () => {
    render(<StatusBadge status="APPROVED" variant="outlined" />);
    
    const chipElement = screen.getByText('Approved').closest('div');
    expect(chipElement).toHaveClass('MuiChip-outlined');
  });

  describe('status color mapping', () => {
    const statusTests = [
      { status: 'APPROVED', expectedColor: 'Success' },
      { status: 'REJECTED', expectedColor: 'Error' },
      { status: 'PRD_DRAFTING', expectedColor: 'Warning' },
      { status: 'PRD_APPROVED', expectedColor: 'Success' },
      { status: 'SYSTEM_DESIGN_PENDING_REVIEW', expectedColor: 'Secondary' },
      { status: 'FINANCIAL_ANALYSIS', expectedColor: 'Primary' },
    ];

    statusTests.forEach(({ status, expectedColor }) => {
      it(`should apply ${expectedColor} color for ${status}`, () => {
        render(<StatusBadge status={status} />);
        
        const formattedText = status
          .replace(/_/g, ' ')
          .toLowerCase()
          .split(' ')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' ');
          
        const chipElement = screen.getByText(formattedText).closest('div');
        expect(chipElement).toHaveClass(`MuiChip-color${expectedColor}`);
      });
    });
  });

  describe('text formatting', () => {
    const formattingTests = [
      { input: 'PRD_DRAFTING', expected: 'Prd Drafting' },
      { input: 'SYSTEM_DESIGN_PENDING_REVIEW', expected: 'System Design Pending Review' },
      { input: 'FINANCIAL_ANALYSIS', expected: 'Financial Analysis' },
      { input: 'APPROVED', expected: 'Approved' },
      { input: 'COSTING_IN_PROGRESS', expected: 'Costing In Progress' },
    ];

    formattingTests.forEach(({ input, expected }) => {
      it(`should format "${input}" as "${expected}"`, () => {
        render(<StatusBadge status={input} />);
        
        expect(screen.getByText(expected)).toBeInTheDocument();
      });
    });
  });
}); 
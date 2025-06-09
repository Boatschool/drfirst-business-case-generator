/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ProgressStepper from '../ProgressStepper';

// Mock useParams to return a test caseId
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom') as any;
  return {
    ...actual,
    useParams: () => ({ caseId: 'test-case-id' }),
    useNavigate: () => vi.fn(),
  };
});

const theme = createTheme();

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <MemoryRouter>
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    </MemoryRouter>
  );
};

describe('ProgressStepper', () => {
  it('renders the progress stepper with correct title', () => {
    renderWithProviders(
      <ProgressStepper currentCaseStatus="PRD_DRAFTING" />
    );
    
    expect(screen.getByText('Business Case Progress')).toBeInTheDocument();
  });

  it('displays all workflow stages', () => {
    renderWithProviders(
      <ProgressStepper currentCaseStatus="PRD_DRAFTING" />
    );
    
    // Check for the main stage labels (using getAllByText since they appear multiple times)
    expect(screen.getAllByText('Intake & PRD Creation')).toHaveLength(2); // In stepper and current stage
    expect(screen.getByText('PRD Review & Approval')).toBeInTheDocument();
    expect(screen.getByText('System Design')).toBeInTheDocument();
    expect(screen.getByText('Final Review & Approval')).toBeInTheDocument();
  });

  it('shows current stage information', () => {
    renderWithProviders(
      <ProgressStepper currentCaseStatus="PRD_DRAFTING" />
    );
    
    expect(screen.getByText('Current Stage:')).toBeInTheDocument();
    expect(screen.getAllByText('Intake & PRD Creation')).toHaveLength(2); // In stepper and current stage
    expect(screen.getByText('Status:')).toBeInTheDocument();
    expect(screen.getByText('PRD DRAFTING')).toBeInTheDocument();
  });

  it('handles completed status correctly', () => {
    renderWithProviders(
      <ProgressStepper currentCaseStatus="APPROVED" />
    );
    
    expect(screen.getAllByText('Final Review & Approval')).toHaveLength(2); // In stepper and current stage
    expect(screen.getByText('APPROVED')).toBeInTheDocument();
  });

  it('can be disabled for navigation', () => {
    renderWithProviders(
      <ProgressStepper currentCaseStatus="PRD_DRAFTING" enableNavigation={false} />
    );
    
    // Should still render the stepper
    expect(screen.getByText('Business Case Progress')).toBeInTheDocument();
  });
}); 
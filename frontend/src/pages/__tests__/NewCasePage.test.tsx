/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-non-null-assertion */
import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import NewCasePage from '../NewCasePage';
import { AgentContext } from '../../contexts/AgentContext';
import { AuthContext } from '../../contexts/AuthContext';
import userEvent from '@testing-library/user-event';

// Mock react-router-dom navigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom') as any;
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Create controllable mocks
const mockInitiateBusinessCase = vi.fn().mockResolvedValue({ caseId: 'test-case-123' });
const mockClearError = vi.fn();

// Mock React's useContext when used with AgentContext
vi.mock('react', async () => {
  const actual = await vi.importActual('react') as any;
  return {
    ...actual,
    useContext: vi.fn((context: any) => {
      if (context.displayName === 'AgentContext' || context._currentValue !== undefined) {
        return {
          initiateBusinessCase: mockInitiateBusinessCase,
          isLoading: false,
          error: null,
          clearError: mockClearError,
        };
      }
      return (actual as any).useContext(context);
    }),
  };
});

// Mock components to focus on NewCasePage logic
vi.mock('../../components/common/Breadcrumbs', () => ({
  Breadcrumbs: ({ items }: { items: any[] }) => (
    <nav data-testid="breadcrumbs">
      {items.map((item, index) => (
        <span key={index}>{item.label}</span>
      ))}
    </nav>
  ),
}));

// Mock auth context
const mockAuthContextValue = {
  currentUser: {
    uid: 'test-user-id',
    email: 'test@example.com',
    displayName: 'Test User',
    photoURL: null,
    emailVerified: true,
    systemRole: 'PRODUCT_OWNER',
  },
  loading: false,
  error: null,
  signUp: vi.fn(),
  signIn: vi.fn(),
  signInWithGoogle: vi.fn(),
  signOut: vi.fn(),
  getIdToken: vi.fn(),
  getIdTokenResult: vi.fn(),
  refreshIdToken: vi.fn(),
  isDrFirstUser: true,
  isValidUser: true,
  systemRole: 'PRODUCT_OWNER',
  isAdmin: false,
  isDeveloper: false,
  isSalesManager: false,
  isFinanceApprover: false,
  isProductOwner: true,
  isFinalApprover: false,
};

// Mock agent context
const mockAgentContextValue = {
  // State
  isLoading: false,
  isLoadingCases: false,
  isLoadingCaseDetails: false,
  error: null,
  casesError: null,
  caseDetailsError: null,
  currentCaseId: null,
  cases: [],
  messages: [],
  currentCaseDetails: null,
  
  // Methods
  initiateBusinessCase: vi.fn().mockResolvedValue({ caseId: 'new-case-123' }),
  sendFeedbackToAgent: vi.fn(),
  fetchUserCases: vi.fn(),
  fetchCaseDetails: vi.fn(),
  updatePrdDraft: vi.fn(),
  updateStatus: vi.fn(),
  submitPrdForReview: vi.fn(),
  approvePrd: vi.fn(),
  rejectPrd: vi.fn(),
  updateSystemDesign: vi.fn(),
  submitSystemDesignForReview: vi.fn(),
  approveSystemDesign: vi.fn(),
  rejectSystemDesign: vi.fn(),
  triggerSystemDesignGeneration: vi.fn(),
  triggerEffortEstimateGeneration: vi.fn(),
  triggerCostAnalysisGeneration: vi.fn(),
  triggerValueAnalysisGeneration: vi.fn(),
  triggerFinancialModelGeneration: vi.fn(),
  updateEffortEstimate: vi.fn(),
  submitEffortEstimateForReview: vi.fn(),
  approveEffortEstimate: vi.fn(),
  rejectEffortEstimate: vi.fn(),
  updateCostEstimate: vi.fn(),
  submitCostEstimateForReview: vi.fn(),
  approveCostEstimate: vi.fn(),
  rejectCostEstimate: vi.fn(),
  updateValueProjection: vi.fn(),
  submitValueProjectionForReview: vi.fn(),
  approveValueProjection: vi.fn(),
  rejectValueProjection: vi.fn(),
  submitFinancialModelForReview: vi.fn(),
  approveFinancialModel: vi.fn(),
  rejectFinancialModel: vi.fn(),
  submitCaseForFinalApproval: vi.fn(),
  approveFinalCase: vi.fn(),
  rejectFinalCase: vi.fn(),
  exportCaseToPdf: vi.fn(),
  clearError: vi.fn(),
  clearAgentState: vi.fn(),
  clearCurrentCaseDetails: vi.fn(),
};

// Test wrapper component
const TestWrapper: React.FC<{ 
  children: React.ReactNode;
  agentContextOverrides?: Partial<typeof mockAgentContextValue>;
  authContextOverrides?: Partial<typeof mockAuthContextValue>;
}> = ({ 
  children, 
  agentContextOverrides = {}, 
  authContextOverrides = {} 
}) => {
  const agentValue = { ...mockAgentContextValue, ...agentContextOverrides };
  const authValue = { ...mockAuthContextValue, ...authContextOverrides };

  return (
    <BrowserRouter>
      <AuthContext.Provider value={authValue}>
        <AgentContext.Provider value={agentValue}>
          {children}
        </AgentContext.Provider>
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('NewCasePage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Page Rendering', () => {
    it('should render the new case form', () => {
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      expect(screen.getByText('Initiate New Business Case')).toBeInTheDocument();
      expect(screen.getByLabelText(/project title/i)).toBeInTheDocument();
      expect(screen.getByRole('textbox', { name: /problem statement/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /initiate case/i })).toBeInTheDocument();
    });

    it('should show form fields with proper labels and placeholders', () => {
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });

      expect(projectTitleInput).toHaveAttribute('placeholder');
      expect(problemStatementTextarea).toHaveAttribute('placeholder');
      expect(projectTitleInput).toBeRequired();
      expect(problemStatementTextarea).toBeRequired();
    });

    it('should render the relevant links section', () => {
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      expect(screen.getByText(/relevant links/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /add another link/i })).toBeInTheDocument();
    });
  });

  describe.skip('Form Validation', () => {
    it('should show validation errors for empty required fields', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /initiate case/i });
      
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/project title is required/i)).toBeInTheDocument();
        expect(screen.getByText(/problem statement is required/i)).toBeInTheDocument();
      });
    });

    it('should validate minimum length for problem statement', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      const submitButton = screen.getByRole('button', { name: /initiate case/i });

      await user.type(projectTitleInput, 'Test Project');
      await user.type(problemStatementTextarea, 'Too short');
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/problem statement must be at least/i)).toBeInTheDocument();
      });
    });

    it('should validate maximum length for fields', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      
      // Type a very long title
      const longTitle = 'A'.repeat(201);
      await user.type(projectTitleInput, longTitle);

      const submitButton = screen.getByRole('button', { name: /initiate case/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/project title must be at most/i)).toBeInTheDocument();
      });
    });

    it('should clear validation errors when fields become valid', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      const submitButton = screen.getByRole('button', { name: /initiate case/i });

      // Trigger validation errors
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/project title is required/i)).toBeInTheDocument();
      });

      // Fix the validation errors
      await user.type(projectTitleInput, 'Valid Project Title');
      await user.type(problemStatementTextarea, 'This is a valid problem statement that meets the minimum length requirement for the form validation.');

      // Errors should clear as user types
      await waitFor(() => {
        expect(screen.queryByText(/project title is required/i)).not.toBeInTheDocument();
        expect(screen.queryByText(/problem statement is required/i)).not.toBeInTheDocument();
      });
    });
  });

  describe.skip('Relevant Links Management', () => {
    it('should add a new link when Add Link button is clicked', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const addButton = screen.getByRole('button', { name: /add link/i });
      
      await user.click(addButton);

      await waitFor(() => {
        expect(screen.getByLabelText(/link name/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/url/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /remove/i })).toBeInTheDocument();
      });
    });

    it('should remove a link when remove button is clicked', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const addButton = screen.getByRole('button', { name: /add link/i });
      
      // Add a link
      await user.click(addButton);

      const removeButton = screen.getByRole('button', { name: /remove/i });
      
      // Remove the link
      await user.click(removeButton);

      await waitFor(() => {
        expect(screen.queryByLabelText(/link name/i)).not.toBeInTheDocument();
        expect(screen.queryByLabelText(/url/i)).not.toBeInTheDocument();
      });
    });

    it('should validate link fields when links are added', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const addButton = screen.getByRole('button', { name: /add link/i });
      
      // Add a link
      await user.click(addButton);

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      const submitButton = screen.getByRole('button', { name: /initiate case/i });

      // Fill required fields but leave link fields empty
      await user.type(projectTitleInput, 'Test Project');
      await user.type(problemStatementTextarea, 'This is a valid problem statement that meets the minimum length requirement.');
      
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/link name is required/i)).toBeInTheDocument();
        expect(screen.getByText(/url is required/i)).toBeInTheDocument();
      });
    });

    it('should validate URL format', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const addButton = screen.getByRole('button', { name: /add link/i });
      
      // Add a link
      await user.click(addButton);

      const linkNameInput = screen.getByLabelText(/link name/i);
      const urlInput = screen.getByLabelText(/url/i);
      const submitButton = screen.getByRole('button', { name: /initiate case/i });

      await user.type(linkNameInput, 'Test Link');
      await user.type(urlInput, 'invalid-url');
      
      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      await user.type(projectTitleInput, 'Test Project');
      await user.type(problemStatementTextarea, 'This is a valid problem statement that meets the minimum length requirement.');
      
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter a valid url/i)).toBeInTheDocument();
      });
    });
  });

  describe.skip('Form Submission', () => {
    it('should call initiateBusinessCase with correct data on valid form submission', async () => {
      const user = userEvent.setup();
      
      // Reset and configure the mock for this test
      mockInitiateBusinessCase.mockClear();
      mockInitiateBusinessCase.mockResolvedValue({
        caseId: 'new-case-123',
        initialMessage: 'Case created successfully'
      });
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      const submitButton = screen.getByRole('button', { name: /initiate case/i });

      await user.type(projectTitleInput, 'My Test Project');
      await user.type(problemStatementTextarea, 'This is a comprehensive problem statement that describes the issue we need to solve with this business case.');
      
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockInitiateBusinessCase).toHaveBeenCalledWith({
          projectTitle: 'My Test Project',
          problemStatement: 'This is a comprehensive problem statement that describes the issue we need to solve with this business case.',
          relevantLinks: []
        });
      });
    });

    it('should include relevant links in submission data', async () => {
      const user = userEvent.setup();
      const mockInitiateBusinessCase = vi.fn().mockResolvedValue({
        caseId: 'new-case-123',
        initialMessage: 'Case created successfully'
      });
      
      render(
        <TestWrapper agentContextOverrides={{ initiateBusinessCase: mockInitiateBusinessCase }}>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      const addButton = screen.getByRole('button', { name: /add link/i });

      await user.type(projectTitleInput, 'My Test Project');
      await user.type(problemStatementTextarea, 'This is a comprehensive problem statement that describes the issue we need to solve.');
      
      // Add a link
      await user.click(addButton);
      
      const linkNameInput = screen.getByLabelText(/link name/i);
      const urlInput = screen.getByLabelText(/url/i);
      
      await user.type(linkNameInput, 'Confluence Doc');
      await user.type(urlInput, 'https://example.com/doc');

      const submitButton = screen.getByRole('button', { name: /initiate case/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockInitiateBusinessCase).toHaveBeenCalledWith({
          projectTitle: 'My Test Project',
          problemStatement: 'This is a comprehensive problem statement that describes the issue we need to solve.',
          relevantLinks: [
            {
              name: 'Confluence Doc',
              url: 'https://example.com/doc'
            }
          ]
        });
      });
    });

    it('should show loading state during submission', async () => {
      const user = userEvent.setup();
      let resolvePromise: (value: any) => void;
      const pendingPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });
      
      const mockInitiateBusinessCase = vi.fn().mockReturnValue(pendingPromise);
      
      render(
        <TestWrapper agentContextOverrides={{ 
          initiateBusinessCase: mockInitiateBusinessCase,
          isLoading: true 
        }}>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });

      await user.type(projectTitleInput, 'Test Project');
      await user.type(problemStatementTextarea, 'This is a valid problem statement for testing loading state.');

      const submitButton = screen.getByRole('button', { name: /initiate case/i });
      await user.click(submitButton);

      // Button should be disabled and show loading state
      await waitFor(() => {
        const button = screen.getByRole('button', { name: /creating.../i });
        expect(button).toBeDisabled();
      });

      // Resolve the promise
      await act(async () => {
        resolvePromise!({ caseId: 'test-case', initialMessage: 'Success' });
      });
    });

    it('should navigate to case details on successful submission', async () => {
      const user = userEvent.setup();
      const mockInitiateBusinessCase = vi.fn().mockResolvedValue({
        caseId: 'new-case-123',
        initialMessage: 'Case created successfully'
      });
      
      render(
        <TestWrapper agentContextOverrides={{ initiateBusinessCase: mockInitiateBusinessCase }}>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      const submitButton = screen.getByRole('button', { name: /initiate case/i });

      await user.type(projectTitleInput, 'Test Project');
      await user.type(problemStatementTextarea, 'This is a valid problem statement for navigation testing.');
      
      await user.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith('/cases/new-case-123');
      });
    });

    it('should not submit when form has validation errors', async () => {
      const user = userEvent.setup();
      const mockInitiateBusinessCase = vi.fn();
      
      render(
        <TestWrapper agentContextOverrides={{ initiateBusinessCase: mockInitiateBusinessCase }}>
          <NewCasePage />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /initiate case/i });
      
      await user.click(submitButton);

      // Should show validation errors
      await waitFor(() => {
        expect(screen.getByText(/project title is required/i)).toBeInTheDocument();
      });

      // Should not call initiateBusinessCase
      expect(mockInitiateBusinessCase).not.toHaveBeenCalled();
    });
  });

  describe.skip('Error Handling', () => {
    it('should display error message when submission fails', async () => {
      const user = userEvent.setup();
      const mockInitiateBusinessCase = vi.fn().mockRejectedValue(new Error('Failed to create case'));
      
      render(
        <TestWrapper agentContextOverrides={{ 
          initiateBusinessCase: mockInitiateBusinessCase,
          error: null
        }}>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      const submitButton = screen.getByRole('button', { name: /initiate case/i });

      await user.type(projectTitleInput, 'Test Project');
      await user.type(problemStatementTextarea, 'This is a valid problem statement for error testing.');
      
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/failed to create case/i)).toBeInTheDocument();
      });
    });

    it('should clear error when user starts typing after an error', async () => {
      const user = userEvent.setup();
      const mockClearError = vi.fn();
      
      render(
        <TestWrapper agentContextOverrides={{ 
          error: null,
          clearError: mockClearError
        }}>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      
      await user.type(projectTitleInput, 'T');

      await waitFor(() => {
        expect(mockClearError).toHaveBeenCalled();
      });
    });
  });

  describe('User Experience', () => {
    it('should allow typing in problem statement field', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      
      await user.type(problemStatementTextarea, 'Test statement');

      expect(problemStatementTextarea).toHaveValue('Test statement');
    });

    it('should maintain form state when switching between fields', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });

      await user.type(projectTitleInput, 'My Project');
      await user.click(problemStatementTextarea);
      await user.type(problemStatementTextarea, 'Problem description');
      await user.click(projectTitleInput);

      expect(projectTitleInput).toHaveValue('My Project');
      expect(problemStatementTextarea).toHaveValue('Problem description');
    });

    it.skip('should focus on first error field when validation fails', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /initiate case/i });
      const projectTitleInput = screen.getByLabelText(/project title/i);
      
      await user.click(submitButton);

      await waitFor(() => {
        expect(projectTitleInput).toHaveFocus();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels and roles', () => {
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const form = screen.getByRole('form');
      expect(form).toBeInTheDocument();

      const projectTitleInput = screen.getByLabelText(/project title/i);
      const problemStatementTextarea = screen.getByRole('textbox', { name: /problem statement/i });
      const submitButton = screen.getByRole('button', { name: /initiate case/i });

      expect(projectTitleInput).toHaveAttribute('required');
      expect(problemStatementTextarea).toHaveAttribute('required');
      expect(submitButton).toBeInTheDocument();
    });

    it.skip('should associate error messages with form fields', async () => {
      const user = userEvent.setup();
      
      render(
        <TestWrapper>
          <NewCasePage />
        </TestWrapper>
      );

      const submitButton = screen.getByRole('button', { name: /initiate case/i });
      
      await user.click(submitButton);

      await waitFor(() => {
        const projectTitleInput = screen.getByLabelText(/project title/i);
        const errorMessage = screen.getByText(/project title is required/i);
        
        expect(projectTitleInput).toHaveAttribute('aria-describedby');
        expect(errorMessage).toHaveAttribute('id');
      });
    });
  });
}); 
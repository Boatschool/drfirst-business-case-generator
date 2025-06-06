import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ErrorDisplay, { FormErrorDisplay, LoadingErrorDisplay, PageErrorDisplay } from '../ErrorDisplay';

describe('ErrorDisplay Component', () => {
  const mockOnRetry = vi.fn();
  const mockOnClose = vi.fn();

  beforeEach(() => {
    mockOnRetry.mockClear();
    mockOnClose.mockClear();
  });

  describe('Basic Rendering', () => {
    it('should render error message', () => {
      render(<ErrorDisplay error="Something went wrong" />);
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    });

    it('should not render when no error provided', () => {
      const { container } = render(<ErrorDisplay />);
      expect(container.firstChild).toBeNull();
    });

    it('should render error icon', () => {
      render(<ErrorDisplay error="Error occurred" />);
      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });

    it('should apply error severity styling', () => {
      const { container } = render(<ErrorDisplay error="Error" />);
      const alert = container.querySelector('.MuiAlert-standardError');
      expect(alert).toBeInTheDocument();
    });

    it('should render with custom title', () => {
      render(<ErrorDisplay error="Failed" title="Custom Error Title" />);
      expect(screen.getByText('Custom Error Title')).toBeInTheDocument();
    });

    it('should render in compact mode', () => {
      render(<ErrorDisplay error="Error" compact={true} />);
      expect(screen.getByText('Error')).toBeInTheDocument();
    });
  });

  describe('Retry Functionality', () => {
    it('should render retry button when showRetry and onRetry props are provided', () => {
      render(<ErrorDisplay error="Network error" showRetry={true} onRetry={mockOnRetry} />);
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    it('should not render retry button when showRetry is false', () => {
      render(<ErrorDisplay error="Network error" showRetry={false} onRetry={mockOnRetry} />);
      expect(screen.queryByRole('button', { name: /try again/i })).not.toBeInTheDocument();
    });

    it('should call onRetry when retry button is clicked', async () => {
      const user = userEvent.setup();
      render(<ErrorDisplay error="Network error" showRetry={true} onRetry={mockOnRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /try again/i });
      await user.click(retryButton);
      
      expect(mockOnRetry).toHaveBeenCalledTimes(1);
    });

    it('should have proper button text for retry', () => {
      render(<ErrorDisplay error="Failed to load" showRetry={true} onRetry={mockOnRetry} />);
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });
  });

  describe('Close Functionality', () => {
    it('should render close button when showClose and onClose props are provided', () => {
      render(<ErrorDisplay error="Dismissible error" showClose={true} onClose={mockOnClose} />);
      expect(screen.getByRole('button', { name: /close/i })).toBeInTheDocument();
    });

    it('should call onClose when close button is clicked', async () => {
      const user = userEvent.setup();
      render(<ErrorDisplay error="Error" showClose={true} onClose={mockOnClose} />);
      
      const closeButton = screen.getByRole('button', { name: /close/i });
      await user.click(closeButton);
      
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Context Handling', () => {
    it('should accept context for error formatting', () => {
      render(<ErrorDisplay error="Failed" context="submit_form" />);
      expect(screen.getByText('Failed')).toBeInTheDocument();
    });
  });

  describe('Error Types', () => {
    it('should handle string errors', () => {
      render(<ErrorDisplay error="String error message" />);
      expect(screen.getByText('String error message')).toBeInTheDocument();
    });

    it('should handle Error objects', () => {
      const error = new Error('Error object message');
      render(<ErrorDisplay error={error} />);
      expect(screen.getByText('Error object message')).toBeInTheDocument();
    });

    it('should handle null error gracefully', () => {
      const { container } = render(<ErrorDisplay error={null} />);
      expect(container.firstChild).toBeNull();
    });
  });

  describe('Accessibility', () => {
    it('should have proper alert role', () => {
      render(<ErrorDisplay error="Access denied" />);
      const alert = screen.getByRole('alert');
      expect(alert).toBeInTheDocument();
    });

    it('should make retry button accessible', () => {
      render(<ErrorDisplay error="Load failed" showRetry={true} onRetry={mockOnRetry} />);
      const retryButton = screen.getByRole('button', { name: /try again/i });
      expect(retryButton).toBeInTheDocument();
      expect(retryButton).toHaveAccessibleName();
    });

    it('should be keyboard navigable', async () => {
      const user = userEvent.setup();
      render(<ErrorDisplay error="Error" showRetry={true} onRetry={mockOnRetry} />);
      
      const retryButton = screen.getByRole('button');
      retryButton.focus();
      expect(retryButton).toHaveFocus();
      
      await user.keyboard('{Enter}');
      expect(mockOnRetry).toHaveBeenCalledTimes(1);
    });
  });

  describe('Specialized Components', () => {
    describe('FormErrorDisplay', () => {
      it('should render form error with close button', () => {
        render(<FormErrorDisplay error="Form validation failed" onClose={mockOnClose} />);
        expect(screen.getByText('Form validation failed')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /close/i })).toBeInTheDocument();
      });

      it('should call onClose when close button is clicked', async () => {
        const user = userEvent.setup();
        render(<FormErrorDisplay error="Error" onClose={mockOnClose} />);
        
        const closeButton = screen.getByRole('button', { name: /close/i });
        await user.click(closeButton);
        
        expect(mockOnClose).toHaveBeenCalledTimes(1);
      });
    });

    describe('LoadingErrorDisplay', () => {
      it('should render loading error with retry button', () => {
        render(<LoadingErrorDisplay error="Failed to load data" onRetry={mockOnRetry} />);
        expect(screen.getByText('Failed to load data')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
      });

      it('should call onRetry when retry button is clicked', async () => {
        const user = userEvent.setup();
        render(<LoadingErrorDisplay error="Load error" onRetry={mockOnRetry} />);
        
        const retryButton = screen.getByRole('button', { name: /try again/i });
        await user.click(retryButton);
        
        expect(mockOnRetry).toHaveBeenCalledTimes(1);
      });

      it('should accept custom context', () => {
        render(<LoadingErrorDisplay error="Error" context="custom_context" onRetry={mockOnRetry} />);
        expect(screen.getByText('Error')).toBeInTheDocument();
      });
    });

    describe('PageErrorDisplay', () => {
      it('should render page error', () => {
        render(<PageErrorDisplay error="Page failed to load" />);
        expect(screen.getByText('Page failed to load')).toBeInTheDocument();
      });

      it('should render with retry when onRetry is provided', () => {
        render(<PageErrorDisplay error="Page error" onRetry={mockOnRetry} />);
        expect(screen.getByText('Page error')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
      });

      it('should not render retry when onRetry is not provided', () => {
        render(<PageErrorDisplay error="Page error" />);
        expect(screen.getByText('Page error')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: /try again/i })).not.toBeInTheDocument();
      });
    });
  });

  describe('Visual States', () => {
    it('should display error severity styling', () => {
      const { container } = render(<ErrorDisplay error="Critical error" />);
      const alert = container.querySelector('.MuiAlert-standardError');
      expect(alert).toBeInTheDocument();
    });

    it('should apply custom sx styling', () => {
      render(<ErrorDisplay error="Error" sx={{ mb: 5 }} />);
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });
}); 
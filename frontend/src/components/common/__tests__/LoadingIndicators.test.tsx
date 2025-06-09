import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  PageLoading,
  LoadingButton,
  InlineLoading,
  LoadingOverlay,
  ListSkeleton,
  TableSkeleton,
  CardSkeleton,
} from '../LoadingIndicators';

// Mock MUI icons
vi.mock('@mui/icons-material/Save', () => ({
  default: () => <div data-testid="save-icon">SaveIcon</div>,
}));

describe('LoadingIndicators Components', () => {
  describe('PageLoading Component', () => {
    it('should render spinner variant by default', () => {
      render(<PageLoading message="Loading..." />);
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('should render skeleton variant when specified', () => {
      render(<PageLoading message="Loading data..." variant="skeleton" skeletonLines={5} />);
      // Should render skeleton lines (skeleton variant doesn't show message text)
      const skeletonElements = document.querySelectorAll('.MuiSkeleton-root');
      expect(skeletonElements.length).toBeGreaterThan(0);
    });

    it('should render default number of skeleton lines when not specified', () => {
      render(<PageLoading message="Loading..." variant="skeleton" />);
      // Should render default skeleton lines (skeleton variant doesn't show message text)
      const skeletonElements = document.querySelectorAll('.MuiSkeleton-root');
      expect(skeletonElements.length).toBeGreaterThan(0);
    });

    it('should render without message', () => {
      render(<PageLoading />);
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<PageLoading message="Loading content..." />);
      const progressbar = screen.getByRole('progressbar');
      expect(progressbar).toHaveAttribute('aria-label', 'Loading content...');
    });

    it('should center content properly', () => {
      const { container } = render(<PageLoading message="Loading..." />);
      const containerDiv = container.firstChild;
      expect(containerDiv).toHaveStyle({
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      });
    });
  });

  describe('LoadingButton Component', () => {
    const mockOnClick = vi.fn();

    beforeEach(() => {
      mockOnClick.mockClear();
    });

    it('should render normal button when not loading', () => {
      render(
        <LoadingButton onClick={mockOnClick} loading={false}>
          Save Changes
        </LoadingButton>
      );
      expect(screen.getByRole('button', { name: 'Save Changes' })).toBeInTheDocument();
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });

    it('should render loading state with spinner', () => {
      render(
        <LoadingButton onClick={mockOnClick} loading={true} loadingText="Saving...">
          Save Changes
        </LoadingButton>
      );
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
      expect(screen.getByText('Saving...')).toBeInTheDocument();
      expect(screen.queryByText('Save Changes')).not.toBeInTheDocument();
    });

    it('should be disabled when loading', () => {
      render(
        <LoadingButton onClick={mockOnClick} loading={true}>
          Save Changes
        </LoadingButton>
      );
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
    });

    it('should be clickable when not loading', async () => {
      const user = userEvent.setup();
      render(
        <LoadingButton onClick={mockOnClick} loading={false}>
          Save Changes
        </LoadingButton>
      );
      
      const button = screen.getByRole('button');
      await user.click(button);
      expect(mockOnClick).toHaveBeenCalledTimes(1);
    });

    it('should not be clickable when loading', async () => {
      render(
        <LoadingButton onClick={mockOnClick} loading={true}>
          Save Changes
        </LoadingButton>
      );
      
      const button = screen.getByRole('button');
      expect(button).toBeDisabled();
      expect(mockOnClick).not.toHaveBeenCalled();
    });

    it('should preserve startIcon when not loading', () => {
      const SaveIcon = () => <div data-testid="save-icon">SaveIcon</div>;
      render(
        <LoadingButton onClick={mockOnClick} loading={false} startIcon={<SaveIcon />}>
          Save Changes
        </LoadingButton>
      );
      expect(screen.getByTestId('save-icon')).toBeInTheDocument();
    });

    it('should show loading text when provided', () => {
      render(
        <LoadingButton onClick={mockOnClick} loading={true} loadingText="Processing...">
          Submit
        </LoadingButton>
      );
      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });

    it('should show children text when no loading text provided', () => {
      render(
        <LoadingButton onClick={mockOnClick} loading={true}>
          Submit
        </LoadingButton>
      );
      expect(screen.getByText('Loading...')).toBeInTheDocument(); // Shows default loading text
    });

    it('should preserve button props like variant and color', () => {
      const { container } = render(
        <LoadingButton 
          onClick={mockOnClick} 
          loading={false} 
          variant="outlined" 
          color="secondary"
        >
          Save
        </LoadingButton>
      );
      const button = container.querySelector('.MuiButton-outlined');
      expect(button).toBeInTheDocument();
    });
  });

  describe('InlineLoading Component', () => {
    it('should render with default props', () => {
      render(<InlineLoading />);
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
    });

    it('should render with custom message', () => {
      render(<InlineLoading message="Loading configuration..." />);
      expect(screen.getByText('Loading configuration...')).toBeInTheDocument();
    });

    it('should render with custom size', () => {
      render(<InlineLoading size={32} />);
      const progressbar = screen.getByRole('progressbar');
      expect(progressbar).toHaveStyle({ width: '32px', height: '32px' });
    });

    it('should center content horizontally', () => {
      const { container } = render(<InlineLoading message="Loading..." />);
      const containerDiv = container.firstChild;
      expect(containerDiv).toHaveStyle({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      });
    });
  });

  describe('LoadingOverlay Component', () => {
    it('should render children when not loading', () => {
      render(
        <LoadingOverlay loading={false}>
          <div>Content</div>
        </LoadingOverlay>
      );
      expect(screen.getByText('Content')).toBeInTheDocument();
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });

    it('should render overlay when loading', () => {
      render(
        <LoadingOverlay loading={true} message="Processing...">
          <div>Content</div>
        </LoadingOverlay>
      );
      expect(screen.getByText('Content')).toBeInTheDocument();
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });

    it('should apply overlay styles when loading', () => {
      const { container } = render(
        <LoadingOverlay loading={true}>
          <div>Content</div>
        </LoadingOverlay>
      );
      // Check for overlay by looking for the Box with overlay styles
      const overlay = container.querySelector('.MuiBox-root');
      expect(overlay).toBeInTheDocument();
    });

    it('should render without message in overlay', () => {
      render(
        <LoadingOverlay loading={true}>
          <div>Content</div>
        </LoadingOverlay>
      );
      expect(screen.getByRole('progressbar')).toBeInTheDocument();
      expect(screen.getByText('Content')).toBeInTheDocument();
    });
  });

  describe('ListSkeleton Component', () => {
    it('should render default number of rows', () => {
      const { container } = render(<ListSkeleton />);
      const skeletonItems = container.querySelectorAll('.MuiSkeleton-root');
      expect(skeletonItems.length).toBeGreaterThanOrEqual(3); // Default rows
    });

    it('should render custom number of rows', () => {
      const { container } = render(<ListSkeleton rows={7} />);
      const skeletonRows = container.querySelectorAll('[role="listitem"]');
      expect(skeletonRows).toHaveLength(7);
    });

    it('should render without avatar by default', () => {
      const { container } = render(<ListSkeleton />);
      const circularSkeletons = container.querySelectorAll('.MuiSkeleton-circular');
      expect(circularSkeletons).toHaveLength(0);
    });

    it('should render with avatars when showAvatar is true', () => {
      const { container } = render(<ListSkeleton showAvatar={true} rows={3} />);
      const circularSkeletons = container.querySelectorAll('.MuiSkeleton-circular');
      expect(circularSkeletons.length).toBeGreaterThan(0);
    });

    it('should render proper list structure', () => {
      const { container } = render(<ListSkeleton rows={2} />);
      const listItems = container.querySelectorAll('[role="listitem"]');
      expect(listItems).toHaveLength(2);
    });
  });

  describe('TableSkeleton Component', () => {
    it('should render default table structure', () => {
      const { container } = render(<TableSkeleton />);
      const table = container.querySelector('table');
      expect(table).toBeInTheDocument();
    });

    it('should render custom number of rows and columns', () => {
      const { container } = render(<TableSkeleton rows={4} columns={6} />);
      const tableRows = container.querySelectorAll('tbody tr');
      expect(tableRows).toHaveLength(4);
      
      const firstRowCells = tableRows[0]?.querySelectorAll('td');
      expect(firstRowCells).toHaveLength(6);
    });

    it('should render table header', () => {
      const { container } = render(<TableSkeleton columns={3} />);
      const headerCells = container.querySelectorAll('thead th');
      expect(headerCells).toHaveLength(3);
    });

    it('should render skeleton cells', () => {
      const { container } = render(<TableSkeleton rows={2} columns={3} />);
      const skeletonElements = container.querySelectorAll('.MuiSkeleton-root');
      expect(skeletonElements.length).toBeGreaterThanOrEqual(6); // At least rows * columns
    });

    it('should have proper table accessibility', () => {
      render(<TableSkeleton />);
      expect(screen.getByRole('table')).toBeInTheDocument();
    });
  });

  describe('CardSkeleton Component', () => {
    it('should render default card structure', () => {
      const { container } = render(<CardSkeleton />);
      const card = container.querySelector('.MuiCard-root');
      expect(card).toBeInTheDocument();
    });

    it('should render custom number of content rows', () => {
      const { container } = render(<CardSkeleton rows={4} />);
      const skeletonElements = container.querySelectorAll('.MuiSkeleton-root');
      expect(skeletonElements.length).toBeGreaterThanOrEqual(4);
    });

    it('should render title skeleton', () => {
      const { container } = render(<CardSkeleton />);
      const titleSkeleton = container.querySelector('.MuiSkeleton-text');
      expect(titleSkeleton).toBeInTheDocument();
    });

    it('should render with proper card padding', () => {
      const { container } = render(<CardSkeleton />);
      const cardContent = container.querySelector('.MuiCardContent-root');
      expect(cardContent).toBeInTheDocument();
    });

    it('should vary skeleton widths for realistic appearance', () => {
      const { container } = render(<CardSkeleton rows={3} />);
      const skeletonElements = container.querySelectorAll('.MuiSkeleton-root');
      
      // Check that not all skeletons have the same width
      const widths = Array.from(skeletonElements).map(el => 
        el.getAttribute('style') || ''
      );
      
      const hasVariedWidths = widths.some((width, index) => 
        index > 0 && width !== widths[0]
      );
      expect(hasVariedWidths).toBe(true);
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels for all loading indicators', () => {
      render(
        <div>
          <PageLoading message="Page loading" />
          <InlineLoading message="Inline loading" />
        </div>
      );
      
      const progressbars = screen.getAllByRole('progressbar');
      expect(progressbars[0]).toHaveAttribute('aria-label', 'Page loading');
    });

    it('should be compatible with screen readers', () => {
      render(<LoadingOverlay loading={true} message="Processing data">
        <div>Content</div>
      </LoadingOverlay>);
      
      const progressbar = screen.getByRole('progressbar');
      expect(progressbar).toBeInTheDocument();
      expect(progressbar).toHaveAccessibleName();
    });
  });
}); 
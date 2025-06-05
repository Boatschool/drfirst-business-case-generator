import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Breadcrumbs from '../Breadcrumbs';

// Mock the AgentContext hook
vi.mock('../../../contexts/AgentContext', () => ({
  useAgentContext: () => ({
    currentCaseDetails: null,
    cases: [],
  }),
}));

// Mock react-router-dom useLocation
const mockUseLocation = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom') as any;
  return {
    ...actual,
    useLocation: () => mockUseLocation(),
  };
});

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('Breadcrumbs Component', () => {
  it('should render without crashing on dashboard', () => {
    mockUseLocation.mockReturnValue({
      pathname: '/dashboard',
      search: '',
      hash: '',
      state: null,
      key: 'default',
    });

    const { container } = render(
      <TestWrapper>
        <Breadcrumbs />
      </TestWrapper>
    );

    // Should not crash
    expect(container).toBeDefined();
  });

  it('should not render on login page', () => {
    mockUseLocation.mockReturnValue({
      pathname: '/login',
      search: '',
      hash: '',
      state: null,
      key: 'default',
    });

    const { container } = render(
      <TestWrapper>
        <Breadcrumbs />
      </TestWrapper>
    );

    // Should not render anything
    expect(container.firstChild).toBeNull();
  });

  it('should not render on signup page', () => {
    mockUseLocation.mockReturnValue({
      pathname: '/signup',
      search: '',
      hash: '',
      state: null,
      key: 'default',
    });

    const { container } = render(
      <TestWrapper>
        <Breadcrumbs />
      </TestWrapper>
    );

    // Should not render anything
    expect(container.firstChild).toBeNull();
  });
}); 
import { test, expect, describe } from 'vitest';
import { render } from '@testing-library/react';

// Simple smoke tests to verify our testing setup works
describe('DashboardPage Tests', () => {
  test('test environment is working', () => {
    expect(true).toBe(true);
  });

  test('can render a simple component', () => {
    const TestComponent = () => <div>Test Component</div>;
    const { getByText } = render(<TestComponent />);
    expect(getByText('Test Component')).toBeDefined();
  });

  test('basic math works in test environment', () => {
    expect(2 + 2).toBe(4);
  });
});

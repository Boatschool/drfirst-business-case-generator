import { describe, it, expect } from 'vitest';

// Utility functions to format status and text
export const formatStatusText = (status: string): string => {
  return status
    .replace(/_/g, ' ')
    .toLowerCase()
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

export const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(amount);
};

export const formatDate = (date: string | Date): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

export const calculateProgress = (completed: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((completed / total) * 100);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  if (maxLength <= 3) return '...';
  return text.slice(0, maxLength - 3) + '...';
};

describe('Utility Functions', () => {
  describe('formatStatusText', () => {
    it('should format underscored status to title case', () => {
      expect(formatStatusText('PRD_DRAFTING')).toBe('Prd Drafting');
      expect(formatStatusText('SYSTEM_DESIGN_PENDING_REVIEW')).toBe('System Design Pending Review');
      expect(formatStatusText('FINANCIAL_ANALYSIS')).toBe('Financial Analysis');
    });

    it('should handle single word status', () => {
      expect(formatStatusText('APPROVED')).toBe('Approved');
      expect(formatStatusText('REJECTED')).toBe('Rejected');
    });

    it('should handle empty string', () => {
      expect(formatStatusText('')).toBe('');
    });

    it('should handle status without underscores', () => {
      expect(formatStatusText('approved')).toBe('Approved');
    });
  });

  describe('formatCurrency', () => {
    it('should format USD currency correctly', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00');
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
    });

    it('should handle zero amount', () => {
      expect(formatCurrency(0)).toBe('$0.00');
    });

    it('should handle negative amounts', () => {
      expect(formatCurrency(-500)).toBe('-$500.00');
    });

    it('should support different currencies', () => {
      expect(formatCurrency(1000, 'EUR')).toContain('1,000.00');
    });

    it('should handle large numbers', () => {
      expect(formatCurrency(1000000)).toBe('$1,000,000.00');
    });
  });

  describe('formatDate', () => {
    it('should format date string correctly', () => {
      const result = formatDate('2024-01-15T10:30:00Z');
      expect(result).toBe('January 15, 2024');
    });

    it('should format Date object correctly', () => {
      const date = new Date('2024-01-15T10:30:00Z');
      const result = formatDate(date);
      expect(result).toBe('January 15, 2024');
    });

    it('should handle different date formats', () => {
      const result = formatDate('2024-12-25T12:00:00Z');
      expect(result).toBe('December 25, 2024');
    });
  });

  describe('calculateProgress', () => {
    it('should calculate percentage correctly', () => {
      expect(calculateProgress(25, 100)).toBe(25);
      expect(calculateProgress(50, 100)).toBe(50);
      expect(calculateProgress(75, 100)).toBe(75);
    });

    it('should handle partial progress', () => {
      expect(calculateProgress(1, 3)).toBe(33);
      expect(calculateProgress(2, 3)).toBe(67);
    });

    it('should handle zero total', () => {
      expect(calculateProgress(10, 0)).toBe(0);
    });

    it('should handle zero completed', () => {
      expect(calculateProgress(0, 100)).toBe(0);
    });

    it('should handle completed exceeding total', () => {
      expect(calculateProgress(150, 100)).toBe(150);
    });

    it('should round to nearest integer', () => {
      expect(calculateProgress(1, 6)).toBe(17); // 16.666... rounded to 17
      expect(calculateProgress(2, 7)).toBe(29); // 28.571... rounded to 29
    });
  });

  describe('truncateText', () => {
    it('should truncate text longer than max length', () => {
      const longText = 'This is a very long text that needs to be truncated';
      expect(truncateText(longText, 20)).toBe('This is a very lo...');
    });

    it('should return original text if shorter than max length', () => {
      const shortText = 'Short text';
      expect(truncateText(shortText, 20)).toBe('Short text');
    });

    it('should handle text exactly at max length', () => {
      const exactText = 'Exactly twenty chars';
      expect(truncateText(exactText, 20)).toBe('Exactly twenty chars');
    });

    it('should handle empty string', () => {
      expect(truncateText('', 10)).toBe('');
    });

    it('should handle very short max length', () => {
      expect(truncateText('Hello World', 5)).toBe('He...');
    });

    it('should handle max length less than 3', () => {
      expect(truncateText('Hello', 2)).toBe('...');
    });
  });
}); 
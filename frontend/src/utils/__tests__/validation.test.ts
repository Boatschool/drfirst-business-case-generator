import { isValidUrl, isNotEmpty, validateRelevantLink } from '../validation';

describe('Validation utilities', () => {
  describe('isValidUrl', () => {
    it('should return true for valid HTTP URLs', () => {
      expect(isValidUrl('http://example.com')).toBe(true);
      expect(isValidUrl('http://confluence.drfirst.com/page')).toBe(true);
    });

    it('should return true for valid HTTPS URLs', () => {
      expect(isValidUrl('https://example.com')).toBe(true);
      expect(isValidUrl('https://jira.drfirst.com/project')).toBe(true);
    });

    it('should return false for invalid URLs', () => {
      expect(isValidUrl('not-a-url')).toBe(false);
      expect(isValidUrl('ftp://example.com')).toBe(false);
      expect(isValidUrl('')).toBe(false);
      expect(isValidUrl('  ')).toBe(false);
    });

    it('should return false for malformed URLs', () => {
      expect(isValidUrl('http://')).toBe(false);
      expect(isValidUrl('https://')).toBe(false);
      expect(isValidUrl('://example.com')).toBe(false);
    });
  });

  describe('isNotEmpty', () => {
    it('should return true for non-empty strings', () => {
      expect(isNotEmpty('hello')).toBe(true);
      expect(isNotEmpty('Project Title')).toBe(true);
      expect(isNotEmpty('  content  ')).toBe(true);
    });

    it('should return false for empty or whitespace-only strings', () => {
      expect(isNotEmpty('')).toBe(false);
      expect(isNotEmpty('  ')).toBe(false);
      expect(isNotEmpty('\t\n')).toBe(false);
    });
  });

  describe('validateRelevantLink', () => {
    it('should validate complete and correct links', () => {
      const result = validateRelevantLink({
        name: 'Confluence Page',
        url: 'https://confluence.drfirst.com/page'
      });
      
      expect(result.isValid).toBe(true);
      expect(result.errors.name).toBe('');
      expect(result.errors.url).toBe('');
    });

    it('should invalidate links with missing name', () => {
      const result = validateRelevantLink({
        name: '',
        url: 'https://example.com'
      });
      
      expect(result.isValid).toBe(false);
      expect(result.errors.name).toBe('Link name is required');
      expect(result.errors.url).toBe('');
    });

    it('should invalidate links with missing URL', () => {
      const result = validateRelevantLink({
        name: 'Test Link',
        url: ''
      });
      
      expect(result.isValid).toBe(false);
      expect(result.errors.name).toBe('');
      expect(result.errors.url).toBe('Link URL is required');
    });

    it('should invalidate links with invalid URL format', () => {
      const result = validateRelevantLink({
        name: 'Test Link',
        url: 'not-a-valid-url'
      });
      
      expect(result.isValid).toBe(false);
      expect(result.errors.name).toBe('');
      expect(result.errors.url).toBe('Please enter a valid URL (http/https)');
    });

    it('should invalidate links with multiple errors', () => {
      const result = validateRelevantLink({
        name: '',
        url: 'invalid-url'
      });
      
      expect(result.isValid).toBe(false);
      expect(result.errors.name).toBe('Link name is required');
      expect(result.errors.url).toBe('Please enter a valid URL (http/https)');
    });

    it('should handle whitespace-only inputs', () => {
      const result = validateRelevantLink({
        name: '  ',
        url: '  '
      });
      
      expect(result.isValid).toBe(false);
      expect(result.errors.name).toBe('Link name is required');
      expect(result.errors.url).toBe('Link URL is required');
    });
  });
}); 
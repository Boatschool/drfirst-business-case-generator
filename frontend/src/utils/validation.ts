/**
 * Validation utility functions for form inputs
 */

/**
 * Validates if a URL has a proper format
 * @param url - The URL string to validate
 * @returns true if the URL is valid, false otherwise
 */
export const isValidUrl = (url: string): boolean => {
  if (!url.trim()) return false;
  
  try {
    const urlObj = new URL(url);
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
  } catch {
    return false;
  }
};

/**
 * Validates if a string is not empty or just whitespace
 * @param value - The string to validate
 * @returns true if the string has content, false otherwise
 */
export const isNotEmpty = (value: string): boolean => {
  return value.trim().length > 0;
};

/**
 * Validates if all fields in a relevant link object are properly filled
 * @param link - The link object with name and url fields
 * @returns Object with validation results
 */
export const validateRelevantLink = (link: { name: string; url: string }) => {
  const hasName = isNotEmpty(link.name);
  const hasUrl = isNotEmpty(link.url);
  const isUrlValid = hasUrl ? isValidUrl(link.url) : true;
  
  return {
    isValid: hasName && hasUrl && isUrlValid,
    errors: {
      name: !hasName ? 'Link name is required' : '',
      url: !hasUrl ? 'Link URL is required' : !isUrlValid ? 'Please enter a valid URL (http/https)' : ''
    }
  };
}; 
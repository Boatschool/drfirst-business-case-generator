import { useEffect } from 'react';

const APP_NAME = 'DrFirst Case Gen';

/**
 * Custom hook to set the document title
 * @param title - The page title (will be appended with app name)
 * @param dependency - Optional dependency to trigger title update
 */
const useDocumentTitle = (title: string, dependency?: any) => {
  useEffect(() => {
    if (title) {
      document.title = `${title} - ${APP_NAME}`;
    } else {
      document.title = APP_NAME;
    }
    
    // Cleanup: Reset to default when component unmounts
    return () => {
      document.title = APP_NAME;
    };
  }, [title, dependency]);
};

export default useDocumentTitle; 
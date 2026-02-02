/**
 * API utility functions
 * Handles common API request patterns with ngrok bypass
 */

/**
 * Get headers for API requests
 * Includes ngrok-skip-browser-warning to bypass ngrok free tier warning page
 */
export const getApiHeaders = (token = null, additionalHeaders = {}) => {
  const headers = {
    'ngrok-skip-browser-warning': 'true', // Bypass ngrok warning page
    ...additionalHeaders
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
};

/**
 * Wrapper for fetch with default headers
 */
export const apiFetch = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  
  const defaultHeaders = getApiHeaders(token, {
    'Content-Type': 'application/json',
    ...options.headers
  });

  return fetch(url, {
    ...options,
    headers: defaultHeaders
  });
};

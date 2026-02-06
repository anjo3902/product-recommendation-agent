import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './Signup.css';

/**
 * Signup Component
 * Handles user registration with email, username, password, and full name
 */
const Signup = ({ onSwitchToLogin, onSignupSuccess }) => {
  const { signup, loading, error } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });
  
  const [formErrors, setFormErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error for this field
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  // Validate form
  const validateForm = () => {
    const errors = {};

    // Email validation
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Invalid email format';
    }

    // Username validation
    if (!formData.username) {
      errors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    } else if (formData.username.length > 20) {
      errors.username = 'Username must be less than 20 characters';
    } else if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(formData.username)) {
      errors.username = 'Username must start with a letter and contain only letters, numbers, and underscores';
    }

    // Password validation
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    } else if (!/[A-Z]/.test(formData.password)) {
      errors.password = 'Password must contain at least one uppercase letter';
    } else if (!/[a-z]/.test(formData.password)) {
      errors.password = 'Password must contain at least one lowercase letter';
    } else if (!/[0-9]/.test(formData.password)) {
      errors.password = 'Password must contain at least one number';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    // Full name validation
    if (!formData.fullName) {
      errors.fullName = 'Full name is required';
    } else if (formData.fullName.length < 2) {
      errors.fullName = 'Full name must be at least 2 characters';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const result = await signup(
      formData.email,
      formData.username,
      formData.password,
      formData.fullName
    );

    if (result.success) {
      // Signup successful
      if (onSignupSuccess) {
        onSignupSuccess();
      }
    }
  };

  // Password strength indicator
  const getPasswordStrength = () => {
    const password = formData.password;
    if (!password) return { label: '', class: '' };

    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;

    if (strength <= 2) return { label: 'Weak', class: 'weak' };
    if (strength === 3) return { label: 'Medium', class: 'medium' };
    return { label: 'Strong', class: 'strong' };
  };

  const passwordStrength = getPasswordStrength();

  return (
    <div className="signup-container">
      <div className="signup-card">
        <div className="signup-header">
          <div className="brand-logo">
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="48" height="48" rx="12" fill="#4f46e5"/>
              <path d="M14 24L20 30L34 16" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
              <circle cx="24" cy="24" r="18" stroke="white" strokeWidth="2" opacity="0.3"/>
            </svg>
            <div className="brand-text">
              <h1>SmartBuy AI</h1>
              <span>Intelligent Shopping Assistant</span>
            </div>
          </div>
          <h2>Create Account</h2>
          <p>Sign up to get started</p>
        </div>

        <form onSubmit={handleSubmit} className="signup-form">
          {/* Full Name Field */}
          <div className="form-group">
            <label htmlFor="fullName">Full Name</label>
            <input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              placeholder="Enter your full name"
              className={formErrors.fullName ? 'error' : ''}
              disabled={loading}
            />
            {formErrors.fullName && (
              <span className="error-message">{formErrors.fullName}</span>
            )}
          </div>

          {/* Email Field */}
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              className={formErrors.email ? 'error' : ''}
              disabled={loading}
            />
            {formErrors.email && (
              <span className="error-message">{formErrors.email}</span>
            )}
          </div>

          {/* Username Field */}
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              className={formErrors.username ? 'error' : ''}
              disabled={loading}
            />
            {formErrors.username && (
              <span className="error-message">{formErrors.username}</span>
            )}
            <small className="field-hint">
              3-20 characters, starts with letter, alphanumeric + underscore
            </small>
          </div>

          {/* Password Field */}
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-wrapper">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Create a password"
                className={formErrors.password ? 'error' : ''}
                disabled={loading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            {formErrors.password && (
              <span className="error-message">{formErrors.password}</span>
            )}
            {formData.password && (
              <div className={`password-strength ${passwordStrength.class}`}>
                <span>Strength: {passwordStrength.label}</span>
              </div>
            )}
            <small className="field-hint">
              Min 8 characters, 1 uppercase, 1 lowercase, 1 number
            </small>
          </div>

          {/* Confirm Password Field */}
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <div className="password-input-wrapper">
              <input
                type={showConfirmPassword ? 'text' : 'password'}
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm your password"
                className={formErrors.confirmPassword ? 'error' : ''}
                disabled={loading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex={-1}
                aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
              >
                {showConfirmPassword ? 'Hide' : 'Show'}
              </button>
            </div>
            {formErrors.confirmPassword && (
              <span className="error-message">{formErrors.confirmPassword}</span>
            )}
          </div>

          {/* Server Error */}
          {error && (
            <div className="alert alert-error">
              <span>{error}</span>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            className={`btn btn-primary ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? (
              <span className="btn-loading">
                <svg className="spinner-svg" viewBox="0 0 50 50">
                  <circle className="path" cx="25" cy="25" r="20" fill="none" strokeWidth="4"></circle>
                </svg>
                <span>Creating account...</span>
              </span>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Switch to Login */}
        <div className="signup-footer">
          <p>
            Already have an account?{' '}
            <button
              type="button"
              className="link-button"
              onClick={onSwitchToLogin}
            >
              Login here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;

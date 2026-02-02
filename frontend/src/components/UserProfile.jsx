import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './UserProfile.css';

/**
 * User Profile Component
 * Displays and allows editing of user profile information
 */
const UserProfile = () => {
  const { user, logout, updateProfile, changePassword } = useAuth();

  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  const [profileData, setProfileData] = useState({
    fullName: user?.full_name || '',
    username: user?.username || ''
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle profile update
  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setMessage(null);
    setLoading(true);

    const updates = {};
    if (profileData.fullName !== user.full_name) {
      updates.full_name = profileData.fullName;
    }
    if (profileData.username !== user.username) {
      updates.username = profileData.username;
    }

    if (Object.keys(updates).length === 0) {
      setMessage({ type: 'info', text: 'No changes to save' });
      setLoading(false);
      return;
    }

    const result = await updateProfile(updates);

    if (result.success) {
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setIsEditingProfile(false);
    } else {
      setMessage({ type: 'error', text: result.error || 'Failed to update profile' });
    }

    setLoading(false);
  };

  // Handle password change
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setMessage(null);

    // Validate
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      return;
    }

    if (passwordData.newPassword.length < 8) {
      setMessage({ type: 'error', text: 'Password must be at least 8 characters' });
      return;
    }

    setLoading(true);
    const result = await changePassword(passwordData.currentPassword, passwordData.newPassword);

    if (result.success) {
      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setIsChangingPassword(false);
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } else {
      setMessage({ type: 'error', text: result.error || 'Failed to change password' });
    }

    setLoading(false);
  };

  // Cancel profile edit
  const handleCancelEdit = () => {
    setProfileData({
      fullName: user?.full_name || '',
      username: user?.username || ''
    });
    setIsEditingProfile(false);
    setMessage(null);
  };

  // Cancel password change
  const handleCancelPasswordChange = () => {
    setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    setIsChangingPassword(false);
    setMessage(null);
  };

  return (
    <div className="profile-container">
      <div className="profile-card">
        {/* Header */}
        <div className="profile-header">
          <div className="profile-avatar">
            {user?.full_name?.charAt(0).toUpperCase() || user?.username?.charAt(0).toUpperCase()}
          </div>
          <h2>{user?.full_name || user?.username}</h2>
          <p className="profile-email">{user?.email}</p>
        </div>

        {/* Message Alert */}
        {message && (
          <div className={`alert alert-${message.type}`}>
            {message.type === 'success' && '✅'}
            {message.type === 'error' && '⚠️'}
            {message.type === 'info' && 'ℹ️'}
            <span>{message.text}</span>
          </div>
        )}

        {/* Profile Information */}
        <div className="profile-section">
          <div className="section-header">
            <h3>Profile Information</h3>
            {!isEditingProfile && (
              <button
                className="btn-edit"
                onClick={() => setIsEditingProfile(true)}
              >
                Edit
              </button>
            )}
          </div>

          {isEditingProfile ? (
            <form onSubmit={handleProfileUpdate} className="profile-form">
              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  value={profileData.fullName}
                  onChange={(e) => setProfileData({ ...profileData, fullName: e.target.value })}
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  value={profileData.username}
                  onChange={(e) => setProfileData({ ...profileData, username: e.target.value })}
                  disabled={loading}
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleCancelEdit}
                  disabled={loading}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="profile-info">
              {console.log('User data:', user)}
              <div className="info-row">
                <span className="info-label">Full Name:</span>
                <span className="info-value" style={{ fontWeight: '600', color: '#1a202c' }}>
                  {user?.full_name || 'Not set'}
                </span>
              </div>
              <div className="info-row">
                <span className="info-label">Username:</span>
                <span className="info-value" style={{ fontWeight: '600', color: '#1a202c' }}>
                  {user?.username || 'Not set'}
                </span>
              </div>
              <div className="info-row">
                <span className="info-label">Email:</span>
                <span className="info-value" style={{ fontWeight: '600', color: '#1a202c' }}>
                  {user?.email || 'Not set'}
                </span>
              </div>
              <div className="info-row">
                <span className="info-label">Member Since:</span>
                <span className="info-value" style={{ fontWeight: '600', color: '#1a202c' }}>
                  {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Not available'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Password Change Section */}
        <div className="profile-section">
          <div className="section-header">
            <h3>Security</h3>
            {!isChangingPassword && (
              <button
                className="btn-edit"
                onClick={() => setIsChangingPassword(true)}
              >
                Change Password
              </button>
            )}
          </div>

          {isChangingPassword ? (
            <form onSubmit={handlePasswordChange} className="profile-form">
              <div className="form-group">
                <label>Current Password</label>
                <input
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, currentPassword: e.target.value })}
                  disabled={loading}
                  required
                />
              </div>

              <div className="form-group">
                <label>New Password</label>
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, newPassword: e.target.value })}
                  disabled={loading}
                  required
                />
              </div>

              <div className="form-group">
                <label>Confirm New Password</label>
                <input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => setPasswordData({ ...passwordData, confirmPassword: e.target.value })}
                  disabled={loading}
                  required
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  {loading ? 'Changing...' : 'Change Password'}
                </button>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleCancelPasswordChange}
                  disabled={loading}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="profile-info">
              <p>Password is encrypted and secure.</p>
            </div>
          )}
        </div>

        {/* Logout Section */}
        <div className="profile-section">
          <button className="btn btn-logout" onClick={logout}>
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;

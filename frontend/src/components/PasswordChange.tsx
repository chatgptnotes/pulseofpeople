import { useState } from 'react';
import { Lock, Eye, EyeOff, Check, X, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { validateField } from '../lib/form-validation';

interface PasswordStrength {
  score: number;
  label: string;
  color: string;
  requirements: {
    length: boolean;
    uppercase: boolean;
    lowercase: boolean;
    number: boolean;
    special: boolean;
  };
}

export default function PasswordChange() {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Calculate password strength
  const getPasswordStrength = (password: string): PasswordStrength => {
    const requirements = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[^A-Za-z0-9]/.test(password)
    };

    const score = Object.values(requirements).filter(Boolean).length;

    let label = 'Weak';
    let color = 'red';

    if (score >= 5) {
      label = 'Very Strong';
      color = 'green';
    } else if (score >= 4) {
      label = 'Strong';
      color = 'emerald';
    } else if (score >= 3) {
      label = 'Medium';
      color = 'yellow';
    } else if (score >= 2) {
      label = 'Fair';
      color = 'orange';
    }

    return { score, label, color, requirements };
  };

  const passwordStrength = getPasswordStrength(formData.newPassword);

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    setErrors(prev => ({ ...prev, [field]: '' }));
    setApiError(null);
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate current password
    if (!formData.currentPassword) {
      newErrors.currentPassword = 'Current password is required';
    }

    // Validate new password
    const passwordValidation = validateField(
      formData.newPassword,
      [{ rule: 'required' }, { rule: 'password' }]
    );
    if (passwordValidation) {
      newErrors.newPassword = passwordValidation;
    }

    // Check if new password is different from current
    if (formData.newPassword && formData.currentPassword === formData.newPassword) {
      newErrors.newPassword = 'New password must be different from current password';
    }

    // Validate confirm password
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your new password';
    } else if (formData.newPassword !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setApiError(null);

    try {
      // TODO: Integrate with actual password change API
      // await authService.changePassword({
      //   currentPassword: formData.currentPassword,
      //   newPassword: formData.newPassword
      // });

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Simulate random error for demo (remove in production)
      if (Math.random() > 0.8) {
        throw new Error('Current password is incorrect');
      }

      // Success!
      setSuccess(true);
      setFormData({ currentPassword: '', newPassword: '', confirmPassword: '' });

      // Hide success message after 3 seconds
      setTimeout(() => {
        setSuccess(false);
      }, 3000);

    } catch (error: any) {
      setApiError(error.message || 'Failed to change password. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center mb-6">
          <Lock className="w-6 h-6 text-blue-600 mr-3" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Change Password</h2>
            <p className="text-sm text-gray-600">Update your password to keep your account secure</p>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <Check className="w-5 h-5 text-green-600 mr-2" />
              <p className="text-green-800 font-medium">Password changed successfully!</p>
            </div>
          </div>
        )}

        {/* API Error Message */}
        {apiError && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-red-600 mr-2 mt-0.5" />
              <div>
                <p className="text-red-800 font-medium">Error</p>
                <p className="text-red-700 text-sm">{apiError}</p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Current Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Password <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type={showPasswords.current ? 'text' : 'password'}
                value={formData.currentPassword}
                onChange={(e) => handleChange('currentPassword', e.target.value)}
                className={`w-full px-4 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.currentPassword ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Enter your current password"
              />
              <button
                type="button"
                onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPasswords.current ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {errors.currentPassword && (
              <p className="text-red-500 text-sm mt-1">{errors.currentPassword}</p>
            )}
          </div>

          {/* New Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Password <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type={showPasswords.new ? 'text' : 'password'}
                value={formData.newPassword}
                onChange={(e) => handleChange('newPassword', e.target.value)}
                className={`w-full px-4 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.newPassword ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Enter your new password"
              />
              <button
                type="button"
                onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPasswords.new ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {errors.newPassword && (
              <p className="text-red-500 text-sm mt-1">{errors.newPassword}</p>
            )}

            {/* Password Strength Meter */}
            {formData.newPassword && (
              <div className="mt-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Password Strength:</span>
                  <span className={`text-sm font-semibold text-${passwordStrength.color}-600`}>
                    {passwordStrength.label}
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full bg-${passwordStrength.color}-500 transition-all duration-300`}
                    style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                  ></div>
                </div>

                {/* Requirements Checklist */}
                <div className="mt-3 space-y-1">
                  <p className="text-xs font-medium text-gray-700 mb-2">Password must contain:</p>
                  {[
                    { key: 'length', label: 'At least 8 characters' },
                    { key: 'uppercase', label: 'One uppercase letter (A-Z)' },
                    { key: 'lowercase', label: 'One lowercase letter (a-z)' },
                    { key: 'number', label: 'One number (0-9)' },
                    { key: 'special', label: 'One special character (!@#$%^&*)' }
                  ].map(req => (
                    <div key={req.key} className="flex items-center text-xs">
                      {passwordStrength.requirements[req.key as keyof typeof passwordStrength.requirements] ? (
                        <Check className="w-4 h-4 text-green-600 mr-2" />
                      ) : (
                        <X className="w-4 h-4 text-gray-400 mr-2" />
                      )}
                      <span className={
                        passwordStrength.requirements[req.key as keyof typeof passwordStrength.requirements]
                          ? 'text-green-700'
                          : 'text-gray-600'
                      }>
                        {req.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirm New Password <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type={showPasswords.confirm ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => handleChange('confirmPassword', e.target.value)}
                className={`w-full px-4 py-2 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Confirm your new password"
              />
              <button
                type="button"
                onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPasswords.confirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            {errors.confirmPassword && (
              <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end space-x-4 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={() => {
                setFormData({ currentPassword: '', newPassword: '', confirmPassword: '' });
                setErrors({});
                setApiError(null);
              }}
              disabled={isSubmitting}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Clear
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Changing Password...
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4 mr-2" />
                  Change Password
                </>
              )}
            </button>
          </div>
        </form>

        {/* Security Tips */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">Password Security Tips</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              Use a unique password that you don't use for other accounts
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              Avoid using personal information like names or birthdays
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              Consider using a password manager to generate and store strong passwords
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              Change your password regularly (every 3-6 months)
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

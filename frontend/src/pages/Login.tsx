import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Eye, EyeOff, Lock, Mail, ArrowLeft, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../lib/supabase';
import Logo from '../components/Logo';

type AuthMode = 'login' | 'forgot-password' | 'magic-link';

export default function Login() {
  const [mode, setMode] = useState<AuthMode>('login');
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [rememberMe, setRememberMe] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      console.log('Login form submitted for:', credentials.email);

      const success = await login(credentials.email, credentials.password);

      if (success) {
        console.log('Login successful, navigating to dashboard...');

        // Store persistence preference
        if (rememberMe) {
          localStorage.setItem('auth_remember', 'true');
        }

        navigate('/dashboard');
      } else {
        setError('Invalid email or password. Please check your credentials.');
      }
    } catch (err: any) {
      console.error('Auth error:', err);
      setError(err.message || 'An error occurred during authentication');
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!credentials.email) {
      setError('Please enter your email address');
      return;
    }

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(credentials.email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });

      if (error) throw error;

      setSuccess('Password reset link sent! Check your email inbox.');
      setTimeout(() => setMode('login'), 3000);
    } catch (err: any) {
      console.error('Password reset error:', err);
      setError(err.message || 'Failed to send password reset email');
    }
  };

  const handleMagicLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!credentials.email) {
      setError('Please enter your email address');
      return;
    }

    try {
      const { error } = await supabase.auth.signInWithOtp({
        email: credentials.email,
        options: {
          emailRedirectTo: `${window.location.origin}/dashboard`,
        },
      });

      if (error) throw error;

      setSuccess('Magic link sent! Check your email to sign in.');
    } catch (err: any) {
      console.error('Magic link error:', err);
      setError(err.message || 'Failed to send magic link');
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'github') => {
    setError('');

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/dashboard`,
        },
      });

      if (error) throw error;
    } catch (err: any) {
      console.error('Social login error:', err);
      setError(err.message || `Failed to sign in with ${provider}`);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
    setSuccess('');
  };

  const renderLoginForm = () => (
    <>
      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-white mb-2">
          Email Address
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Mail className="h-5 w-5 text-gray-400" />
          </div>
          <input
            id="email"
            name="email"
            type="email"
            required
            autoComplete="email"
            value={credentials.email}
            onChange={handleInputChange}
            className="block w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
            placeholder="Enter your email"
          />
        </div>
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-white mb-2">
          Password
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Lock className="h-5 w-5 text-gray-400" />
          </div>
          <input
            id="password"
            name="password"
            type={showPassword ? 'text' : 'password'}
            required
            autoComplete="current-password"
            value={credentials.password}
            onChange={handleInputChange}
            className="block w-full pl-10 pr-12 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
            placeholder="Enter your password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            {showPassword ? (
              <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-300 transition-colors" />
            ) : (
              <Eye className="h-5 w-5 text-gray-400 hover:text-gray-300 transition-colors" />
            )}
          </button>
        </div>
      </div>

      {/* Remember Me & Forgot Password */}
      <div className="flex items-center justify-between">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            className="w-4 h-4 rounded border-white/20 bg-white/10 text-blue-500 focus:ring-2 focus:ring-blue-400 focus:ring-offset-0"
          />
          <span className="ml-2 text-sm text-white">Remember me</span>
        </label>
        <button
          type="button"
          onClick={() => setMode('forgot-password')}
          className="text-sm text-blue-200 hover:text-white transition-colors"
        >
          Forgot password?
        </button>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-3 rounded-xl hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 disabled:transform-none"
      >
        {isLoading ? (
          <div className="flex items-center justify-center">
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
            Signing in...
          </div>
        ) : (
          'Sign In'
        )}
      </button>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-white/20"></div>
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-transparent text-gray-300">Or continue with</span>
        </div>
      </div>

      {/* Social Login Buttons */}
      <div className="grid grid-cols-2 gap-3">
        <button
          type="button"
          onClick={() => handleSocialLogin('google')}
          className="flex items-center justify-center px-4 py-3 bg-white/10 border border-white/20 rounded-xl hover:bg-white/20 transition-all"
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path fill="#EA4335" d="M5.266 9.765A7.077 7.077 0 0 1 12 4.909c1.69 0 3.218.6 4.418 1.582L19.91 3C17.782 1.145 15.055 0 12 0 7.27 0 3.198 2.698 1.24 6.65l4.026 3.115Z"/>
            <path fill="#34A853" d="M16.04 18.013c-1.09.703-2.474 1.078-4.04 1.078a7.077 7.077 0 0 1-6.723-4.823l-4.04 3.067A11.965 11.965 0 0 0 12 24c2.933 0 5.735-1.043 7.834-3l-3.793-2.987Z"/>
            <path fill="#4A90E2" d="M19.834 21c2.195-2.048 3.62-5.096 3.62-9 0-.71-.109-1.473-.272-2.182H12v4.637h6.436c-.317 1.559-1.17 2.766-2.395 3.558L19.834 21Z"/>
            <path fill="#FBBC05" d="M5.277 14.268A7.12 7.12 0 0 1 4.909 12c0-.782.125-1.533.357-2.235L1.24 6.65A11.934 11.934 0 0 0 0 12c0 1.92.445 3.73 1.237 5.335l4.04-3.067Z"/>
          </svg>
          <span className="text-white text-sm font-medium">Google</span>
        </button>

        <button
          type="button"
          onClick={() => handleSocialLogin('github')}
          className="flex items-center justify-center px-4 py-3 bg-white/10 border border-white/20 rounded-xl hover:bg-white/20 transition-all"
        >
          <svg className="w-5 h-5 mr-2" fill="white" viewBox="0 0 24 24">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12Z"/>
          </svg>
          <span className="text-white text-sm font-medium">GitHub</span>
        </button>
      </div>

      {/* Magic Link Option */}
      <button
        type="button"
        onClick={() => setMode('magic-link')}
        className="w-full text-center text-sm text-blue-200 hover:text-white transition-colors"
      >
        Or sign in with a magic link →
      </button>
    </>
  );

  const renderForgotPasswordForm = () => (
    <>
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-white mb-2">Reset Password</h2>
        <p className="text-sm text-blue-200">
          Enter your email and we'll send you a reset link
        </p>
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-white mb-2">
          Email Address
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Mail className="h-5 w-5 text-gray-400" />
          </div>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={credentials.email}
            onChange={handleInputChange}
            className="block w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
            placeholder="Enter your email"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-3 rounded-xl hover:shadow-xl transition-all duration-300 disabled:opacity-50"
      >
        Send Reset Link
      </button>

      <button
        type="button"
        onClick={() => setMode('login')}
        className="w-full text-center text-sm text-blue-200 hover:text-white transition-colors"
      >
        ← Back to sign in
      </button>
    </>
  );

  const renderMagicLinkForm = () => (
    <>
      <div className="text-center mb-6">
        <h2 className="text-xl font-bold text-white mb-2">Magic Link Sign In</h2>
        <p className="text-sm text-blue-200">
          No password needed. We'll email you a link to sign in.
        </p>
      </div>

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-white mb-2">
          Email Address
        </label>
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Mail className="h-5 w-5 text-gray-400" />
          </div>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={credentials.email}
            onChange={handleInputChange}
            className="block w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
            placeholder="Enter your email"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-3 rounded-xl hover:shadow-xl transition-all duration-300 disabled:opacity-50"
      >
        Send Magic Link
      </button>

      <button
        type="button"
        onClick={() => setMode('login')}
        className="w-full text-center text-sm text-blue-200 hover:text-white transition-colors"
      >
        ← Back to password sign in
      </button>
    </>
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    switch (mode) {
      case 'login':
        return handleLogin(e);
      case 'forgot-password':
        return handleForgotPassword(e);
      case 'magic-link':
        return handleMagicLink(e);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/20"></div>

      <div className="relative w-full max-w-md">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 p-8">
          {/* Header */}
          {mode === 'login' && (
            <div className="text-center mb-8">
              <div className="flex items-center justify-center mb-6">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                  <Logo size="medium" variant="stacked" />
                </div>
              </div>
              <h1 className="text-2xl font-bold text-white mb-2">
                Welcome Back
              </h1>
              <p className="text-blue-200">
                Access your Pulse of People dashboard
              </p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            {error && (
              <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-3 flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-200 flex-shrink-0 mt-0.5" />
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}

            {/* Success Message */}
            {success && (
              <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-3 flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-green-200 flex-shrink-0 mt-0.5" />
                <p className="text-green-200 text-sm">{success}</p>
              </div>
            )}

            {/* Dynamic Form Content */}
            {mode === 'login' && renderLoginForm()}
            {mode === 'forgot-password' && renderForgotPasswordForm()}
            {mode === 'magic-link' && renderMagicLinkForm()}

            {/* Test Credentials (only in login mode) */}
            {mode === 'login' && process.env.NODE_ENV === 'development' && (
              <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-400/30 rounded-lg p-4">
                <p className="text-green-100 text-xs font-bold mb-3 flex items-center gap-2">
                  <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  Development Mode - Test Credentials
                </p>
                <div className="space-y-2 text-xs">
                  <div className="bg-white/5 rounded px-2 py-1 flex justify-between items-center">
                    <span className="text-green-200">Admin:</span>
                    <span className="text-green-100 font-mono">admin@tvk.com / admin123456</span>
                  </div>
                  <div className="bg-white/5 rounded px-2 py-1 flex justify-between items-center">
                    <span className="text-green-200">Manager:</span>
                    <span className="text-green-100 font-mono">manager@tvk.com / manager123456</span>
                  </div>
                </div>
              </div>
            )}
          </form>

          {/* Back to Home (only in login mode) */}
          {mode === 'login' && (
            <div className="mt-6 text-center">
              <button
                onClick={() => navigate('/')}
                className="flex items-center justify-center text-blue-200 hover:text-white text-sm transition-colors mx-auto"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back to Home
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Background Elements */}
      <div className="absolute top-20 left-10 w-20 h-20 bg-blue-500/10 rounded-full animate-pulse"></div>
      <div className="absolute bottom-20 right-10 w-32 h-32 bg-purple-500/10 rounded-full animate-bounce"></div>
      <div className="absolute top-1/2 right-20 w-16 h-16 bg-indigo-500/10 rounded-full animate-ping"></div>
    </div>
  );
}

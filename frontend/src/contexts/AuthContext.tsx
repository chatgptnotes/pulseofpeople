import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { djangoApi } from '../services/djangoApi';
import type { UserRole } from '../utils/permissions';

interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatar?: string;
  permissions: string[];
  ward?: string;
  constituency?: string;
  is_super_admin?: boolean;
  organization_id?: string;
  tenant_id?: string;
  status?: 'active' | 'inactive' | 'suspended';
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (email: string, password: string, name: string, role?: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
  isInitializing: boolean;
  hasPermission: (permission: string) => boolean;
  isWorker: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async () => {
    console.log('[AuthContext] 🔄 Checking session...');
    try {
      const accessToken = localStorage.getItem('access_token');
      const refreshToken = localStorage.getItem('refresh_token');
      console.log('[AuthContext] Tokens found:', {
        hasAccess: !!accessToken,
        hasRefresh: !!refreshToken
      });

      if (!accessToken) {
        console.log('[AuthContext] ❌ No access token, initialization complete');
        setIsInitializing(false);
        return;
      }

      // Load user profile
      try {
        console.log('[AuthContext] 📡 Fetching user profile...');
        const profile = await djangoApi.getUserProfile();
        console.log('[AuthContext] ✅ Profile loaded:', profile.email, profile.role);

        setUser({
          id: profile.id.toString(),
          name: profile.name,
          email: profile.email,
          role: profile.role,
          permissions: profile.permissions || [],
          avatar: profile.avatar_url,
          ward: profile.ward,
          constituency: profile.constituency,
        });

        console.log('[AuthContext] ✅ User set, initialization complete');
        setIsInitializing(false);
      } catch (error) {
        console.error('[AuthContext] ❌ Failed to load profile:', error);

        // Try to refresh token
        if (refreshToken) {
          try {
            console.log('[AuthContext] 🔄 Attempting token refresh...');
            const { access } = await djangoApi.refreshToken(refreshToken);
            localStorage.setItem('access_token', access);
            console.log('[AuthContext] ✅ Token refreshed, retrying...');
            // Don't set isInitializing here, let the retry complete
            await checkSession(); // Retry
            return; // Important: return here to avoid setting isInitializing again
          } catch (refreshError) {
            console.error('[AuthContext] ❌ Token refresh failed:', refreshError);
            // Clear session
            localStorage.clear();
            setIsInitializing(false);
          }
        } else {
          console.log('[AuthContext] ❌ No refresh token, clearing session');
          localStorage.clear();
          setIsInitializing(false);
        }
      }
    } catch (error) {
      console.error('[AuthContext] ❌ Session check failed:', error);
      setIsInitializing(false);
    }
  };

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true);

      // Call Django login endpoint
      const response = await djangoApi.login(email, password);

      // Store tokens
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);

      // Load user profile
      const profile = await djangoApi.getUserProfile();

      const userData: User = {
        id: profile.id.toString(),
        name: profile.name,
        email: profile.email,
        role: profile.role as UserRole,
        permissions: profile.permissions || [],
        avatar: profile.avatar_url,
        ward: profile.ward,
        constituency: profile.constituency,
      };

      setUser(userData);

      // Also store user data for quick access
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('auth_token', 'authenticated');

      setIsLoading(false);
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      setIsLoading(false);
      return false;
    }
  };

  const signup = async (email: string, password: string, name: string, role: string = 'user'): Promise<boolean> => {
    try {
      setIsLoading(true);

      // Call Django signup endpoint
      const response = await djangoApi.register({
        email,
        password,
        name,
        role,
      });

      // Store tokens from signup response
      localStorage.setItem('access_token', response.tokens.access);
      localStorage.setItem('refresh_token', response.tokens.refresh);

      const userData: User = {
        id: response.user.id.toString(),
        name: response.user.name,
        email: response.user.email,
        role: response.user.role as UserRole,
        permissions: response.user.permissions || [],
      };

      setUser(userData);

      // Store user data
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('auth_token', 'authenticated');

      setIsLoading(false);
      return true;
    } catch (error: any) {
      console.error('Signup failed:', error);
      alert(error.message || 'Signup failed. Please try again.');
      setIsLoading(false);
      return false;
    }
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      try {
        await djangoApi.logout(refreshToken);
      } catch (error) {
        console.error('Logout error:', error);
      }
    }

    setUser(null);
    localStorage.clear();
  };

  // Check if user has a specific permission
  const hasPermission = (permission: string): boolean => {
    if (!user) return false;

    // Super admins have all permissions
    if (user.is_super_admin) return true;

    // Admins have all permissions
    if (user.role === 'admin' || user.role === 'superadmin') return true;

    // Check user's permissions array
    return user.permissions?.includes(permission) || false;
  };

  // Check if user is a field worker
  const isWorker = (): boolean => {
    if (!user) return false;
    return ['volunteer', 'user'].includes(user.role);
  };

  const value: AuthContextType = {
    user,
    login,
    signup,
    logout,
    isLoading,
    isInitializing,
    hasPermission,
    isWorker
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Export for backward compatibility (some components might use this)
export const supabase = null;

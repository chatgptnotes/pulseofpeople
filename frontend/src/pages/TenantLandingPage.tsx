import React, { useEffect, useState } from 'react';
import { useTenant } from '../contexts/TenantContext';
import LandingPage from './LandingPage';
import BJPLandingPage from './BJPLandingPage';
import TVKLandingPage from './TVKLandingPage';

export default function TenantLandingPage() {
  const { tenantSlug, tenantConfig } = useTenant();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Give tenant context time to load
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  // Show loading state briefly
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // Render TVK landing page for party-a subdomain
  if (tenantSlug === 'party-a' || tenantConfig?.subdomain === 'party-a') {
    return <TVKLandingPage />;
  }

  // Render BJP landing page for party-b subdomain
  if (tenantSlug === 'party-b' || tenantConfig?.subdomain === 'party-b') {
    return <BJPLandingPage />;
  }

  // Default landing page for all other tenants (including no tenant)
  return <LandingPage />;
}
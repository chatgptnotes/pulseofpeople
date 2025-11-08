import React, { useState } from 'react'
import RealTimeIndicator from './RealTimeIndicator'
import LoginModal from './LoginModal'
import { EnhancedNavigation } from './EnhancedNavigation'
import { CheckCircle as CheckIcon } from '@mui/icons-material'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [showLoginModal, setShowLoginModal] = useState(false)

  return (
    <div className="min-h-screen bg-bg-secondary">
      {/* Enhanced Navigation Sidebar */}
      <EnhancedNavigation />

      {/* Main content - ChatGPT-inspired spacing and padding */}
      <div className="md:pl-64 flex flex-col flex-1 min-h-screen">
        <main className="flex-1">
          <div className="py-8 sm:py-10">
            <div className="max-w-7xl mx-auto px-6 sm:px-8 md:px-10 lg:px-12">
              <div className="md:hidden mb-6">
                <RealTimeIndicator />
              </div>
              {/* Content wrapper with subtle background */}
              <div className="space-y-6">
                {children}
              </div>
            </div>
          </div>
        </main>

        {/* Version Footer - Modern ChatGPT style */}
        <footer className="bg-bg-primary border-t border-border-light py-5 px-8">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-text-tertiary">
            <div className="font-medium">
              Pulse of People - Tamil Nadu Voter Platform (TVK 2026)
            </div>
            <div className="flex items-center gap-3 flex-wrap justify-center sm:justify-end text-xs">
              <span className="font-semibold text-text-secondary px-3 py-1 bg-bg-tertiary rounded-md">
                Version 1.4
              </span>
              <span className="hidden sm:inline text-text-disabled">•</span>
              <span>Updated: November 8, 2025</span>
              <span className="hidden sm:inline text-text-disabled">•</span>
              <span className="text-accent font-medium flex items-center gap-1 px-3 py-1 bg-accent-light rounded-md">
                Interactive Mapbox Map
                <CheckIcon className="w-3.5 h-3.5" />
              </span>
            </div>
          </div>
        </footer>
      </div>

      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
    </div>
  )
}

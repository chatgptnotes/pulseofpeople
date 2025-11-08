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
    <div className="min-h-screen bg-gray-50">
      {/* Enhanced Navigation Sidebar */}
      <EnhancedNavigation />

      {/* Main content */}
      <div className="md:pl-64 flex flex-col flex-1">
        <main className="flex-1">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              <div className="md:hidden mb-4">
                <RealTimeIndicator />
              </div>
              {children}
            </div>
          </div>
        </main>

        {/* Version Footer */}
        <footer className="bg-white border-t border-gray-200 py-4 px-6">
          <div className="max-w-7xl mx-auto flex items-center justify-between text-xs text-gray-500">
            <div>
              Pulse of People - Tamil Nadu Voter Platform (TVK 2026)
            </div>
            <div className="flex items-center space-x-4">
              <span className="font-semibold text-gray-700">Version 1.4</span>
              <span>•</span>
              <span>Updated: November 8, 2025</span>
              <span>•</span>
              <span className="text-green-600 font-bold flex items-center">
                Interactive Mapbox Map
                <CheckIcon className="w-4 h-4 ml-1" />
              </span>
            </div>
          </div>
        </footer>
      </div>

      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
    </div>
  )
}

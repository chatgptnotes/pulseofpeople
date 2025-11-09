import React, { useState } from 'react'
import RealTimeIndicator from './RealTimeIndicator'
import LoginModal from './LoginModal'
import DualSidebarLayout from './navigation/DualSidebarLayout'
import { CheckCircle as CheckIcon } from '@mui/icons-material'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [showLoginModal, setShowLoginModal] = useState(false)

  return (
    <DualSidebarLayout>
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

      {/* Version Footer - TVK Brand Colors */}
      <footer className="bg-gradient-to-r from-red-50 to-yellow-50 border-t-2 border-red-600 py-5 px-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-700">
          <div className="font-semibold text-gray-800">
            Pulse of People - Tamil Nadu Voter Platform (TVK 2026)
          </div>
          <div className="flex items-center gap-3 flex-wrap justify-center sm:justify-end text-xs">
            <span className="font-bold text-white px-3 py-1 bg-red-600 rounded-md shadow-sm">
              Version 1.4
            </span>
            <span className="hidden sm:inline text-red-600">•</span>
            <span className="text-gray-700">Updated: November 8, 2025</span>
            <span className="hidden sm:inline text-yellow-600">•</span>
            <span className="text-yellow-700 font-semibold flex items-center gap-1 px-3 py-1 bg-yellow-100 border border-yellow-300 rounded-md">
              Interactive Mapbox Map
              <CheckIcon className="w-3.5 h-3.5" />
            </span>
          </div>
        </div>
      </footer>

      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
    </DualSidebarLayout>
  )
}

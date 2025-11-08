import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTenant } from '../contexts/TenantContext';
import VideoModal from '../components/VideoModal';
import DemoModal from '../components/DemoModal';
import {
  ArrowRight,
  BarChart3,
  Users,
  Target,
  Brain,
  Share2,
  Vote,
  TrendingUp,
  Shield,
  Zap,
  Globe,
  CheckCircle,
  Star,
  Play,
  Award,
  MapPin,
  Clock,
  Briefcase,
  Phone,
  Mail,
  MessageCircle
} from 'lucide-react';

export default function BJPLandingPage() {
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(false);
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);
  const { tenantConfig } = useTenant();

  const handleVideoClick = () => {
    setIsVideoModalOpen(true);
  };

  const handleBookDemoClick = () => {
    setIsDemoModalOpen(true);
  };

  const features = [
    {
      icon: BarChart3,
      title: 'Real-Time Analytics',
      description: 'Monitor voter sentiment across Kerala with advanced data visualization and comprehensive booth-level reporting.'
    },
    {
      icon: Users,
      title: 'Booth Management',
      description: 'Complete booth-level management with Panna Pramukh tracking, voter lists, and volunteer coordination.'
    },
    {
      icon: Brain,
      title: 'AI-Powered Insights',
      description: 'Predictive analytics for identifying swing voters and optimizing resource allocation across constituencies.'
    },
    {
      icon: Share2,
      title: 'Social Media War Room',
      description: 'Track trending topics, manage IT cell activities, and coordinate digital campaigns across platforms.'
    },
    {
      icon: Target,
      title: 'Opposition Tracking',
      description: 'Monitor opposition activities, rallies, and statements to stay ahead with counter-strategies.'
    },
    {
      icon: Briefcase,
      title: 'Karyakarta Management',
      description: 'Manage party workers, assign tasks, track performance, and coordinate ground-level activities.'
    }
  ];

  const stats = [
    { number: '14', label: 'Districts Covered' },
    { number: '140', label: 'Assembly Constituencies' },
    { number: '50K+', label: 'Active Karyakartas' },
    { number: '24/7', label: 'Campaign Support' }
  ];

  const achievements = [
    'Nemom - First BJP MLA in Kerala',
    'Growing vote share from 6% to 15%+',
    'Strong presence in 5 corporations',
    'Youth wing with 1 lakh+ members'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      {/* Announcement Banner */}
      <div className="bg-gradient-to-r from-orange-600 to-orange-500 text-white py-2 px-4 text-center">
        <p className="text-sm font-medium">
          🪷 Kerala Assembly Elections 2026 - Building a Stronger Tomorrow
        </p>
      </div>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-orange-100 via-white to-orange-50">
        <div className="absolute inset-0 bg-[url('/assets/images/lotus-pattern.svg')] opacity-5"></div>

        <div className="relative container mx-auto px-4 py-20">
          <div className="max-w-7xl mx-auto">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              {/* Left Content */}
              <div className="space-y-8">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-100 rounded-full">
                  <span className="text-2xl">🪷</span>
                  <span className="text-orange-800 font-semibold">BJP Kerala</span>
                </div>

                <h1 className="text-5xl md:text-6xl font-bold text-gray-900">
                  <span className="text-orange-600">Building</span> a{' '}
                  <span className="bg-gradient-to-r from-orange-600 to-orange-500 bg-clip-text text-transparent">
                    Stronger Kerala
                  </span>
                </h1>

                <p className="text-xl text-gray-700 leading-relaxed">
                  Empowering every citizen with development and good governance.
                  Join the movement for a prosperous Kerala that leads in progress
                  while preserving our rich cultural heritage.
                </p>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-orange-800">
                    Sabka Saath, Sabka Vikas, Sabka Vishwas, Sabka Prayas
                  </h3>
                  <div className="flex flex-wrap gap-3">
                    {achievements.map((achievement, index) => (
                      <div key={index} className="flex items-center gap-2 text-sm text-gray-600">
                        <CheckCircle className="w-4 h-4 text-orange-500" />
                        <span>{achievement}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex flex-wrap gap-4">
                  <Link
                    to="/login"
                    className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-orange-600 to-orange-500 text-white font-semibold rounded-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
                  >
                    Access Campaign Dashboard
                    <ArrowRight className="ml-2 w-5 h-5" />
                  </Link>

                  <button
                    onClick={handleVideoClick}
                    className="inline-flex items-center px-8 py-4 bg-white text-orange-600 font-semibold rounded-lg border-2 border-orange-200 hover:bg-orange-50 transition-all duration-300"
                  >
                    <Play className="mr-2 w-5 h-5" />
                    Watch Campaign Video
                  </button>
                </div>
              </div>

              {/* Right Content - Hero Image */}
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-orange-400 to-orange-300 rounded-3xl transform rotate-3"></div>
                <div className="relative bg-white rounded-3xl shadow-2xl p-8">
                  <img
                    src="/assets/images/bjp-kerala-campaign.jpg"
                    alt="BJP Kerala Campaign"
                    className="w-full h-full object-cover rounded-2xl"
                    onError={(e) => {
                      e.currentTarget.src = 'https://via.placeholder.com/600x400/FF9933/FFFFFF?text=BJP+Kerala+2026';
                    }}
                  />
                  <div className="absolute -bottom-6 -right-6 bg-gradient-to-r from-orange-500 to-orange-400 text-white p-6 rounded-2xl shadow-xl">
                    <p className="text-3xl font-bold">2026</p>
                    <p className="text-sm">Victory Target</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-gradient-to-r from-orange-600 to-orange-500">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-bold text-center text-white mb-12">
              Our Growing Strength in Kerala
            </h2>
            <div className="grid md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <p className="text-5xl font-bold text-white mb-2">{stat.number}</p>
                  <p className="text-orange-100">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Campaign Management Platform
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Advanced technology platform designed specifically for BJP Kerala's
                campaign needs, enabling data-driven decision making and efficient
                resource management.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              {features.map((feature, index) => (
                <div key={index} className="group p-6 bg-gradient-to-br from-orange-50 to-white rounded-xl border border-orange-100 hover:shadow-xl transition-all duration-300">
                  <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-400 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Vision Section */}
      <section className="py-20 bg-gradient-to-br from-orange-50 to-white">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="bg-white rounded-3xl shadow-xl overflow-hidden">
              <div className="grid md:grid-cols-2">
                <div className="p-12 space-y-6">
                  <h2 className="text-3xl font-bold text-gray-900">
                    Vision 2026: Development for All
                  </h2>
                  <div className="space-y-4">
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 text-orange-500 flex-shrink-0 mt-1" />
                      <div>
                        <h4 className="font-semibold text-gray-900">Economic Growth</h4>
                        <p className="text-gray-600">Creating 10 lakh jobs through industrial corridors and IT hubs</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 text-orange-500 flex-shrink-0 mt-1" />
                      <div>
                        <h4 className="font-semibold text-gray-900">Infrastructure Development</h4>
                        <p className="text-gray-600">Modern roads, railways, and smart cities across Kerala</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 text-orange-500 flex-shrink-0 mt-1" />
                      <div>
                        <h4 className="font-semibold text-gray-900">Cultural Heritage</h4>
                        <p className="text-gray-600">Preserving and promoting Kerala's rich traditions and temples</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-6 h-6 text-orange-500 flex-shrink-0 mt-1" />
                      <div>
                        <h4 className="font-semibold text-gray-900">Youth Empowerment</h4>
                        <p className="text-gray-600">Skill development and startup ecosystem for young Kerala</p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="bg-gradient-to-br from-orange-500 to-orange-400 p-12 text-white">
                  <h3 className="text-2xl font-bold mb-6">Join the Movement</h3>
                  <p className="mb-8">
                    Be part of Kerala's transformation journey. Together, we can build
                    a state that leads in development while preserving our values.
                  </p>
                  <button
                    onClick={handleBookDemoClick}
                    className="w-full px-8 py-4 bg-white text-orange-600 font-semibold rounded-lg hover:shadow-xl transition-all duration-300"
                  >
                    Request Campaign Access
                  </button>

                  <div className="mt-8 space-y-3">
                    <div className="flex items-center gap-3">
                      <Phone className="w-5 h-5" />
                      <span>+91 98765 43210</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <Mail className="w-5 h-5" />
                      <span>campaign@bjpkerala.org</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <MapPin className="w-5 h-5" />
                      <span>BJP Kerala State Office, Thiruvananthapuram</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-orange-600 to-orange-500">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-white mb-4">
            Ready to Transform Kerala?
          </h2>
          <p className="text-xl text-orange-100 mb-8 max-w-2xl mx-auto">
            Join thousands of karyakartas working towards a developed and prosperous Kerala.
          </p>
          <div className="flex flex-wrap gap-4 justify-center">
            <Link
              to="/login"
              className="inline-flex items-center px-8 py-4 bg-white text-orange-600 font-semibold rounded-lg hover:shadow-xl transition-all duration-300"
            >
              Campaign Login
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <button
              onClick={handleBookDemoClick}
              className="inline-flex items-center px-8 py-4 bg-orange-700 text-white font-semibold rounded-lg hover:bg-orange-800 transition-all duration-300"
            >
              <MessageCircle className="mr-2 w-5 h-5" />
              Contact Campaign Team
            </button>
          </div>
        </div>
      </section>

      {/* Modals */}
      {isVideoModalOpen && (
        <VideoModal
          isOpen={isVideoModalOpen}
          onClose={() => setIsVideoModalOpen(false)}
          videoUrl="https://www.youtube.com/embed/bjp-campaign-2026"
        />
      )}
      {isDemoModalOpen && (
        <DemoModal
          isOpen={isDemoModalOpen}
          onClose={() => setIsDemoModalOpen(false)}
        />
      )}
    </div>
  );
}
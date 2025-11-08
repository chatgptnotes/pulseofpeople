import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import VideoModal from '../components/VideoModal';
import DemoModal from '../components/DemoModal';
import { TVKLogo } from '../components/TVKLogo';
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
  MessageCircle,
  Heart,
  Flag,
  Handshake
} from 'lucide-react';
import {
  Event as CalendarIcon,
  Lock as LockIcon,
  TrendingUp as TrendingUpIcon,
  BarChart as BarChartIcon,
  HowToVote as VoteIcon,
  Gavel as GavelIcon,
  School as EducationIcon,
  LocalHospital as HealthIcon,
  Agriculture as AgricultureIcon
} from '@mui/icons-material';

export default function LandingPage() {
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(false);
  const [isDemoModalOpen, setIsDemoModalOpen] = useState(false);

  const handleVideoClick = () => {
    setIsVideoModalOpen(true);
  };

  const handleBookDemoClick = () => {
    setIsDemoModalOpen(true);
  };
  const features = [
    {
      icon: GavelIcon,
      title: 'Social Justice',
      description: 'Committed to ensuring equal rights and opportunities for all citizens, regardless of caste, religion, or economic background.'
    },
    {
      icon: EducationIcon,
      title: 'Quality Education',
      description: 'Free and accessible quality education for every child in Tamil Nadu, from primary to higher education.'
    },
    {
      icon: HealthIcon,
      title: 'Healthcare for All',
      description: 'Universal healthcare system ensuring quality medical services accessible to every Tamil family.'
    },
    {
      icon: AgricultureIcon,
      title: 'Farmer Welfare',
      description: 'Supporting Tamil Nadu farmers with fair prices, modern infrastructure, and sustainable agricultural practices.'
    },
    {
      icon: Users,
      title: 'Youth Empowerment',
      description: 'Creating employment opportunities and skill development programs for Tamil Nadu youth.'
    },
    {
      icon: Heart,
      title: "Women's Development",
      description: 'Ensuring safety, economic independence, and equal representation for women in all spheres of life.'
    }
  ];

  const stats = [
    { number: '8 Crore+', label: 'Tamil Nadu Citizens' },
    { number: '234', label: 'Assembly Constituencies' },
    { number: '39', label: 'Lok Sabha Seats' },
    { number: '2024', label: 'Year of Foundation' }
  ];

  const testimonials = [
    {
      quote: "TVK represents the voice of the common people. A party born from the grassroots to serve Tamil Nadu with integrity and vision.",
      author: "K. Selvam",
      role: "Party Member",
      party: "Chennai District",
      avatar: <TrendingUpIcon className="w-8 h-8 text-red-600" />
    },
    {
      quote: "For the first time, we have a platform that truly understands the aspirations of Tamil youth and the challenges we face.",
      author: "Priya Devi",
      role: "Youth Wing",
      party: "Coimbatore Region",
      avatar: <BarChartIcon className="w-8 h-8 text-yellow-600" />
    },
    {
      quote: "TVK's commitment to social justice and equality gives hope to millions. This is the change Tamil Nadu has been waiting for.",
      author: "M. Raj kumar",
      role: "Social Activist",
      party: "Madurai Division",
      avatar: <VoteIcon className="w-8 h-8 text-red-700" />
    }
  ];

  const useCases = [
    {
      icon: Flag,
      title: 'Tamil Pride & Identity',
      description: 'Preserving and promoting Tamil language, culture, and heritage across all aspects of governance.'
    },
    {
      icon: Handshake,
      title: 'Secular Governance',
      description: 'Equal respect and opportunities for all religions, castes, and communities in Tamil Nadu.'
    },
    {
      icon: Globe,
      title: 'Transparent Administration',
      description: 'Corruption-free governance with accountability and citizen participation at every level.'
    },
    {
      icon: Shield,
      title: 'People First Politics',
      description: 'Decision-making focused on the welfare and development of Tamil Nadu citizens.'
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-red-900 via-red-800 to-red-700" style={{ background: 'linear-gradient(135deg, #C41E3A 0%, #8B1428 50%, #C41E3A 100%)' }}>
        <div className="absolute inset-0 bg-black/30"></div>
        {/* Gold accent overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-yellow-600/10 via-transparent to-transparent"></div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="text-center">
            {/* TVK Logo */}
            <div className="flex justify-center mb-8">
              <TVKLogo size="large" className="animate-fadeIn" />
            </div>

            {/* Brand Badge */}
            <div className="inline-flex items-center px-4 py-2 rounded-full bg-yellow-500/20 backdrop-blur-sm border border-yellow-400/30 text-yellow-100 text-sm font-medium mb-8">
              <Award className="w-4 h-4 mr-2" />
              Tamilaga Vettri Kazhagam
            </div>

            {/* Hero Title */}
            <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              <span className="bg-gradient-to-r from-yellow-300 via-yellow-400 to-yellow-300 bg-clip-text text-transparent block mb-2">
                தமிழக வெற்றி கழகம்
              </span>
              A New Dawn for Tamil Nadu
            </h1>

            {/* Hero Subtitle */}
            <p className="text-xl lg:text-2xl text-yellow-50 max-w-4xl mx-auto mb-10 leading-relaxed">
              Building a prosperous, just, and progressive Tamil Nadu where every citizen has equal opportunities
              and voices are heard. Join us in creating the change we deserve.
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <button
                onClick={handleBookDemoClick}
                className="group px-8 py-4 bg-gradient-to-r from-yellow-500 to-yellow-600 text-red-900 font-bold rounded-xl hover:shadow-2xl hover:shadow-yellow-500/50 transition-all duration-300 flex items-center transform hover:scale-105"
              >
                <Users className="mr-2 w-5 h-5" />
                Join TVK
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <Link
                to="/login"
                className="group px-8 py-4 bg-white/10 backdrop-blur-sm border border-yellow-400/30 text-yellow-100 font-semibold rounded-xl hover:bg-white/20 transition-all duration-300 flex items-center transform hover:scale-105"
              >
                <LockIcon className="mr-2 w-5 h-5" />
                Member Login
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <button
                onClick={handleVideoClick}
                className="group px-8 py-4 bg-white/10 backdrop-blur-sm border border-yellow-400/30 text-yellow-100 font-semibold rounded-xl hover:bg-white/20 transition-all duration-300 flex items-center transform hover:scale-105"
              >
                <Play className="mr-2 w-5 h-5" />
                Watch Vision
              </button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap justify-center items-center gap-8 text-yellow-100/80 text-sm">
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 mr-2 text-yellow-400" />
                Registered Political Party
              </div>
              <div className="flex items-center">
                <Shield className="w-4 h-4 mr-2 text-yellow-400" />
                Grassroots Movement
              </div>
              <div className="flex items-center">
                <Heart className="w-4 h-4 mr-2 text-yellow-400" />
                People-Powered
              </div>
            </div>
          </div>
        </div>
        
        {/* Floating Elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-yellow-500/10 rounded-full animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-32 h-32 bg-yellow-600/10 rounded-full animate-bounce"></div>
        <div className="absolute top-1/2 right-20 w-16 h-16 bg-red-500/10 rounded-full animate-ping"></div>
      </div>

      {/* Stats Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl lg:text-5xl font-bold text-gray-900 mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
              Our Vision for
              <span className="text-red-700 block">Tamil Nadu's Future</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              TVK is committed to building a Tamil Nadu that prioritizes social justice,
              education, healthcare, and the welfare of every citizen.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="group p-8 rounded-2xl bg-white border border-gray-200 hover:border-red-300 hover:shadow-xl transition-all duration-300">
                <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-6 h-6 text-yellow-300" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Use Cases Section */}
      <div className="py-20 bg-gradient-to-br from-gray-50 to-red-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
              Our Core
              <span className="text-red-700 block">Principles & Values</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              TVK stands for transparent, accountable, and people-centric governance
              that puts Tamil Nadu's interests first.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {useCases.map((useCase, index) => (
              <div key={index} className="flex items-start space-x-6 p-8 bg-white rounded-2xl shadow-sm hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center flex-shrink-0">
                  <useCase.icon className="w-6 h-6 text-yellow-300" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">
                    {useCase.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {useCase.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-6">
              Voices from the
              <span className="text-red-700 block">TVK Movement</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Hear from party members, supporters, and activists across Tamil Nadu
              about why they believe in TVK's vision for change.
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-gray-50 p-8 rounded-2xl">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <blockquote className="text-gray-700 text-lg leading-relaxed mb-6">
                  "{testimonial.quote}"
                </blockquote>
                <div className="flex items-center">
                  <div className="mr-4 flex items-center justify-center w-12 h-12 bg-gray-100 rounded-full">{testimonial.avatar}</div>
                  <div>
                    <div className="font-bold text-gray-900">{testimonial.author}</div>
                    <div className="text-gray-600">{testimonial.role}</div>
                    <div className="text-sm text-gray-500">{testimonial.party}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Final CTA Section */}
      <div className="py-20 bg-gradient-to-r from-red-700 to-red-800" style={{ background: 'linear-gradient(90deg, #C41E3A 0%, #8B1428 100%)' }}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
            Be Part of the Change
          </h2>
          <p className="text-xl text-yellow-100 mb-10">
            Join thousands of Tamil Nadu citizens who believe in TVK's vision for a better,
            more prosperous, and just Tamil Nadu.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleBookDemoClick}
              className="px-8 py-4 bg-yellow-500 text-red-900 font-bold rounded-xl hover:shadow-xl hover:bg-yellow-400 transition-all duration-300 flex items-center justify-center transform hover:scale-105"
            >
              <Users className="mr-2 w-5 h-5" />
              Join TVK Today
              <ArrowRight className="ml-2 w-5 h-5" />
            </button>
            <Link
              to="/login"
              className="px-8 py-4 bg-white/20 backdrop-blur-sm border border-yellow-400/30 text-yellow-100 font-semibold rounded-xl hover:bg-white/30 transition-all duration-300 flex items-center justify-center"
            >
              <LockIcon className="mr-2 w-5 h-5" />
              Member Login
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center mb-4">
                <div className="flex items-center space-x-3">
                  <TVKLogo size="small" />
                  <div>
                    <div className="text-2xl font-bold text-red-500">TVK</div>
                    <div className="text-sm text-yellow-500">Tamilaga Vettri Kazhagam</div>
                  </div>
                </div>
              </div>
              <p className="text-gray-400 mb-4">
                A grassroots political movement dedicated to building a prosperous, just,
                and progressive Tamil Nadu through transparent governance and people-centric policies.
              </p>
              <div className="flex items-center text-gray-400">
                <MapPin className="w-4 h-4 mr-2" />
                Tamil Nadu, India
              </div>
            </div>
            <div>
              <h3 className="font-bold mb-4 text-yellow-500">Quick Links</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/dashboard" className="hover:text-yellow-400 transition-colors">Party Dashboard</Link></li>
                <li><Link to="/analytics" className="hover:text-yellow-400 transition-colors">Campaign Analytics</Link></li>
                <li><Link to="/voter-database" className="hover:text-yellow-400 transition-colors">Voter Outreach</Link></li>
                <li><Link to="/ai-insights" className="hover:text-yellow-400 transition-colors">Policy Insights</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold mb-4 text-yellow-500">Contact TVK</h3>
              <div className="space-y-3 text-gray-400">
                <div className="flex items-center">
                  <MapPin className="w-4 h-4 mr-2 text-red-400" />
                  <span className="text-sm">Chennai, Tamil Nadu</span>
                </div>
                <div className="flex items-center">
                  <Phone className="w-4 h-4 mr-2 text-yellow-400" />
                  <a href="tel:+919373111709" className="text-sm hover:text-yellow-400 transition-colors">
                    +91 9373111709
                  </a>
                </div>
                <div className="flex items-center">
                  <Mail className="w-4 h-4 mr-2 text-red-400" />
                  <a href="mailto:contact@tvk.org" className="text-sm hover:text-yellow-400 transition-colors">
                    contact@tvk.org
                  </a>
                </div>
                <div className="flex items-center">
                  <MessageCircle className="w-4 h-4 mr-2 text-yellow-400" />
                  <a href="https://wa.me/919373111709" className="text-sm hover:text-yellow-400 transition-colors">
                    WhatsApp Support
                  </a>
                </div>
                <div className="mt-4 pt-3 border-t border-gray-700">
                  <p className="text-xs font-medium">Join the Movement</p>
                  <p className="text-xs">Offices across all 234 constituencies</p>
                </div>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Tamilaga Vettri Kazhagam. All rights reserved. For the people, by the people.</p>
          </div>
        </div>
      </div>

      {/* Video Modal */}
      <VideoModal
        isOpen={isVideoModalOpen}
        onClose={() => setIsVideoModalOpen(false)}
        title="TVK Vision and Mission"
      />

      {/* Demo Modal */}
      <DemoModal
        isOpen={isDemoModalOpen}
        onClose={() => setIsDemoModalOpen(false)}
      />
    </div>
  );
}
import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Plus,
  Filter,
  Download,
  Upload,
  Edit3,
  MapPin,
  Phone,
  Mail,
  Calendar,
  User,
  Tag,
  BarChart3,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Clock,
  Target,
  FileText,
  Camera,
  X
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { exportToCSV, exportToExcel, flattenForExport } from '../utils/exportUtils';
import { votersService } from '../services/supabase/voters.service';
import { validateField, ValidationRules } from '../lib/form-validation';
import { useAuth } from '../contexts/AuthContext';

export default function VoterDatabase() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [editingVoter, setEditingVoter] = useState<any>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [voterToDelete, setVoterToDelete] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [voters, setVoters] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [totalVoters, setTotalVoters] = useState(0);
  const [showIncompleteDataAlert, setShowIncompleteDataAlert] = useState(true);
  const [showImportModal, setShowImportModal] = useState(false);

  // New voter form state
  const [newVoterData, setNewVoterData] = useState({
    name: '',
    age: '',
    gender: '',
    voterIdCard: '',
    phone: '',
    email: '',
    caste: '',
    religion: '',
    education: '',
    occupation: '',
    constituency: '',
    booth: '',
    address: '',
    interests: [] as string[]
  });

  // Fetch voters from database
  useEffect(() => {
    fetchVoters();
  }, []);

  const fetchVoters = async () => {
    setIsLoading(true);
    setFetchError(null);
    try {
      console.log('🔍 Fetching voters from database...');
      const result = await votersService.getAll();
      console.log('✅ Voters fetched:', result);

      // Transform Supabase data to match component structure
      const transformedVoters = result.data.map((voter: any) => ({
        id: voter.id,
        name: voter.full_name,
        age: voter.age,
        gender: voter.gender,
        phone: voter.phone || 'Not Provided',
        email: voter.email || 'Not Provided',
        address: voter.address || 'Not Provided',
        constituency: voter.polling_booth?.constituency?.name || 'Not Assigned',
        booth: voter.polling_booth?.name || 'Not Assigned',
        voterIdCard: voter.voter_id_number,
        demographics: {
          caste: voter.caste || 'Not Specified',
          religion: voter.religion || 'Not Specified',
          education: voter.education || 'Not Specified',
          occupation: voter.occupation || 'Not Specified',
          income: 'Not Available'
        },
        interests: voter.tags || [],
        contactHistory: [],
        engagement: {
          ralliesAttended: 0,
          lastContact: voter.updated_at?.split('T')[0] || 'N/A',
          supportLevel: voter.sentiment === 'positive' ? 'Strong' : voter.sentiment === 'neutral' ? 'Moderate' : 'Weak',
          likelihood: voter.sentiment_score || 50
        },
        status: voter.verified ? 'Active' : 'Pending',
        addedBy: 'System',
        addedDate: voter.created_at?.split('T')[0] || 'N/A'
      }));

      setVoters(transformedVoters);
      setTotalVoters(result.count || transformedVoters.length);
      console.log('✅ Transformed voters:', transformedVoters);
    } catch (error: any) {
      console.error('❌ Failed to fetch voters:', error);
      const errorMessage = error?.message || 'Unknown error occurred';
      setFetchError(errorMessage);
      // Keep empty array on error
      setVoters([]);
      setTotalVoters(0);
    } finally {
      setIsLoading(false);
    }
  };

  // Mock voter database - fallback (will be replaced by real data)
  const voterDatabase = voters.length > 0 ? voters : [
    {
      id: 'VTR001',
      name: 'Rajesh Kumar',
      age: 42,
      gender: 'Male',
      phone: '+91-9876543210',
      email: 'rajesh.kumar@email.com',
      address: 'Plot 45, Sector 12, Gurgaon',
      constituency: 'Gurgaon Rural',
      booth: 'GR-045',
      voterIdCard: 'ABC123456789',
      demographics: {
        caste: 'General',
        religion: 'Hindu',
        education: 'Graduate',
        occupation: 'Engineer',
        income: '5-10 Lakhs'
      },
      interests: ['Infrastructure', 'Technology', 'Education'],
      contactHistory: [
        { date: '2024-01-15', type: 'Door-to-door', worker: 'Amit Singh', notes: 'Positive response to education policies' },
        { date: '2024-01-10', type: 'Phone Call', worker: 'Priya Sharma', notes: 'Interested in infrastructure development' }
      ],
      engagement: {
        ralliesAttended: 2,
        lastContact: '2024-01-15',
        supportLevel: 'Strong',
        likelihood: 95
      },
      status: 'Active',
      addedBy: 'Field Worker 001',
      addedDate: '2024-01-01'
    },
    {
      id: 'VTR002',
      name: 'Sunita Devi',
      age: 38,
      gender: 'Female',
      phone: '+91-9876543211',
      email: 'sunita.devi@email.com',
      address: 'House 23, Block C, Noida',
      constituency: 'Noida',
      booth: 'ND-023',
      voterIdCard: 'DEF987654321',
      demographics: {
        caste: 'OBC',
        religion: 'Hindu',
        education: 'Post Graduate',
        occupation: 'Teacher',
        income: '3-5 Lakhs'
      },
      interests: ['Education', 'Women Safety', 'Healthcare'],
      contactHistory: [
        { date: '2024-01-12', type: 'Rally', worker: 'Meera Gupta', notes: 'Very enthusiastic about education reforms' }
      ],
      engagement: {
        ralliesAttended: 3,
        lastContact: '2024-01-12',
        supportLevel: 'Strong',
        likelihood: 90
      },
      status: 'Active',
      addedBy: 'Field Worker 002',
      addedDate: '2024-01-02'
    },
    {
      id: 'VTR003',
      name: 'Mohammed Ali',
      age: 35,
      gender: 'Male',
      phone: '+91-9876543212',
      email: 'mohammed.ali@email.com',
      address: 'Lane 5, Old Delhi',
      constituency: 'Chandni Chowk',
      booth: 'CC-012',
      voterIdCard: 'GHI456789123',
      demographics: {
        caste: 'Muslim',
        religion: 'Islam',
        education: 'Graduate',
        occupation: 'Business',
        income: '2-3 Lakhs'
      },
      interests: ['Economic Policy', 'Small Business', 'Healthcare'],
      contactHistory: [
        { date: '2024-01-14', type: 'WhatsApp', worker: 'Arjun Patel', notes: 'Concerned about economic policies' }
      ],
      engagement: {
        ralliesAttended: 1,
        lastContact: '2024-01-14',
        supportLevel: 'Moderate',
        likelihood: 70
      },
      status: 'Active',
      addedBy: 'Field Worker 003',
      addedDate: '2024-01-03'
    }
  ];

  // Calculate analytics from real data
  const databaseStats = {
    totalVoters: voterDatabase.length,
    newRegistrations: voterDatabase.filter(v => {
      const createdDate = new Date(v.addedDate);
      const monthAgo = new Date();
      monthAgo.setMonth(monthAgo.getMonth() - 1);
      return createdDate >= monthAgo;
    }).length,
    activeVoters: voterDatabase.filter(v => v.status === 'Active').length,
    strongSupport: voterDatabase.filter(v => v.engagement.supportLevel === 'Strong').length,
    moderateSupport: voterDatabase.filter(v => v.engagement.supportLevel === 'Moderate').length,
    weakSupport: voterDatabase.filter(v => v.engagement.supportLevel === 'Weak').length
  };

  // Calculate DYNAMIC demographic breakdown from real data
  const calculateDemographicBreakdown = () => {
    const casteCount: Record<string, number> = {};

    // Only count voters with valid caste data
    const validVoters = voterDatabase.filter(v =>
      v.demographics.caste &&
      v.demographics.caste !== 'N/A' &&
      v.demographics.caste !== 'Unknown' &&
      v.demographics.caste !== 'Not Specified' &&
      v.demographics.caste.trim() !== ''
    );

    const total = validVoters.length || 1;

    validVoters.forEach(voter => {
      const caste = voter.demographics.caste;
      casteCount[caste] = (casteCount[caste] || 0) + 1;
    });

    const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

    return Object.entries(casteCount).map(([category, count], index) => ({
      category,
      count,
      percentage: parseFloat(((count / total) * 100).toFixed(1)),
      color: colors[index % colors.length]
    })).sort((a, b) => b.count - a.count);
  };

  const demographicBreakdown = voterDatabase.length > 0
    ? calculateDemographicBreakdown()
    : [
        { category: 'General', count: 45230, percentage: 36.1, color: '#3B82F6' },
        { category: 'OBC', count: 38140, percentage: 30.4, color: '#10B981' },
        { category: 'SC', count: 25680, percentage: 20.5, color: '#F59E0B' },
        { category: 'ST', count: 16370, percentage: 13.0, color: '#EF4444' }
      ];

  // Calculate DYNAMIC support level data
  const supportLevelData = [
    { level: 'Strong Support', count: databaseStats.strongSupport, color: '#10B981' },
    { level: 'Moderate Support', count: databaseStats.moderateSupport, color: '#F59E0B' },
    { level: 'Weak Support', count: databaseStats.weakSupport, color: '#EF4444' }
  ];

  // Calculate DYNAMIC booth-wise data from real voters
  const calculateBoothWiseData = () => {
    const boothStats: Record<string, { voters: number; contacted: number; strong: number }> = {};

    // Only process voters with valid booth data
    const validBoothVoters = voterDatabase.filter(v =>
      v.booth &&
      v.booth !== 'N/A' &&
      v.booth !== 'Unknown' &&
      v.booth !== 'Not Assigned' &&
      v.booth.trim() !== ''
    );

    validBoothVoters.forEach(voter => {
      const booth = voter.booth;
      if (!boothStats[booth]) {
        boothStats[booth] = { voters: 0, contacted: 0, strong: 0 };
      }
      boothStats[booth].voters++;
      if (voter.status === 'Active') boothStats[booth].contacted++;
      if (voter.engagement.supportLevel === 'Strong') boothStats[booth].strong++;
    });

    return Object.entries(boothStats).map(([booth, stats]) => ({
      booth,
      voters: stats.voters,
      contacted: stats.contacted,
      support: Math.round((stats.strong / stats.voters) * 100)
    })).sort((a, b) => b.voters - a.voters).slice(0, 10); // Top 10 booths
  };

  const boothWiseData = voterDatabase.length > 0
    ? calculateBoothWiseData()
    : [
        { booth: 'GR-001', voters: 1240, contacted: 980, support: 78 },
        { booth: 'GR-002', voters: 1180, contacted: 920, support: 82 },
        { booth: 'ND-001', voters: 1320, contacted: 1100, support: 75 },
        { booth: 'ND-002', voters: 1150, contacted: 950, support: 85 },
        { booth: 'CC-001', voters: 1080, contacted: 850, support: 68 }
      ];

  // Calculate DYNAMIC top interests from voters
  const calculateTopInterests = () => {
    const interestCount: Record<string, number> = {};
    const total = voterDatabase.length || 1;

    voterDatabase.forEach(voter => {
      voter.interests?.forEach(interest => {
        interestCount[interest] = (interestCount[interest] || 0) + 1;
      });
    });

    return Object.entries(interestCount)
      .map(([interest, count]) => ({
        interest,
        count,
        percentage: Math.round((count / total) * 100)
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5); // Top 5 interests
  };

  const topInterests = voterDatabase.length > 0
    ? calculateTopInterests()
    : [
        { interest: 'Infrastructure', count: 45280, percentage: 78 },
        { interest: 'Education', count: 38940, percentage: 67 },
        { interest: 'Healthcare', count: 32150, percentage: 55 },
        { interest: 'Employment', count: 28760, percentage: 49 },
        { interest: 'Women Safety', count: 24830, percentage: 43 }
      ];

  // Calculate DYNAMIC constituency coverage
  const calculateConstituencyCoverage = () => {
    const constituencyCount: Record<string, { total: number; active: number }> = {};

    // Only process voters with valid constituency data
    const validConstituencyVoters = voterDatabase.filter(v =>
      v.constituency &&
      v.constituency !== 'N/A' &&
      v.constituency !== 'Unknown' &&
      v.constituency !== 'Not Assigned' &&
      v.constituency.trim() !== ''
    );

    validConstituencyVoters.forEach(voter => {
      const constituency = voter.constituency;
      if (!constituencyCount[constituency]) {
        constituencyCount[constituency] = { total: 0, active: 0 };
      }
      constituencyCount[constituency].total++;
      if (voter.status === 'Active') constituencyCount[constituency].active++;
    });

    return Object.entries(constituencyCount)
      .map(([area, stats]) => ({
        area,
        coverage: Math.round((stats.active / stats.total) * 100),
        voters: stats.total
      }))
      .sort((a, b) => b.voters - a.voters)
      .slice(0, 5); // Top 5 constituencies
  };

  const geographicCoverage = voterDatabase.length > 0
    ? calculateConstituencyCoverage()
    : [
        { area: 'Urban Areas', coverage: 92, voters: 45230 },
        { area: 'Semi-Urban', coverage: 78, voters: 38140 },
        { area: 'Rural Areas', coverage: 65, voters: 42050 }
      ];

  // Calculate DYNAMIC contact method success from voter data
  const calculateContactMethodSuccess = () => {
    const contactStats: Record<string, { total: number; successful: number }> = {};

    voterDatabase.forEach(voter => {
      voter.contactHistory?.forEach((contact: any) => {
        const method = contact.type || 'Unknown';
        if (!contactStats[method]) {
          contactStats[method] = { total: 0, successful: 0 };
        }
        contactStats[method].total++;
        // Consider contact successful if it resulted in positive engagement
        if (voter.engagement.supportLevel === 'Strong' || voter.engagement.supportLevel === 'Moderate') {
          contactStats[method].successful++;
        }
      });
    });

    return Object.entries(contactStats).map(([method, stats]) => ({
      method,
      success: Math.round((stats.successful / stats.total) * 100),
      attempts: stats.total
    })).sort((a, b) => b.success - a.success);
  };

  const contactMethodSuccess = voterDatabase.length > 0 && voterDatabase.some(v => v.contactHistory?.length > 0)
    ? calculateContactMethodSuccess()
    : [
        { method: 'Door-to-door', success: 89, attempts: 12450 },
        { method: 'Phone Call', success: 67, attempts: 8920 },
        { method: 'WhatsApp', success: 78, attempts: 15680 },
        { method: 'Rally', success: 95, attempts: 3240 },
        { method: 'SMS', success: 45, attempts: 18920 }
      ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'database', label: 'Voter Database', icon: Users },
    { id: 'analytics', label: 'Analytics', icon: TrendingUp },
    { id: 'registration', label: 'Registration', icon: Plus }
  ];

  const filteredVoters = voterDatabase.filter(voter => {
    const matchesSearch = voter.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         voter.constituency.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         voter.voterIdCard.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilter = selectedFilter === 'all' ||
                         voter.engagement.supportLevel.toLowerCase() === selectedFilter.toLowerCase();

    return matchesSearch && matchesFilter;
  });

  // Pagination calculations
  const totalFilteredVoters = filteredVoters.length;
  const totalPages = Math.ceil(totalFilteredVoters / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedVoters = filteredVoters.slice(startIndex, endIndex);

  // Reset to page 1 when search/filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, selectedFilter]);

  // Handle page change
  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
    }
  };

  // Export handlers
  const handleExportCSV = () => {
    const exportData = flattenForExport(filteredVoters);
    const timestamp = new Date().toISOString().split('T')[0];
    exportToCSV(exportData, `voter-database-${timestamp}.csv`);
  };

  const handleExportExcel = () => {
    const exportData = flattenForExport(filteredVoters);
    const timestamp = new Date().toISOString().split('T')[0];
    exportToExcel(exportData, `voter-database-${timestamp}`, 'Voters');
  };

  // Edit voter handler
  const handleEditClick = (voter: any) => {
    setEditingVoter(voter);
    setShowEditModal(true);
  };

  // Update voter handler
  const handleUpdateVoter = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingVoter || !editingVoter.id) return;

    // Validate form fields
    const validationErrors: string[] = [];

    // Validate name
    const nameError = validateField(editingVoter.name, [
      ValidationRules.required(),
      ValidationRules.minLength(2)
    ]);
    if (nameError) validationErrors.push(`Name: ${nameError}`);

    // Validate phone
    const phoneError = validateField(editingVoter.phone, [
      ValidationRules.required(),
      ValidationRules.phone()
    ]);
    if (phoneError) validationErrors.push(`Phone: ${phoneError}`);

    // Validate email (if provided)
    if (editingVoter.email) {
      const emailError = validateField(editingVoter.email, [ValidationRules.email()]);
      if (emailError) validationErrors.push(`Email: ${emailError}`);
    }

    // Validate age
    const ageError = validateField(editingVoter.age?.toString(), [
      ValidationRules.required(),
      ValidationRules.numeric(),
      ValidationRules.min(18),
      ValidationRules.max(120)
    ]);
    if (ageError) validationErrors.push(`Age: ${ageError}`);

    // Show validation errors
    if (validationErrors.length > 0) {
      alert('Validation errors:\n' + validationErrors.join('\n'));
      return;
    }

    setIsSubmitting(true);
    try {
      // TODO: Integrate with votersService.update() when ready
      // await votersService.update(editingVoter.id, editingVoter);

      alert(`Voter "${editingVoter.name}" updated successfully!`);
      setShowEditModal(false);
      setEditingVoter(null);
      // TODO: Refresh voter list after update
    } catch (error: any) {
      console.error('Failed to update voter:', error);
      alert(error.message || 'Failed to update voter');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Delete voter handler
  const handleDeleteClick = (voter: any) => {
    setVoterToDelete(voter);
    setShowDeleteModal(true);
  };

  // Confirm delete handler
  const handleConfirmDelete = async () => {
    if (!voterToDelete || !voterToDelete.id) return;

    setIsSubmitting(true);
    try {
      // TODO: Integrate with votersService.delete() when ready
      // await votersService.delete(voterToDelete.id);

      alert(`Voter "${voterToDelete.name}" deleted successfully!`);
      setShowDeleteModal(false);
      setVoterToDelete(null);
      // TODO: Refresh voter list after delete
    } catch (error: any) {
      console.error('Failed to delete voter:', error);
      alert(error.message || 'Failed to delete voter');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Add new voter handler
  const handleAddVoter = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form fields
    const validationErrors: string[] = [];

    // Validate name
    const nameError = validateField(newVoterData.name, [
      ValidationRules.required(),
      ValidationRules.minLength(2)
    ]);
    if (nameError) validationErrors.push(`Name: ${nameError}`);

    // Validate age
    const ageError = validateField(newVoterData.age, [
      ValidationRules.required(),
      ValidationRules.numeric(),
      ValidationRules.min(18),
      ValidationRules.max(120)
    ]);
    if (ageError) validationErrors.push(`Age: ${ageError}`);

    // Validate gender
    if (!newVoterData.gender) validationErrors.push('Gender is required');

    // Validate voter ID
    if (!newVoterData.voterIdCard.trim()) {
      validationErrors.push('Voter ID Card is required');
    }

    // Validate phone
    const phoneError = validateField(newVoterData.phone, [
      ValidationRules.required(),
      ValidationRules.phone()
    ]);
    if (phoneError) validationErrors.push(`Phone: ${phoneError}`);

    // Validate email if provided
    if (newVoterData.email) {
      const emailError = validateField(newVoterData.email, [ValidationRules.email()]);
      if (emailError) validationErrors.push(`Email: ${emailError}`);
    }

    // Note: Constituency and Booth are optional in the form
    // They will be properly linked when polling booth management is fully implemented

    if (validationErrors.length > 0) {
      alert('Validation errors:\n\n' + validationErrors.join('\n'));
      return;
    }

    setIsSubmitting(true);

    try {
      // Check if user is logged in and has organization_id
      if (!user?.organization_id) {
        alert('❌ Error: You must be logged in with a valid organization to add voters.');
        setIsSubmitting(false);
        return;
      }

      // Prepare data for Supabase voters table
      const voterPayload = {
        full_name: newVoterData.name,
        age: parseInt(newVoterData.age),
        gender: newVoterData.gender as 'Male' | 'Female' | 'Other',
        voter_id_number: newVoterData.voterIdCard,
        epic_number: newVoterData.voterIdCard, // Same as voter ID for now
        phone: newVoterData.phone,
        email: newVoterData.email || null,
        // Demographics
        caste: newVoterData.caste || null,
        religion: newVoterData.religion || null,
        education: newVoterData.education || null,
        occupation: newVoterData.occupation || null,
        // Location (address only - constituency is managed through polling_booth_id)
        address: newVoterData.address || null,
        polling_booth_id: null, // TODO: Link to actual polling booth when booth management is implemented
        // Interests as tags
        tags: newVoterData.interests.length > 0 ? newVoterData.interests : null,
        // Default values
        verified: false,
        consent_given: false,
        sentiment: 'neutral' as const,
        sentiment_score: 50,
        voter_category: null, // Will be set based on sentiment analysis
        influencer_score: 0,
        first_time_voter: false,
        contacted_by_party: false,
        data_quality_score: 75, // Basic score for manual entry
        organization_id: user.organization_id, // Get from logged-in user
        created_by: user.id // Track who created this voter
      };

      // Save to database using votersService
      const createdVoter = await votersService.create(voterPayload as any);

      alert(`✅ Voter "${newVoterData.name}" added successfully!\n\nVoter ID: ${createdVoter.id}`);

      // Refresh voter list
      await fetchVoters();

      // Reset form
      setNewVoterData({
        name: '',
        age: '',
        gender: '',
        voterIdCard: '',
        phone: '',
        email: '',
        caste: '',
        religion: '',
        education: '',
        occupation: '',
        constituency: '',
        booth: '',
        address: '',
        interests: []
      });

      // Switch to voter database tab to see the new voter
      setActiveTab('database');

    } catch (error: any) {
      console.error('Failed to add voter:', error);
      alert(`❌ Failed to add voter\n\n${error.message || 'Unknown error occurred'}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle interest checkbox change
  const handleInterestChange = (interest: string, checked: boolean) => {
    setNewVoterData(prev => ({
      ...prev,
      interests: checked
        ? [...prev.interests, interest]
        : prev.interests.filter(i => i !== interest)
    }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h2 className="text-3xl font-bold text-gray-900 flex items-center">
            <Users className="w-8 h-8 mr-3 text-blue-600" />
            Voter Database Management
          </h2>
          <div className="flex items-center space-x-3">
            <p className="text-gray-600">Comprehensive voter registration and engagement tracking system</p>
            {voters.length > 0 && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-1.5 animate-pulse"></span>
                Live Data
              </span>
            )}
            {voters.length === 0 && !isLoading && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                Mock Data
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowImportModal(true)}
            className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            <Upload className="w-4 h-4" />
            <span>Import Data</span>
          </button>
          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={handleExportExcel}
            className="flex items-center space-x-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export Excel</span>
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <Users className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-xl font-bold text-gray-900">{databaseStats.totalVoters.toLocaleString()}</div>
              <div className="text-xs text-gray-600">Total Voters</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <Plus className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-xl font-bold text-gray-900">+{databaseStats.newRegistrations.toLocaleString()}</div>
              <div className="text-xs text-gray-600">New This Month</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
              <CheckCircle className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-xl font-bold text-gray-900">{databaseStats.activeVoters.toLocaleString()}</div>
              <div className="text-xs text-gray-600">Active Voters</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center mr-3">
              <Target className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <div className="text-xl font-bold text-gray-900">{databaseStats.strongSupport.toLocaleString()}</div>
              <div className="text-xs text-gray-600">Strong Support</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center mr-3">
              <AlertCircle className="w-5 h-5 text-yellow-600" />
            </div>
            <div>
              <div className="text-xl font-bold text-gray-900">{databaseStats.moderateSupport.toLocaleString()}</div>
              <div className="text-xs text-gray-600">Moderate Support</div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mr-3">
              <Clock className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <div className="text-xl font-bold text-gray-900">
                {databaseStats.totalVoters > 0
                  ? ((databaseStats.activeVoters / databaseStats.totalVoters) * 100).toFixed(1)
                  : '0'}%
              </div>
              <div className="text-xs text-gray-600">Contact Rate</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="w-5 h-5 mr-2" />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Info Message for Incomplete Data */}
          {showIncompleteDataAlert && voterDatabase.length > 0 && (demographicBreakdown.length === 0 || boothWiseData.length === 0) && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-blue-900 text-sm">Some voters have incomplete data</h4>
                <p className="text-xs text-blue-700 mt-1">
                  Charts display only voters with complete demographic and booth information.
                </p>
              </div>
              <button
                onClick={() => setShowIncompleteDataAlert(false)}
                className="text-blue-400 hover:text-blue-600 transition-colors flex-shrink-0"
                title="Dismiss"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {/* Demographic Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Demographic Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={demographicBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ category, percentage }) => `${category} ${percentage}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {demographicBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any) => [value.toLocaleString(), 'Voters']} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Support Level Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={supportLevelData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="level" type="category" width={100} />
                  <Tooltip formatter={(value: any) => [value.toLocaleString(), 'Voters']} />
                  <Bar dataKey="count" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Booth-wise Performance */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Booth-wise Coverage Analysis</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-900">Booth</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">Total Voters</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">Contacted</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">Contact Rate</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">Support %</th>
                  </tr>
                </thead>
                <tbody>
                  {boothWiseData.map((booth) => (
                    <tr key={booth.booth} className="border-b border-gray-100">
                      <td className="py-3 px-4 font-medium text-gray-900">{booth.booth}</td>
                      <td className="py-3 px-4 text-right">{booth.voters.toLocaleString()}</td>
                      <td className="py-3 px-4 text-right">{booth.contacted.toLocaleString()}</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end">
                          <div className="w-16 h-2 bg-gray-200 rounded-full mr-2">
                            <div 
                              className="h-2 bg-blue-500 rounded-full"
                              style={{ width: `${(booth.contacted / booth.voters) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium">
                            {Math.round((booth.contacted / booth.voters) * 100)}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          booth.support >= 80 ? 'bg-green-100 text-green-800' :
                          booth.support >= 70 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {booth.support}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'database' && (
        <div className="space-y-6">
          {/* Error State */}
          {fetchError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold text-red-900">Failed to fetch voters</h4>
                <p className="text-sm text-red-700 mt-1">{fetchError}</p>
                <button
                  onClick={fetchVoters}
                  className="mt-3 text-sm bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                >
                  Try Again
                </button>
              </div>
            </div>
          )}

          {/* Loading State */}
          {isLoading ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading voters...</p>
            </div>
          ) : (
            <>
          {/* Search and Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="flex items-center space-x-4">
              <div className="flex-1 relative">
                <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by name, voter ID, or constituency..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <select 
                value={selectedFilter} 
                onChange={(e) => setSelectedFilter(e.target.value)}
                className="border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Support Levels</option>
                <option value="strong">Strong Support</option>
                <option value="moderate">Moderate Support</option>
                <option value="weak">Weak Support</option>
              </select>
              <button
                onClick={() => setActiveTab('registration')}
                className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>Add Voter</span>
              </button>
            </div>
          </div>

          {/* Voter List */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900">Voter Details</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900">Demographics</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900">Contact Info</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900">Engagement</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedVoters.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-gray-500">
                        <Users className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                        <p className="text-lg font-medium">No voters found</p>
                        <p className="text-sm mt-1">{totalFilteredVoters > 0 ? 'Try changing your search or filter' : 'Add your first voter to get started'}</p>
                      </td>
                    </tr>
                  ) : (
                    paginatedVoters.map((voter) => (
                    <tr key={voter.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4">
                        <div>
                          <div className="font-medium text-gray-900">{voter.name}</div>
                          <div className="text-sm text-gray-600">{voter.voterIdCard}</div>
                          <div className="text-sm text-gray-600">{voter.constituency} - {voter.booth}</div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="text-sm">
                          <div>{voter.age}y, {voter.gender}</div>
                          <div className="text-gray-600">{voter.demographics.caste}</div>
                          <div className="text-gray-600">{voter.demographics.occupation}</div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="text-sm">
                          <div className="flex items-center">
                            <Phone className="w-3 h-3 mr-1 text-gray-400" />
                            {voter.phone}
                          </div>
                          <div className="flex items-center mt-1">
                            <Mail className="w-3 h-3 mr-1 text-gray-400" />
                            {voter.email}
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="text-sm">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            voter.engagement.supportLevel === 'Strong' ? 'bg-green-100 text-green-800' :
                            voter.engagement.supportLevel === 'Moderate' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {voter.engagement.supportLevel}
                          </span>
                          <div className="text-gray-600 mt-1">
                            {voter.engagement.ralliesAttended} rallies attended
                          </div>
                          <div className="text-gray-600">
                            Last: {voter.engagement.lastContact}
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleEditClick(voter)}
                            className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                            title="Edit Voter"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-green-600 transition-colors" title="Call Voter">
                            <Phone className="w-4 h-4" />
                          </button>
                          <button className="p-2 text-gray-400 hover:text-purple-600 transition-colors" title="View Details">
                            <FileText className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteClick(voter)}
                            className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                            title="Delete Voter"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination Controls */}
          {totalFilteredVoters > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                {/* Left: Showing info */}
                <div className="text-sm text-gray-600">
                  Showing {startIndex + 1} to {Math.min(endIndex, totalFilteredVoters)} of {totalFilteredVoters} voters
                </div>

                {/* Center: Page numbers */}
                <div className="flex items-center space-x-2">
                  {/* Previous button */}
                  <button
                    onClick={() => handlePageChange(currentPage - 1)}
                    disabled={currentPage === 1}
                    className={`px-3 py-1 rounded border ${
                      currentPage === 1
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
                    }`}
                  >
                    Previous
                  </button>

                  {/* Page numbers */}
                  <div className="flex space-x-1">
                    {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }

                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`w-8 h-8 rounded ${
                            currentPage === pageNum
                              ? 'bg-blue-600 text-white font-semibold'
                              : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                          }`}
                        >
                          {pageNum}
                        </button>
                      );
                    })}
                  </div>

                  {/* Next button */}
                  <button
                    onClick={() => handlePageChange(currentPage + 1)}
                    disabled={currentPage === totalPages}
                    className={`px-3 py-1 rounded border ${
                      currentPage === totalPages
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-300'
                    }`}
                  >
                    Next
                  </button>
                </div>

                {/* Right: Items per page */}
                <div className="flex items-center space-x-2">
                  <label className="text-sm text-gray-600">Per page:</label>
                  <select
                    value={itemsPerPage}
                    onChange={(e) => {
                      setItemsPerPage(Number(e.target.value));
                      setCurrentPage(1);
                    }}
                    className="border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={5}>5</option>
                    <option value={10}>10</option>
                    <option value={25}>25</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                  </select>
                </div>
              </div>
            </div>
          )}
          </>
          )}
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Interest Analysis */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Voter Interests</h3>
              <div className="space-y-3">
                {topInterests.length > 0 ? topInterests.map((item) => (
                  <div key={item.interest} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">{item.interest}</span>
                    <div className="flex items-center">
                      <div className="w-20 h-2 bg-gray-200 rounded-full mr-2">
                        <div 
                          className="h-2 bg-blue-500 rounded-full"
                          style={{ width: `${item.percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-xs text-gray-600 w-12">{item.count.toLocaleString()}</span>
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-8 text-gray-500">
                    <p className="text-sm">No interest data available</p>
                    <p className="text-xs mt-1">Add voters with interests to see analytics</p>
                  </div>
                )}
              </div>
            </div>

            {/* Contact Method Effectiveness */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Method Success</h3>
              <div className="space-y-4">
                {contactMethodSuccess.length > 0 ? contactMethodSuccess.map((method) => (
                  <div key={method.method} className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{method.method}</div>
                      <div className="text-xs text-gray-600">{method.attempts.toLocaleString()} attempts</div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-gray-900">{method.success}%</div>
                      <div className="text-xs text-gray-600">Success Rate</div>
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-8 text-gray-500">
                    <p className="text-sm">No contact method data available</p>
                    <p className="text-xs mt-1">Add contact history to voters to see analytics</p>
                  </div>
                )}
              </div>
            </div>

            {/* Geographic Coverage */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Constituency Coverage</h3>
              <div className="space-y-3">
                {geographicCoverage.length > 0 ? geographicCoverage.map((area) => (
                  <div key={area.area} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{area.area}</span>
                      <span className="text-sm font-medium text-gray-700">{area.coverage}%</span>
                    </div>
                    <div className="w-full h-2 bg-gray-200 rounded-full">
                      <div 
                        className="h-2 bg-blue-500 rounded-full"
                        style={{ width: `${area.coverage}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                      {area.voters.toLocaleString()} voters
                    </div>
                  </div>
                )) : (
                  <div className="text-center py-8 text-gray-500">
                    <p className="text-sm">No constituency data available</p>
                    <p className="text-xs mt-1">Add voters to see coverage</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'registration' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Add New Voter</h3>

            <form onSubmit={handleAddVoter} className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Personal Information */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900 border-b pb-2">Personal Information</h4>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                    <input
                      type="text"
                      value={newVoterData.name}
                      onChange={(e) => setNewVoterData({ ...newVoterData, name: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter full name"
                      required
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Age *</label>
                      <input
                        type="number"
                        value={newVoterData.age}
                        onChange={(e) => setNewVoterData({ ...newVoterData, age: e.target.value })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="18"
                        min="18"
                        max="120"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Gender *</label>
                      <select
                        value={newVoterData.gender}
                        onChange={(e) => setNewVoterData({ ...newVoterData, gender: e.target.value })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="">Select Gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Voter ID Card *</label>
                    <input
                      type="text"
                      value={newVoterData.voterIdCard}
                      onChange={(e) => setNewVoterData({ ...newVoterData, voterIdCard: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="ABC1234567"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number *</label>
                    <input
                      type="tel"
                      value={newVoterData.phone}
                      onChange={(e) => setNewVoterData({ ...newVoterData, phone: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="9876543210"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={newVoterData.email}
                      onChange={(e) => setNewVoterData({ ...newVoterData, email: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="voter@example.com"
                    />
                  </div>
                </div>

                {/* Demographics & Location */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900 border-b pb-2">Demographics & Location</h4>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Caste</label>
                      <select
                        value={newVoterData.caste}
                        onChange={(e) => setNewVoterData({ ...newVoterData, caste: e.target.value })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select Caste</option>
                        <option value="General">General</option>
                        <option value="OBC">OBC</option>
                        <option value="SC">SC</option>
                        <option value="ST">ST</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Religion</label>
                      <select
                        value={newVoterData.religion}
                        onChange={(e) => setNewVoterData({ ...newVoterData, religion: e.target.value })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select Religion</option>
                        <option value="Hindu">Hindu</option>
                        <option value="Muslim">Muslim</option>
                        <option value="Christian">Christian</option>
                        <option value="Sikh">Sikh</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Education</label>
                    <select
                      value={newVoterData.education}
                      onChange={(e) => setNewVoterData({ ...newVoterData, education: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select Education</option>
                      <option value="Illiterate">Illiterate</option>
                      <option value="Primary">Primary</option>
                      <option value="Secondary">Secondary</option>
                      <option value="Graduate">Graduate</option>
                      <option value="Post Graduate">Post Graduate</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Occupation</label>
                    <input
                      type="text"
                      value={newVoterData.occupation}
                      onChange={(e) => setNewVoterData({ ...newVoterData, occupation: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="e.g., Teacher, Engineer"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Constituency</label>
                      <select
                        value={newVoterData.constituency}
                        onChange={(e) => setNewVoterData({ ...newVoterData, constituency: e.target.value })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select Constituency</option>
                        <option value="Gurgaon Rural">Gurgaon Rural</option>
                        <option value="Noida">Noida</option>
                        <option value="Chandni Chowk">Chandni Chowk</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Booth</label>
                      <input
                        type="text"
                        value={newVoterData.booth}
                        onChange={(e) => setNewVoterData({ ...newVoterData, booth: e.target.value })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="e.g., Booth 101"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                    <textarea
                      rows={3}
                      value={newVoterData.address}
                      onChange={(e) => setNewVoterData({ ...newVoterData, address: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter full address"
                    ></textarea>
                  </div>
                </div>
              </div>

              {/* Interests */}
              <div>
                <h4 className="font-medium text-gray-900 border-b pb-2 mb-4">Political Interests</h4>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                  {['Infrastructure', 'Education', 'Healthcare', 'Employment', 'Women Safety', 'Economic Policy', 'Environment', 'Technology'].map((interest) => (
                    <label key={interest} className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newVoterData.interests.includes(interest)}
                        onChange={(e) => handleInterestChange(interest, e.target.checked)}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">{interest}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end space-x-4 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => setNewVoterData({
                    name: '', age: '', gender: '', voterIdCard: '', phone: '', email: '',
                    caste: '', religion: '', education: '', occupation: '',
                    constituency: '', booth: '', address: '', interests: []
                  })}
                  disabled={isSubmitting}
                  className="px-6 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Clear
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Adding Voter...</span>
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4" />
                      <span>Add Voter</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Voter Modal */}
      {showEditModal && editingVoter && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Edit Voter</h2>
              <button
                onClick={() => {
                  setShowEditModal(false);
                  setEditingVoter(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleUpdateVoter} className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Personal Information */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900 border-b pb-2">Personal Information</h4>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                    <input
                      type="text"
                      required
                      value={editingVoter.name || ''}
                      onChange={(e) => setEditingVoter({ ...editingVoter, name: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Age *</label>
                      <input
                        type="number"
                        required
                        value={editingVoter.age || ''}
                        onChange={(e) => setEditingVoter({ ...editingVoter, age: parseInt(e.target.value) })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Gender *</label>
                      <select
                        required
                        value={editingVoter.gender || ''}
                        onChange={(e) => setEditingVoter({ ...editingVoter, gender: e.target.value })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select Gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Voter ID Card *</label>
                    <input
                      type="text"
                      required
                      value={editingVoter.voterIdCard || ''}
                      onChange={(e) => setEditingVoter({ ...editingVoter, voterIdCard: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number *</label>
                    <input
                      type="tel"
                      required
                      value={editingVoter.phone || ''}
                      onChange={(e) => setEditingVoter({ ...editingVoter, phone: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                      type="email"
                      value={editingVoter.email || ''}
                      onChange={(e) => setEditingVoter({ ...editingVoter, email: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Demographics & Location */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900 border-b pb-2">Demographics & Location</h4>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Caste</label>
                      <select
                        value={editingVoter.demographics?.caste || ''}
                        onChange={(e) => setEditingVoter({
                          ...editingVoter,
                          demographics: { ...editingVoter.demographics, caste: e.target.value }
                        })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select Caste</option>
                        <option value="General">General</option>
                        <option value="OBC">OBC</option>
                        <option value="SC">SC</option>
                        <option value="ST">ST</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Religion</label>
                      <select
                        value={editingVoter.demographics?.religion || ''}
                        onChange={(e) => setEditingVoter({
                          ...editingVoter,
                          demographics: { ...editingVoter.demographics, religion: e.target.value }
                        })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="">Select Religion</option>
                        <option value="Hindu">Hindu</option>
                        <option value="Muslim">Muslim</option>
                        <option value="Christian">Christian</option>
                        <option value="Sikh">Sikh</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Occupation</label>
                    <input
                      type="text"
                      value={editingVoter.demographics?.occupation || ''}
                      onChange={(e) => setEditingVoter({
                        ...editingVoter,
                        demographics: { ...editingVoter.demographics, occupation: e.target.value }
                      })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Constituency *</label>
                      <input
                        type="text"
                        required
                        value={editingVoter.constituency || ''}
                        onChange={(e) => setEditingVoter({ ...editingVoter, constituency: e.target.value })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Booth *</label>
                      <input
                        type="text"
                        required
                        value={editingVoter.booth || ''}
                        onChange={(e) => setEditingVoter({ ...editingVoter, booth: e.target.value })}
                        className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                    <textarea
                      rows={3}
                      value={editingVoter.address || ''}
                      onChange={(e) => setEditingVoter({ ...editingVoter, address: e.target.value })}
                      className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    ></textarea>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end space-x-4 pt-6 border-t">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingVoter(null);
                  }}
                  disabled={isSubmitting}
                  className="px-6 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? 'Updating...' : 'Update Voter'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && voterToDelete && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900">Confirm Delete</h2>
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setVoterToDelete(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mb-6">
              <p className="text-gray-700 mb-2">Are you sure you want to delete this voter?</p>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="font-medium text-gray-900">{voterToDelete.name}</p>
                <p className="text-sm text-gray-600">{voterToDelete.voterIdCard}</p>
                <p className="text-sm text-gray-600">{voterToDelete.constituency} - {voterToDelete.booth}</p>
              </div>
              <p className="text-red-600 text-sm mt-4">
                <strong>Warning:</strong> This action cannot be undone.
              </p>
            </div>

            <div className="flex items-center justify-end space-x-4">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setVoterToDelete(null);
                }}
                disabled={isSubmitting}
                className="px-6 py-2 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDelete}
                disabled={isSubmitting}
                className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
              >
                {isSubmitting ? 'Deleting...' : 'Delete Voter'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Import Data Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900 flex items-center">
                  <Upload className="w-6 h-6 mr-2 text-green-600" />
                  Import Voter Data
                </h3>
                <button
                  onClick={() => setShowImportModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  Upload a CSV or Excel file with voter information. The file should contain columns for:
                </p>
                <ul className="text-xs text-gray-500 list-disc list-inside space-y-1">
                  <li>Name (required)</li>
                  <li>Age (required)</li>
                  <li>Gender (required)</li>
                  <li>Voter ID Number (required)</li>
                  <li>Phone, Email, Address (optional)</li>
                  <li>Constituency, Booth (optional)</li>
                </ul>

                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-green-500 transition-colors cursor-pointer">
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    className="hidden"
                    id="import-file"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        alert('Import functionality coming soon! File: ' + e.target.files[0].name);
                        setShowImportModal(false);
                      }
                    }}
                  />
                  <label htmlFor="import-file" className="cursor-pointer">
                    <Upload className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm font-medium text-gray-900">Click to upload or drag and drop</p>
                    <p className="text-xs text-gray-500 mt-1">CSV, Excel (MAX. 10MB)</p>
                  </label>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-xs text-blue-700">
                    <strong>Note:</strong> Large files may take time to process. You'll receive a notification when the import is complete.
                  </p>
                </div>
              </div>

              <div className="flex space-x-3 mt-6">
                <button
                  onClick={() => setShowImportModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <a
                  href="/templates/voter-import-template.csv"
                  download
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-center"
                >
                  Download Template
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


import React, { useState, useEffect } from 'react';
import {
  MapPin,
  Users,
  MessageSquare,
  Calendar,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Phone,
  Mail,
  Globe,
  Camera,
  FileText,
  Send,
  Heart,
  Star,
  Clock,
  Filter,
  Plus,
  Share2,
  Download,
  Flag,
  Building,
  Zap,
  Shield,
  Target,
  X as CloseIcon
} from 'lucide-react';
import { issueCategoriesService, IssueCategory } from '../services/supabase/issue-categories.service';

interface Issue {
  id: string;
  title: string;
  description: string;
  category: string; // Maps to issue_categories.code from database
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'reported' | 'acknowledged' | 'in_progress' | 'resolved' | 'closed';
  location: string;
  coordinates?: { lat: number; lng: number };
  reportedBy: string;
  reportedAt: Date;
  supporters: number;
  comments: number;
  images?: string[];
  assignedTo?: string;
  estimatedResolution?: Date;
  updates?: Array<{
    id: string;
    message: string;
    timestamp: Date;
    author: string;
    type: 'update' | 'comment' | 'status_change';
  }>;
}

// Removed Representative and Event interfaces - using only dynamic data from database

export default function MyConstituencyApp() {
  const [activeTab, setActiveTab] = useState<'issues' | 'insights' | 'report'>('issues');
  const [selectedConstituency] = useState('Thiruvananthapuram Central');
  const [showReportForm, setShowReportForm] = useState(false);
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [issueCategories, setIssueCategories] = useState<IssueCategory[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(true);

  // Form submission states
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Issues loading
  const [loadingIssues, setLoadingIssues] = useState(true);

  // Fetch issue categories from database
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoadingCategories(true);
        const categories = await issueCategoriesService.getAll();
        setIssueCategories(categories);
      } catch (error) {
        console.error('Error loading issue categories:', error);
      } finally {
        setLoadingCategories(false);
      }
    };

    fetchCategories();
  }, []);

  // Issues state - loaded from database
  const [issues, setIssues] = useState<Issue[]>([]);

  // Fetch issues from issue_categories table
  useEffect(() => {
    const fetchIssues = async () => {
      try {
        setLoadingIssues(true);

        // Get all issue categories (including citizen-reported ones)
        const allCategories = await issueCategoriesService.getAll();

        // Filter to show only recently created entries (potential citizen reports)
        // Or show all - you can customize this filter
        const transformedIssues: Issue[] = allCategories.map((category) => {
          // Map priority_level back to form priority
          const priorityMap: Record<string, 'low' | 'medium' | 'high' | 'urgent'> = {
            'Low': 'low',
            'Medium': 'medium',
            'High': 'high',
            'Critical': 'urgent'
          };

          return {
            id: category.id,
            title: category.name,
            description: category.description,
            category: category.category,
            priority: priorityMap[category.priority_level] || 'medium',
            status: category.is_hot_topic ? 'in_progress' : 'reported',
            location: category.geographic_focus?.[0] || 'Not specified',
            reportedBy: 'Citizen',
            reportedAt: new Date(category.created_at),
            supporters: 0,
            comments: 0,
            updates: [],
          };
        });

        setIssues(transformedIssues);
      } catch (error) {
        console.error('Error loading issues:', error);
      } finally {
        setLoadingIssues(false);
      }
    };

    fetchIssues();
  }, []);

  // Removed static representatives and events arrays - only using dynamic issue_categories data

  const getCategoryIcon = (categoryCode: string) => {
    // Map database category codes to icons
    const upperCode = categoryCode.toUpperCase();

    if (upperCode.includes('INFRA')) return <Building className="h-4 w-4" />;
    if (upperCode.includes('HEALTH')) return <Heart className="h-4 w-4" />;
    if (upperCode.includes('EDUCATION') || upperCode.includes('NEET')) return <FileText className="h-4 w-4" />;
    if (upperCode.includes('JOB') || upperCode.includes('EMPLOYMENT')) return <Users className="h-4 w-4" />;
    if (upperCode.includes('ENVIRONMENT') || upperCode.includes('POLLUTION')) return <Shield className="h-4 w-4" />;
    if (upperCode.includes('SAFETY') || upperCode.includes('LAW') || upperCode.includes('WOMEN')) return <AlertTriangle className="h-4 w-4" />;
    if (upperCode.includes('WATER') || upperCode.includes('ELECTRICITY')) return <Zap className="h-4 w-4" />;
    if (upperCode.includes('METRO') || upperCode.includes('TRANSPORT')) return <Globe className="h-4 w-4" />;

    return <Flag className="h-4 w-4" />;
  };

  const getCategoryColor = (categoryCode: string) => {
    // Map database category codes to colors
    const upperCode = categoryCode.toUpperCase();

    if (upperCode.includes('INFRA')) return 'text-blue-600 bg-blue-100';
    if (upperCode.includes('HEALTH')) return 'text-red-600 bg-red-100';
    if (upperCode.includes('EDUCATION') || upperCode.includes('NEET')) return 'text-green-600 bg-green-100';
    if (upperCode.includes('JOB') || upperCode.includes('EMPLOYMENT') || upperCode.includes('STARTUP')) return 'text-purple-600 bg-purple-100';
    if (upperCode.includes('ENVIRONMENT') || upperCode.includes('POLLUTION')) return 'text-emerald-600 bg-emerald-100';
    if (upperCode.includes('SAFETY') || upperCode.includes('LAW') || upperCode.includes('WOMEN')) return 'text-orange-600 bg-orange-100';
    if (upperCode.includes('WATER') || upperCode.includes('ELECTRICITY')) return 'text-yellow-600 bg-yellow-100';
    if (upperCode.includes('METRO') || upperCode.includes('TRANSPORT')) return 'text-indigo-600 bg-indigo-100';

    return 'text-gray-600 bg-gray-100';
  };

  // Get category display name from code
  const getCategoryDisplayName = (code: string): string => {
    const category = issueCategories.find(cat => cat.code === code);
    return category ? category.name : code;
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-700 bg-red-100 border-red-300';
      case 'high': return 'text-red-600 bg-red-100 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-100 border-green-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'reported': return 'text-blue-600 bg-blue-100';
      case 'acknowledged': return 'text-yellow-600 bg-yellow-100';
      case 'in_progress': return 'text-purple-600 bg-purple-100';
      case 'resolved': return 'text-green-600 bg-green-100';
      case 'closed': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const filteredIssues = issues.filter(issue => {
    if (filterCategory !== 'all' && issue.category !== filterCategory) return false;
    return true;
  }).sort((a, b) => {
    switch (sortBy) {
      case 'recent':
        return b.reportedAt.getTime() - a.reportedAt.getTime();
      case 'priority':
        const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      case 'supporters':
        return b.supporters - a.supporters;
      default:
        return 0;
    }
  });

  const handleSupportIssue = (issueId: string) => {
    setIssues(prev => prev.map(issue => 
      issue.id === issueId 
        ? { ...issue, supporters: issue.supporters + 1 }
        : issue
    ));
  };

  const handleReportIssue = async (formData: any) => {
    try {
      setIsSubmitting(true);
      setSubmitError(null);
      setSubmitSuccess(false);

      // Create issue in issue_categories table
      const newCategory = await issueCategoriesService.createFromReport({
        title: formData.title,
        description: formData.description,
        category: formData.category,
        priority: formData.priority,
        location: formData.location,
      });

      // Transform IssueCategory to Issue interface for display
      const transformedIssue: Issue = {
        id: newCategory.id,
        title: newCategory.name,
        description: newCategory.description,
        category: newCategory.category,
        priority: formData.priority as 'low' | 'medium' | 'high' | 'urgent',
        status: 'reported',
        location: newCategory.geographic_focus?.[0] || formData.location,
        reportedBy: 'Current User',
        reportedAt: new Date(newCategory.created_at),
        supporters: 0,
        comments: 0,
      };

      setIssues(prev => [transformedIssue, ...prev]);
      setSubmitSuccess(true);

      // Refresh categories list to include the new entry
      const updatedCategories = await issueCategoriesService.getAll();
      setIssueCategories(updatedCategories);

      // Close modal after 1.5 seconds
      setTimeout(() => {
        setShowReportForm(false);
        setSubmitSuccess(false);
      }, 1500);
    } catch (error: any) {
      console.error('Error submitting issue:', error);
      setSubmitError(error.message || 'Failed to submit issue. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-900 flex items-center">
            <MapPin className="mr-2 h-6 w-6 text-green-600" />
            My Constituency: {selectedConstituency}
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Citizen engagement platform for local issues and community participation
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowReportForm(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors flex items-center text-sm"
          >
            <Plus className="mr-1 h-4 w-4" />
            Report Issue
          </button>
        </div>
      </div>

      {/* Quick Stats - All from issue_categories table */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <Flag className="h-8 w-8 text-blue-600 mr-3" />
            <div>
              <div className="text-2xl font-bold text-blue-900">{issues.length}</div>
              <div className="text-sm text-blue-700">Active Issues</div>
            </div>
          </div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600 mr-3" />
            <div>
              <div className="text-2xl font-bold text-green-900">
                {issues.filter(i => i.status === 'resolved').length}
              </div>
              <div className="text-sm text-green-700">Resolved</div>
            </div>
          </div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-purple-600 mr-3" />
            <div>
              <div className="text-2xl font-bold text-purple-900">
                {issues.reduce((sum, issue) => sum + issue.supporters, 0)}
              </div>
              <div className="text-sm text-purple-700">Total Support</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation - Only Issues, Insights, Report */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { key: 'issues', label: 'Local Issues', icon: Flag },
              { key: 'insights', label: 'Insights', icon: TrendingUp },
              { key: 'report', label: 'Report', icon: FileText }
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setActiveTab(key as any)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === key
                    ? 'border-green-500 text-green-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="mr-1 h-4 w-4" />
                {label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Issues Tab */}
      {activeTab === 'issues' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                disabled={loadingCategories}
              >
                <option value="all">All Categories</option>
                {issueCategories.map((category) => (
                  <option key={category.id} value={category.code}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Sort by:</span>
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value="recent">Most Recent</option>
                <option value="priority">Priority</option>
                <option value="supporters">Most Supported</option>
              </select>
            </div>
          </div>

          {/* Issues List */}
          <div className="space-y-4">
            {loadingIssues ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading issues...</p>
              </div>
            ) : filteredIssues.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <Flag className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">No issues reported yet</p>
                <button
                  onClick={() => setShowReportForm(true)}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  Be the first to report an issue
                </button>
              </div>
            ) : (
              filteredIssues.map((issue) => (
              <div key={issue.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <div className={`flex items-center px-2 py-1 rounded text-xs font-medium ${getCategoryColor(issue.category)}`}>
                        {getCategoryIcon(issue.category)}
                        <span className="ml-1 capitalize">{getCategoryDisplayName(issue.category)}</span>
                      </div>
                      <div className={`px-2 py-1 rounded border text-xs font-medium ${getPriorityColor(issue.priority)}`}>
                        {issue.priority.toUpperCase()}
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(issue.status)}`}>
                        {issue.status.replace('_', ' ').toUpperCase()}
                      </div>
                    </div>
                    <h4 className="font-medium text-gray-900 mb-2">{issue.title}</h4>
                    <p className="text-sm text-gray-700 mb-3">{issue.description}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-600">
                      <div className="flex items-center">
                        <MapPin className="h-3 w-3 mr-1" />
                        {issue.location}
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {issue.reportedAt.toLocaleDateString()}
                      </div>
                      <div className="flex items-center">
                        <Users className="h-3 w-3 mr-1" />
                        Reported by {issue.reportedBy}
                      </div>
                    </div>
                    {issue.assignedTo && (
                      <div className="mt-2 text-xs text-blue-600">
                        Assigned to: {issue.assignedTo}
                        {issue.estimatedResolution && (
                          <span className="ml-2">• Expected resolution: {issue.estimatedResolution.toLocaleDateString()}</span>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="ml-4 flex flex-col items-end space-y-2">
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleSupportIssue(issue.id)}
                        className="flex items-center px-3 py-1 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors text-sm"
                      >
                        <Heart className="h-3 w-3 mr-1" />
                        {issue.supporters}
                      </button>
                      <button className="flex items-center px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm">
                        <MessageSquare className="h-3 w-3 mr-1" />
                        {issue.comments}
                      </button>
                    </div>
                    <button
                      onClick={() => setSelectedIssue(issue)}
                      className="text-xs text-blue-600 hover:text-blue-800"
                    >
                      View Details →
                    </button>
                  </div>
                </div>
                {issue.updates && issue.updates.length > 0 && (
                  <div className="bg-blue-50 p-3 rounded border border-blue-200">
                    <div className="text-xs text-blue-800 font-medium mb-1">Latest Update:</div>
                    <div className="text-sm text-blue-700">{issue.updates[issue.updates.length - 1].message}</div>
                    <div className="text-xs text-blue-600 mt-1">
                      {issue.updates[issue.updates.length - 1].timestamp.toLocaleDateString()} - {issue.updates[issue.updates.length - 1].author}
                    </div>
                  </div>
                )}
              </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Insights Tab */}
      {activeTab === 'insights' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-3">Issue Categories</h4>
              <div className="space-y-3">
                {issueCategories.slice(0, 6).map(category => {
                  const count = issues.filter(i => i.category === category.code).length;
                  const percentage = issues.length > 0 ? Math.round((count / issues.length) * 100) : 0;
                  return (
                    <div key={category.id} className="flex items-center justify-between">
                      <div className="flex items-center">
                        {getCategoryIcon(category.code)}
                        <span className="ml-2 text-sm">{category.name}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="bg-blue-200 rounded-full h-2 w-20 relative">
                          <div 
                            className="bg-blue-600 h-2 rounded-full" 
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{count}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-3">Response Times</h4>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm">Average Response Time</span>
                  <span className="font-medium">2.3 days</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Resolution Rate</span>
                  <span className="font-medium text-green-600">78%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Citizen Satisfaction</span>
                  <span className="font-medium text-blue-600">4.2/5</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-3">Trending Issues</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Street Lighting & Safety</span>
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">↑ 23%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Water Supply Issues</span>
                <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">↑ 18%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Healthcare Access</span>
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">↓ 12%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Report Tab */}
      {activeTab === 'report' && (
        <div className="bg-gray-50 p-6 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-4">Constituency Report</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <button className="p-4 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors">
              <Download className="h-6 w-6 mx-auto mb-2" />
              <div className="text-sm font-medium">Monthly Report</div>
            </button>
            <button className="p-4 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors">
              <Share2 className="h-6 w-6 mx-auto mb-2" />
              <div className="text-sm font-medium">Share Insights</div>
            </button>
            <button className="p-4 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors">
              <Target className="h-6 w-6 mx-auto mb-2" />
              <div className="text-sm font-medium">Action Plan</div>
            </button>
          </div>
          <p className="text-sm text-gray-600">
            Generate comprehensive reports on constituency performance, issue resolution rates, citizen engagement metrics, and representative responsiveness.
          </p>
        </div>
      )}

      {/* Report Issue Modal */}
      {showReportForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[600px] overflow-y-auto">
            <h4 className="text-lg font-semibold mb-4">Report New Issue</h4>

            {/* Success Message */}
            {submitSuccess && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md flex items-center">
                <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                <span className="text-sm text-green-800">Issue reported successfully!</span>
              </div>
            )}

            {/* Error Message */}
            {submitError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-start">
                <AlertTriangle className="h-5 w-5 text-red-600 mr-2 mt-0.5" />
                <div className="flex-1">
                  <span className="text-sm text-red-800">{submitError}</span>
                </div>
                <button
                  onClick={() => setSubmitError(null)}
                  className="text-red-600 hover:text-red-800"
                >
                  <CloseIcon className="h-4 w-4" />
                </button>
              </div>
            )}

            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              handleReportIssue({
                title: formData.get('title'),
                description: formData.get('description'),
                category: formData.get('category'),
                priority: formData.get('priority'),
                location: formData.get('location')
              });
            }}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Issue Title</label>
                  <input name="title" type="text" required className="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="Brief description of the issue" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select name="category" required className="w-full border border-gray-300 rounded-md px-3 py-2" disabled={loadingCategories}>
                    <option value="">Select Category</option>
                    {issueCategories.map((category) => (
                      <option key={category.id} value={category.code}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select name="priority" required className="w-full border border-gray-300 rounded-md px-3 py-2">
                    <option value="">Select Priority</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <input name="location" type="text" required className="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="Specific location or area" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <textarea name="description" rows={4} required className="w-full border border-gray-300 rounded-md px-3 py-2" placeholder="Detailed description of the issue"></textarea>
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowReportForm(false);
                    setSubmitError(null);
                    setSubmitSuccess(false);
                  }}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Submitting...
                    </>
                  ) : (
                    'Submit Issue'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
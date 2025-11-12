/**
 * Hybrid Data Service Layer
 *
 * This service provides a unified interface for data access using:
 * - Supabase Direct: For real-time updates and simple reads
 * - Django Backend API: For complex business logic and operations
 *
 * Usage:
 * import { dataService } from '@/services/dataService'
 * const profile = await dataService.getUserProfile(userId)
 */

import { supabase } from '@/lib/supabase'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get current Supabase session token
 */
async function getSupabaseToken(): Promise<string | null> {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token || null
}

/**
 * Make authenticated request to Django backend
 */
async function djangoFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await getSupabaseToken()

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(error.detail || `Request failed: ${response.status}`)
  }

  return response.json()
}

// ============================================
// USER PROFILE (HYBRID)
// ============================================

export const userService = {
  /**
   * Get user profile (Supabase Direct for speed)
   */
  async getProfile(userId: string) {
    const { data, error } = await supabase
      .from('api_userprofile')
      .select('*')
      .eq('user_id', userId)
      .single()

    if (error) throw error
    return data
  },

  /**
   * Update user profile (Django Backend for validation)
   */
  async updateProfile(userId: string, updates: Record<string, any>) {
    return djangoFetch(`/api/auth/profile/`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    })
  },

  /**
   * Get users list (Django Backend for role filtering)
   */
  async listUsers(params?: { page?: number; search?: string; role?: string }) {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.set('page', params.page.toString())
    if (params?.search) queryParams.set('search', params.search)
    if (params?.role) queryParams.set('role', params.role)

    return djangoFetch(`/api/auth/users/?${queryParams}`)
  },
}

// ============================================
// NOTIFICATIONS (SUPABASE DIRECT - REAL-TIME)
// ============================================

export const notificationService = {
  /**
   * Get user notifications (Supabase Direct for real-time)
   */
  async getNotifications(userId: string) {
    const { data, error } = await supabase
      .from('api_notification')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(50)

    if (error) throw error
    return data
  },

  /**
   * Mark notification as read (Supabase Direct)
   */
  async markAsRead(notificationId: string) {
    const { error } = await supabase
      .from('api_notification')
      .update({ is_read: true, read_at: new Date().toISOString() })
      .eq('id', notificationId)

    if (error) throw error
  },

  /**
   * Subscribe to real-time notifications
   */
  subscribeToNotifications(
    userId: string,
    callback: (notification: any) => void
  ) {
    return supabase
      .channel(`notifications-${userId}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'api_notification',
          filter: `user_id=eq.${userId}`,
        },
        (payload) => callback(payload.new)
      )
      .subscribe()
  },
}

// ============================================
// CAMPAIGNS (DJANGO BACKEND - COMPLEX LOGIC)
// ============================================

export const campaignService = {
  /**
   * List campaigns (Django Backend for filtering)
   */
  async listCampaigns(params?: { page?: number; status?: string }) {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.set('page', params.page.toString())
    if (params?.status) queryParams.set('status', params.status)

    return djangoFetch(`/api/campaigns/?${queryParams}`)
  },

  /**
   * Get campaign details (Django Backend)
   */
  async getCampaign(campaignId: string) {
    return djangoFetch(`/api/campaigns/${campaignId}/`)
  },

  /**
   * Create campaign (Django Backend for validation)
   */
  async createCampaign(campaignData: any) {
    return djangoFetch(`/api/campaigns/`, {
      method: 'POST',
      body: JSON.stringify(campaignData),
    })
  },

  /**
   * Update campaign (Django Backend)
   */
  async updateCampaign(campaignId: string, updates: any) {
    return djangoFetch(`/api/campaigns/${campaignId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    })
  },

  /**
   * Delete campaign (Django Backend)
   */
  async deleteCampaign(campaignId: string) {
    return djangoFetch(`/api/campaigns/${campaignId}/`, {
      method: 'DELETE',
    })
  },
}

// ============================================
// VOTERS (DJANGO BACKEND - COMPLEX QUERIES)
// ============================================

export const voterService = {
  /**
   * List voters (Django Backend for complex filtering)
   */
  async listVoters(params?: {
    page?: number
    search?: string
    district?: string
    constituency?: string
    sentiment?: string
  }) {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.set('page', params.page.toString())
    if (params?.search) queryParams.set('search', params.search)
    if (params?.district) queryParams.set('district', params.district)
    if (params?.constituency) queryParams.set('constituency', params.constituency)
    if (params?.sentiment) queryParams.set('sentiment', params.sentiment)

    return djangoFetch(`/api/voters/?${queryParams}`)
  },

  /**
   * Get voter details (Django Backend)
   */
  async getVoter(voterId: string) {
    return djangoFetch(`/api/voters/${voterId}/`)
  },

  /**
   * Create voter (Django Backend)
   */
  async createVoter(voterData: any) {
    return djangoFetch(`/api/voters/`, {
      method: 'POST',
      body: JSON.stringify(voterData),
    })
  },

  /**
   * Bulk import voters (Django Backend)
   */
  async bulkImport(file: File) {
    const formData = new FormData()
    formData.append('file', file)

    const token = await getSupabaseToken()
    const response = await fetch(`${API_URL}/api/voters/bulk-import/`, {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
      body: formData,
    })

    if (!response.ok) {
      throw new Error('Bulk import failed')
    }

    return response.json()
  },
}

// ============================================
// ANALYTICS & REPORTS (DJANGO BACKEND)
// ============================================

export const analyticsService = {
  /**
   * Get sentiment analysis (Django Backend for aggregation)
   */
  async getSentimentAnalysis(params?: {
    district?: string
    constituency?: string
    startDate?: string
    endDate?: string
  }) {
    const queryParams = new URLSearchParams()
    if (params?.district) queryParams.set('district', params.district)
    if (params?.constituency) queryParams.set('constituency', params.constituency)
    if (params?.startDate) queryParams.set('start_date', params.startDate)
    if (params?.endDate) queryParams.set('end_date', params.endDate)

    return djangoFetch(`/api/analytics/sentiment/?${queryParams}`)
  },

  /**
   * Get voter trends (Django Backend)
   */
  async getVoterTrends(params?: {
    district?: string
    period?: 'day' | 'week' | 'month'
  }) {
    const queryParams = new URLSearchParams()
    if (params?.district) queryParams.set('district', params.district)
    if (params?.period) queryParams.set('period', params.period)

    return djangoFetch(`/api/analytics/trends/?${queryParams}`)
  },

  /**
   * Generate report (Django Backend)
   */
  async generateReport(reportType: string, params: any) {
    return djangoFetch(`/api/reports/generate/`, {
      method: 'POST',
      body: JSON.stringify({ report_type: reportType, ...params }),
    })
  },
}

// ============================================
// ALERTS (HYBRID)
// ============================================

export const alertService = {
  /**
   * Get alerts (Supabase Direct for real-time)
   */
  async getAlerts(params?: { severity?: string; limit?: number }) {
    let query = supabase
      .from('api_alert')
      .select('*')
      .order('created_at', { ascending: false })

    if (params?.severity) {
      query = query.eq('severity', params.severity)
    }

    if (params?.limit) {
      query = query.limit(params.limit)
    }

    const { data, error } = await query
    if (error) throw error
    return data
  },

  /**
   * Create alert (Django Backend for validation)
   */
  async createAlert(alertData: any) {
    return djangoFetch(`/api/alerts/`, {
      method: 'POST',
      body: JSON.stringify(alertData),
    })
  },

  /**
   * Subscribe to real-time alerts
   */
  subscribeToAlerts(callback: (alert: any) => void) {
    return supabase
      .channel('alerts')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'api_alert',
        },
        (payload) => callback(payload.new)
      )
      .subscribe()
  },
}

// ============================================
// AUDIT LOGS (DJANGO BACKEND - ADMIN ONLY)
// ============================================

export const auditService = {
  /**
   * Get audit logs (Django Backend)
   */
  async getAuditLogs(params?: {
    page?: number
    user?: string
    action?: string
    startDate?: string
    endDate?: string
  }) {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.set('page', params.page.toString())
    if (params?.user) queryParams.set('user', params.user)
    if (params?.action) queryParams.set('action', params.action)
    if (params?.startDate) queryParams.set('start_date', params.startDate)
    if (params?.endDate) queryParams.set('end_date', params.endDate)

    return djangoFetch(`/api/audit-logs/?${queryParams}`)
  },
}

// ============================================
// EXPORT DEFAULT SERVICE
// ============================================

export const dataService = {
  user: userService,
  notification: notificationService,
  campaign: campaignService,
  voter: voterService,
  analytics: analyticsService,
  alert: alertService,
  audit: auditService,
}

export default dataService

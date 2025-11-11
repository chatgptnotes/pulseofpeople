/**
 * Constituency Issues Service
 * Handles citizen-reported issues in constituencies
 */

import { supabase, handleSupabaseError } from './index';

export interface ConstituencyIssue {
  id: string;
  constituency_id?: string;
  title: string;
  description: string;
  category: string; // Maps to issue_categories.code
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'reported' | 'acknowledged' | 'in_progress' | 'resolved' | 'closed';
  location: string;
  coordinates?: { lat: number; lng: number };
  reported_by: string; // user_id
  reported_at: string;
  supporters: number;
  comments_count: number;
  assigned_to?: string;
  estimated_resolution?: string;
  created_at: string;
  updated_at: string;
}

export interface IssueInsert {
  title: string;
  description: string;
  category: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  location: string;
  constituency_id?: string;
  coordinates?: { lat: number; lng: number };
}

class ConstituencyIssuesService {
  private tableName = 'constituency_issues';

  /**
   * Get all issues for a constituency
   */
  async getByConstituency(constituencyId: string): Promise<ConstituencyIssue[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .eq('constituency_id', constituencyId)
        .order('created_at', { ascending: false });

      if (error) handleSupabaseError(error);

      return (data as ConstituencyIssue[]) || [];
    } catch (error) {
      console.error('Error fetching constituency issues:', error);
      throw error;
    }
  }

  /**
   * Get all issues (for testing/demo)
   */
  async getAll(): Promise<ConstituencyIssue[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .order('created_at', { ascending: false })
        .limit(100);

      if (error) handleSupabaseError(error);

      return (data as ConstituencyIssue[]) || [];
    } catch (error) {
      console.error('Error fetching all issues:', error);
      throw error;
    }
  }

  /**
   * Get issue by ID
   */
  async getById(id: string): Promise<ConstituencyIssue | null> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .eq('id', id)
        .single();

      if (error) {
        if (error.code === 'PGRST116') return null;
        handleSupabaseError(error);
      }

      return data as ConstituencyIssue;
    } catch (error) {
      console.error('Error fetching issue:', error);
      throw error;
    }
  }

  /**
   * Report a new issue
   */
  async create(issueData: IssueInsert): Promise<ConstituencyIssue> {
    try {
      const { data: { user } } = await supabase.auth.getUser();

      if (!user) {
        throw new Error('User must be logged in to report issues');
      }

      const { data, error } = await supabase
        .from(this.tableName)
        .insert({
          ...issueData,
          reported_by: user.id,
          reported_at: new Date().toISOString(),
          status: 'reported',
          supporters: 0,
          comments_count: 0
        })
        .select()
        .single();

      if (error) handleSupabaseError(error);

      return data as ConstituencyIssue;
    } catch (error) {
      console.error('Error creating issue:', error);
      throw error;
    }
  }

  /**
   * Update issue status
   */
  async updateStatus(
    id: string,
    status: ConstituencyIssue['status'],
    assignedTo?: string
  ): Promise<ConstituencyIssue> {
    try {
      const updateData: any = {
        status,
        updated_at: new Date().toISOString()
      };

      if (assignedTo) {
        updateData.assigned_to = assignedTo;
      }

      const { data, error } = await supabase
        .from(this.tableName)
        .update(updateData)
        .eq('id', id)
        .select()
        .single();

      if (error) handleSupabaseError(error);

      return data as ConstituencyIssue;
    } catch (error) {
      console.error('Error updating issue status:', error);
      throw error;
    }
  }

  /**
   * Support/Like an issue
   */
  async supportIssue(id: string): Promise<void> {
    try {
      const { data: issue, error: fetchError } = await supabase
        .from(this.tableName)
        .select('supporters')
        .eq('id', id)
        .single();

      if (fetchError) handleSupabaseError(fetchError);

      const { error: updateError } = await supabase
        .from(this.tableName)
        .update({
          supporters: (issue.supporters || 0) + 1
        })
        .eq('id', id);

      if (updateError) handleSupabaseError(updateError);
    } catch (error) {
      console.error('Error supporting issue:', error);
      throw error;
    }
  }

  /**
   * Get issues by category
   */
  async getByCategory(category: string): Promise<ConstituencyIssue[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .eq('category', category)
        .order('created_at', { ascending: false });

      if (error) handleSupabaseError(error);

      return (data as ConstituencyIssue[]) || [];
    } catch (error) {
      console.error('Error fetching issues by category:', error);
      throw error;
    }
  }

  /**
   * Get issues by status
   */
  async getByStatus(status: ConstituencyIssue['status']): Promise<ConstituencyIssue[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .eq('status', status)
        .order('created_at', { ascending: false});

      if (error) handleSupabaseError(error);

      return (data as ConstituencyIssue[]) || [];
    } catch (error) {
      console.error('Error fetching issues by status:', error);
      throw error;
    }
  }

  /**
   * Search issues
   */
  async search(keyword: string): Promise<ConstituencyIssue[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .or(`title.ilike.%${keyword}%,description.ilike.%${keyword}%,location.ilike.%${keyword}%`)
        .order('created_at', { ascending: false});

      if (error) handleSupabaseError(error);

      return (data as ConstituencyIssue[]) || [];
    } catch (error) {
      console.error('Error searching issues:', error);
      throw error;
    }
  }
}

export const constituencyIssuesService = new ConstituencyIssuesService();

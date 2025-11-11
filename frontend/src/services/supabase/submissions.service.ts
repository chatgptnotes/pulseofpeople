/**
 * Data Submissions Service
 * Handles field worker data submission operations
 */

import { SupabaseService } from './crud';
import { supabase } from './index';

// Submission type based on DataSubmission.tsx
export interface DataSubmission {
  id?: string;
  user_id?: string;
  organization_id?: string;
  submission_type: 'daily' | 'weekly' | 'monthly';
  worker_role: 'ward-coordinator' | 'social-media' | 'survey-team' | 'truth-team';
  location: {
    ward: string;
    area: string;
    coordinates?: string;
  };
  sentiment_entries: {
    id: string;
    type: 'positive' | 'negative';
    quote: string;
    location: string;
    source: string;
    verified: boolean;
  }[];
  viral_content: {
    description: string;
    link: string;
    platform: string;
    reach?: number;
  }[];
  issues: {
    description: string;
    severity: 'low' | 'medium' | 'high';
    location: string;
    category: string;
  }[];
  additional_notes: string;
  verified_by: string;
  attachments?: string[]; // File URLs after upload
  status?: 'draft' | 'submitted' | 'reviewed' | 'approved';
  submitted_at?: string;
  created_at?: string;
  updated_at?: string;
}

export type DataSubmissionInsert = Omit<DataSubmission, 'id' | 'created_at' | 'updated_at'>;
export type DataSubmissionUpdate = Partial<DataSubmissionInsert>;

class SubmissionsService extends SupabaseService<DataSubmission, DataSubmissionInsert, DataSubmissionUpdate> {
  constructor() {
    super('data_submissions');
  }

  /**
   * Create a new data submission
   */
  async createSubmission(submission: DataSubmissionInsert): Promise<DataSubmission> {
    const submissionData = {
      ...submission,
      status: 'submitted',
      submitted_at: new Date().toISOString()
    };

    return this.create(submissionData as any);
  }

  /**
   * Get submissions by user
   */
  async getByUser(userId: string): Promise<DataSubmission[]> {
    const { data } = await this.getAll({
      filters: { user_id: userId },
      sort: { column: 'created_at', direction: 'desc' }
    });
    return data;
  }

  /**
   * Get submissions by organization
   */
  async getByOrganization(organizationId: string): Promise<DataSubmission[]> {
    const { data } = await this.getAll({
      filters: { organization_id: organizationId },
      sort: { column: 'created_at', direction: 'desc' }
    });
    return data;
  }

  /**
   * Get submissions by type
   */
  async getByType(submissionType: 'daily' | 'weekly' | 'monthly'): Promise<DataSubmission[]> {
    const { data } = await this.getAll({
      filters: { submission_type: submissionType },
      sort: { column: 'created_at', direction: 'desc' }
    });
    return data;
  }

  /**
   * Get submissions by date range
   */
  async getByDateRange(startDate: string, endDate: string): Promise<DataSubmission[]> {
    const { data, error } = await supabase
      .from('data_submissions')
      .select('*')
      .gte('submitted_at', startDate)
      .lte('submitted_at', endDate)
      .order('submitted_at', { ascending: false });

    if (error) throw error;
    return (data as DataSubmission[]) || [];
  }

  /**
   * Update submission status
   */
  async updateStatus(
    submissionId: string,
    status: 'draft' | 'submitted' | 'reviewed' | 'approved'
  ): Promise<DataSubmission> {
    return this.update(submissionId, { status } as any);
  }

  /**
   * Save submission as draft
   */
  async saveDraft(submission: DataSubmissionInsert): Promise<DataSubmission> {
    const draftData = {
      ...submission,
      status: 'draft'
    };

    return this.create(draftData as any);
  }

  /**
   * Upload attachment files
   */
  async uploadAttachments(files: File[], submissionId: string): Promise<string[]> {
    const uploadPromises = files.map(async (file, index) => {
      const fileName = `${submissionId}/${index}-${file.name}`;
      const { data, error } = await supabase.storage
        .from('submission-attachments')
        .upload(fileName, file);

      if (error) throw error;

      // Get public URL
      const { data: { publicUrl } } = supabase.storage
        .from('submission-attachments')
        .getPublicUrl(fileName);

      return publicUrl;
    });

    return Promise.all(uploadPromises);
  }

  /**
   * Get submissions statistics
   */
  async getStatistics(organizationId?: string): Promise<{
    total: number;
    by_type: Record<string, number>;
    by_status: Record<string, number>;
    by_worker_role: Record<string, number>;
  }> {
    let query = supabase.from('data_submissions').select('*');

    if (organizationId) {
      query = query.eq('organization_id', organizationId);
    }

    const { data, error } = await query;
    if (error) throw error;

    const submissions = (data as DataSubmission[]) || [];

    return {
      total: submissions.length,
      by_type: submissions.reduce((acc, s) => {
        acc[s.submission_type] = (acc[s.submission_type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      by_status: submissions.reduce((acc, s) => {
        acc[s.status || 'submitted'] = (acc[s.status || 'submitted'] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      by_worker_role: submissions.reduce((acc, s) => {
        acc[s.worker_role] = (acc[s.worker_role] || 0) + 1;
        return acc;
      }, {} as Record<string, number>)
    };
  }
}

// Export singleton instance
export const submissionsService = new SubmissionsService();

// Export class for testing
export { SubmissionsService };

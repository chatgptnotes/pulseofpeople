/**
 * Issue Categories Service
 * Handles fetching issue categories from Supabase
 */

import { supabase, handleSupabaseError } from './index';

export interface IssueCategory {
  id: string;
  code: string;
  name: string;
  name_tamil: string;
  description: string;
  detailed_description?: string;
  category: string; // Economic, Social, Infrastructure, etc.
  sub_category?: string;
  priority_level: 'Critical' | 'High' | 'Medium' | 'Low';
  tvk_stance?: string;
  tvk_priority?: 'Top' | 'High' | 'Medium' | 'Low';
  relevant_segments?: string[];
  geographic_focus?: string[];
  keywords?: string[];
  hashtags?: string[];
  messaging_points?: string[];
  incumbent_performance?: string;
  media_coverage_level?: 'Very High' | 'High' | 'Medium' | 'Low';
  is_active: boolean;
  is_hot_topic: boolean;
  created_at: string;
  updated_at: string;
}

class IssueCategoriesService {
  private tableName = 'issue_categories';

  /**
   * Get all active issue categories
   */
  async getAll(): Promise<IssueCategory[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .eq('is_active', true)
        .order('priority_level', { ascending: true });

      if (error) handleSupabaseError(error);

      return (data as IssueCategory[]) || [];
    } catch (error) {
      console.error('Error fetching issue categories:', error);
      throw error;
    }
  }

  /**
   * Get issue categories by main category
   */
  async getByCategory(category: string): Promise<IssueCategory[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .eq('category', category)
        .eq('is_active', true)
        .order('priority_level', { ascending: true });

      if (error) handleSupabaseError(error);

      return (data as IssueCategory[]) || [];
    } catch (error) {
      console.error(`Error fetching ${category} categories:`, error);
      throw error;
    }
  }

  /**
   * Get hot topic issues
   */
  async getHotTopics(): Promise<IssueCategory[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .eq('is_hot_topic', true)
        .eq('is_active', true)
        .order('media_coverage_level', { ascending: true });

      if (error) handleSupabaseError(error);

      return (data as IssueCategory[]) || [];
    } catch (error) {
      console.error('Error fetching hot topics:', error);
      throw error;
    }
  }

  /**
   * Get top priority issues
   */
  async getTopPriority(): Promise<IssueCategory[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .in('tvk_priority', ['Top', 'High'])
        .eq('is_active', true)
        .order('priority_level', { ascending: true });

      if (error) handleSupabaseError(error);

      return (data as IssueCategory[]) || [];
    } catch (error) {
      console.error('Error fetching top priority issues:', error);
      throw error;
    }
  }

  /**
   * Search issues by keyword
   */
  async search(keyword: string): Promise<IssueCategory[]> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .or(`name.ilike.%${keyword}%,description.ilike.%${keyword}%`)
        .eq('is_active', true);

      if (error) handleSupabaseError(error);

      return (data as IssueCategory[]) || [];
    } catch (error) {
      console.error('Error searching issues:', error);
      throw error;
    }
  }

  /**
   * Get issue by code
   */
  async getByCode(code: string): Promise<IssueCategory | null> {
    try {
      const { data, error } = await supabase
        .from(this.tableName)
        .select('*')
        .eq('code', code)
        .single();

      if (error) {
        if (error.code === 'PGRST116') return null; // Not found
        handleSupabaseError(error);
      }

      return data as IssueCategory;
    } catch (error) {
      console.error(`Error fetching issue ${code}:`, error);
      throw error;
    }
  }

  /**
   * Get categories grouped by main category
   */
  async getCategoriesGrouped(): Promise<Record<string, IssueCategory[]>> {
    try {
      const allCategories = await this.getAll();

      const grouped: Record<string, IssueCategory[]> = {};

      allCategories.forEach(category => {
        if (!grouped[category.category]) {
          grouped[category.category] = [];
        }
        grouped[category.category].push(category);
      });

      return grouped;
    } catch (error) {
      console.error('Error grouping categories:', error);
      throw error;
    }
  }

  /**
   * Map issue category code to display name
   */
  getCategoryDisplayName(code: string): string {
    const mapping: Record<string, string> = {
      'JOBS': 'Employment',
      'AGRICULTURE': 'Agriculture',
      'EDUCATION': 'Education',
      'HEALTHCARE': 'Healthcare',
      'WATER': 'Water Supply',
      'INFRASTRUCTURE': 'Infrastructure',
      'ELECTRICITY': 'Electricity',
      'CORRUPTION': 'Corruption',
      'LAW_ORDER': 'Law & Order',
      'TAMIL': 'Tamil Language',
      'CAUVERY': 'Cauvery Water',
      'NEET': 'NEET Exam',
      'WOMEN_SAFETY': 'Women Safety',
      'SOCIAL_JUSTICE': 'Social Justice',
      'POLLUTION': 'Environment',
      'COASTAL': 'Coastal Issues'
    };

    return mapping[code] || code;
  }

  /**
   * Create a new issue category from citizen report
   * Maps form data to issue_categories table structure
   */
  async createFromReport(reportData: {
    title: string;
    description: string;
    category: string;
    priority: string;
    location: string;
  }): Promise<IssueCategory> {
    try {
      // Generate unique code from title
      const code = reportData.title
        .toUpperCase()
        .replace(/[^A-Z0-9]/g, '_')
        .substring(0, 50) + '_' + Date.now();

      // Map priority to priority_level
      const priorityMap: Record<string, 'Critical' | 'High' | 'Medium' | 'Low'> = {
        'urgent': 'Critical',
        'high': 'High',
        'medium': 'Medium',
        'low': 'Low'
      };

      // Map category CODE to category TYPE (to satisfy CHECK constraint)
      // The database allows: Economic, Social, Infrastructure, Governance, Cultural, Regional, Environmental, Education, Healthcare
      const categoryTypeMap: Record<string, string> = {
        'JOBS': 'Economic',
        'AGRICULTURE': 'Economic',
        'ECONOMY': 'Economic',
        'STARTUPS': 'Economic',
        'COASTAL': 'Economic',

        'EDUCATION': 'Education',
        'NEET': 'Education',

        'HEALTHCARE': 'Healthcare',
        'WOMEN_SAFETY': 'Social',
        'SOCIAL_JUSTICE': 'Social',
        'LIQUOR': 'Social',

        'WATER': 'Infrastructure',
        'INFRASTRUCTURE': 'Infrastructure',
        'METRO': 'Infrastructure',
        'ELECTRICITY': 'Infrastructure',

        'CORRUPTION': 'Governance',
        'LAW_ORDER': 'Governance',
        'GOVERNANCE': 'Governance',

        'TAMIL': 'Cultural',
        'JALLIKATTU': 'Cultural',
        'CAUVERY': 'Regional',

        'POLLUTION': 'Environmental',
      };

      // Get the category type, default to 'Social' if not mapped
      const categoryType = categoryTypeMap[reportData.category] || 'Social';

      const { data, error } = await supabase
        .from(this.tableName)
        .insert({
          code: code,
          name: reportData.title,
          name_tamil: reportData.title, // Use same as English for now
          description: reportData.description,
          detailed_description: `Location: ${reportData.location}\n\n${reportData.description}`,
          category: categoryType, // Use mapped category type instead of code
          priority_level: priorityMap[reportData.priority] || 'Medium',
          is_active: true,
          is_hot_topic: reportData.priority === 'urgent',
          geographic_focus: [reportData.location],
          tvk_stance: 'Under review',
          tvk_priority: reportData.priority === 'urgent' || reportData.priority === 'high' ? 'High' : 'Medium'
        })
        .select()
        .single();

      if (error) handleSupabaseError(error);

      return data as IssueCategory;
    } catch (error) {
      console.error('Error creating issue category from report:', error);
      throw error;
    }
  }
}

export const issueCategoriesService = new IssueCategoriesService();

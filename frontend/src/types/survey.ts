/**
 * Survey Builder Types
 */

export type QuestionType = 'multiple-choice' | 'text' | 'rating' | 'yes-no' | 'checkbox';

export interface QuestionOption {
  id: string;
  label: string;
  value: string;
  goToQuestion?: string; // For logic branching
}

export interface Question {
  id: string;
  type: QuestionType;
  text: string;
  description?: string;
  required: boolean;
  options?: QuestionOption[]; // For multiple-choice, checkbox
  ratingScale?: number; // For rating (default 5)
  showIf?: {
    questionId: string;
    answer: string;
  }; // Conditional logic
}

export interface Survey {
  id?: string;
  title: string;
  description: string;
  questions: Question[];
  status?: 'draft' | 'active' | 'closed';
  created_by?: string;
  organization_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SurveyResponse {
  id?: string;
  survey_id: string;
  respondent_id?: string;
  answers: {
    question_id: string;
    answer: string | string[]; // String for single, array for checkbox
  }[];
  submitted_at?: string;
}

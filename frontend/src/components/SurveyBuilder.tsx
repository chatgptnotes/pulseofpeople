import { useState } from 'react';
import {
  Plus,
  Trash2,
  Eye,
  Save,
  ChevronUp,
  ChevronDown,
  Copy,
  Settings,
  X,
  CheckSquare,
  Type,
  Star,
  CheckCircle
} from 'lucide-react';
import { Survey, Question, QuestionType, QuestionOption } from '../types/survey';
import { validateField } from '../lib/form-validation';

const questionTypes: { type: QuestionType; label: string; icon: any }[] = [
  { type: 'multiple-choice', label: 'Multiple Choice', icon: CheckCircle },
  { type: 'text', label: 'Text Answer', icon: Type },
  { type: 'rating', label: 'Rating Scale', icon: Star },
  { type: 'yes-no', label: 'Yes/No', icon: CheckSquare },
  { type: 'checkbox', label: 'Checkboxes', icon: CheckSquare }
];

export default function SurveyBuilder() {
  const [survey, setSurvey] = useState<Survey>({
    title: '',
    description: '',
    questions: [],
    status: 'draft'
  });

  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Add new question
  const addQuestion = (type: QuestionType) => {
    const newQuestion: Question = {
      id: `q-${Date.now()}`,
      type,
      text: '',
      required: false,
      options: type === 'multiple-choice' || type === 'checkbox'
        ? [
            { id: `opt-${Date.now()}-1`, label: 'Option 1', value: 'option1' },
            { id: `opt-${Date.now()}-2`, label: 'Option 2', value: 'option2' }
          ]
        : undefined,
      ratingScale: type === 'rating' ? 5 : undefined
    };

    setSurvey(prev => ({
      ...prev,
      questions: [...prev.questions, newQuestion]
    }));

    setEditingQuestionId(newQuestion.id);
  };

  // Update question
  const updateQuestion = (questionId: string, updates: Partial<Question>) => {
    setSurvey(prev => ({
      ...prev,
      questions: prev.questions.map(q =>
        q.id === questionId ? { ...q, ...updates } : q
      )
    }));
  };

  // Delete question
  const deleteQuestion = (questionId: string) => {
    setSurvey(prev => ({
      ...prev,
      questions: prev.questions.filter(q => q.id !== questionId)
    }));
    if (editingQuestionId === questionId) {
      setEditingQuestionId(null);
    }
  };

  // Duplicate question
  const duplicateQuestion = (questionId: string) => {
    const question = survey.questions.find(q => q.id === questionId);
    if (!question) return;

    const newQuestion: Question = {
      ...question,
      id: `q-${Date.now()}`,
      text: `${question.text} (Copy)`,
      options: question.options?.map((opt, idx) => ({
        ...opt,
        id: `opt-${Date.now()}-${idx}`
      }))
    };

    setSurvey(prev => ({
      ...prev,
      questions: [...prev.questions, newQuestion]
    }));
  };

  // Move question up/down
  const moveQuestion = (questionId: string, direction: 'up' | 'down') => {
    const index = survey.questions.findIndex(q => q.id === questionId);
    if (index === -1) return;

    const newIndex = direction === 'up' ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= survey.questions.length) return;

    const newQuestions = [...survey.questions];
    [newQuestions[index], newQuestions[newIndex]] = [newQuestions[newIndex], newQuestions[index]];

    setSurvey(prev => ({ ...prev, questions: newQuestions }));
  };

  // Add option to question
  const addOption = (questionId: string) => {
    const question = survey.questions.find(q => q.id === questionId);
    if (!question || !question.options) return;

    const newOption: QuestionOption = {
      id: `opt-${Date.now()}`,
      label: `Option ${question.options.length + 1}`,
      value: `option${question.options.length + 1}`
    };

    updateQuestion(questionId, {
      options: [...question.options, newOption]
    });
  };

  // Update option
  const updateOption = (questionId: string, optionId: string, updates: Partial<QuestionOption>) => {
    const question = survey.questions.find(q => q.id === questionId);
    if (!question || !question.options) return;

    updateQuestion(questionId, {
      options: question.options.map(opt =>
        opt.id === optionId ? { ...opt, ...updates } : opt
      )
    });
  };

  // Delete option
  const deleteOption = (questionId: string, optionId: string) => {
    const question = survey.questions.find(q => q.id === questionId);
    if (!question || !question.options) return;

    updateQuestion(questionId, {
      options: question.options.filter(opt => opt.id !== optionId)
    });
  };

  // Validate survey
  const validateSurvey = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!survey.title.trim()) {
      newErrors.title = 'Survey title is required';
    }

    if (survey.questions.length === 0) {
      newErrors.questions = 'Add at least one question';
    }

    survey.questions.forEach((q, index) => {
      if (!q.text.trim()) {
        newErrors[`question-${q.id}`] = `Question ${index + 1} text is required`;
      }

      if ((q.type === 'multiple-choice' || q.type === 'checkbox') && (!q.options || q.options.length < 2)) {
        newErrors[`question-${q.id}-options`] = `Question ${index + 1} needs at least 2 options`;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Save survey
  const handleSave = async () => {
    if (!validateSurvey()) {
      return;
    }

    setIsSaving(true);

    try {
      // TODO: Integrate with surveys service
      // await surveysService.create(survey);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);

    } catch (error) {
      console.error('Failed to save survey:', error);
      setErrors({ save: 'Failed to save survey. Please try again.' });
    } finally {
      setIsSaving(false);
    }
  };

  // Render question editor
  const renderQuestionEditor = (question: Question) => {
    const isEditing = editingQuestionId === question.id;
    const questionIndex = survey.questions.findIndex(q => q.id === question.id);

    return (
      <div
        key={question.id}
        className={`bg-white border-2 rounded-lg p-4 transition-all ${
          isEditing ? 'border-blue-500 shadow-lg' : 'border-gray-200'
        }`}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <span className="text-sm font-semibold text-gray-500">Q{questionIndex + 1}</span>
              <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                {questionTypes.find(t => t.type === question.type)?.label}
              </span>
              {question.required && (
                <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded">Required</span>
              )}
            </div>

            {isEditing ? (
              <div className="space-y-3">
                <div>
                  <input
                    type="text"
                    value={question.text}
                    onChange={(e) => updateQuestion(question.id, { text: e.target.value })}
                    placeholder="Enter question text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  {errors[`question-${question.id}`] && (
                    <p className="text-red-500 text-xs mt-1">{errors[`question-${question.id}`]}</p>
                  )}
                </div>

                <input
                  type="text"
                  value={question.description || ''}
                  onChange={(e) => updateQuestion(question.id, { description: e.target.value })}
                  placeholder="Description (optional)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />

                {/* Options for multiple-choice and checkbox */}
                {(question.type === 'multiple-choice' || question.type === 'checkbox') && (
                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700">Options:</label>
                    {question.options?.map((option, idx) => (
                      <div key={option.id} className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500 w-6">{idx + 1}.</span>
                        <input
                          type="text"
                          value={option.label}
                          onChange={(e) => updateOption(question.id, option.id, { label: e.target.value, value: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                          placeholder={`Option ${idx + 1}`}
                          className="flex-1 px-3 py-1.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        />
                        {question.options && question.options.length > 2 && (
                          <button
                            onClick={() => deleteOption(question.id, option.id)}
                            className="p-1 text-red-600 hover:bg-red-50 rounded"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                    <button
                      onClick={() => addOption(question.id)}
                      className="text-sm text-blue-600 hover:text-blue-700 flex items-center"
                    >
                      <Plus className="w-4 h-4 mr-1" />
                      Add Option
                    </button>
                    {errors[`question-${question.id}-options`] && (
                      <p className="text-red-500 text-xs">{errors[`question-${question.id}-options`]}</p>
                    )}
                  </div>
                )}

                {/* Rating scale */}
                {question.type === 'rating' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Rating Scale:</label>
                    <select
                      value={question.ratingScale || 5}
                      onChange={(e) => updateQuestion(question.id, { ratingScale: parseInt(e.target.value) })}
                      className="px-3 py-1.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {[3, 5, 7, 10].map(scale => (
                        <option key={scale} value={scale}>1 to {scale}</option>
                      ))}
                    </select>
                  </div>
                )}

                {/* Required toggle */}
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={question.required}
                    onChange={(e) => updateQuestion(question.id, { required: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2"
                  />
                  Required question
                </label>
              </div>
            ) : (
              <div>
                <p className="text-gray-900 font-medium">{question.text || 'Untitled Question'}</p>
                {question.description && (
                  <p className="text-sm text-gray-600 mt-1">{question.description}</p>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center space-x-1 ml-4">
            <button
              onClick={() => setEditingQuestionId(isEditing ? null : question.id)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded"
              title={isEditing ? "Collapse" : "Edit"}
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={() => moveQuestion(question.id, 'up')}
              disabled={questionIndex === 0}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded disabled:opacity-30"
              title="Move up"
            >
              <ChevronUp className="w-4 h-4" />
            </button>
            <button
              onClick={() => moveQuestion(question.id, 'down')}
              disabled={questionIndex === survey.questions.length - 1}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded disabled:opacity-30"
              title="Move down"
            >
              <ChevronDown className="w-4 h-4" />
            </button>
            <button
              onClick={() => duplicateQuestion(question.id)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded"
              title="Duplicate"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={() => deleteQuestion(question.id)}
              className="p-2 text-red-600 hover:bg-red-50 rounded"
              title="Delete"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Preview of question */}
        {!isEditing && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            {question.type === 'multiple-choice' && question.options && (
              <div className="space-y-2">
                {question.options.map(opt => (
                  <label key={opt.id} className="flex items-center text-sm text-gray-700">
                    <input type="radio" name={`preview-${question.id}`} className="mr-2" disabled />
                    {opt.label}
                  </label>
                ))}
              </div>
            )}
            {question.type === 'checkbox' && question.options && (
              <div className="space-y-2">
                {question.options.map(opt => (
                  <label key={opt.id} className="flex items-center text-sm text-gray-700">
                    <input type="checkbox" className="mr-2 rounded" disabled />
                    {opt.label}
                  </label>
                ))}
              </div>
            )}
            {question.type === 'text' && (
              <input
                type="text"
                placeholder="Text answer"
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded bg-gray-50 text-sm"
              />
            )}
            {question.type === 'rating' && (
              <div className="flex items-center space-x-2">
                {Array.from({ length: question.ratingScale || 5 }, (_, i) => (
                  <Star key={i} className="w-6 h-6 text-gray-300" />
                ))}
              </div>
            )}
            {question.type === 'yes-no' && (
              <div className="flex items-center space-x-4">
                <label className="flex items-center text-sm text-gray-700">
                  <input type="radio" name={`preview-${question.id}`} className="mr-2" disabled />
                  Yes
                </label>
                <label className="flex items-center text-sm text-gray-700">
                  <input type="radio" name={`preview-${question.id}`} className="mr-2" disabled />
                  No
                </label>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  if (previewMode) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-gray-900">{survey.title || 'Untitled Survey'}</h1>
            <button
              onClick={() => setPreviewMode(false)}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
            >
              Exit Preview
            </button>
          </div>

          {survey.description && (
            <p className="text-gray-600 mb-8">{survey.description}</p>
          )}

          <div className="space-y-6">
            {survey.questions.map((question, index) => (
              <div key={question.id} className="border-b border-gray-200 pb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  {index + 1}. {question.text}
                  {question.required && <span className="text-red-500 ml-1">*</span>}
                </h3>
                {question.description && (
                  <p className="text-sm text-gray-600 mb-3">{question.description}</p>
                )}

                {question.type === 'multiple-choice' && question.options && (
                  <div className="space-y-2">
                    {question.options.map(opt => (
                      <label key={opt.id} className="flex items-center text-gray-700">
                        <input type="radio" name={`question-${question.id}`} className="mr-3" />
                        {opt.label}
                      </label>
                    ))}
                  </div>
                )}

                {question.type === 'checkbox' && question.options && (
                  <div className="space-y-2">
                    {question.options.map(opt => (
                      <label key={opt.id} className="flex items-center text-gray-700">
                        <input type="checkbox" className="mr-3 rounded" />
                        {opt.label}
                      </label>
                    ))}
                  </div>
                )}

                {question.type === 'text' && (
                  <textarea
                    rows={3}
                    placeholder="Your answer"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  ></textarea>
                )}

                {question.type === 'rating' && (
                  <div className="flex items-center space-x-2">
                    {Array.from({ length: question.ratingScale || 5 }, (_, i) => (
                      <button key={i} className="focus:outline-none hover:scale-110 transition-transform">
                        <Star className="w-8 h-8 text-gray-300 hover:text-yellow-400" />
                      </button>
                    ))}
                  </div>
                )}

                {question.type === 'yes-no' && (
                  <div className="flex items-center space-x-6">
                    <label className="flex items-center text-gray-700">
                      <input type="radio" name={`question-${question.id}`} className="mr-2" />
                      Yes
                    </label>
                    <label className="flex items-center text-gray-700">
                      <input type="radio" name={`question-${question.id}`} className="mr-2" />
                      No
                    </label>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
              Submit Survey
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Survey Builder</h1>

        {/* Success message */}
        {saveSuccess && (
          <div className="mb-4 bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 font-medium">Survey saved successfully!</p>
          </div>
        )}

        {errors.save && (
          <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{errors.save}</p>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Survey Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={survey.title}
              onChange={(e) => setSurvey(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Enter survey title"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.title ? 'border-red-500' : 'border-gray-300'
              }`}
            />
            {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              rows={2}
              value={survey.description}
              onChange={(e) => setSurvey(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe the purpose of this survey"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>
        </div>

        <div className="flex items-center justify-between mt-6">
          <div className="text-sm text-gray-600">
            {survey.questions.length} {survey.questions.length === 1 ? 'question' : 'questions'}
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setPreviewMode(true)}
              disabled={survey.questions.length === 0}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 flex items-center"
            >
              <Eye className="w-4 h-4 mr-2" />
              Preview
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save Survey
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Questions */}
      <div className="space-y-4">
        {survey.questions.map(question => renderQuestionEditor(question))}

        {errors.questions && survey.questions.length === 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-yellow-800">{errors.questions}</p>
          </div>
        )}
      </div>

      {/* Add Question */}
      <div className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-300 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Add Question</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {questionTypes.map(({ type, label, icon: Icon }) => (
            <button
              key={type}
              onClick={() => addQuestion(type)}
              className="flex flex-col items-center justify-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors group"
            >
              <Icon className="w-8 h-8 text-gray-400 group-hover:text-blue-600 mb-2" />
              <span className="text-sm font-medium text-gray-700 group-hover:text-blue-600 text-center">
                {label}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

import type {
  AggregatedModelExams,
  AggregatedModelJudgments,
  ModelSummary,
  ModelDetail,
} from '../types';

// Mock model summaries
const mockModels: Record<string, ModelSummary> = {
  'model_1': { id: 'model_1', name: 'Model 1', isPolish: false, config: {} },
  'model_2': { id: 'model_2', name: 'Model 2', isPolish: true, config: {} },
  'model_3': { id: 'model_3', name: 'Model 3', isPolish: false, config: {} },
};

export const mockExamsData: AggregatedModelExams[] = [
  {
    model: mockModels['model_1'],
    accuracyMetrics: { answer: 0.92, legal_basis: 0.85 },
    textMetrics: { exact_match: 0.72, rouge_n_f1: 0.88, rouge_n_tfidf: 0.91, rouge_w: 0.86 },
  },
  {
    model: mockModels['model_2'],
    accuracyMetrics: { answer: 0.78, legal_basis: 0.71 },
    textMetrics: { exact_match: 0.58, rouge_n_f1: 0.74, rouge_n_tfidf: 0.79, rouge_w: 0.72 },
  },
  {
    model: mockModels['model_3'],
    accuracyMetrics: { answer: 0.85, legal_basis: 0.79 },
    textMetrics: { exact_match: 0.65, rouge_n_f1: 0.82, rouge_n_tfidf: 0.85, rouge_w: 0.80 },
  },
];

export const mockJudgmentsData: AggregatedModelJudgments[] = [
  {
    model: mockModels['model_1'],
    accuracyMetrics: { legal_basis: 0.88 },
    textMetrics: { exact_match: 0.70, rouge_n_f1: 0.85, rouge_n_tfidf: 0.89, rouge_w: 0.84 },
  },
  {
    model: mockModels['model_2'],
    accuracyMetrics: { legal_basis: 0.74 },
    textMetrics: { exact_match: 0.55, rouge_n_f1: 0.71, rouge_n_tfidf: 0.76, rouge_w: 0.69 },
  },
  {
    model: mockModels['model_3'],
    accuracyMetrics: { legal_basis: 0.81 },
    textMetrics: { exact_match: 0.62, rouge_n_f1: 0.79, rouge_n_tfidf: 0.83, rouge_w: 0.77 },
  },
];

export const mockModelDetails: Record<string, ModelDetail> = {
  'model_1': {
    profile: mockModels['model_1'],
    exams: [
      {
        examType: 'all',
        year: 0,
        accuracyMetrics: { answer: 0.92, legal_basis: 0.85 },
        textMetrics: { exact_match: 0.72, rouge_n_f1: 0.88, rouge_n_tfidf: 0.91, rouge_w: 0.86 },
      },
      {
        examType: 'adwokacki_radcowy',
        year: 2025,
        accuracyMetrics: { answer: 0.94, legal_basis: 0.87 },
        textMetrics: { exact_match: 0.75, rouge_n_f1: 0.90, rouge_n_tfidf: 0.93, rouge_w: 0.88 },
      },
      {
        examType: 'adwokacki_radcowy',
        year: 2024,
        accuracyMetrics: { answer: 0.90, legal_basis: 0.83 },
        textMetrics: { exact_match: 0.69, rouge_n_f1: 0.86, rouge_n_tfidf: 0.89, rouge_w: 0.84 },
      },
    ],
    judgments: {
      accuracyMetrics: { legal_basis: 0.88 },
      textMetrics: { exact_match: 0.70, rouge_n_f1: 0.85, rouge_n_tfidf: 0.89, rouge_w: 0.84 },
    },
  },
  'model_2': {
    profile: mockModels['model_2'],
    exams: [
      {
        examType: 'all',
        year: 0,
        accuracyMetrics: { answer: 0.78, legal_basis: 0.71 },
        textMetrics: { exact_match: 0.58, rouge_n_f1: 0.74, rouge_n_tfidf: 0.79, rouge_w: 0.72 },
      },
      {
        examType: 'adwokacki_radcowy',
        year: 2025,
        accuracyMetrics: { answer: 0.80, legal_basis: 0.73 },
        textMetrics: { exact_match: 0.60, rouge_n_f1: 0.76, rouge_n_tfidf: 0.81, rouge_w: 0.74 },
      },
      {
        examType: 'notarialny',
        year: 2025,
        accuracyMetrics: { answer: 0.76, legal_basis: 0.69 },
        textMetrics: { exact_match: 0.56, rouge_n_f1: 0.72, rouge_n_tfidf: 0.77, rouge_w: 0.70 },
      },
    ],
    judgments: {
      accuracyMetrics: { legal_basis: 0.74 },
      textMetrics: { exact_match: 0.55, rouge_n_f1: 0.71, rouge_n_tfidf: 0.76, rouge_w: 0.69 },
    },
  },
  'model_3': {
    profile: mockModels['model_3'],
    exams: [
      {
        examType: 'all',
        year: 0,
        accuracyMetrics: { answer: 0.85, legal_basis: 0.79 },
        textMetrics: { exact_match: 0.65, rouge_n_f1: 0.82, rouge_n_tfidf: 0.85, rouge_w: 0.80 },
      },
      {
        examType: 'adwokacki_radcowy',
        year: 2025,
        accuracyMetrics: { answer: 0.87, legal_basis: 0.81 },
        textMetrics: { exact_match: 0.67, rouge_n_f1: 0.84, rouge_n_tfidf: 0.87, rouge_w: 0.82 },
      },
      {
        examType: 'komorniczy',
        year: 2025,
        accuracyMetrics: { answer: 0.83, legal_basis: 0.77 },
        textMetrics: { exact_match: 0.63, rouge_n_f1: 0.80, rouge_n_tfidf: 0.83, rouge_w: 0.78 },
      },
    ],
    judgments: {
      accuracyMetrics: { legal_basis: 0.81 },
      textMetrics: { exact_match: 0.62, rouge_n_f1: 0.79, rouge_n_tfidf: 0.83, rouge_w: 0.77 },
    },
  },
};

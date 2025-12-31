import type {
  AggregatedModelExams,
  AggregatedModelJudgments,
  ModelSummary,
  ModelDetail,
} from '../types';

// Mock model summaries
const mockModels: Record<string, ModelSummary> = {
  'gpt-4o': { id: 'gpt-4o', name: 'GPT-4o', isPolish: false, config: {} },
  'claude-3-5-sonnet': { id: 'claude-3-5-sonnet', name: 'Claude 3.5 Sonnet', isPolish: false, config: {} },
  'llama-3-70b': { id: 'llama-3-70b', name: 'Llama-3-70B', isPolish: false, config: {} },
  'bielik-11b-v2': { id: 'bielik-11b-v2', name: 'Bielik-11B-v2', isPolish: true, config: {} },
  'gpt-4-turbo': { id: 'gpt-4-turbo', name: 'GPT-4-Turbo', isPolish: false, config: {} },
  'claude-3-opus': { id: 'claude-3-opus', name: 'Claude 3 Opus', isPolish: false, config: {} },
};

export const mockExamsData: AggregatedModelExams[] = [
  {
    model: mockModels['gpt-4o'],
    accuracyMetrics: { answer: 0.892, identification: 0.82 },
    textMetrics: { exact_match: 0.654, bleu: 0.82, weighted_bleu: 0.85 },
  },
  {
    model: mockModels['claude-3-5-sonnet'],
    accuracyMetrics: { answer: 0.875, identification: 0.795 },
    textMetrics: { exact_match: 0.631, bleu: 0.79, weighted_bleu: 0.83 },
  },
  {
    model: mockModels['llama-3-70b'],
    accuracyMetrics: { answer: 0.81, identification: 0.65 },
    textMetrics: { exact_match: 0.452, bleu: 0.68, weighted_bleu: 0.71 },
  },
  {
    model: mockModels['bielik-11b-v2'],
    accuracyMetrics: { answer: 0.745, identification: 0.68 },
    textMetrics: { exact_match: 0.41, bleu: 0.55, weighted_bleu: 0.62 },
  },
];

export const mockJudgmentsData: AggregatedModelJudgments[] = [
  {
    model: mockModels['gpt-4-turbo'],
    accuracyMetrics: { retrieval: 0.924 },
    textMetrics: { exact_match: 0.624, bleu: 0.76, weighted_bleu: 0.78 },
  },
  {
    model: mockModels['claude-3-opus'],
    accuracyMetrics: { retrieval: 0.901 },
    textMetrics: { exact_match: 0.601, bleu: 0.72, weighted_bleu: 0.75 },
  },
  {
    model: mockModels['bielik-11b-v2'],
    accuracyMetrics: { retrieval: 0.785 },
    textMetrics: { exact_match: 0.45, bleu: 0.51, weighted_bleu: 0.55 },
  },
];

export const mockModelDetails: Record<string, ModelDetail> = {
  'gpt-4o': {
    profile: mockModels['gpt-4o'],
    exams: [
      {
        examType: 'Radcowski',
        year: 2024,
        accuracyMetrics: { answer: 0.912, identification: 0.845 },
        textMetrics: { exact_match: 0.682, bleu: 0.84, weighted_bleu: 0.87 },
      },
      {
        examType: 'Radcowski',
        year: 2023,
        accuracyMetrics: { answer: 0.878, identification: 0.801 },
        textMetrics: { exact_match: 0.625, bleu: 0.80, weighted_bleu: 0.83 },
      },
      {
        examType: 'Adwokacki',
        year: 2024,
        accuracyMetrics: { answer: 0.905, identification: 0.832 },
        textMetrics: { exact_match: 0.668, bleu: 0.83, weighted_bleu: 0.86 },
      },
    ],
    judgments: {
      accuracyMetrics: { retrieval: 0.918 },
      textMetrics: { exact_match: 0.615, bleu: 0.75, weighted_bleu: 0.77 },
    },
  },
  'claude-3-5-sonnet': {
    profile: mockModels['claude-3-5-sonnet'],
    exams: [
      {
        examType: 'Radcowski',
        year: 2024,
        accuracyMetrics: { answer: 0.891, identification: 0.812 },
        textMetrics: { exact_match: 0.654, bleu: 0.81, weighted_bleu: 0.85 },
      },
      {
        examType: 'Radcowski',
        year: 2023,
        accuracyMetrics: { answer: 0.856, identification: 0.778 },
        textMetrics: { exact_match: 0.608, bleu: 0.77, weighted_bleu: 0.81 },
      },
    ],
    judgments: {
      accuracyMetrics: { retrieval: 0.895 },
      textMetrics: { exact_match: 0.598, bleu: 0.71, weighted_bleu: 0.74 },
    },
  },
  'llama-3-70b': {
    profile: mockModels['llama-3-70b'],
    exams: [
      {
        examType: 'Radcowski',
        year: 2024,
        accuracyMetrics: { answer: 0.825, identification: 0.668 },
        textMetrics: { exact_match: 0.471, bleu: 0.70, weighted_bleu: 0.73 },
      },
    ],
    judgments: {
      accuracyMetrics: { retrieval: 0.824 },
      textMetrics: { exact_match: 0.521, bleu: 0.62, weighted_bleu: 0.65 },
    },
  },
  'bielik-11b-v2': {
    profile: mockModels['bielik-11b-v2'],
    exams: [
      {
        examType: 'Radcowski',
        year: 2024,
        accuracyMetrics: { answer: 0.762, identification: 0.701 },
        textMetrics: { exact_match: 0.435, bleu: 0.58, weighted_bleu: 0.65 },
      },
      {
        examType: 'Radcowski',
        year: 2023,
        accuracyMetrics: { answer: 0.728, identification: 0.659 },
        textMetrics: { exact_match: 0.385, bleu: 0.52, weighted_bleu: 0.59 },
      },
    ],
    judgments: {
      accuracyMetrics: { retrieval: 0.785 },
      textMetrics: { exact_match: 0.45, bleu: 0.51, weighted_bleu: 0.55 },
    },
  },
  'gpt-4-turbo': {
    profile: mockModels['gpt-4-turbo'],
    exams: [
      {
        examType: 'Radcowski',
        year: 2024,
        accuracyMetrics: { answer: 0.898, identification: 0.822 },
        textMetrics: { exact_match: 0.665, bleu: 0.82, weighted_bleu: 0.85 },
      },
    ],
    judgments: {
      accuracyMetrics: { retrieval: 0.924 },
      textMetrics: { exact_match: 0.624, bleu: 0.76, weighted_bleu: 0.78 },
    },
  },
  'claude-3-opus': {
    profile: mockModels['claude-3-opus'],
    exams: [
      {
        examType: 'Radcowski',
        year: 2024,
        accuracyMetrics: { answer: 0.885, identification: 0.80 },
        textMetrics: { exact_match: 0.642, bleu: 0.79, weighted_bleu: 0.83 },
      },
    ],
    judgments: {
      accuracyMetrics: { retrieval: 0.901 },
      textMetrics: { exact_match: 0.601, bleu: 0.72, weighted_bleu: 0.75 },
    },
  },
};

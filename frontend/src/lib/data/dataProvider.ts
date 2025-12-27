import { cacheTag } from 'next/cache';
import { mockExamsData, mockJudgmentsData, mockModelDetails } from './mockData';
import type {
  AggregatedModelExams,
  AggregatedModelJudgments,
  ModelDetail,
} from '../types';

const useMockData =
  process.env.NODE_ENV === 'development' &&
  process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

// Get base URL for API calls (handles both server and client)
function getApiBaseUrl(): string {
  // For server-side calls in development
  if (typeof window === 'undefined') {
    return process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:3000';
  }
  // For client-side calls
  return '';
}

export async function getExamsData(): Promise<AggregatedModelExams[]> {
  'use cache';
  cacheTag('exams');

  if (useMockData) {
    return mockExamsData;
  }

  const res = await fetch(`${getApiBaseUrl()}/api/exams`);
  if (!res.ok) {
    throw new Error('Failed to fetch exams');
  }
  return res.json();
}

export async function getJudgmentsData(): Promise<AggregatedModelJudgments[]> {
  'use cache';
  cacheTag('judgments');

  if (useMockData) {
    return mockJudgmentsData;
  }

  const res = await fetch(`${getApiBaseUrl()}/api/judgments`);
  if (!res.ok) {
    throw new Error('Failed to fetch judgments');
  }
  return res.json();
}

export async function getModelData(modelId: string): Promise<ModelDetail | null> {
  'use cache';
  cacheTag(`model-${modelId}`);

  if (useMockData) {
    return mockModelDetails[modelId] ?? null;
  }

  const res = await fetch(`${getApiBaseUrl()}/api/models/${modelId}`);
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error('Failed to fetch model');
  }
  return res.json();
}

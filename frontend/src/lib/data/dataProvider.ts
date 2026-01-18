import 'server-only';

import {
  mockExamsData,
  mockJudgmentsData,
  mockModelDetails,
} from './mockData';
import {
  getAggregatedExams,
  getAllJudgments,
  getModelDetail,
} from '@/lib/server/firestore';
import type {
  AggregatedModelExams,
  AggregatedModelJudgments,
  ModelDetail,
} from '../types';

const USE_MOCK_DATA = process.env.NODE_ENV === 'development' && process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

export async function getExamsData(): Promise<AggregatedModelExams[]> {
  if (USE_MOCK_DATA) {
    return mockExamsData;
  }
  return getAggregatedExams();
}

export async function getJudgmentsData(): Promise<AggregatedModelJudgments[]> {
  if (USE_MOCK_DATA) {
    return mockJudgmentsData;
  }
  return getAllJudgments();
}

export async function getModelData(modelId: string): Promise<ModelDetail | null> {
  if (USE_MOCK_DATA) {
    return mockModelDetails[modelId] || null;
  }
  return getModelDetail(modelId);
}

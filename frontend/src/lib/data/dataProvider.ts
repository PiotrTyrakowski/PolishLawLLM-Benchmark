import 'server-only';

// Re-export firestore functions directly
// Caching is handled at the source in firestore.ts via 'use cache' directives
export {
  getAggregatedExams as getExamsData,
  getAllJudgments as getJudgmentsData,
  getModelDetail as getModelData,
} from '@/lib/server/firestore';

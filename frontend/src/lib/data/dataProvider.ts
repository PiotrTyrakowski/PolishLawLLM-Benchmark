import { cacheTag } from 'next/cache';
import { collection, getDocs, doc, getDoc } from 'firebase/firestore';
import { db } from '../firebase';
import { mockExamsData, mockJudgmentsData, mockModelDetails } from './mockData';
import type {
  FirestoreModelDoc,
  FirestoreExamDoc,
  FirestoreJudgmentDoc,
  ExamResult,
  JudgmentResult,
  ModelDetailData,
  ExamBreakdown,
} from '../types';

const useMockData =
  process.env.NODE_ENV === 'development' &&
  process.env.NEXT_PUBLIC_USE_MOCK_DATA === 'true';

const RESULTS_COLLECTION =
  process.env.NEXT_PUBLIC_RESULTS_COLLECTION || 'results';

// ===== Transform Functions =====

function transformExam(
  examDoc: FirestoreExamDoc,
  modelId: string,
  modelData: FirestoreModelDoc
): ExamResult {
  return {
    modelId,
    model: modelData.model_name,
    isPolish: modelData.is_polish_model,
    year: String(examDoc.year),
    examType: examDoc.type,
    accuracy: examDoc.accuracy_metrics.answer,
    lawAccuracy: examDoc.accuracy_metrics.identification,
    exactMatch: examDoc.text_metrics.exact_match,
    bleu: examDoc.text_metrics.bleu,
    wBleu: examDoc.text_metrics.weighted_bleu,
  };
}

function transformJudgment(
  judgmentDoc: FirestoreJudgmentDoc,
  modelId: string,
  modelData: FirestoreModelDoc
): JudgmentResult {
  return {
    modelId,
    model: modelData.model_name,
    isPolish: modelData.is_polish_model,
    retrieval: judgmentDoc.accuracy_metrics.identification,
    exactMatch: judgmentDoc.text_metrics.exact_match,
    bleu: judgmentDoc.text_metrics.bleu,
    wBleu: judgmentDoc.text_metrics.weighted_bleu,
  };
}

function avg(nums: number[]): number {
  return nums.length ? nums.reduce((a, b) => a + b, 0) / nums.length : 0;
}

// ===== Data Fetching =====

export async function getExamsData(): Promise<ExamResult[]> {
  'use cache';
  cacheTag('exams');

  if (useMockData) {
    return mockExamsData;
  }

  const results: ExamResult[] = [];
  const modelsSnapshot = await getDocs(collection(db, RESULTS_COLLECTION));

  for (const modelDoc of modelsSnapshot.docs) {
    const modelData = modelDoc.data() as FirestoreModelDoc;
    const examsSnapshot = await getDocs(
      collection(db, RESULTS_COLLECTION, modelDoc.id, 'exams')
    );

    for (const examDoc of examsSnapshot.docs) {
      results.push(
        transformExam(
          examDoc.data() as FirestoreExamDoc,
          modelDoc.id,
          modelData
        )
      );
    }
  }

  return results;
}

export async function getJudgmentsData(): Promise<JudgmentResult[]> {
  'use cache';
  cacheTag('judgments');

  if (useMockData) {
    return mockJudgmentsData;
  }

  const results: JudgmentResult[] = [];
  const modelsSnapshot = await getDocs(collection(db, RESULTS_COLLECTION));

  for (const modelDoc of modelsSnapshot.docs) {
    const modelData = modelDoc.data() as FirestoreModelDoc;
    const judgmentsSnapshot = await getDocs(
      collection(db, RESULTS_COLLECTION, modelDoc.id, 'judgments')
    );

    for (const judgmentDoc of judgmentsSnapshot.docs) {
      results.push(
        transformJudgment(
          judgmentDoc.data() as FirestoreJudgmentDoc,
          modelDoc.id,
          modelData
        )
      );
    }
  }

  return results;
}

export async function getModelData(
  modelId: string
): Promise<ModelDetailData | null> {
  'use cache';
  cacheTag(`model-${modelId}`);

  if (useMockData) {
    return mockModelDetails[modelId] ?? null;
  }

  const modelDocRef = doc(db, RESULTS_COLLECTION, modelId);
  const modelSnapshot = await getDoc(modelDocRef);

  if (!modelSnapshot.exists()) {
    return null;
  }

  const modelData = modelSnapshot.data() as FirestoreModelDoc;

  // Fetch exams
  const examsSnapshot = await getDocs(
    collection(db, RESULTS_COLLECTION, modelId, 'exams')
  );
  const examsBreakdown: ExamBreakdown[] = [];

  for (const examDoc of examsSnapshot.docs) {
    const exam = examDoc.data() as FirestoreExamDoc;
    examsBreakdown.push({
      examType: exam.type,
      year: String(exam.year),
      accuracy: exam.accuracy_metrics.answer,
      lawAccuracy: exam.accuracy_metrics.identification,
      exactMatch: exam.text_metrics.exact_match,
      bleu: exam.text_metrics.bleu,
      wBleu: exam.text_metrics.weighted_bleu,
    });
  }

  // Calculate exams overall (average of all exams)
  const examsOverall =
    examsBreakdown.length > 0
      ? {
          accuracy: avg(examsBreakdown.map((e) => e.accuracy)),
          lawAccuracy: avg(examsBreakdown.map((e) => e.lawAccuracy)),
          exactMatch: avg(examsBreakdown.map((e) => e.exactMatch)),
          bleu: avg(examsBreakdown.map((e) => e.bleu)),
          wBleu: avg(examsBreakdown.map((e) => e.wBleu)),
        }
      : { accuracy: 0, lawAccuracy: 0, exactMatch: 0, bleu: 0, wBleu: 0 };

  // Fetch judgments
  const judgmentsSnapshot = await getDocs(
    collection(db, RESULTS_COLLECTION, modelId, 'judgments')
  );
  const judgmentDoc = judgmentsSnapshot.docs[0]?.data() as
    | FirestoreJudgmentDoc
    | undefined;

  const judgmentsOverall = judgmentDoc
    ? {
        retrieval: judgmentDoc.accuracy_metrics.identification,
        exactMatch: judgmentDoc.text_metrics.exact_match,
        bleu: judgmentDoc.text_metrics.bleu,
        wBleu: judgmentDoc.text_metrics.weighted_bleu,
      }
    : { retrieval: 0, exactMatch: 0, bleu: 0, wBleu: 0 };

  return {
    profile: {
      id: modelId,
      name: modelData.model_name,
      isPolish: modelData.is_polish_model,
    },
    examsOverall,
    examsBreakdown,
    judgmentsOverall,
  };
}

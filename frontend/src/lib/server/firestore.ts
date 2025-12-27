import 'server-only';

import { adminDb } from '../firebase-admin';
import type {
  FirestoreModel,
  FirestoreExam,
  FirestoreJudgment,
  ModelSummary,
  AggregatedModelExams,
  AggregatedModelJudgments,
  ExamData,
  ModelDetail,
} from '../types';

const COLLECTION = process.env.RESULTS_COLLECTION || 'results';

// Helper: Calculate average of metric records
function averageMetrics(metricsArray: Record<string, number>[]): Record<string, number> {
  if (metricsArray.length === 0) return {};

  const allKeys = new Set<string>();
  metricsArray.forEach((m) => Object.keys(m).forEach((k) => allKeys.add(k)));

  const result: Record<string, number> = {};
  allKeys.forEach((key) => {
    const values = metricsArray.map((m) => m[key]).filter((v) => v !== undefined);
    result[key] = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
  });

  return result;
}

// Helper: Transform Firestore model doc to ModelSummary
function toModelSummary(id: string, data: FirestoreModel): ModelSummary {
  return {
    id,
    name: data.model_name,
    isPolish: data.is_polish,
    config: data.model_config || {},
  };
}

// Get all models with their aggregated exam metrics
export async function getAggregatedExams(): Promise<AggregatedModelExams[]> {
  const modelsSnap = await adminDb.collection(COLLECTION).get();
  const results: AggregatedModelExams[] = [];

  for (const modelDoc of modelsSnap.docs) {
    const modelData = modelDoc.data() as FirestoreModel;
    const model = toModelSummary(modelDoc.id, modelData);

    const examsSnap = await adminDb
      .collection(COLLECTION)
      .doc(modelDoc.id)
      .collection('exams')
      .get();

    if (examsSnap.empty) continue;

    const accuracyMetricsArray: Record<string, number>[] = [];
    const textMetricsArray: Record<string, number>[] = [];

    for (const examDoc of examsSnap.docs) {
      const exam = examDoc.data() as FirestoreExam;
      accuracyMetricsArray.push(exam.accuracy_metrics);
      textMetricsArray.push(exam.text_metrics);
    }

    results.push({
      model,
      accuracyMetrics: averageMetrics(accuracyMetricsArray),
      textMetrics: averageMetrics(textMetricsArray),
    });
  }

  return results;
}

// Get all models with their judgment metrics (single doc per model, no averaging)
export async function getAllJudgments(): Promise<AggregatedModelJudgments[]> {
  const modelsSnap = await adminDb.collection(COLLECTION).get();
  const results: AggregatedModelJudgments[] = [];

  for (const modelDoc of modelsSnap.docs) {
    const modelData = modelDoc.data() as FirestoreModel;
    const model = toModelSummary(modelDoc.id, modelData);

    // Per the spec: /results/{model_id}/judgments/all
    const judgmentDoc = await adminDb
      .collection(COLLECTION)
      .doc(modelDoc.id)
      .collection('judgments')
      .doc('all')
      .get();

    if (!judgmentDoc.exists) continue;

    const judgment = judgmentDoc.data() as FirestoreJudgment;
    results.push({
      model,
      accuracyMetrics: judgment.accuracy_metrics,
      textMetrics: judgment.text_metrics,
    });
  }

  return results;
}

// Get detailed data for a specific model
export async function getModelDetail(modelId: string): Promise<ModelDetail | null> {
  const modelDoc = await adminDb.collection(COLLECTION).doc(modelId).get();

  if (!modelDoc.exists) return null;

  const modelData = modelDoc.data() as FirestoreModel;
  const profile = toModelSummary(modelId, modelData);

  // Get all exams for this model
  const examsSnap = await adminDb
    .collection(COLLECTION)
    .doc(modelId)
    .collection('exams')
    .get();

  const exams: ExamData[] = examsSnap.docs.map((doc) => {
    const exam = doc.data() as FirestoreExam;
    return {
      examType: exam.type,
      year: exam.year,
      accuracyMetrics: exam.accuracy_metrics,
      textMetrics: exam.text_metrics,
    };
  });

  // Get judgment (single doc)
  const judgmentDoc = await adminDb
    .collection(COLLECTION)
    .doc(modelId)
    .collection('judgments')
    .doc('all')
    .get();

  const judgments = judgmentDoc.exists
    ? {
        accuracyMetrics: (judgmentDoc.data() as FirestoreJudgment).accuracy_metrics,
        textMetrics: (judgmentDoc.data() as FirestoreJudgment).text_metrics,
      }
    : null;

  return {
    profile,
    exams,
    judgments,
  };
}

// Get all model IDs for static generation
export async function getAllModelIds(): Promise<string[]> {
  const modelsSnap = await adminDb.collection(COLLECTION).get();
  return modelsSnap.docs.map((doc) => doc.id);
}

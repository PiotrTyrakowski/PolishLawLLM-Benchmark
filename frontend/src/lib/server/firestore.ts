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

function getDb() {
  if (!adminDb) {
    throw new Error('Firebase is disabled. This function should not be called when using mock data.');
  }
  return adminDb;
}

function toModelSummary(id: string, data: FirestoreModel): ModelSummary {
  return {
    id,
    name: data.model_name,
    isPolish: data.is_polish,
    config: data.model_config || {},
  };
}

export async function getAggregatedExams(): Promise<AggregatedModelExams[]> {
  const modelsSnap = await getDb().collection(COLLECTION).get();
  const results: AggregatedModelExams[] = [];

  for (const modelDoc of modelsSnap.docs) {
    const modelData = modelDoc.data() as FirestoreModel;
    const model = toModelSummary(modelDoc.id, modelData);

    const allDoc = await getDb()
      .collection(COLLECTION)
      .doc(modelDoc.id)
      .collection('exams')
      .doc('all')
      .get();

    if (!allDoc.exists) continue;

    const examData = allDoc.data() as FirestoreExam;
    results.push({
      model,
      accuracyMetrics: examData.accuracy_metrics,
      textMetrics: examData.text_metrics,
    });
  }

  return results;
}

export async function getAllJudgments(): Promise<AggregatedModelJudgments[]> {
  const modelsSnap = await getDb().collection(COLLECTION).get();
  const results: AggregatedModelJudgments[] = [];

  for (const modelDoc of modelsSnap.docs) {
    const modelData = modelDoc.data() as FirestoreModel;
    const model = toModelSummary(modelDoc.id, modelData);

    const judgmentDoc = await getDb()
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

export async function getModelDetail(modelId: string): Promise<ModelDetail | null> {
  const modelDoc = await getDb().collection(COLLECTION).doc(modelId).get();

  if (!modelDoc.exists) return null;

  const modelData = modelDoc.data() as FirestoreModel;
  const profile = toModelSummary(modelId, modelData);

  const examsSnap = await getDb()
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

  const judgmentDoc = await getDb()
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

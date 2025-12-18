// ===== Firestore Types (snake_case, matches DB) =====
export interface FirestoreModelDoc {
  model_name: string;
  is_polish_model: boolean;
}

export interface FirestoreExamDoc {
  accuracy_metrics: { answer: number; identification: number };
  text_metrics: { exact_match: number; bleu: number; weighted_bleu: number };
  type: string;
  year: number;
}

export interface FirestoreJudgmentDoc {
  accuracy_metrics: { identification: number };
  text_metrics: { exact_match: number; bleu: number; weighted_bleu: number };
}

// ===== App Types (camelCase) =====
export interface ExamResult {
  modelId: string;
  model: string;
  isPolish: boolean;
  year: string;
  examType: string;
  accuracy: number;
  lawAccuracy: number;
  exactMatch: number;
  bleu: number;
  wBleu: number;
}

export interface JudgmentResult {
  modelId: string;
  model: string;
  isPolish: boolean;
  retrieval: number;
  exactMatch: number;
  bleu: number;
  wBleu: number;
}

export interface ModelProfile {
  id: string;
  name: string;
  isPolish: boolean;
}

export interface ExamBreakdown {
  examType: string;
  year: string;
  accuracy: number;
  lawAccuracy: number;
  exactMatch: number;
  bleu: number;
  wBleu: number;
}

export interface ModelDetailData {
  profile: ModelProfile;
  examsOverall: {
    accuracy: number;
    lawAccuracy: number;
    exactMatch: number;
    bleu: number;
    wBleu: number;
  };
  examsBreakdown: ExamBreakdown[];
  judgmentsOverall: {
    retrieval: number;
    exactMatch: number;
    bleu: number;
    wBleu: number;
  };
}

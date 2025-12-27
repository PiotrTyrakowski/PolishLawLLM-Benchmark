export interface DynamicMetrics {
  accuracy_metrics: Record<string, number>;
  text_metrics: Record<string, number>;
}

// ===== Firestore Document Types (snake_case, matches DB) =====

export interface FirestoreModel {
  model_name: string;
  is_polish: boolean;
  model_config: Record<string, unknown>;
}

export interface FirestoreExam extends DynamicMetrics {
  type: string;
  year: number;
}

export interface FirestoreJudgment extends DynamicMetrics {}

// ===== API Response Types =====

export interface ModelSummary {
  id: string;
  name: string;
  isPolish: boolean;
  config: Record<string, unknown>;
}

// Home page table row - model with aggregated metrics
export interface AggregatedModelExams {
  model: ModelSummary;
  accuracyMetrics: Record<string, number>;
  textMetrics: Record<string, number>;
}

// Home page table row - model with judgment metrics (same structure)
export interface AggregatedModelJudgments {
  model: ModelSummary;
  accuracyMetrics: Record<string, number>;
  textMetrics: Record<string, number>;
}

// Model detail page
export interface ExamData {
  examType: string;
  year: number;
  accuracyMetrics: Record<string, number>;
  textMetrics: Record<string, number>;
}

export interface JudgmentData {
  accuracyMetrics: Record<string, number>;
  textMetrics: Record<string, number>;
}

export interface ModelDetail {
  profile: ModelSummary;
  exams: ExamData[];
  judgments: JudgmentData | null;
}

// ===== Utility types for metric display =====
export interface MetricDisplayInfo {
  key: string;
  label: string;
  isPercentage: boolean;
}

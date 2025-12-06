import { doc, getDoc } from "firebase/firestore";
import { db } from "./firebase";

type FirestoreRecord = Record<string, unknown>;

/**
 * Get a single test result by id.
 *
 * Firestore path:
 * results/{modelName}/exams/{examKey}/responses/{responseId}
 *
 * - modelName: e.g. "gemini-2.5-pro"
 * - examKey: e.g. "adwokacki_radcowy_2024"
 * - responseId: Firestore document id, e.g. "0001"
 */
export async function getTestResultById(
  modelName: string,
  examKey: string,
  responseId: string,
): Promise<(FirestoreRecord & { id: string }) | null> {
  const ref = doc(
    db,
    "results",
    modelName,
    "exams",
    examKey,
    "responses",
    responseId,
  );
  const snap = await getDoc(ref);

  if (!snap.exists()) return null;

  return { id: snap.id, ...(snap.data() as FirestoreRecord) };
}



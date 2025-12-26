import { doc, getDoc } from "firebase/firestore";
import { db } from "./firebase";

type FirestoreRecord = Record<string, unknown>;

/**
 * Get model profile by id.
 *
 * Assumes Firestore structure: models/{modelId}
 * Adjust if your actual structure differs.
 */
export async function getModelProfileById(
  modelId: string,
): Promise<(FirestoreRecord & { id: string }) | null> {
  const ref = doc(db, "models", modelId);
  const snap = await getDoc(ref);

  if (!snap.exists()) return null;

  return { id: snap.id, ...(snap.data() as FirestoreRecord) };

  console.log(snap.data());
}



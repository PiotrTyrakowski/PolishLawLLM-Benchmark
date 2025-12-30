import type { AggregatedModelJudgments } from '@/lib/types';
import DataTableClient from './DataTableClient';

interface JudgmentsTableClientProps {
  initialData: AggregatedModelJudgments[];
}

export default function JudgmentsTableClient({ initialData }: JudgmentsTableClientProps) {
  return (
    <DataTableClient
      initialData={initialData}
      title="Interpretacja Orzecznictwa"
      description="Generatywna identyfikacja zamaskowanych artykułów w treści orzeczeń"
      accuracyGroupLabel="Identyfikacja"
      textGroupLabel="Jakość Generacji Tekstu"
    />
  );
}

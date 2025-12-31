import type { AggregatedModelExams } from '@/lib/types';
import DataTableClient from './DataTableClient';

interface ExamsTableClientProps {
  initialData: AggregatedModelExams[];
}

export default function ExamsTableClient({ initialData }: ExamsTableClientProps) {
  return (
    <DataTableClient
      initialData={initialData}
      title="Egzaminy Zawodowe"
      description="Średnie wyniki wszystkich egzaminów dla każdego modelu."
      accuracyGroupLabel="Decyzja i Wiedza"
      textGroupLabel="Jakość Treści Uzasadnienia"
    />
  );
}

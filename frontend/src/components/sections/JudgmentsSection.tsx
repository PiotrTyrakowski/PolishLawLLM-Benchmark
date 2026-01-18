import { getJudgmentsData } from '@/lib/data/dataProvider';
import JudgmentsTableClient from '@/components/tables/JudgmentsTableClient';

export default async function JudgmentsSection() {
  const data = await getJudgmentsData();

  return (
    <section id="judgments" className="min-w-0">
      <JudgmentsTableClient initialData={data} />
    </section>
  );
}

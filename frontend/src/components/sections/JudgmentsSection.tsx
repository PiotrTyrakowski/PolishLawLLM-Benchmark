import { getJudgmentsData } from '@/lib/data/dataProvider';
import JudgmentsTableClient from '@/components/tables/JudgmentsTableClient';

export default async function JudgmentsSection() {
  const data = await getJudgmentsData();

  return (
    <section id="judgments">
      <JudgmentsTableClient initialData={data} />
    </section>
  );
}

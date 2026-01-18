import { getExamsData } from '@/lib/data/dataProvider';
import ExamsTableClient from '@/components/tables/ExamsTableClient';

export default async function ExamsSection() {
  const data = await getExamsData();

  return (
    <section id="exams" className="min-w-0">
      <ExamsTableClient initialData={data} />
    </section>
  );
}

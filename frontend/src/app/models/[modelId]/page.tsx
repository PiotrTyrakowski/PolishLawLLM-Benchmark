import { Suspense } from 'react';
import { notFound } from 'next/navigation';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import ModelHeroSection from '@/components/sections/ModelHeroSection';
import ModelStatsSection from '@/components/sections/ModelStatsSection';
import {
  getModelData,
  getExamsData,
  getJudgmentsData,
} from '@/lib/data/dataProvider';

interface ModelPageProps {
  params: Promise<{
    modelId: string;
  }>;
}

export async function generateStaticParams() {
  const examsData = await getExamsData();
  const modelIds = [...new Set(examsData.map((e) => e.model.id))];
  return modelIds.map((modelId) => ({ modelId }));
}

// Helper: Calculate average of first accuracy metric for ranking
function getFirstAccuracyMetricAvg(
  data: { accuracyMetrics: Record<string, number> }[]
): number {
  if (data.length === 0) return 0;
  const firstKey = Object.keys(data[0].accuracyMetrics)[0];
  if (!firstKey) return 0;
  const values = data.map((d) => d.accuracyMetrics[firstKey] ?? 0);
  return values.reduce((a, b) => a + b, 0) / values.length;
}

async function ModelContent({ modelId }: { modelId: string }) {
  // Fetch model data and all results in parallel
  const [modelData, allExams, allJudgments] = await Promise.all([
    getModelData(modelId),
    getExamsData(),
    getJudgmentsData(),
  ]);

  if (!modelData) {
    notFound();
  }

  // Calculate exams rank: aggregate by model, sort by avg of first accuracy metric
  const modelExamsMap = new Map<string, { accuracyMetrics: Record<string, number> }[]>();
  for (const exam of allExams) {
    const list = modelExamsMap.get(exam.model.id) || [];
    list.push({ accuracyMetrics: exam.accuracyMetrics });
    modelExamsMap.set(exam.model.id, list);
  }

  const modelExamsAvg = Array.from(modelExamsMap.entries())
    .map(([id, exams]) => ({
      modelId: id,
      avgMetric: getFirstAccuracyMetricAvg(exams),
    }))
    .sort((a, b) => b.avgMetric - a.avgMetric);

  const examsRank =
    modelExamsAvg.findIndex((m) => m.modelId === modelId) + 1 || 1;

  // Calculate judgments rank: sort by first accuracy metric
  const sortedJudgments = [...allJudgments].sort((a, b) => {
    const aKey = Object.keys(a.accuracyMetrics)[0];
    const bKey = Object.keys(b.accuracyMetrics)[0];
    const aVal = aKey ? a.accuracyMetrics[aKey] : 0;
    const bVal = bKey ? b.accuracyMetrics[bKey] : 0;
    return bVal - aVal;
  });
  const judgmentsRank =
    sortedJudgments.findIndex((j) => j.model.id === modelId) + 1 || 1;

  return (
    <>
      <ModelHeroSection
        data={modelData}
        examsRank={examsRank}
        judgmentsRank={judgmentsRank}
      />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 flex-1 w-full">
        <ModelStatsSection data={modelData} />
      </main>
    </>
  );
}

function LoadingSkeleton() {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-slate-500">Ladowanie...</div>
    </div>
  );
}

export default async function ModelPage({ params }: ModelPageProps) {
  const { modelId } = await params;

  return (
    <div className="bg-gray-50 text-gray-800 antialiased min-h-screen flex flex-col">
      <Header />
      <Suspense fallback={<LoadingSkeleton />}>
        <ModelContent modelId={modelId} />
      </Suspense>
      <Footer />
    </div>
  );
}

export async function generateMetadata({ params }: ModelPageProps) {
  const { modelId } = await params;
  const modelData = await getModelData(modelId);

  if (!modelData) {
    return {
      title: 'Model nie znaleziony | PolishLawLLM Benchmark',
    };
  }

  return {
    title: `${modelData.profile.name} | PolishLawLLM Benchmark`,
    description: `Szczegolowe wyniki ${modelData.profile.name} w polskim benchmarku prawniczym.`,
  };
}

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

// Revalidate data every 600 seconds (ISR)
export const revalidate = 600;

interface ModelPageProps {
  params: Promise<{
    modelId: string;
  }>;
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

  // Calculate exams rank: data is already aggregated per model, just sort by first accuracy metric
  const sortedExams = [...allExams].sort((a, b) => {
    const aKey = Object.keys(a.accuracyMetrics)[0];
    const bKey = Object.keys(b.accuracyMetrics)[0];
    const aVal = aKey ? a.accuracyMetrics[aKey] : 0;
    const bVal = bKey ? b.accuracyMetrics[bKey] : 0;
    return bVal - aVal;
  });
  const examsRank =
    sortedExams.findIndex((e) => e.model.id === modelId) + 1 || 1;

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
      <div className="text-slate-500">Ładowanie...</div>
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
    description: `Szczegółowe wyniki ${modelData.profile.name} w polskim benchmarku prawniczym.`,
  };
}

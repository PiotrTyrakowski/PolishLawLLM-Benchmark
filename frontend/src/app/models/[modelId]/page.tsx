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
  const modelIds = [...new Set(examsData.map((e) => e.modelId))];
  return modelIds.map((modelId) => ({ modelId }));
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

  // Calculate exams rank: aggregate by model, sort by avg accuracy
  const modelExamsMap = new Map<string, number[]>();
  for (const exam of allExams) {
    const accuracies = modelExamsMap.get(exam.modelId) || [];
    accuracies.push(exam.accuracy);
    modelExamsMap.set(exam.modelId, accuracies);
  }

  const modelExamsAvg = Array.from(modelExamsMap.entries())
    .map(([id, accuracies]) => ({
      modelId: id,
      avgAccuracy: accuracies.reduce((a, b) => a + b, 0) / accuracies.length,
    }))
    .sort((a, b) => b.avgAccuracy - a.avgAccuracy);

  const examsRank =
    modelExamsAvg.findIndex((m) => m.modelId === modelId) + 1 || 1;

  // Calculate judgments rank: sort by retrieval
  const sortedJudgments = [...allJudgments].sort(
    (a, b) => b.retrieval - a.retrieval
  );
  const judgmentsRank =
    sortedJudgments.findIndex((j) => j.modelId === modelId) + 1 || 1;

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
    description: `Szczegółowe wyniki ${modelData.profile.name} w polskim benchmarku prawniczym. Skuteczność: ${modelData.examsOverall.accuracy.toFixed(1)}%`,
  };
}

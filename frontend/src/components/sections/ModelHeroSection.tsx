import type { ModelDetailData } from '@/lib/types';
import Link from 'next/link';

interface ModelHeroSectionProps {
  data: ModelDetailData;
  examsRank: number;
  judgmentsRank: number;
}

export default function ModelHeroSection({
  data,
  examsRank,
  judgmentsRank,
}: ModelHeroSectionProps) {
  const { profile, examsOverall } = data;

  return (
    <div className="bg-white border-b border-slate-200 pt-8 pb-10 shadow-sm relative overflow-hidden">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full overflow-hidden pointer-events-none opacity-40">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-100 rounded-full mix-blend-multiply filter blur-3xl" />
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-indigo-100 rounded-full mix-blend-multiply filter blur-3xl" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="mb-6">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-indigo-600 transition-colors"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 19l-7-7 7-7"
              />
            </svg>
            Powrót do rankingu
          </Link>
        </div>

        <div className="flex flex-col md:flex-row md:items-start gap-6">
          <div
            className={`h-20 w-20 rounded-2xl ${
              profile.isPolish
                ? 'bg-white border-2 border-amber-200'
                : 'bg-indigo-600'
            } text-white flex items-center justify-center text-2xl font-bold shadow-lg flex-shrink-0`}
          >
            {profile.isPolish ? (
              <span className="text-4xl">🦅</span>
            ) : (
              <span>{profile.name.substring(0, 2).toUpperCase()}</span>
            )}
          </div>

          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-3 mb-2">
              <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight">
                {profile.name}
              </h1>
              {profile.isPolish && (
                <span className="px-2.5 py-1 rounded-md bg-amber-100 text-amber-700 text-xs font-bold border border-amber-200 uppercase">
                  PL Model
                </span>
              )}
            </div>
          </div>

          <div className="flex gap-4 md:gap-6 flex-shrink-0">
            <div className="text-center">
              <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-1">
                Egzaminy
              </div>
              <div className="text-3xl font-bold text-slate-900">
                #{examsRank}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-1">
                Orzecznictwo
              </div>
              <div className="text-3xl font-bold text-slate-900">
                #{judgmentsRank}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-1">
                Skuteczność
              </div>
              <div className="text-3xl font-bold text-indigo-600">
                {examsOverall.accuracy.toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

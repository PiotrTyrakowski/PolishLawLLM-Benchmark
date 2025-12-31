'use client';

import { useMemo } from 'react';
import type { ModelDetail } from '@/lib/types';
import { getMetricLabel, formatMetricValue, extractMetricKeys } from '@/lib/metricConfig';

interface ModelStatsSectionProps {
  data: ModelDetail;
}

function ProgressBar({ value, max = 1, color = 'bg-indigo-600' }: { value: number; max?: number; color?: string }) {
  const percentage = Math.min((value / max) * 100, 100);
  return (
    <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
      <div className={`${color} h-1.5 rounded-full transition-all`} style={{ width: `${percentage}%` }} />
    </div>
  );
}

function StatCard({ label, value, color = 'text-slate-900' }: { label: string; value: number; color?: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>
        {formatMetricValue(value)}
      </div>
      <ProgressBar value={value} />
    </div>
  );
}

export default function ModelStatsSection({ data }: ModelStatsSectionProps) {
  const { profile, exams, judgments } = data;
  const accentColor = profile.isPolish ? 'bg-amber-500' : 'bg-indigo-600';

  // Get the 'all' document for overall stats
  const examsOverall = useMemo(() => {
    const allDoc = exams.find(e => e.examType === 'all');
    return allDoc
      ? { accuracyMetrics: allDoc.accuracyMetrics, textMetrics: allDoc.textMetrics }
      : { accuracyMetrics: {}, textMetrics: {} };
  }, [exams]);

  // Filter out 'all' document for the breakdown table
  const individualExams = useMemo(() => exams.filter(e => e.examType !== 'all'), [exams]);

  const { accuracyKeys: examAccKeys, textKeys: examTextKeys } = useMemo(() => {
    if (!exams) return { accuracyKeys: [], textKeys: [] };
    return extractMetricKeys(exams);
  }, [exams]);

  const { accuracyKeys: judgmentAccKeys, textKeys: judgmentTextKeys } = useMemo(() => {
    if (!judgments) return { accuracyKeys: [], textKeys: [] };
    return extractMetricKeys([judgments]);
  }, [judgments]);

  return (
    <div className="space-y-12">
      {/* Exams Section */}
      <section>
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <span className="bg-indigo-100 text-indigo-700 p-1.5 rounded-md">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </span>
            Egzaminy Zawodowe
          </h2>
          <p className="text-sm text-slate-500 mt-2">
            Wyniki na egzaminach wstępnych na aplikacje prawnicze.
          </p>
        </div>

        {/* Overall stats cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          {examAccKeys.map((key, idx) => (
            <StatCard
              key={`acc-${key}`}
              label={getMetricLabel(key)}
              value={examsOverall.accuracyMetrics[key] ?? 0}
              color={idx === 0 ? 'text-indigo-600' : undefined}
            />
          ))}
          {examTextKeys.map((key) => (
            <StatCard
              key={`text-${key}`}
              label={getMetricLabel(key)}
              value={examsOverall.textMetrics[key] ?? 0}
            />
          ))}
        </div>

        {/* Breakdown table */}
        {individualExams.length > 0 && (
          <div className="bg-white shadow-xl shadow-slate-200/50 rounded-2xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 bg-slate-50 border-b border-slate-200">
              <h3 className="font-semibold text-slate-900">Wyniki wg typu egzaminu i roku</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead>
                  <tr className="bg-slate-50/80">
                    <th scope="col" className="px-6 py-4 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">
                      Typ Egzaminu
                    </th>
                    <th scope="col" className="px-4 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
                      Rok
                    </th>
                    {examAccKeys.map((key, idx) => (
                      <th
                        key={`acc-${key}`}
                        scope="col"
                        className={`px-4 py-4 text-center text-xs font-bold uppercase tracking-wider ${
                          idx === 0 ? 'text-indigo-900 bg-indigo-50/30 border-l border-slate-200' : 'text-slate-500'
                        }`}
                      >
                        {getMetricLabel(key)}
                      </th>
                    ))}
                    {examTextKeys.map((key, idx) => (
                      <th
                        key={`text-${key}`}
                        scope="col"
                        className={`px-4 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider ${
                          idx === 0 ? 'border-l border-slate-200' : ''
                        }`}
                      >
                        {getMetricLabel(key)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-100 text-sm">
                  {individualExams.map((item) => (
                    <tr key={`${item.examType}-${item.year}`} className="hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-900">
                        {item.examType}
                      </td>
                      <td className="px-4 py-4 text-center text-slate-600">
                        {item.year}
                      </td>
                      {examAccKeys.map((key, idx) => (
                        <td
                          key={`acc-${key}`}
                          className={`px-4 py-4 text-center ${
                            idx === 0 ? 'border-l border-slate-200 bg-indigo-50/10' : ''
                          }`}
                        >
                          {idx === 0 ? (
                            <>
                              <div className="font-bold text-slate-900">{formatMetricValue(item.accuracyMetrics[key] ?? 0)}</div>
                              <div className="w-full bg-slate-200 rounded-full h-1 mt-1.5 overflow-hidden">
                                <div className={`${accentColor} h-1 rounded-full`} style={{ width: `${Math.min((item.accuracyMetrics[key] ?? 0) * 100, 100)}%` }} />
                              </div>
                            </>
                          ) : (
                            <span className="text-slate-600">{formatMetricValue(item.accuracyMetrics[key] ?? 0)}</span>
                          )}
                        </td>
                      ))}
                      {examTextKeys.map((key, idx) => (
                        <td
                          key={`text-${key}`}
                          className={`px-4 py-4 text-center text-slate-600 ${
                            idx === 0 ? 'border-l border-slate-200' : ''
                          }`}
                        >
                          {formatMetricValue(item.textMetrics[key] ?? 0)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      {/* Judgments Section */}
      {judgments && (
        <section>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <span className="bg-indigo-100 text-indigo-700 p-1.5 rounded-md">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                </svg>
              </span>
              Interpretacja Orzecznictwa
            </h2>
            <p className="text-sm text-slate-500 mt-2">
              Zdolnosc do identyfikacji zamaskowanych przepisow w tresci uzasadnien sadowych.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {judgmentAccKeys.map((key, idx) => (
              <StatCard
                key={`acc-${key}`}
                label={getMetricLabel(key)}
                value={judgments.accuracyMetrics[key] ?? 0}
                color={idx === 0 ? 'text-indigo-600' : undefined}
              />
            ))}
            {judgmentTextKeys.map((key) => (
              <StatCard
                key={`text-${key}`}
                label={getMetricLabel(key)}
                value={judgments.textMetrics[key] ?? 0}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

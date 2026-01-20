'use client';

import { useState, useMemo } from 'react';
import { ArrowUp, ArrowDown } from '@phosphor-icons/react';
import type { ModelDetail } from '@/lib/types';
import { getMetricLabel, formatMetricValue, extractMetricKeys } from '@/lib/metricConfig';
import { getMetricDescription } from '@/lib/metricDescriptions';
import Tooltip from '@/components/ui/Tooltip';

interface ModelStatsSectionProps {
  data: ModelDetail;
}

function ProgressBar({ value, max = 1, color = 'bg-indigo-600' }: { value: number; max?: number; color?: string }) {
  const percentage = Math.min((value / max) * 100, 100);
  return (
    <div className="w-full bg-slate-200 rounded-full h-1 sm:h-1.5 overflow-hidden">
      <div className={`${color} h-1 sm:h-1.5 rounded-full transition-all`} style={{ width: `${percentage}%` }} />
    </div>
  );
}

function StatCard({ label, value, color = 'text-slate-900', metricKey }: { label: string; value: number; color?: string; metricKey?: string }) {
  return (
    <div className="bg-white rounded-lg sm:rounded-xl border border-slate-200 p-2 sm:p-3 md:p-4 shadow-sm">
      <div className="text-[10px] sm:text-xs uppercase tracking-wider text-slate-500 font-semibold mb-0.5 sm:mb-1 flex items-center gap-1">
        <span className="truncate">{label}</span>
        {metricKey && <Tooltip content={getMetricDescription(metricKey)} />}
      </div>
      <div className={`text-lg sm:text-xl md:text-2xl font-bold ${color}`}>
        {formatMetricValue(value, metricKey)}
      </div>
      <ProgressBar value={value} />
    </div>
  );
}

export default function ModelStatsSection({ data }: ModelStatsSectionProps) {
  const { profile, exams, judgments } = data;
  const accentColor = profile.isPolish ? 'bg-amber-500' : 'bg-indigo-600';

  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortAsc, setSortAsc] = useState(false);

  const examsOverall = useMemo(() => {
    const allDoc = exams.find(e => e.examType === 'all');
    return allDoc
      ? { accuracyMetrics: allDoc.accuracyMetrics, textMetrics: allDoc.textMetrics }
      : { accuracyMetrics: {}, textMetrics: {} };
  }, [exams]);

  const individualExams = useMemo(() => exams.filter(e => e.examType !== 'all'), [exams]);

  const { accuracyKeys: examAccKeys, textKeys: examTextKeys } = useMemo(() => {
    if (!exams) return { accuracyKeys: [], textKeys: [] };
    return extractMetricKeys(exams);
  }, [exams]);

  const { accuracyKeys: judgmentAccKeys, textKeys: judgmentTextKeys } = useMemo(() => {
    if (!judgments) return { accuracyKeys: [], textKeys: [] };
    return extractMetricKeys([judgments]);
  }, [judgments]);

  const sortedExams = useMemo(() => {
    if (!sortKey) return individualExams;

    return [...individualExams].sort((a, b) => {
      let aVal: number | string;
      let bVal: number | string;

      if (sortKey === 'examType') {
        aVal = a.examType;
        bVal = b.examType;
        return sortAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      } else if (sortKey === 'year') {
        aVal = a.year ?? 0;
        bVal = b.year ?? 0;
      } else {
        aVal = a.accuracyMetrics[sortKey] ?? a.textMetrics[sortKey] ?? 0;
        bVal = b.accuracyMetrics[sortKey] ?? b.textMetrics[sortKey] ?? 0;
      }
      return sortAsc ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
    });
  }, [individualExams, sortKey, sortAsc]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(false);
    }
  };

  return (
    <div className="space-y-8 sm:space-y-12">
      {/* Judgments Section */}
      {judgments && (
        <section>
          <div className="mb-4 sm:mb-6">
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 flex items-center gap-2">
              <span className="bg-indigo-100 text-indigo-700 p-1 sm:p-1.5 rounded-md">
                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
                </svg>
              </span>
              Interpretacja Orzecznictwa
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-1.5 sm:mt-2">
              Zdolność do identyfikacji zamaskowanych przepisów w treści uzasadnień sądowych.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 sm:gap-3 md:gap-4">
            {judgmentAccKeys.map((key, idx) => (
              <StatCard
                key={`acc-${key}`}
                label={getMetricLabel(key)}
                value={judgments.accuracyMetrics[key] ?? 0}
                color={idx === 0 ? 'text-indigo-600' : undefined}
                metricKey={key}
              />
            ))}
            {judgmentTextKeys.map((key) => (
              <StatCard
                key={`text-${key}`}
                label={getMetricLabel(key)}
                value={judgments.textMetrics[key] ?? 0}
                metricKey={key}
              />
            ))}
          </div>
        </section>
      )}

      {/* Exams Section */}
      <section>
        <div className="mb-4 sm:mb-6">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 flex items-center gap-2">
            <span className="bg-indigo-100 text-indigo-700 p-1 sm:p-1.5 rounded-md">
              <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </span>
            Egzaminy Zawodowe
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-1.5 sm:mt-2">
            Wyniki na egzaminach wstępnych na aplikacje prawnicze.
          </p>
        </div>

        {/* Overall stats cards */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 sm:gap-3 md:gap-4 mb-6 sm:mb-8">
          {examAccKeys.map((key, idx) => (
            <StatCard
              key={`acc-${key}`}
              label={getMetricLabel(key)}
              value={examsOverall.accuracyMetrics[key] ?? 0}
              color={idx === 0 ? 'text-indigo-600' : undefined}
              metricKey={key}
            />
          ))}
          {examTextKeys.map((key) => (
            <StatCard
              key={`text-${key}`}
              label={getMetricLabel(key)}
              value={examsOverall.textMetrics[key] ?? 0}
              metricKey={key}
            />
          ))}
        </div>

        {/* Breakdown table */}
        {individualExams.length > 0 && (
          <div className="bg-white shadow-xl shadow-slate-200/50 rounded-xl sm:rounded-2xl border border-slate-200 overflow-hidden">
            <div className="px-3 sm:px-6 py-3 sm:py-4 bg-slate-50 border-b border-slate-200">
              <h3 className="font-semibold text-sm sm:text-base text-slate-900">Wyniki wg typu egzaminu i roku</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead>
                  <tr className="bg-slate-50/80">
                    <th
                      scope="col"
                      className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 md:py-4 text-left text-[10px] sm:text-xs font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100"
                      onClick={() => handleSort('examType')}
                    >
                      <span className="inline-flex items-center gap-0.5 sm:gap-1">
                        Typ Egzaminu
                        {sortKey === 'examType' ? (
                          sortAsc ? <ArrowUp size={14} weight="bold" className="text-indigo-600" /> : <ArrowDown size={14} weight="bold" className="text-indigo-600" />
                        ) : (
                          <ArrowDown size={14} className="text-slate-300" />
                        )}
                      </span>
                    </th>
                    <th
                      scope="col"
                      className="px-2 sm:px-4 py-2 sm:py-3 md:py-4 text-center text-[10px] sm:text-xs font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-slate-100"
                      onClick={() => handleSort('year')}
                    >
                      <span className="inline-flex items-center gap-0.5 sm:gap-1">
                        Rok
                        {sortKey === 'year' ? (
                          sortAsc ? <ArrowUp size={14} weight="bold" className="text-indigo-600" /> : <ArrowDown size={14} weight="bold" className="text-indigo-600" />
                        ) : (
                          <ArrowDown size={14} className="text-slate-300" />
                        )}
                      </span>
                    </th>
                    {examAccKeys.map((key, idx) => (
                      <th
                        key={`acc-${key}`}
                        scope="col"
                        className={`px-2 sm:px-4 py-2 sm:py-3 md:py-4 text-center text-[10px] sm:text-xs font-bold uppercase tracking-wider whitespace-nowrap cursor-pointer hover:bg-slate-100 ${
                          idx === 0 ? 'text-indigo-900 bg-indigo-50/30 border-l border-slate-200' : 'text-slate-500'
                        }`}
                        onClick={() => handleSort(key)}
                      >
                        <span className="inline-flex items-center gap-0.5 sm:gap-1">
                          {getMetricLabel(key)}
                          {sortKey === key ? (
                            sortAsc ? <ArrowUp size={14} weight="bold" className="text-indigo-600" /> : <ArrowDown size={14} weight="bold" className="text-indigo-600" />
                          ) : (
                            <ArrowDown size={14} className="text-slate-300" />
                          )}
                          <Tooltip content={getMetricDescription(key)} />
                        </span>
                      </th>
                    ))}
                    {examTextKeys.map((key, idx) => (
                      <th
                        key={`text-${key}`}
                        scope="col"
                        className={`px-2 sm:px-4 py-2 sm:py-3 md:py-4 text-center text-[10px] sm:text-xs font-bold text-slate-500 uppercase tracking-wider whitespace-nowrap cursor-pointer hover:bg-slate-100 ${
                          idx === 0 ? 'border-l border-slate-200' : ''
                        }`}
                        onClick={() => handleSort(key)}
                      >
                        <span className="inline-flex items-center gap-0.5 sm:gap-1">
                          {getMetricLabel(key)}
                          {sortKey === key ? (
                            sortAsc ? <ArrowUp size={14} weight="bold" className="text-indigo-600" /> : <ArrowDown size={14} weight="bold" className="text-indigo-600" />
                          ) : (
                            <ArrowDown size={14} className="text-slate-300" />
                          )}
                          <Tooltip content={getMetricDescription(key)} />
                        </span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-100 text-xs sm:text-sm">
                  {sortedExams.map((item) => (
                    <tr key={`${item.examType}-${item.year}`} className="hover:bg-slate-50 transition-colors">
                      <td className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 md:py-4 font-medium text-slate-900 text-xs sm:text-sm whitespace-nowrap">
                        {item.examType}
                      </td>
                      <td className="px-2 sm:px-4 py-2 sm:py-3 md:py-4 text-center text-slate-600">
                        {item.year}
                      </td>
                      {examAccKeys.map((key, idx) => (
                        <td
                          key={`acc-${key}`}
                          className={`px-2 sm:px-4 py-2 sm:py-3 md:py-4 text-center ${
                            idx === 0 ? 'border-l border-slate-200 bg-indigo-50/10' : ''
                          }`}
                        >
                          {idx === 0 ? (
                            <>
                              <div className="font-bold text-slate-900 text-xs sm:text-sm">{formatMetricValue(item.accuracyMetrics[key] ?? 0, key)}</div>
                              <div className="w-full bg-slate-200 rounded-full h-0.5 sm:h-1 mt-1 sm:mt-1.5 overflow-hidden">
                                <div className={`${accentColor} h-0.5 sm:h-1 rounded-full`} style={{ width: `${Math.min((item.accuracyMetrics[key] ?? 0) * 100, 100)}%` }} />
                              </div>
                            </>
                          ) : (
                            <span className="text-slate-600">{formatMetricValue(item.accuracyMetrics[key] ?? 0, key)}</span>
                          )}
                        </td>
                      ))}
                      {examTextKeys.map((key, idx) => (
                        <td
                          key={`text-${key}`}
                          className={`px-2 sm:px-4 py-2 sm:py-3 md:py-4 text-center text-slate-600 ${
                            idx === 0 ? 'border-l border-slate-200' : ''
                          }`}
                        >
                          {formatMetricValue(item.textMetrics[key] ?? 0, key)}
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
    </div>
  );
}

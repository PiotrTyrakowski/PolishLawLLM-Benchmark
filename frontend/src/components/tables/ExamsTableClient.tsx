'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import type { AggregatedModelExams } from '@/lib/types';
import { getMetricLabel, formatMetricValue, extractMetricKeys } from '@/lib/metricConfig';

interface ExamsTableClientProps {
  initialData: AggregatedModelExams[];
}

export default function ExamsTableClient({ initialData }: ExamsTableClientProps) {
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortAsc, setSortAsc] = useState(false);

  // Extract all metric keys dynamically from the data
  const { accuracyKeys, textKeys } = useMemo(
    () => extractMetricKeys(initialData),
    [initialData]
  );

  // Set default sort key to first accuracy metric if not set
  const effectiveSortKey = sortKey ?? accuracyKeys[0] ?? null;

  // Sort data
  const sorted = useMemo(() => {
    if (!effectiveSortKey) return initialData;

    return [...initialData].sort((a, b) => {
      const aVal = a.accuracyMetrics[effectiveSortKey] ?? a.textMetrics[effectiveSortKey] ?? 0;
      const bVal = b.accuracyMetrics[effectiveSortKey] ?? b.textMetrics[effectiveSortKey] ?? 0;
      return sortAsc ? aVal - bVal : bVal - aVal;
    });
  }, [initialData, effectiveSortKey, sortAsc]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(false);
    }
  };

  return (
    <>
      <div className="mb-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              Egzaminy Zawodowe
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Średnie wyniki wszystkich egzaminów dla każdego modelu.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              {/* Group header row */}
              <tr className="bg-gray-50 text-xs font-bold text-gray-500 uppercase tracking-wider text-center">
                <th scope="col" className="px-6 py-3 text-left w-16 bg-gray-50" rowSpan={2}>
                  #
                </th>
                <th scope="col" className="px-6 py-3 text-left bg-gray-50" rowSpan={2}>
                  Model
                </th>
                {accuracyKeys.length > 0 && (
                  <th
                    colSpan={accuracyKeys.length}
                    className="px-4 py-2 border-b border-gray-200 border-l-2 border-l-gray-200"
                  >
                    Decyzja i Wiedza
                  </th>
                )}
                {textKeys.length > 0 && (
                  <th
                    colSpan={textKeys.length}
                    className="px-4 py-2 border-b border-gray-200 border-l-2 border-l-gray-200"
                  >
                    Jakosc Tresci Uzasadnienia
                  </th>
                )}
              </tr>
              {/* Metric header row */}
              <tr className="bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider text-center">
                {accuracyKeys.map((key, idx) => (
                  <th
                    key={`acc-${key}`}
                    scope="col"
                    className={`px-4 py-2 cursor-pointer hover:bg-gray-100 ${
                      idx === 0 ? 'border-l-2 border-l-gray-200' : ''
                    }`}
                    onClick={() => handleSort(key)}
                  >
                    {getMetricLabel(key)}
                    {effectiveSortKey === key && (sortAsc ? ' ↑' : ' ↓')}
                  </th>
                ))}
                {textKeys.map((key, idx) => (
                  <th
                    key={`text-${key}`}
                    scope="col"
                    className={`px-4 py-2 cursor-pointer hover:bg-gray-100 ${
                      idx === 0 ? 'border-l-2 border-l-gray-200' : ''
                    }`}
                    onClick={() => handleSort(key)}
                  >
                    {getMetricLabel(key)}
                    {effectiveSortKey === key && (sortAsc ? ' ↑' : ' ↓')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200 text-sm">
              {sorted.map((item, index) => (
                <tr
                  key={item.model.id}
                  className={`hover:bg-gray-50 transition-colors ${
                    item.model.isPolish ? 'bg-red-50/20 hover:bg-red-50/40' : ''
                  }`}
                >
                  <td className="px-6 py-4 text-gray-400 font-medium">{index + 1}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <Link
                        href={`/models/${item.model.id}`}
                        className="font-semibold text-gray-900 hover:text-indigo-600 transition-colors"
                      >
                        {item.model.name}
                      </Link>
                      {item.model.isPolish && (
                        <span className="ml-2" title="Polski Model">
                          PL
                        </span>
                      )}
                    </div>
                  </td>
                  {accuracyKeys.map((key, idx) => (
                    <td
                      key={`acc-${key}`}
                      className={`px-4 py-4 text-center ${
                        idx === 0
                          ? 'border-l-2 border-l-gray-200 font-medium text-gray-900'
                          : 'text-gray-600'
                      }`}
                    >
                      {formatMetricValue(item.accuracyMetrics[key] ?? 0)}
                    </td>
                  ))}
                  {textKeys.map((key, idx) => (
                    <td
                      key={`text-${key}`}
                      className={`px-4 py-4 text-center ${
                        idx === 0 ? 'border-l-2 border-l-gray-200' : ''
                      } text-gray-600`}
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
    </>
  );
}

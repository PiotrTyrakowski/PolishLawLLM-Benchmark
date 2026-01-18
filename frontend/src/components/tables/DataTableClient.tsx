'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import type { ModelSummary } from '@/lib/types';
import { getMetricLabel, formatMetricValue, extractMetricKeys } from '@/lib/metricConfig';
import { getMetricDescription } from '@/lib/metricDescriptions';
import Tooltip from '@/components/ui/Tooltip';

interface DataItem {
  model: ModelSummary;
  accuracyMetrics: Record<string, number>;
  textMetrics: Record<string, number>;
}

interface DataTableClientProps {
  initialData: DataItem[];
  title: string;
  description: string;
  accuracyGroupLabel: string;
  textGroupLabel: string;
}

export default function DataTableClient({
  initialData,
  title,
  description,
  accuracyGroupLabel,
  textGroupLabel,
}: DataTableClientProps) {
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
    <div className="min-w-0">
      <div className="mb-4 sm:mb-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-2 sm:gap-4">
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 flex items-center gap-2">
              {title}
            </h2>
            <p className="text-xs sm:text-sm text-gray-500 mt-1">
              {description}
            </p>
          </div>
        </div>
      </div>

      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 -webkit-overflow-scrolling-touch">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              {/* Group header row */}
              <tr className="bg-gray-50 text-[10px] sm:text-xs font-bold text-gray-500 uppercase tracking-wider text-center">
                <th scope="col" className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 text-left w-10 sm:w-16 bg-gray-50" rowSpan={2}>
                  #
                </th>
                <th scope="col" className="px-2 sm:px-4 md:px-6 py-2 sm:py-3 text-left bg-gray-50 min-w-[100px] sm:min-w-[180px]" rowSpan={2}>
                  Model
                </th>
                {accuracyKeys.length > 0 && (
                  <th
                    colSpan={accuracyKeys.length}
                    className="px-2 sm:px-4 py-1.5 sm:py-2 border-b border-gray-200 border-l-2 border-l-gray-200"
                  >
                    {accuracyGroupLabel}
                  </th>
                )}
                {textKeys.length > 0 && (
                  <th
                    colSpan={textKeys.length}
                    className="px-2 sm:px-4 py-1.5 sm:py-2 border-b border-gray-200 border-l-2 border-l-gray-200"
                  >
                    {textGroupLabel}
                  </th>
                )}
              </tr>
              {/* Metric header row */}
              <tr className="bg-gray-50 text-[10px] sm:text-xs font-medium text-gray-500 uppercase tracking-wider text-center">
                {accuracyKeys.map((key, idx) => (
                  <th
                    key={`acc-${key}`}
                    scope="col"
                    className={`px-2 sm:px-4 py-1.5 sm:py-2 cursor-pointer hover:bg-gray-100 whitespace-nowrap ${
                      idx === 0 ? 'border-l-2 border-l-gray-200' : ''
                    }`}
                    onClick={() => handleSort(key)}
                  >
                    <span className="inline-flex items-center gap-0.5 sm:gap-1.5">
                      {getMetricLabel(key)}
                      {effectiveSortKey === key && (sortAsc ? ' ↑' : ' ↓')}
                      <Tooltip content={getMetricDescription(key)} />
                    </span>
                  </th>
                ))}
                {textKeys.map((key, idx) => (
                  <th
                    key={`text-${key}`}
                    scope="col"
                    className={`px-2 sm:px-4 py-1.5 sm:py-2 cursor-pointer hover:bg-gray-100 whitespace-nowrap ${
                      idx === 0 ? 'border-l-2 border-l-gray-200' : ''
                    }`}
                    onClick={() => handleSort(key)}
                  >
                    <span className="inline-flex items-center gap-0.5 sm:gap-1.5">
                      {getMetricLabel(key)}
                      {effectiveSortKey === key && (sortAsc ? ' ↑' : ' ↓')}
                      <Tooltip content={getMetricDescription(key)} />
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200 text-xs sm:text-sm">
              {sorted.map((item, index) => (
                <tr
                  key={item.model.id}
                  className={`hover:bg-gray-50 transition-colors ${
                    item.model.isPolish ? 'bg-amber-50/30 hover:bg-amber-50/50' : ''
                  }`}
                >
                  <td className="px-2 sm:px-4 md:px-6 py-2 sm:py-4 text-gray-400 font-medium">{index + 1}</td>
                  <td className="px-2 sm:px-4 md:px-6 py-2 sm:py-4">
                    <div className="flex items-center">
                      <Link
                        href={`/models/${item.model.id}`}
                        className="font-semibold text-gray-900 hover:text-indigo-600 transition-colors text-xs sm:text-sm"
                      >
                        {item.model.name}
                      </Link>
                      {item.model.isPolish && (
                        <span className="ml-1 sm:ml-2 text-[10px] sm:text-xs" title="Polski Model">
                          PL
                        </span>
                      )}
                    </div>
                  </td>
                  {accuracyKeys.map((key, idx) => (
                    <td
                      key={`acc-${key}`}
                      className={`px-2 sm:px-4 py-2 sm:py-4 text-center whitespace-nowrap ${
                        idx === 0
                          ? 'border-l-2 border-l-gray-200 font-medium text-gray-900'
                          : 'text-gray-600'
                      }`}
                    >
                      {formatMetricValue(item.accuracyMetrics[key] ?? 0, key)}
                    </td>
                  ))}
                  {textKeys.map((key, idx) => (
                    <td
                      key={`text-${key}`}
                      className={`px-2 sm:px-4 py-2 sm:py-4 text-center whitespace-nowrap ${
                        idx === 0 ? 'border-l-2 border-l-gray-200' : ''
                      } text-gray-600`}
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
    </div>
  );
}

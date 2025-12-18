'use client';

import { useState } from 'react';
import Link from 'next/link';
import type { ExamResult } from '@/lib/types';
import TableFilters from './TableFilters';

interface ExamsTableClientProps {
  initialData: ExamResult[];
}

export default function ExamsTableClient({
  initialData,
}: ExamsTableClientProps) {
  const [year, setYear] = useState('all');
  const [examType, setExamType] = useState('all');

  // Sort by accuracy descending and calculate ranks
  const sorted = [...initialData].sort((a, b) => b.accuracy - a.accuracy);

  const filtered = sorted.filter((item) => {
    if (year !== 'all' && item.year !== year) return false;
    if (examType !== 'all' && item.examType !== examType) return false;
    return true;
  });

  return (
    <>
      <div className="mb-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              Egzaminy Zawodowe
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              Testy wyboru (A/B/C) oraz weryfikacja cytowanej podstawy prawnej.
            </p>
            <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
              <svg
                className="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>
                Oficjalny próg zdawalności egzaminu wstępnego wynosi ok. 66%
                (100/150 pkt).
              </span>
            </div>
          </div>

          <TableFilters
            year={year}
            setYear={setYear}
            examType={examType}
            setExamType={setExamType}
          />
        </div>
      </div>

      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr className="bg-gray-50 text-xs font-bold text-gray-500 uppercase tracking-wider text-center">
                <th
                  scope="col"
                  className="px-6 py-3 text-left w-16 bg-gray-50"
                  rowSpan={2}
                >
                  #
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left bg-gray-50"
                  rowSpan={2}
                >
                  Model
                </th>
                <th
                  colSpan={2}
                  className="px-4 py-2 border-b border-gray-200 border-l-2 border-l-gray-200"
                >
                  Decyzja i Wiedza
                </th>
                <th
                  colSpan={3}
                  className="px-4 py-2 border-b border-gray-200 border-l-2 border-l-gray-200"
                >
                  Jakość Treści Uzasadnienia
                </th>
              </tr>
              <tr className="bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider text-center">
                <th
                  scope="col"
                  className="px-4 py-2 border-l-2 border-l-gray-200"
                  title="Procent poprawnych odpowiedzi A/B/C"
                >
                  Skuteczność (ABC)
                </th>
                <th
                  scope="col"
                  className="px-4 py-2"
                  title="Czy model wskazał poprawny artykuł"
                >
                  Trafność Przepisu
                </th>
                <th
                  scope="col"
                  className="px-4 py-2 border-l-2 border-l-gray-200"
                  title="Exact Match"
                >
                  Exact Match
                </th>
                <th scope="col" className="px-4 py-2" title="BLEU Score">
                  BLEU
                </th>
                <th scope="col" className="px-4 py-2" title="Weighted BLEU">
                  W-BLEU
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200 text-sm">
              {filtered.map((item, index) => (
                <tr
                  key={`${item.modelId}-${item.examType}-${item.year}`}
                  className={`hover:bg-gray-50 transition-colors ${
                    item.isPolish ? 'bg-red-50/20 hover:bg-red-50/40' : ''
                  }`}
                >
                  <td className="px-6 py-4 text-gray-400 font-medium">
                    {index + 1}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <Link
                        href={`/models/${item.modelId}`}
                        className="font-semibold text-gray-900 hover:text-indigo-600 transition-colors"
                      >
                        {item.model}
                      </Link>
                      {item.isPolish && (
                        <span className="ml-2" title="Polski Model">
                          🇵🇱
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 text-center border-l-2 border-l-gray-200 font-medium text-gray-900">
                    {item.accuracy}%
                  </td>
                  <td className="px-4 py-4 text-center text-gray-600">
                    {item.lawAccuracy}%
                  </td>
                  <td className="px-4 py-4 text-center border-l-2 border-l-gray-200 text-gray-600">
                    {item.exactMatch}%
                  </td>
                  <td className="px-4 py-4 text-center text-gray-600">
                    {item.bleu}
                  </td>
                  <td className="px-4 py-4 text-center text-gray-600">
                    {item.wBleu}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

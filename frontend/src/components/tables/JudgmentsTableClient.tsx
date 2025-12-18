'use client';

import Link from 'next/link';
import type { JudgmentResult } from '@/lib/types';

interface JudgmentsTableClientProps {
  initialData: JudgmentResult[];
}

export default function JudgmentsTableClient({
  initialData,
}: JudgmentsTableClientProps) {
  // Sort by retrieval descending
  const sorted = [...initialData].sort((a, b) => b.retrieval - a.retrieval);

  return (
    <>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          Interpretacja Orzecznictwa
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          Generatywna identyfikacja zamaskowanych artykułów w treści orzeczeń.
        </p>
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
                  scope="col"
                  className="px-4 py-2 border-b border-gray-200 border-l-2 border-l-gray-200"
                  rowSpan={2}
                >
                  Identyfikacja (Retrieval)
                </th>
                <th
                  colSpan={3}
                  className="px-4 py-2 border-b border-gray-200 border-l-2 border-l-gray-200"
                >
                  Jakość Generacji Tekstu
                </th>
              </tr>
              <tr className="bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider text-center">
                <th
                  scope="col"
                  className="px-4 py-2 border-l-2 border-l-gray-200"
                >
                  Exact Match
                </th>
                <th scope="col" className="px-4 py-2">
                  BLEU
                </th>
                <th scope="col" className="px-4 py-2">
                  W-BLEU
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200 text-sm">
              {sorted.map((item, index) => (
                <tr
                  key={item.modelId}
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
                    {item.retrieval}%
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

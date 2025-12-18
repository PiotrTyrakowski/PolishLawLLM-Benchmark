import type { ModelDetailData } from '@/lib/types';

interface ModelStatsSectionProps {
  data: ModelDetailData;
}

function ProgressBar({ value, max = 100, color = 'bg-indigo-600' }: { value: number; max?: number; color?: string }) {
  const percentage = (value / max) * 100;
  return (
    <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
      <div className={`${color} h-1.5 rounded-full transition-all`} style={{ width: `${percentage}%` }} />
    </div>
  );
}

function StatCard({ label, value, suffix = '%', color = 'text-slate-900' }: { label: string; value: number; suffix?: string; color?: string }) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
      <div className="text-xs uppercase tracking-wider text-slate-500 font-semibold mb-1">{label}</div>
      <div className={`text-2xl font-bold ${color}`}>
        {value}{suffix}
      </div>
      <ProgressBar value={value} />
    </div>
  );
}

export default function ModelStatsSection({ data }: ModelStatsSectionProps) {
  const { profile, examsOverall, examsBreakdown, judgmentsOverall } = data;
  const accentColor = profile.isPolish ? 'bg-amber-500' : 'bg-indigo-600';

  return (
    <div className="space-y-12">
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
            Wyniki na egzaminach wstępnych na aplikacje prawnicze. Próg zdawalności: 66%.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <StatCard label="Skuteczność (ABC)" value={examsOverall.accuracy} color="text-indigo-600" />
          <StatCard label="Trafność Przepisu" value={examsOverall.lawAccuracy} />
          <StatCard label="Exact Match" value={examsOverall.exactMatch} />
          <StatCard label="BLEU" value={examsOverall.bleu} suffix="" />
          <StatCard label="W-BLEU" value={examsOverall.wBleu} suffix="" />
        </div>

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
                  <th scope="col" className="px-4 py-4 text-center text-xs font-bold text-indigo-900 uppercase tracking-wider bg-indigo-50/30 border-l border-slate-200">
                    Skuteczność
                  </th>
                  <th scope="col" className="px-4 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
                    Trafność Przepisu
                  </th>
                  <th scope="col" className="px-4 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider border-l border-slate-200">
                    Exact Match
                  </th>
                  <th scope="col" className="px-4 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
                    BLEU
                  </th>
                  <th scope="col" className="px-4 py-4 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">
                    W-BLEU
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-100 text-sm">
                {examsBreakdown.map((item) => (
                  <tr key={`${item.examType}-${item.year}`} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-900">
                      {item.examType}
                    </td>
                    <td className="px-4 py-4 text-center text-slate-600">
                      {item.year}
                    </td>
                    <td className="px-4 py-4 text-center border-l border-slate-200 bg-indigo-50/10">
                      <div className="font-bold text-slate-900">{item.accuracy}%</div>
                      <div className="w-full bg-slate-200 rounded-full h-1 mt-1.5 overflow-hidden">
                        <div className={`${accentColor} h-1 rounded-full`} style={{ width: `${item.accuracy}%` }} />
                      </div>
                    </td>
                    <td className="px-4 py-4 text-center text-slate-600">
                      {item.lawAccuracy}%
                    </td>
                    <td className="px-4 py-4 text-center text-slate-600 border-l border-slate-200">
                      {item.exactMatch}%
                    </td>
                    <td className="px-4 py-4 text-center text-slate-600 font-mono">
                      {item.bleu}
                    </td>
                    <td className="px-4 py-4 text-center text-slate-600 font-mono">
                      {item.wBleu}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

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
            Zdolność do identyfikacji zamaskowanych przepisów w treści uzasadnień sądowych (Retrieval + Generation).
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Skuteczność (RAG)" value={judgmentsOverall.retrieval} color="text-indigo-600" />
          <StatCard label="Exact Match" value={judgmentsOverall.exactMatch} />
          <StatCard label="BLEU" value={judgmentsOverall.bleu} suffix="" />
          <StatCard label="W-BLEU" value={judgmentsOverall.wBleu} suffix="" />
        </div>
      </section>
    </div>
  );
}

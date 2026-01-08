import Link from 'next/link';
import { Scales, Exam, FileText, ArrowRight } from '@phosphor-icons/react/dist/ssr';

export default function AboutSection() {
  return (
    <section className="py-12 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-3 gap-6">
          {/* Card 1: O benchmarku */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
              <Scales size={24} className="text-indigo-600" weight="duotone" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              Cel projektu
            </h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              Obiektywna ocena możliwości modeli AI w dziedzinie polskiego prawa.
              Weryfikujemy nie tylko poprawność odpowiedzi, ale także zdolność do
              wskazania podstawy prawnej i dokładnego przytoczenia przepisów.
            </p>
          </div>

          {/* Card 2: Test egzaminów */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
              <Exam size={24} className="text-emerald-600" weight="duotone" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              Test egzaminów prawniczych
            </h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              Modele odpowiadają na pytania z oficjalnych egzaminów na aplikacje
              prawnicze (adwokacka, radcowska, notarialna, komornicza). Oceniamy
              poprawność odpowiedzi, identyfikację artykułu i dokładność cytowania.
            </p>
          </div>

          {/* Card 3: Test orzeczeń */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow">
            <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center mb-4">
              <FileText size={24} className="text-amber-600" weight="duotone" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900 mb-2">
              Test orzeczeń sądowych
            </h3>
            <p className="text-gray-600 text-sm leading-relaxed">
              W uzasadnieniach orzeczeń sądowych maskujemy przepisy prawne. Model
              musi na podstawie kontekstu zidentyfikować zamaskowany artykuł
              i przytoczyć jego dokładną treść.
            </p>
          </div>
        </div>

        <div className="text-center mt-8">
          <Link
            href="/about"
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium transition-colors"
          >
            Dowiedz się więcej o metodologii
            <ArrowRight size={18} weight="bold" />
          </Link>
        </div>
      </div>
    </section>
  );
}

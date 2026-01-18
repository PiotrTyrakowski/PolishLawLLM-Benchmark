import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import Link from 'next/link';
import { ArrowLeft, Scales, Exam, FileText, ChartLine, Books } from '@phosphor-icons/react/dist/ssr';

export const metadata = {
  title: 'O benchmarku | PolishLawLLM Benchmark',
  description: 'Szczegółowa dokumentacja metodologii PolishLawLLM Benchmark - testowanie modeli językowych w zakresie polskiego prawa.',
};

export default function AboutPage() {
  return (
    <div className="bg-gray-50 text-gray-800 antialiased min-h-screen flex flex-col overflow-x-hidden">
      <Header />

      {/* Hero */}
      <div className="bg-white border-b border-gray-200 py-8 sm:py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm text-slate-500 hover:text-indigo-600 transition-colors mb-4 sm:mb-6"
          >
            <ArrowLeft size={14} className="sm:hidden" weight="bold" />
            <ArrowLeft size={16} className="hidden sm:block" weight="bold" />
            Powrót do rankingu
          </Link>

        </div>
      </div>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 sm:py-12 flex-1">
        <div className="space-y-10 sm:space-y-16">

          {/* Wprowadzenie */}
          <section>
            <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                <Scales size={18} className="text-indigo-600 sm:hidden" weight="duotone" />
                <Scales size={22} className="text-indigo-600 hidden sm:block" weight="duotone" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Cel projektu</h2>
            </div>
            <div className="space-y-4">
              <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                PolishLawLLM Benchmark to projekt badawczy mający na celu obiektywną ocenę
                możliwości dużych modeli językowych (LLM) w dziedzinie polskiego prawa.
                W ramach benchmarku przeprowadzamy dwa komplementarne testy:
              </p>
              <div className="grid gap-3 sm:gap-4">
                <div className="flex gap-3 items-start">
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2 flex-shrink-0"></div>
                  <p className="text-slate-700 text-sm sm:text-base">
                    <span className="font-semibold text-slate-900">Test egzaminów prawniczych</span>
                    <span className="text-slate-500"> - </span>
                    bazujący na oficjalnych pytaniach z egzaminów na aplikacje prawnicze
                  </p>
                </div>
                <div className="flex gap-3 items-start">
                  <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-2 flex-shrink-0"></div>
                  <p className="text-slate-700 text-sm sm:text-base">
                    <span className="font-semibold text-slate-900">Test orzeczeń sądowych</span>
                    <span className="text-slate-500"> - </span>
                    weryfikujący zdolność do identyfikacji przepisów w kontekście uzasadnień sądowych
                  </p>
                </div>
              </div>
              <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                W obu testach modele są proszone o przytoczenie dokładnej treści przepisów prawnych,
                co pozwala ocenić nie tylko znajomość prawa, ale także dokładność generowanego tekstu.
              </p>
            </div>
          </section>

          {/* Test egzaminów */}
          <section>
            <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                <Exam size={18} className="text-emerald-600 sm:hidden" weight="duotone" />
                <Exam size={22} className="text-emerald-600 hidden sm:block" weight="duotone" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Test egzaminów prawniczych</h2>
            </div>
            <div className="space-y-6">
              {/* Charakterystyka */}
              <div className="space-y-3">
                <h3 className="text-base sm:text-lg font-semibold text-slate-800">Charakterystyka egzaminów</h3>
                <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                  Egzaminy na aplikację prawniczą są kluczowym elementem rekrutacji do odbycia
                  aplikacji przygotowującej do wykonywania zawodu prawniczego. W Polsce występują
                  trzy rodzaje takich egzaminów:
                </p>
                <div className="grid gap-2 pl-1">
                  <div className="flex gap-3 items-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"></div>
                    <span className="text-slate-700 text-sm sm:text-base">Egzamin na aplikację adwokacką i radcowską</span>
                  </div>
                  <div className="flex gap-3 items-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"></div>
                    <span className="text-slate-700 text-sm sm:text-base">Egzamin na aplikację notarialną</span>
                  </div>
                  <div className="flex gap-3 items-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0"></div>
                    <span className="text-slate-700 text-sm sm:text-base">Egzamin na aplikację komorniczą</span>
                  </div>
                </div>
                <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                  Każdy egzamin ma formę testu jednokrotnego wyboru z 3 możliwymi odpowiedziami.
                  Pytania odnoszą się do przepisów obowiązujących na dzień ogłoszenia wykazu
                  tytułów aktów prawnych przez Ministra Sprawiedliwości.
                </p>
              </div>

              {/* Metodologia */}
              <div className="space-y-3">
                <h3 className="text-base sm:text-lg font-semibold text-slate-800">Metodologia testu</h3>
                <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                  Test polega na zadawaniu modelom pytań zamkniętych z egzaminów i weryfikacji
                  trzech aspektów odpowiedzi:
                </p>
                <div className="grid gap-3 pl-1">
                  <div className="flex gap-3 items-start">
                    <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 text-xs font-semibold flex items-center justify-center flex-shrink-0">1</span>
                    <p className="text-slate-700 text-sm sm:text-base">
                      <span className="font-semibold text-slate-900">Poprawność odpowiedzi</span>
                      <span className="text-slate-500"> - </span>
                      oceniana binarnie (1 punkt za poprawną, 0 za niepoprawną)
                    </p>
                  </div>
                  <div className="flex gap-3 items-start">
                    <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 text-xs font-semibold flex items-center justify-center flex-shrink-0">2</span>
                    <p className="text-slate-700 text-sm sm:text-base">
                      <span className="font-semibold text-slate-900">Identyfikacja podstawy prawnej</span>
                      <span className="text-slate-500"> - </span>
                      model podaje identyfikator przepisu (np. &quot;art. 415 k.c.&quot;), na którym oparł odpowiedź
                    </p>
                  </div>
                  <div className="flex gap-3 items-start">
                    <span className="w-6 h-6 rounded-full bg-emerald-100 text-emerald-700 text-xs font-semibold flex items-center justify-center flex-shrink-0">3</span>
                    <p className="text-slate-700 text-sm sm:text-base">
                      <span className="font-semibold text-slate-900">Przytoczenie treści przepisu</span>
                      <span className="text-slate-500"> - </span>
                      model cytuje dokładną treść wskazanego przepisu, którą oceniamy za pomocą metryk tekstowych
                    </p>
                  </div>
                </div>
              </div>

              {/* Przykład */}
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 sm:p-5">
                <p className="font-semibold text-slate-900 text-sm sm:text-base mb-3">Przykładowe pytanie:</p>
                <p className="italic text-slate-700 text-sm sm:text-base mb-4 leading-relaxed">
                  Zgodnie z Kodeksem karnym, czyn zabroniony uważa się za popełniony w miejscu, w którym:
                </p>
                <div className="space-y-2 text-sm text-slate-600">
                  <div className="flex gap-2">
                    <span className="font-semibold text-slate-700 w-6">A.</span>
                    <span>sprawca działał lub zaniechał działania, do którego był obowiązany, albo gdzie skutek stanowiący znamię czynu zabronionego nastąpił lub według zamiaru sprawcy miał nastąpić</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="font-semibold text-slate-700 w-6">B.</span>
                    <span>ujawniono czyn zabroniony</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="font-semibold text-slate-700 w-6">C.</span>
                    <span>zatrzymano sprawcę czynu zabronionego</span>
                  </div>
                </div>
                <div className="mt-4 pt-3 border-t border-slate-200">
                  <p className="text-sm text-slate-500">
                    Poprawna odpowiedź: <span className="font-semibold text-emerald-600">A</span> (art. 6 § 2 Kodeksu karnego)
                  </p>
                </div>
              </div>

              {/* Źródła */}
              <div className="space-y-3">
                <h3 className="text-base sm:text-lg font-semibold text-slate-800">Źródła danych</h3>
                <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                  Pytania egzaminacyjne oraz klucze odpowiedzi zostały pozyskane ze strony
                  Ministerstwa Sprawiedliwości. Teksty jednolite kodeksów prawnych pobrano
                  z Internetowego Systemu Aktów Prawnych (ISAP). Zbiór zawiera łącznie
                  <span className="font-semibold text-slate-900"> 1994 pytania</span> z egzaminów przeprowadzonych w latach 2016-2025.
                </p>
              </div>
            </div>
          </section>

          {/* Test orzeczeń */}
          <section>
            <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <FileText size={18} className="text-amber-600 sm:hidden" weight="duotone" />
                <FileText size={22} className="text-amber-600 hidden sm:block" weight="duotone" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Test orzeczeń sądowych</h2>
            </div>
            <div className="space-y-6">
              {/* Charakterystyka */}
              <div className="space-y-3">
                <h3 className="text-base sm:text-lg font-semibold text-slate-800">Charakterystyka orzeczeń</h3>
                <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                  Orzeczenia sądowe są oficjalnymi rozstrzygnięciami sądów wydawanymi w sprawach
                  cywilnych, karnych i administracyjnych. Każde orzeczenie składa się z rozstrzygnięcia
                  (wyroku lub postanowienia) oraz uzasadnienia przedstawiającego motywy sądu.
                </p>
                <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                  Uzasadnienia zawierają bezpośrednie cytowania i interpretacje przepisów prawnych,
                  co pozwala weryfikować zdolność modeli do rozpoznawania podstaw prawnych
                  rozstrzygnięć.
                </p>
              </div>

              {/* Metodologia */}
              <div className="space-y-3">
                <h3 className="text-base sm:text-lg font-semibold text-slate-800">Metodologia testu</h3>
                <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                  Test polega na prezentowaniu modelom orzeczeń sądowych, w których zamaskowano:
                </p>
                <div className="grid gap-3 pl-1">
                  <div className="flex gap-3 items-start">
                    <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 flex-shrink-0"></div>
                    <p className="text-slate-700 text-sm sm:text-base">
                      <span className="font-semibold text-slate-900">Identyfikator artykułu</span>
                      <span className="text-slate-500"> - </span>
                      np. &quot;art. 415 k.c.&quot;, oznaczony jako <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs sm:text-sm font-mono text-slate-700">&lt;ART_MASK&gt;</code>
                    </p>
                  </div>
                  <div className="flex gap-3 items-start">
                    <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-2 flex-shrink-0"></div>
                    <p className="text-slate-700 text-sm sm:text-base">
                      <span className="font-semibold text-slate-900">Treść przepisu</span>
                      <span className="text-slate-500"> - </span>
                      dosłowną lub sparafrazowaną, oznaczoną jako <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs sm:text-sm font-mono text-slate-700">&lt;TREŚĆ_MASK&gt;</code>
                    </p>
                  </div>
                </div>
                <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                  Zadaniem modelu jest wywnioskowanie na podstawie kontekstu uzasadnienia,
                  jaki przepis został zamaskowany, oraz przytoczenie jego treści.
                </p>
              </div>

              {/* Źródła */}
              <div className="space-y-3">
                <h3 className="text-base sm:text-lg font-semibold text-slate-800">Źródła danych</h3>
                <p className="text-slate-600 text-sm sm:text-base leading-relaxed">
                  Orzeczenia pozyskano z Portalu Orzeczeń Sądów Powszechnych. Zbiór zawiera
                  <span className="font-semibold text-slate-900"> 50 ręcznie zamaskowanych orzeczeń</span> sądów różnych instancji
                  (rejonowych, okręgowych i apelacyjnych).
                </p>
              </div>
            </div>
          </section>

          {/* Metryki */}
          <section>
            <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <ChartLine size={18} className="text-purple-600 sm:hidden" weight="duotone" />
                <ChartLine size={22} className="text-purple-600 hidden sm:block" weight="duotone" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Wykorzystane metryki</h2>
            </div>

            <p className="text-slate-600 mb-6 text-sm sm:text-base leading-relaxed">
              Do oceny jakości wygenerowanych przez modele treści przepisów prawnych stosujemy
              metryki z rodziny ROUGE, które pozwalają na automatyczne porównanie tekstu
              przytoczonego przez model z tekstem referencyjnym.
            </p>

            <div className="grid gap-4 sm:gap-6">
              {/* ROUGE-W */}
              <div className="bg-white rounded-lg sm:rounded-xl border border-slate-200 p-4 sm:p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900 text-sm sm:text-base mb-2">ROUGE-W</h3>
                <p className="text-slate-600 text-xs sm:text-sm leading-relaxed">
                  Metryka mierząca, jak długie fragmenty tekstu wygenerowanego przez model
                  pokrywają się z tekstem oryginalnego przepisu. Im dłuższy ciągły fragment
                  jest zgodny z oryginałem, tym wyższa ocena. Przykładowo: jeśli model
                  przytoczył 10 słów z rzędu dokładnie tak jak w przepisie, otrzyma wyższą
                  ocenę niż gdyby te same 10 słów było rozrzuconych w różnych miejscach tekstu.
                </p>
              </div>

              {/* ROUGE-N */}
              <div className="bg-white rounded-lg sm:rounded-xl border border-slate-200 p-4 sm:p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900 text-sm sm:text-base mb-2">ROUGE-N</h3>
                <p className="text-slate-600 text-xs sm:text-sm leading-relaxed">
                  Metryka bazująca na analizie n-gramów, czyli ciągów n kolejnych słów.
                  Obliczamy miarę F1 dla n-gramów o długości od 1 do 3, a następnie wyznaczamy
                  średnią arytmetyczną tych wartości.
                </p>
              </div>

              {/* ROUGE-N TF-IDF */}
              <div className="bg-white rounded-lg sm:rounded-xl border border-slate-200 p-4 sm:p-6 shadow-sm">
                <h3 className="font-semibold text-slate-900 text-sm sm:text-base mb-2">ROUGE-N TF-IDF</h3>
                <p className="text-slate-600 text-xs sm:text-sm leading-relaxed">
                  Rozszerzona wersja ROUGE-N wykorzystująca TF-IDF - metodę wyznaczania wag słów
                  łączącą dwa komponenty: częstość słowa w artykule (TF) oraz odwrotną częstość
                  w całym kodeksie (IDF), pozwalając na identyfikację słów, które są jednocześnie
                  istotne dla danego dokumentu i wyróżniające w kontekście całego korpusu dokumentów.
                </p>
              </div>
            </div>
          </section>

          {/* Źródła */}
          <section>
            <div className="flex items-center gap-2 sm:gap-3 mb-4 sm:mb-6">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                <Books size={18} className="text-slate-600 sm:hidden" weight="duotone" />
                <Books size={22} className="text-slate-600 hidden sm:block" weight="duotone" />
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Źródła danych</h2>
            </div>
            <div className="grid gap-3 sm:gap-4">
              <div className="flex gap-3 items-start">
                <div className="w-1.5 h-1.5 rounded-full bg-slate-400 mt-2 flex-shrink-0"></div>
                <p className="text-slate-700 text-sm sm:text-base">
                  <span className="font-semibold text-slate-900">Pytania egzaminacyjne</span>
                  <span className="text-slate-500"> - </span>
                  <a href="https://www.gov.pl/web/sprawiedliwosc/zestawy-pytan-testowych" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-700 hover:underline transition-colors">
                    Ministerstwo Sprawiedliwości
                  </a>
                </p>
              </div>
              <div className="flex gap-3 items-start">
                <div className="w-1.5 h-1.5 rounded-full bg-slate-400 mt-2 flex-shrink-0"></div>
                <p className="text-slate-700 text-sm sm:text-base">
                  <span className="font-semibold text-slate-900">Teksty jednolite kodeksów</span>
                  <span className="text-slate-500"> - </span>
                  <a href="https://isap.sejm.gov.pl/" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-700 hover:underline transition-colors">
                    Internetowy System Aktów Prawnych (ISAP)
                  </a>
                </p>
              </div>
              <div className="flex gap-3 items-start">
                <div className="w-1.5 h-1.5 rounded-full bg-slate-400 mt-2 flex-shrink-0"></div>
                <p className="text-slate-700 text-sm sm:text-base">
                  <span className="font-semibold text-slate-900">Orzeczenia sądowe</span>
                  <span className="text-slate-500"> - </span>
                  <a href="https://orzeczenia.ms.gov.pl/" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-700 hover:underline transition-colors">
                    Portal Orzeczeń Sądów Powszechnych
                  </a>
                </p>
              </div>
            </div>
          </section>

        </div>
      </main>

      <Footer />
    </div>
  );
}

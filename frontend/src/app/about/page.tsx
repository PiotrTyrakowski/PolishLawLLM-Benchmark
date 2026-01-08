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
    <div className="bg-gray-50 text-gray-800 antialiased min-h-screen flex flex-col">
      <Header />

      {/* Hero */}
      <div className="bg-white border-b border-gray-200 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-indigo-600 transition-colors mb-6"
          >
            <ArrowLeft size={16} weight="bold" />
            Powrót do rankingu
          </Link>
         
        </div>
      </div>

      <main className="max-w-4xl mx-auto px-4 py-12 flex-1">
        <div className="space-y-16">

          {/* Wprowadzenie */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                <Scales size={22} className="text-indigo-600" weight="duotone" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">Cel projektu</h2>
            </div>
            <div className="prose prose-slate max-w-none">
              <p>
                PolishLawLLM Benchmark to projekt badawczy mający na celu obiektywną ocenę
                możliwości dużych modeli językowych (LLM) w dziedzinie polskiego prawa.
                W ramach benchmarku przeprowadzamy dwa komplementarne testy:
              </p>
              <ul>
                <li><strong>Test egzaminów prawniczych</strong> - bazujący na oficjalnych pytaniach z egzaminów na aplikacje prawnicze</li>
                <li><strong>Test orzeczeń sądowych</strong> - weryfikujący zdolność do identyfikacji przepisów w kontekście uzasadnień sądowych</li>
              </ul>
              <p>
                W obu testach modele są proszone o przytoczenie dokładnej treści przepisów prawnych,
                co pozwala ocenić nie tylko znajomość prawa, ale także dokładność generowanego tekstu.
              </p>
            </div>
          </section>

          {/* Test egzaminów */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                <Exam size={22} className="text-emerald-600" weight="duotone" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">Test egzaminów prawniczych</h2>
            </div>
            <div className="prose prose-slate max-w-none">
              <h3>Charakterystyka egzaminów</h3>
              <p>
                Egzaminy na aplikację prawniczą są kluczowym elementem rekrutacji do odbycia
                aplikacji przygotowującej do wykonywania zawodu prawniczego. W Polsce występują
                trzy rodzaje takich egzaminów:
              </p>
              <ul>
                <li>Egzamin na aplikację adwokacką i radcowską</li>
                <li>Egzamin na aplikację notarialną</li>
                <li>Egzamin na aplikację komorniczą</li>
              </ul>
              <p>
                Każdy egzamin ma formę testu jednokrotnego wyboru z 3 możliwymi odpowiedziami.
                Pytania odnoszą się do przepisów obowiązujących na dzień ogłoszenia wykazu
                tytułów aktów prawnych przez Ministra Sprawiedliwości.
              </p>

              <h3>Metodologia testu</h3>
              <p>
                Test polega na zadawaniu modelom pytań zamkniętych z egzaminów i weryfikacji
                trzech aspektów odpowiedzi:
              </p>
              <ol>
                <li>
                  <strong>Poprawność odpowiedzi</strong> - oceniana binarnie (1 punkt za poprawną,
                  0 za niepoprawną)
                </li>
                <li>
                  <strong>Identyfikacja podstawy prawnej</strong> - model podaje identyfikator
                  przepisu (np. &quot;art. 415 k.c.&quot;), na którym oparł odpowiedź
                </li>
                <li>
                  <strong>Przytoczenie treści przepisu</strong> - model cytuje dokładną treść
                  wskazanego przepisu, którą oceniamy za pomocą metryk tekstowych
                </li>
              </ol>

              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 my-6">
                <p className="font-semibold text-slate-900 mb-2">Przykładowe pytanie:</p>
                <p className="italic text-slate-700 mb-3">
                  Zgodnie z Kodeksem karnym, czyn zabroniony uważa się za popełniony w miejscu, w którym:
                </p>
                <ul className="text-sm text-slate-600 space-y-1">
                  <li><strong>A.</strong> sprawca działał lub zaniechał działania, do którego był obowiązany, albo gdzie skutek stanowiący znamię czynu zabronionego nastąpił lub według zamiaru sprawcy miał nastąpić</li>
                  <li><strong>B.</strong> ujawniono czyn zabroniony</li>
                  <li><strong>C.</strong> zatrzymano sprawcę czynu zabronionego</li>
                </ul>
                <p className="text-sm text-slate-500 mt-3">
                  Poprawna odpowiedź: A (art. 6 § 2 Kodeksu karnego)
                </p>
              </div>

              <h3>Źródła danych</h3>
              <p>
                Pytania egzaminacyjne oraz klucze odpowiedzi zostały pozyskane ze strony
                Ministerstwa Sprawiedliwości. Teksty jednolite kodeksów prawnych pobrano
                z Internetowego Systemu Aktów Prawnych (ISAP). Zbiór zawiera łącznie
                <strong> 1994 pytania</strong> z egzaminów przeprowadzonych w latach 2016-2025.
              </p>
            </div>
          </section>

          {/* Test orzeczeń */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <FileText size={22} className="text-amber-600" weight="duotone" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">Test orzeczeń sądowych</h2>
            </div>
            <div className="prose prose-slate max-w-none">
              <h3>Charakterystyka orzeczeń</h3>
              <p>
                Orzeczenia sądowe są oficjalnymi rozstrzygnięciami sądów wydawanymi w sprawach
                cywilnych, karnych i administracyjnych. Każde orzeczenie składa się z rozstrzygnięcia
                (wyroku lub postanowienia) oraz uzasadnienia przedstawiającego motywy sądu.
              </p>
              <p>
                Uzasadnienia zawierają bezpośrednie cytowania i interpretacje przepisów prawnych,
                co pozwala weryfikować zdolność modeli do rozpoznawania podstaw prawnych
                rozstrzygnięć.
              </p>

              <h3>Metodologia testu</h3>
              <p>
                Test polega na prezentowaniu modelom orzeczeń sądowych, w których zamaskowano:
              </p>
              <ul>
                <li><strong>Identyfikator artykułu</strong> (np. &quot;art. 415 k.c.&quot;) - oznaczony jako <code>&lt;ART_MASK&gt;</code></li>
                <li><strong>Treść przepisu</strong> (dosłowną lub sparafrazowaną) - oznaczoną jako <code>&lt;TREŚĆ_MASK&gt;</code></li>
              </ul>
              <p>
                Zadaniem modelu jest wywnioskowanie na podstawie kontekstu uzasadnienia,
                jaki przepis został zamaskowany, oraz przytoczenie jego treści.
              </p>

              <h3>Źródła danych</h3>
              <p>
                Orzeczenia pozyskano z Portalu Orzeczeń Sądów Powszechnych. Zbiór zawiera
                <strong> 50 ręcznie zamaskowanych orzeczeń</strong> sądów różnych instancji
                (rejonowych, okręgowych i apelacyjnych).
              </p>
            </div>
          </section>

          {/* Metryki */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <ChartLine size={22} className="text-purple-600" weight="duotone" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">Wykorzystane metryki</h2>
            </div>
            <div className="prose prose-slate max-w-none">
              <p>
                Do oceny jakości wygenerowanych przez modele treści przepisów prawnych stosujemy
                metryki z rodziny ROUGE, które pozwalają na automatyczne porównanie tekstu
                przytoczonego przez model z tekstem referencyjnym.
              </p>

              <h3>ROUGE-W (Weighted Longest Common Subsequence)</h3>
              <p>
                Rozszerzenie klasycznej metryki ROUGE-L, które premiuje ciągłe sekwencje
                dopasowań. Wykorzystuje funkcję ważącą f(k) = k<sup>α</sup>, gdzie parametr α
                kontroluje stopień premiowania ciągłości. W naszym benchmarku przyjęliśmy
                wartość α = 1.2. Dzięki temu teksty zawierające
                długie, spójne fragmenty zgodne z referencją otrzymują wyższe oceny.
              </p>

              <h3>ROUGE-N (N-gram Overlap)</h3>
              <p>
                Metryka bazująca na analizie n-gramów, czyli ciągów n kolejnych słów.
                Obliczamy miarę F1 dla n-gramów o długości od 1 do 3, a następnie wyznaczamy
                średnią arytmetyczną tych wartości.
              </p>

              <h3>Ważona czułość ROUGE-N (z TF-IDF)</h3>
              <p>
                Rozszerzona wersja ROUGE-N, która przypisuje większe wagi n-gramom zawierającym
                terminy unikalne dla danego przepisu (wysokie wartości TF-IDF). Dzięki temu
                pominięcie kluczowych terminów prawnych (np. konkretnych kwot, dat, nazw własnych)
                skutkuje większym spadkiem wartości metryki.
              </p>

            </div>
          </section>

          {/* Źródła */}
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
                <Books size={22} className="text-slate-600" weight="duotone" />
              </div>
              <h2 className="text-2xl font-bold text-slate-900">Źródła danych</h2>
            </div>
            <div className="prose prose-slate max-w-none">
              <ul>
                <li>
                  <strong>Pytania egzaminacyjne:</strong>{' '}
                  <a href="https://www.gov.pl/web/sprawiedliwosc/zestawy-pytan-testowych" target="_blank" rel="noopener noreferrer">
                    Ministerstwo Sprawiedliwości - zestawy pytań testowych
                  </a>
                </li>
                <li>
                  <strong>Teksty jednolite kodeksów:</strong>{' '}
                  <a href="https://isap.sejm.gov.pl/" target="_blank" rel="noopener noreferrer">
                    Internetowy System Aktów Prawnych (ISAP)
                  </a>
                </li>
                <li>
                  <strong>Orzeczenia sądowe:</strong>{' '}
                  <a href="https://orzeczenia.ms.gov.pl/" target="_blank" rel="noopener noreferrer">
                    Portal Orzeczeń Sądów Powszechnych
                  </a>
                </li>
              </ul>
            </div>
          </section>

        </div>
      </main>

      <Footer />
    </div>
  );
}

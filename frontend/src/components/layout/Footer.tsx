import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-8 sm:py-10 mt-8 sm:mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8">
          {/* About */}
          <div className="sm:col-span-2 md:col-span-1">
            <h3 className="text-white font-semibold mb-2 sm:mb-3 text-sm sm:text-base">PolishLawLLM Benchmark</h3>
            <p className="text-xs sm:text-sm leading-relaxed">
              Projekt badawczy oceniający zdolność modeli językowych do rozumienia
              i stosowania polskiego prawa.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-semibold mb-2 sm:mb-3 text-sm sm:text-base">Nawigacja</h3>
            <ul className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
              <li>
                <Link href="/" className="hover:text-white transition-colors">
                  Ranking modeli
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-white transition-colors">
                  O benchmarku
                </Link>
              </li>
            </ul>
          </div>

          {/* Data sources */}
          <div>
            <h3 className="text-white font-semibold mb-2 sm:mb-3 text-sm sm:text-base">Dane</h3>
            <ul className="space-y-1.5 sm:space-y-2 text-xs sm:text-sm">
              <li>
                <a
                  href="https://www.gov.pl/web/sprawiedliwosc/zestawy-pytan-testowych"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  Ministerstwo Sprawiedliwości
                </a>
              </li>
              <li>
                <a
                  href="https://isap.sejm.gov.pl/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  ISAP
                </a>
              </li>
              <li>
                <a
                  href="https://orzeczenia.ms.gov.pl/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-white transition-colors"
                >
                  Portal Orzeczeń
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-slate-800 mt-6 sm:mt-8 pt-4 sm:pt-6 text-center text-xs sm:text-sm">
          <p>&copy; {new Date().getFullYear()} PolishLawLLM Benchmark</p>
        </div>
      </div>
    </footer>
  );
}

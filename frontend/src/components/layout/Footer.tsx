import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-10 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="text-white font-semibold mb-3">PolishLawLLM Benchmark</h3>
            <p className="text-sm leading-relaxed">
              Projekt badawczy oceniający zdolność modeli językowych do rozumienia
              i stosowania polskiego prawa.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-semibold mb-3">Nawigacja</h3>
            <ul className="space-y-2 text-sm">
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
            <h3 className="text-white font-semibold mb-3">Dane</h3>
            <ul className="space-y-2 text-sm">
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

        <div className="border-t border-slate-800 mt-8 pt-6 text-center text-sm">
          <p>&copy; {new Date().getFullYear()} PolishLawLLM Benchmark</p>
        </div>
      </div>
    </footer>
  );
}

import Link from 'next/link';
import { Gavel, Info } from '@phosphor-icons/react/dist/ssr';

export default function Header() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 border-b border-slate-200 shadow-sm backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8">
        <div className="flex justify-between h-14 sm:h-16">
          <Link href="/" className="flex items-center gap-2 sm:gap-3 px-2 py-1 -ml-2 rounded-lg hover:bg-slate-100 transition-colors">
            <div className="w-8 h-8 sm:w-9 sm:h-9 bg-gradient-to-br from-indigo-900 to-slate-800 rounded-lg flex items-center justify-center text-white shadow-md">
              <Gavel size={18} className="sm:hidden" weight="fill" />
              <Gavel size={20} className="hidden sm:block" weight="fill" />
            </div>
            <span className="font-bold text-base sm:text-lg tracking-tight text-slate-900">
              PolishLaw<span className="text-indigo-600">LLM</span> <span className="text-slate-600 font-semibold">Benchmark</span>
            </span>
          </Link>
          <div className="flex items-center">
            <Link
              href="/about"
              className="flex items-center gap-1.5 sm:gap-2 px-3 py-1.5 sm:px-4 sm:py-2 text-xs sm:text-sm text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 bg-indigo-50/50 rounded-full transition-colors font-medium border border-indigo-200 whitespace-nowrap"
            >
              <Info size={16} className="sm:hidden" weight="duotone" />
              <Info size={18} className="hidden sm:block" weight="duotone" />
              <span>O benchmarku</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

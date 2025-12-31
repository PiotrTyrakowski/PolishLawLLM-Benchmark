import { Gavel } from '@phosphor-icons/react/dist/ssr';

export default function Header() {
  return (
    <nav className="sticky top-0 z-50 bg-white/90 border-b border-slate-200 shadow-sm backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-indigo-900 to-slate-800 rounded-lg flex items-center justify-center text-white shadow-md">
              <Gavel size={20} weight="fill" />
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight text-slate-900 block leading-tight">
                PolishLaw<span className="text-indigo-600">LLM</span>
              </span>
              <span className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Benchmark Prawniczy
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

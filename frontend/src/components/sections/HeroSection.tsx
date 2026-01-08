export default function HeroSection() {
  return (
    <div className="bg-white border-b border-gray-200 py-12">
      <div className="max-w-4xl mx-auto px-4 text-center">
        <h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
          Czym jest PolishLawLLM Benchmark?
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Projekt badawczy oceniający zdolność dużych modeli językowych (LLM) do rozumienia
          i stosowania polskiego prawa. Testujemy modele na autentycznych pytaniach
          egzaminacyjnych oraz rzeczywistych orzeczeniach sądowych.
        </p>
      </div>
    </div>
  );
}

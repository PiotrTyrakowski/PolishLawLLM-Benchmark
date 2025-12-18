import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import HeroSection from '@/components/sections/HeroSection';
import ExamsSection from '@/components/sections/ExamsSection';
import JudgmentsSection from '@/components/sections/JudgmentsSection';

export default function Home() {
  return (
    <div className="bg-gray-50 text-gray-800 antialiased min-h-screen flex flex-col">
      <Header />
      <HeroSection />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-16 flex-1">
        <ExamsSection />
        <JudgmentsSection />
      </main>
      <Footer />
    </div>
  );
}

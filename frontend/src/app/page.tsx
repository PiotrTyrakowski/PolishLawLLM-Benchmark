import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import HeroSection from '@/components/sections/HeroSection';
import AboutSection from '@/components/sections/AboutSection';
import ExamsSection from '@/components/sections/ExamsSection';
import JudgmentsSection from '@/components/sections/JudgmentsSection';

export default function Home() {
  return (
    <div className="bg-gray-50 text-gray-800 antialiased min-h-screen flex flex-col overflow-x-hidden">
      <Header />
      <div className="h-14 sm:h-16" /> {/* Spacer for fixed header */}
      <HeroSection />
      <AboutSection />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-16 flex-1 w-full">
        <ExamsSection />
        <JudgmentsSection />
      </main>
      <Footer />
    </div>
  );
}

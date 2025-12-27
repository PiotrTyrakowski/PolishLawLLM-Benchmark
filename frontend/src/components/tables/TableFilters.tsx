'use client';

interface TableFiltersProps {
  year: string;
  setYear: (year: string) => void;
  examType: string;
  setExamType: (type: string) => void;
}

export default function TableFilters({
  year,
  setYear,
  examType,
  setExamType,
}: TableFiltersProps) {
  return (
    <div className="flex gap-2 bg-gray-100 p-1.5 rounded-lg border border-gray-200">
      <select
        value={year}
        onChange={(e) => setYear(e.target.value)}
        className="bg-white border-gray-300 text-gray-700 text-sm rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"
      >
        <option value="all">Średnia (Wszystkie lata)</option>
        <option value="2024">Rok 2024</option>
        <option value="2023">Rok 2023</option>
      </select>
      <select
        value={examType}
        onChange={(e) => setExamType(e.target.value)}
        className="bg-white border-gray-300 text-gray-700 text-sm rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 py-1.5 px-3"
      >
        <option value="all">Średnia (Wszystkie typy)</option>
        <option value="radca">Radcowski / Adwokacki</option>
        <option value="komornik">Komorniczy</option>
        <option value="notariusz">Notarialny</option>
      </select>
    </div>
  );
}

// Descriptions of metrics for tooltips
export const metricDescriptions: Record<string, string> = {
  // Accuracy metrics 
  answer:
    'Odsetek poprawnych odpowiedzi na pytania zamknięte z egzaminów prawniczych.',
  legal_basis:
    'Odsetek poprawnie zidentyfikowanych artykułów będących podstawą prawną odpowiedzi.',

  // Text metrics
  exact_match:
    'Odsetek odpowiedzi, w których przytoczony przepis jest identyczny z tekstem referencyjnym.',
  rouge_w:
    'ROUGE-W: Miara podobieństwa bazująca na ważonych najdłuższych wspólnych podsekwencjach. Premiuje ciągłe fragmenty tekstu.',
  rouge_n_f1:
    'ROUGE-N: Średnia harmoniczna precyzji i czułości dla n-gramów (1-3). Mierzy pokrycie słów i fraz.',
  rouge_n_tfidf:
    'Ważona czułość ROUGE-N z wagami TF-IDF. Wyższe wagi dla unikalnych terminów prawnych specyficznych dla danego przepisu.',
  
  // Fallback for unknown metrics
  default: 'Metryka oceny jakości odpowiedzi modelu.',
};

export function getMetricDescription(key: string): string {
  
  const lowerKey = key.toLowerCase();
  if (metricDescriptions[lowerKey]) {
    return metricDescriptions[lowerKey];
  }

  return metricDescriptions.default;
}

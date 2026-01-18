// Descriptions of metrics for tooltips
export const metricDescriptions: Record<string, string> = {
  // Accuracy metrics - Exams
  answer:
    'Odsetek poprawnych odpowiedzi na pytania zamknięte z egzaminów prawniczych.',
  legal_basis:
    'Odsetek poprawnie zidentyfikowanych artykułów będących podstawą prawną odpowiedzi.',

  // Accuracy metrics - Judgments
  article_accuracy:
    'Odsetek poprawnie zidentyfikowanych zamaskowanych artykułów w orzeczeniach.',
  retrieval:
    'Skuteczność identyfikacji zamaskowanych przepisów prawnych w treści orzeczeń.',

  // Text metrics
  exact_match:
    'Odsetek odpowiedzi, w których przytoczony przepis jest identyczny z tekstem referencyjnym.',
  rouge_w:
    'ROUGE-W: Miara podobieństwa bazująca na ważonych najdłuższych wspólnych podsekwencjach. Premiuje ciągłe fragmenty tekstu.',
  rouge_n_f1:
    'ROUGE-N: Średnia harmoniczna precyzji i czułości dla n-gramów (1-3). Mierzy pokrycie słów i fraz.',
  rouge_n_tfidf:
    'Ważona czułość ROUGE-N z wagami TF-IDF. Wyższe wagi dla unikalnych terminów prawnych specyficznych dla danego przepisu.',
  bleu:
    'BLEU: Miara jakości tłumaczenia maszynowego, oceniająca podobieństwo n-gramów między tekstem wygenerowanym a referencyjnym.',
  weighted_bleu:
    'Ważony BLEU z większą wagą dla kluczowych terminów prawnych.',

  // Fallback for unknown metrics
  default: 'Metryka oceny jakości odpowiedzi modelu.',
};

// Get description for a metric key (handles snake_case keys)
export function getMetricDescription(key: string): string {
  // Try exact match first
  if (metricDescriptions[key]) {
    return metricDescriptions[key];
  }

  // Try lowercase version
  const lowerKey = key.toLowerCase();
  if (metricDescriptions[lowerKey]) {
    return metricDescriptions[lowerKey];
  }

  // Return default
  return metricDescriptions.default;
}

// Get display label for a metric key - dynamically converts snake_case to Title Case
export function getMetricLabel(key: string): string {
  let label = key
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  // Remove " F1" suffix if present
  if (label.endsWith(' F1')) {
    label = label.slice(0, -3);
  }

  return label;
}

export function formatMetricValue(value: number, metricKey?: string): string {
  if (metricKey && metricKey.toLowerCase().includes('rouge')) {
    return value.toFixed(2);
  }
  return `${(value * 100).toFixed(0)}%`;
}

export function extractMetricKeys(
  data: Array<{ accuracyMetrics: Record<string, number>; textMetrics: Record<string, number> }>
): { accuracyKeys: string[]; textKeys: string[] } {
  const accuracyKeys = new Set<string>();
  const textKeys = new Set<string>();

  data.forEach((item) => {
    Object.keys(item.accuracyMetrics).forEach((k) => accuracyKeys.add(k));
    Object.keys(item.textMetrics).forEach((k) => textKeys.add(k));
  });

  return {
    accuracyKeys: Array.from(accuracyKeys).sort(),
    textKeys: Array.from(textKeys).sort(),
  };
}

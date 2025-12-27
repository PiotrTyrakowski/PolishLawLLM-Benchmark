// Convert snake_case to Title Case for display
function snakeToTitleCase(str: string): string {
  return str
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Get display label for a metric key - dynamically converts snake_case to Title Case
export function getMetricLabel(key: string): string {
  return snakeToTitleCase(key);
}

// Format metric value for display
// All values are treated as decimals, displayed with 2 decimal places
export function formatMetricValue(value: number): string {
  return value.toFixed(2);
}

// Extract all unique metric keys from data array
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

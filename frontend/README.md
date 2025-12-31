# PolishLawLLM Benchmark Frontend

Next.js frontend for displaying benchmark results of LLMs on Polish legal exams and judgment interpretation tasks.

## Setup

1. Install dependencies:
```bash
bun install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
```

3. Add Firebase Admin SDK credentials to `.env.local`:
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
RESULTS_COLLECTION=results
```

4. Run development server:
```bash
bun run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Architecture

### Firebase Structure
```
/results/{model_id}/
  - fields: model_name, is_polish, model_config
  - /exams/{exam_doc_id}
    - fields: accuracy_metrics, text_metrics, type, year
  - /judgments/all
    - fields: accuracy_metrics, text_metrics
```

### API Routes
- `GET /api/exams` - Aggregated exam metrics per model
- `GET /api/judgments` - Judgment metrics per model
- `GET /api/models/[modelId]` - Detailed model data

### Key Files
- `src/lib/firebase-admin.ts` - Firebase Admin SDK (server-only)
- `src/lib/server/firestore.ts` - Firestore query functions
- `src/lib/types.ts` - TypeScript types
- `src/lib/metricConfig.ts` - Metric display utilities

## Dynamic Metrics

The frontend dynamically renders whatever metrics exist in `accuracy_metrics` and `text_metrics` objects. No metric names are hardcoded - column headers are generated from snake_case keys (e.g., `exact_match` becomes "Exact Match").

## Development Mode

To use mock data instead of Firebase:
```
NEXT_PUBLIC_USE_MOCK_DATA=true
```

## Build

```bash
bun run build
```

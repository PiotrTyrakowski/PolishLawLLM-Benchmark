# PolishLawLLM Benchmark Frontend

Next.js frontend for displaying benchmark results of LLMs on Polish legal exams and judgment interpretation tasks.

> **Note:** We use [Bun](https://bun.sh/) as our package manager, but you can use any package manager you prefer (npm, yarn, pnpm).

## Setup

1. Install dependencies:
```bash
bun install
# or: npm install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
```

By default, mock data is enabled (`NEXT_PUBLIC_USE_MOCK_DATA=true`), so you can skip step 3.

3. Add Firebase Admin SDK credentials to `.env.local` if you want to use real data:
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
RESULTS_COLLECTION=results
NEXT_PUBLIC_USE_MOCK_DATA=false
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

To use mock data instead of Firebase during development, set in `.env.local`:
```
NEXT_PUBLIC_USE_MOCK_DATA=true
```

Mock data is only active when running `bun run dev` (development mode). Production builds always use Firebase regardless of this setting.

## Build & Production

```bash
bun run build
bun run start
```

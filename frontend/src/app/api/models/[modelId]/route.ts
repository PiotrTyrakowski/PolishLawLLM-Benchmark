import { NextResponse } from 'next/server';
import { getModelDetail } from '@/lib/server/firestore';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ modelId: string }> }
) {
  const { modelId } = await params;

  try {
    const data = await getModelDetail(modelId);

    if (!data) {
      return NextResponse.json({ error: 'Model not found' }, { status: 404 });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching model:', error);
    return NextResponse.json({ error: 'Failed to fetch model' }, { status: 500 });
  }
}

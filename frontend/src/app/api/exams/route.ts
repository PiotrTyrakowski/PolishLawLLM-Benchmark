import { NextResponse } from 'next/server';
import { getAggregatedExams } from '@/lib/server/firestore';

export async function GET() {
  try {
    const data = await getAggregatedExams();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching exams:', error);
    return NextResponse.json({ error: 'Failed to fetch exams' }, { status: 500 });
  }
}

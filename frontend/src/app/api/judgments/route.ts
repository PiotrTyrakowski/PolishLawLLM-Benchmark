import { NextResponse } from 'next/server';
import { getAllJudgments } from '@/lib/server/firestore';

export async function GET() {
  try {
    const data = await getAllJudgments();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching judgments:', error);
    return NextResponse.json({ error: 'Failed to fetch judgments' }, { status: 500 });
  }
}

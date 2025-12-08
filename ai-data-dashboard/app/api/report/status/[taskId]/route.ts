import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET(
  request: Request,
  { params }: { params: { taskId: string } }
) {
  try {
    const { taskId } = params;
    
    const response = await fetch(`${API_BASE_URL}/api/report/status/${taskId}`, {
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Report status API error:', error);
    return NextResponse.json(
      { error: 'Failed to check report status' },
      { status: 500 }
    );
  }
}

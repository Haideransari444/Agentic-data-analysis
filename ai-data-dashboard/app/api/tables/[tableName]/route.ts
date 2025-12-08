import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';

export async function GET(
  request: Request,
  { params }: { params: { tableName: string } }
) {
  try {
    const { tableName } = params;
    
    const response = await fetch(`${API_BASE_URL}/api/tables/${tableName}`, {
      cache: 'no-store',
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Table info API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch table information' },
      { status: 500 }
    );
  }
}

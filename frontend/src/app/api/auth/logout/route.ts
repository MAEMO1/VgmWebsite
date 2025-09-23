import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
    
    const backendResponse = await fetch(`${backendUrl}/api/auth/logout/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': request.headers.get('X-CSRFToken') || '',
        'Cookie': request.headers.get('cookie') || '',
      },
    });

    const data = await backendResponse.json();
    
    // Clear cookies on logout
    const response = NextResponse.json(data);
    response.cookies.delete('sessionid');
    response.cookies.delete('csrftoken');
    return response;
  } catch (error) {
    console.error('Logout error:', error);
    return NextResponse.json(
      { error: 'Logout failed' },
      { status: 500 }
    );
  }
}

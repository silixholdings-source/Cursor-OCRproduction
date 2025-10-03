import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'nodejs'

function getApiBase(): string {
  // Hardcoded to ensure it always works
  return 'http://127.0.0.1:8001/api/v1'
}

export async function POST(req: NextRequest) {
  try {
    const backend = `${getApiBase()}/processing/process`
    const form = await req.formData()
    const auth = req.headers.get('authorization') || undefined
    const res = await fetch(backend, {
      method: 'POST',
      headers: auth ? { 'authorization': auth } : undefined,
      body: form as any,
    })
    const text = await res.text()
    return new NextResponse(text, {
      status: res.status,
      headers: { 'content-type': res.headers.get('content-type') || 'application/json' }
    })
  } catch (e: any) {
    return NextResponse.json({ detail: e?.message || 'Proxy error' }, { status: 500 })
  }
}









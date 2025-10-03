import { redirect } from 'next/navigation'

export default function LoginPage() {
  // Redirect to the correct auth login page
  redirect('/auth/login')
}


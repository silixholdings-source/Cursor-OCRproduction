import { redirect } from 'next/navigation'

export default function SignupPage() {
  // Redirect to the correct auth register page
  redirect('/auth/register')
}


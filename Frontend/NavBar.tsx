'use client'

import Link from 'next/link'
import { useAuth } from '../contexts/AuthContext'

export default function NavBar() {
  const { isAuthenticated, logout } = useAuth()

  return (
    <nav className="hidden md:flex gap-6 items-center">
      <Link href="/recipes" className="hover:text-accent-secondary">Recipes</Link>
      <Link href="/celebrations" className="hover:text-accent-secondary">Celebrations</Link>
      <Link href="/ethnicities" className="hover:text-accent-secondary">Ethnicities</Link>
      <Link href="/seasons" className="hover:text-accent-secondary">Seasons</Link>
      {isAuthenticated ? (
        <button 
          onClick={logout}
          className="bg-accent-secondary text-white px-4 py-2 rounded hover:bg-accent-secondary/90"
        >
          Logout
        </button>
      ) : (
        <Link 
          href="/login"
          className="bg-accent-secondary text-white px-4 py-2 rounded hover:bg-accent-secondary/90"
        >
          Login
        </Link>
      )}
    </nav>
  )
}
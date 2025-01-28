import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from './contexts/AuthContext'
import Link from 'next/link'
import NavBar from './components/NavBar'  

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Tunisian Culinary Chronicles',
  description: 'Explore the rich flavors of Tunisian cuisine',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-cream min-h-screen`}>
        <AuthProvider>
          <header className="bg-secondary shadow-md">
            <div className="container mx-auto flex items-center justify-between p-4">
              <Link href="/" className="flex items-center gap-4">
                <img 
                  src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/Capture_d_%C3%A9cran_2025-01-16_000733-removebg-v6Lbkei8vH506EnxsTm7xaZi4FYog6.png"
                  alt="Tunisian Culinary Chronicles Logo" 
                  className="h-16 w-auto"
                />
                <h1 className="text-2xl font-bold text-primary">Tunisian Culinary Chronicles</h1>
              </Link>
              <NavBar />
            </div>
          </header>
          <main className="container mx-auto p-4">
            {children}
          </main>
          <footer className="bg-secondary shadow-md mt-8">
            <div className="container mx-auto p-4 text-center text-primary">
              <p>&copy; 2025 Tunisian Culinary Chronicles</p>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  )
}
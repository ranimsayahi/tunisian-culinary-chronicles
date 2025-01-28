"use client"

import type React from "react"
import { createContext, useState, useContext, useEffect } from "react"
import { useRouter } from "next/navigation"
import { config } from "../config"

interface User {
  UserID: number
  Username: string
  Email: string
  Role: string
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  isAdmin: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      fetchUserData(token)
    }
  }, [])

  const fetchUserData = async (token: string) => {
    try {
      const response = await fetch(`${config.apiUrl}/profile`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        logout()
      }
    } catch (error) {
      console.error("Error fetching user data:", error)
      logout()
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${config.apiUrl}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ Email: email, Password: password }), // Match backend expected format
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || "Login failed")
      }

      const data = await response.json()
      localStorage.setItem("token", data.access_token)
      await fetchUserData(data.access_token)
      router.push("/")
    } catch (error) {
      console.error("Login error:", error)
      throw error
    }
  }

  const register = async (username: string, email: string, password: string) => {
    try {
      const response = await fetch(`${config.apiUrl}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          Username: username,
          Email: email,
          Password: password,
        }), // Match backend expected format
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || "Registration failed")
      }

      await login(email, password)
    } catch (error) {
      console.error("Registration error:", error)
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem("token")
    setUser(null)
    router.push("/login")
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        isAdmin: user?.Role === "admin",
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}


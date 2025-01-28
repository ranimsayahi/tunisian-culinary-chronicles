"use client"

import { useState, useEffect } from "react"
import { useAuth } from "../contexts/AuthContext"
import Link from "next/link"

interface Season {
  SeasonID: number
  Season: string
  Description: string
}

export default function Seasons() {
  const [seasons, setSeasons] = useState<Season[]>([])
  const { isAuthenticated, user } = useAuth()

  useEffect(() => {
    if (isAuthenticated) {
      const token = localStorage.getItem("token")
      fetch("http://localhost:5000/seasons", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((response) => response.json())
        .then((data) => setSeasons(data))
        .catch((error) => console.error("Error fetching seasons:", error))
    }
  }, [isAuthenticated])

  if (!isAuthenticated) {
    return (
      <div className="text-center">
        <p className="mb-4">Please log in to view seasons.</p>
        <Link href="/login" className="bg-primary text-cream py-2 px-4 rounded hover:bg-primary/90">
          Login
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-primary">Seasonal Recipes</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {seasons.map((season) => (
          <div key={season.SeasonID} className="bg-cream p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-primary mb-2">{season.Season}</h3>
            <p className="text-primary/80 mb-4">{season.Description}</p>
            <Link href={`/seasons/${season.SeasonID}/recipes`} className="text-accent hover:underline">
              View Seasonal Recipes
            </Link>
          </div>
        ))}
      </div>
    </div>
  )
}


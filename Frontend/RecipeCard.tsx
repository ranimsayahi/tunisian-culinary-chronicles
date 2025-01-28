import Link from "next/link"

interface RecipeCardProps {
  RecipeID: number
  Name: string
  Description: string
  Difficulty: string
  CookingTime: string
}

export default function RecipeCard({ RecipeID, Name, Description, Difficulty, CookingTime }: RecipeCardProps) {
  return (
    <Link
      href={`/recipes/${RecipeID}`}
      className="block p-6 bg-white rounded-lg border border-gray-200 shadow-md hover:bg-gray-100"
    >
      <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-900">{Name}</h5>
      <p className="font-normal text-gray-700">{Description}</p>
      <div className="mt-4 flex justify-between text-sm text-gray-600">
        <span>Difficulty: {Difficulty}</span>
        <span>Cooking Time: {CookingTime}</span>
      </div>
    </Link>
  )
}


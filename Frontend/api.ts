import axios from "axios"
import { config } from "../config"

const api = axios.create({
  baseURL: config.apiUrl,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authApi = {
  login: (email: string, password: string) => api.post(config.endpoints.login, { email, password }),
  register: (username: string, email: string, password: string) =>
    api.post(config.endpoints.register, { username, email, password }),
}

export const recipesApi = {
  getAll: () => api.get(config.endpoints.recipes),
  getById: (id: number) => api.get(`${config.endpoints.recipes}/${id}`),
  create: (recipe: Partial<Recipe>) => api.post(config.endpoints.recipes, recipe),
  update: (id: number, recipe: Partial<Recipe>) => api.put(`${config.endpoints.recipes}/${id}`, recipe),
  delete: (id: number) => api.delete(`${config.endpoints.recipes}/${id}`),
}

export const tipsApi = {
  getByRecipe: (recipeId: number) => api.get(`${config.endpoints.recipes}/${recipeId}/tips`),
  create: (tip: Partial<Tip>) => api.post(config.endpoints.tips, tip),
  update: (id: number, tip: Partial<Tip>) => api.put(`${config.endpoints.tips}/${id}`, tip),
  delete: (id: number) => api.delete(`${config.endpoints.tips}/${id}`),
}


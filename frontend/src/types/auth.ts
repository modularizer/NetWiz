/**
 * Authentication types for NetWiz Frontend
 */

export interface User {
  id: string
  username: string
  user_type: 'user' | 'admin'
  created_at: string
  is_active: boolean
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  refresh_expires_in: number
}

export interface UserCreate {
  username: string
  password: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface AuthState {
  user: User | null
  token: Token | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface AuthContextType extends AuthState {
  signin: (credentials: UserLogin) => Promise<void>
  signup: (userData: UserCreate) => Promise<void>
  signout: () => Promise<void>
  changePassword: (passwordData: ChangePasswordRequest) => Promise<void>
  refreshToken: () => Promise<void>
  clearError: () => void
}

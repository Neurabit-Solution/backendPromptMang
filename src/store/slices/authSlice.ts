import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { authAPI } from '@/lib/api'
import type { Admin, LoginRequest } from '@/types'
import toast from 'react-hot-toast'

interface AuthState {
  user: Admin | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

const getUserFromStorage = () => {
  try {
    const userStr = localStorage.getItem('admin_user')
    return userStr ? JSON.parse(userStr) : null
  } catch (e) {
    return null
  }
}

const initialState: AuthState = {
  user: getUserFromStorage(),
  token: localStorage.getItem('admin_token'),
  isAuthenticated: !!localStorage.getItem('admin_token'),
  isLoading: false,
  error: null,
}

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginRequest, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials)
      
      // Handle the documented API response structure
      if (response.data.success) {
        const { admin, access_token } = response.data.data

        localStorage.setItem('admin_token', access_token)
        localStorage.setItem('admin_user', JSON.stringify(admin))

        toast.success('Login successful!')
        return { user: admin, token: access_token }
      } else {
        // Handle application-level errors with success: false
        const message = response.data.error?.message || 'Login failed'
        return rejectWithValue(message)
      }
    } catch (error: any) {
      // Handle HTTP errors and other exceptions
      const message = error.response?.data?.error?.message || 
                     error.response?.data?.detail || 
                     'Login failed'
      return rejectWithValue(message)
    }
  }
)

export const logout = createAsyncThunk(
  'auth/logout',
  async (_, { dispatch }) => {
    try {
      await authAPI.logout()
    } catch (error) {
      // Continue with logout even if API call fails
    } finally {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      toast.success('Logged out successfully')
    }
  }
)

export const checkAuth = createAsyncThunk(
  'auth/checkAuth',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.me()
      return response.data.data
    } catch (error: any) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      return rejectWithValue('Authentication failed')
    }
  }
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    updateUser: (state, action: PayloadAction<Partial<Admin>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload }
        localStorage.setItem('admin_user', JSON.stringify(state.user))
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = true
        state.user = action.payload.user
        state.token = action.payload.token
        state.error = null
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.error = action.payload as string
      })

      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.isAuthenticated = false
        state.user = null
        state.token = null
        state.error = null
      })

      // Check Auth
      .addCase(checkAuth.pending, (state) => {
        state.isLoading = true
      })
      .addCase(checkAuth.fulfilled, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = true
        state.user = action.payload
      })
      .addCase(checkAuth.rejected, (state) => {
        state.isLoading = false
        state.isAuthenticated = false
        state.user = null
        state.token = null
      })
  },
})

export const { clearError, updateUser } = authSlice.actions
export default authSlice.reducer
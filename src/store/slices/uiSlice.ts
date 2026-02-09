import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UiState {
  sidebarCollapsed: boolean
  theme: 'light' | 'dark'
  loading: {
    [key: string]: boolean
  }
}

const initialState: UiState = {
  sidebarCollapsed: localStorage.getItem('sidebar_collapsed') === 'true',
  theme: (localStorage.getItem('theme') as 'light' | 'dark') || 'light',
  loading: {},
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed
      localStorage.setItem('sidebar_collapsed', state.sidebarCollapsed.toString())
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload
      localStorage.setItem('sidebar_collapsed', action.payload.toString())
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload
      localStorage.setItem('theme', action.payload)
    },
    setLoading: (state, action: PayloadAction<{ key: string; loading: boolean }>) => {
      state.loading[action.payload.key] = action.payload.loading
    },
  },
})

export const { toggleSidebar, setSidebarCollapsed, setTheme, setLoading } = uiSlice.actions
export default uiSlice.reducer
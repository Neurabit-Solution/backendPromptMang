import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { checkAuth } from './store/slices/authSlice'
import { RootState, AppDispatch } from './store'
import Layout from './components/Layout'
import LoginPage from './pages/auth/LoginPage'
import SignupPage from './pages/auth/SignupPage'
import Dashboard from './pages/Dashboard'
import UsersPage from './pages/users/UsersPage'
import UserDetailPage from './pages/users/UserDetailPage'
import CreateUserPage from './pages/users/CreateUserPage'
import CreditsTransactionsPage from './pages/credits/TransactionsPage'
import AddCreditsPage from './pages/credits/AddCreditsPage'
import CreditStatsPage from './pages/credits/StatsPage'
import StylesPage from './pages/styles/StylesPage'
import StyleDetailPage from './pages/styles/StyleDetailPage'
import CreateStylePage from './pages/styles/CreateStylePage'
import CategoriesPage from './pages/styles/CategoriesPage'
import CreationsPage from './pages/creations/CreationsPage'
import CreationDetailPage from './pages/creations/CreationDetailPage'
import AnalyticsPage from './pages/analytics/AnalyticsPage'
import SettingsPage from './pages/settings/SettingsPage'
import AdminsPage from './pages/admins/AdminsPage'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  const dispatch = useDispatch<AppDispatch>()
  const { isAuthenticated, isLoading } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    const token = localStorage.getItem('admin_token')
    if (token && !isAuthenticated) {
      dispatch(checkAuth())
    }
  }, [dispatch, isAuthenticated])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/admin/login" element={<LoginPage />} />
      <Route path="/admin/signup" element={<SignupPage />} />
      <Route
        path="/admin/*"
        element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route index element={<Navigate to="/admin/dashboard" replace />} />
                <Route path="dashboard" element={<Dashboard />} />

                {/* Users */}
                <Route path="users" element={<UsersPage />} />
                <Route path="users/create" element={<CreateUserPage />} />
                <Route path="users/:id" element={<UserDetailPage />} />

                {/* Credits */}
                <Route path="credits/transactions" element={<CreditsTransactionsPage />} />
                <Route path="credits/add" element={<AddCreditsPage />} />
                <Route path="credits/stats" element={<CreditStatsPage />} />

                {/* Styles */}
                <Route path="styles" element={<StylesPage />} />
                <Route path="styles/create" element={<CreateStylePage />} />
                <Route path="styles/categories" element={<CategoriesPage />} />
                <Route path="styles/:id" element={<StyleDetailPage />} />

                {/* Creations */}
                <Route path="creations" element={<CreationsPage />} />
                <Route path="creations/:id" element={<CreationDetailPage />} />

                {/* Analytics */}
                <Route path="analytics" element={<AnalyticsPage />} />

                {/* Settings */}
                <Route path="settings" element={<SettingsPage />} />
                <Route path="admins" element={<AdminsPage />} />
              </Routes>
            </Layout>
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
    </Routes>
  )
}

export default App
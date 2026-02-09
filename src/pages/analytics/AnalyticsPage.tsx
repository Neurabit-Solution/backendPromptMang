import { useQuery } from '@tanstack/react-query'
import { TrendingUp, Users, Image, CreditCard } from 'lucide-react'
import { dashboardAPI } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

export default function AnalyticsPage() {
  const { data: stats } = useQuery({
    queryKey: ['analytics-stats'],
    queryFn: () => dashboardAPI.stats(),
  })

  const { data: userChart } = useQuery({
    queryKey: ['analytics-users', '30d'],
    queryFn: () => dashboardAPI.charts('users', '30d'),
  })

  const { data: creditsChart } = useQuery({
    queryKey: ['analytics-credits', '30d'],
    queryFn: () => dashboardAPI.charts('credits', '30d'),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600">Comprehensive platform analytics and insights</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Users</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(stats?.data.data.users.total || 0)}
              </p>
              <p className="text-sm text-green-600">+12% from last month</p>
            </div>
            <Users className="h-8 w-8 text-primary-600" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Creations</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(stats?.data.data.content.total_creations || 0)}
              </p>
              <p className="text-sm text-green-600">+8% from last month</p>
            </div>
            <Image className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Credits Spent</p>
              <p className="text-2xl font-bold text-gray-900">
                {formatNumber(stats?.data.data.credits.total_in_system || 0)}
              </p>
              <p className="text-sm text-green-600">+15% from last month</p>
            </div>
            <CreditCard className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Growth Rate</p>
              <p className="text-2xl font-bold text-gray-900">12.5%</p>
              <p className="text-sm text-green-600">Monthly average</p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">User Growth</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={userChart?.data.data || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="users" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Credits Usage</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={creditsChart?.data.data || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="credits" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Additional Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Styles</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Anime Style</span>
              <span className="text-sm font-medium">2,543 uses</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Realistic Portrait</span>
              <span className="text-sm font-medium">1,892 uses</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Abstract Art</span>
              <span className="text-sm font-medium">1,234 uses</span>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">User Engagement</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Daily Active Users</span>
              <span className="text-sm font-medium">1,234</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Avg. Session Time</span>
              <span className="text-sm font-medium">12m 34s</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Retention Rate</span>
              <span className="text-sm font-medium">68%</span>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Monthly Revenue</span>
              <span className="text-sm font-medium">$12,345</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">ARPU</span>
              <span className="text-sm font-medium">$8.50</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Conversion Rate</span>
              <span className="text-sm font-medium">3.2%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
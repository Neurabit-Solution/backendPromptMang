import { useQuery } from '@tanstack/react-query'
import { Users, CreditCard, Image, AlertTriangle } from 'lucide-react'
import { dashboardAPI } from '@/lib/api'
import { formatNumber, formatRelativeTime } from '@/lib/utils'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ComponentType<{ className?: string }>
  trend?: {
    value: number
    isPositive: boolean
  }
}

function StatCard({ title, value, subtitle, icon: Icon, trend }: StatCardProps) {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
        <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
          <Icon className="h-6 w-6 text-primary-600" />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center">
          <span
            className={`text-sm font-medium ${
              trend.isPositive ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {trend.isPositive ? '+' : ''}{trend.value}%
          </span>
          <span className="text-sm text-gray-500 ml-2">from last week</span>
        </div>
      )}
    </div>
  )
}

export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardAPI.stats(),
  })

  const { data: recentActivity } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: () => dashboardAPI.recentActivity(),
  })

  const { data: chartData } = useQuery({
    queryKey: ['user-chart', '30d'],
    queryFn: () => dashboardAPI.charts('users', '30d'),
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const dashboardStats = stats?.data.data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome to the MagicPic Admin Panel</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value={formatNumber(dashboardStats?.users.total || 0)}
          subtitle={`${dashboardStats?.users.new_today || 0} new today`}
          icon={Users}
          trend={{
            value: 12,
            isPositive: true,
          }}
        />
        <StatCard
          title="Credits in System"
          value={formatNumber(dashboardStats?.credits.total_in_system || 0)}
          subtitle={`${formatNumber(dashboardStats?.credits.spent_today || 0)} spent today`}
          icon={CreditCard}
          trend={{
            value: 8,
            isPositive: true,
          }}
        />
        <StatCard
          title="Total Creations"
          value={formatNumber(dashboardStats?.content.total_creations || 0)}
          subtitle={`${dashboardStats?.content.featured_creations || 0} featured`}
          icon={Image}
          trend={{
            value: 15,
            isPositive: true,
          }}
        />
        <StatCard
          title="Pending Reports"
          value={dashboardStats?.content.pending_reports || 0}
          subtitle="Needs attention"
          icon={AlertTriangle}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Registration Chart */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">User Registration Trend</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData?.data.data || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="users" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {recentActivity?.data.data?.slice(0, 5).map((activity: any, index: number) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="h-2 w-2 bg-primary-600 rounded-full mt-2"></div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900">{activity.description}</p>
                  <p className="text-xs text-gray-500">
                    {formatRelativeTime(activity.created_at)}
                  </p>
                </div>
              </div>
            )) || (
              <p className="text-sm text-gray-500">No recent activity</p>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="btn-primary p-4 text-left">
            <h4 className="font-medium">Create User</h4>
            <p className="text-sm opacity-90">Add a new user to the system</p>
          </button>
          <button className="btn-secondary p-4 text-left">
            <h4 className="font-medium">Add Credits</h4>
            <p className="text-sm opacity-90">Grant credits to a user</p>
          </button>
          <button className="btn-secondary p-4 text-left">
            <h4 className="font-medium">Create Style</h4>
            <p className="text-sm opacity-90">Add a new AI style</p>
          </button>
          <button className="btn-secondary p-4 text-left">
            <h4 className="font-medium">Review Reports</h4>
            <p className="text-sm opacity-90">Moderate reported content</p>
          </button>
        </div>
      </div>
    </div>
  )
}
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, TrendingDown, Users, CreditCard } from 'lucide-react'
import { creditsAPI } from '@/lib/api'
import { formatNumber, formatCredits } from '@/lib/utils'

export default function CreditStatsPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['credit-stats'],
    queryFn: () => creditsAPI.stats(),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Credit Statistics</h1>
        <p className="text-gray-600">Overview of credit usage and distribution</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Credits</p>
              <p className="text-2xl font-bold text-gray-900">2.5M</p>
            </div>
            <CreditCard className="h-8 w-8 text-primary-600" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Credits Spent Today</p>
              <p className="text-2xl font-bold text-gray-900">15.2K</p>
            </div>
            <TrendingDown className="h-8 w-8 text-red-600" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Average per User</p>
              <p className="text-2xl font-bold text-gray-900">2,500</p>
            </div>
            <Users className="h-8 w-8 text-blue-600" />
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Growth Rate</p>
              <p className="text-2xl font-bold text-gray-900">+12%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-600" />
          </div>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Credit Distribution</h3>
        <p className="text-gray-500">Detailed statistics will be implemented here</p>
      </div>
    </div>
  )
}
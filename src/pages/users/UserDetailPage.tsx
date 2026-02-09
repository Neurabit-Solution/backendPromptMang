import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, CreditCard, User, Activity, Settings } from 'lucide-react'
import { usersAPI } from '@/lib/api'
import { formatDate, formatCredits, getInitials } from '@/lib/utils'

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const { data: user, isLoading } = useQuery({
    queryKey: ['user', id],
    queryFn: () => usersAPI.get(Number(id)),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!user?.data.data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">User not found</p>
      </div>
    )
  }

  const userData = user.data.data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/admin/users')}
          className="p-2 hover:bg-gray-100 rounded-md"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Details</h1>
          <p className="text-gray-600">View and manage user information</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User Profile Card */}
        <div className="lg:col-span-1">
          <div className="card p-6">
            <div className="text-center">
              <div className="h-20 w-20 bg-primary-600 rounded-full flex items-center justify-center text-white text-2xl font-medium mx-auto mb-4">
                {getInitials(userData.name)}
              </div>
              <h2 className="text-xl font-semibold text-gray-900">{userData.name}</h2>
              <p className="text-gray-600">{userData.email}</p>
              {userData.phone && (
                <p className="text-gray-600">{userData.phone}</p>
              )}
            </div>

            <div className="mt-6 space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Credits</span>
                <span className="font-semibold">{formatCredits(userData.credits)}</span>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Status</span>
                <div className="flex space-x-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    userData.is_verified 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {userData.is_verified ? 'Verified' : 'Unverified'}
                  </span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    userData.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {userData.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Joined</span>
                <span className="text-sm">{formatDate(userData.created_at)}</span>
              </div>

              {userData.last_login && (
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Last Login</span>
                  <span className="text-sm">{formatDate(userData.last_login)}</span>
                </div>
              )}
            </div>

            <div className="mt-6 space-y-2">
              <button className="w-full btn-primary">
                <CreditCard className="h-4 w-4 mr-2" />
                Manage Credits
              </button>
              <button className="w-full btn-secondary">
                <Settings className="h-4 w-4 mr-2" />
                Edit User
              </button>
            </div>
          </div>
        </div>

        {/* User Statistics and Activity */}
        <div className="lg:col-span-2 space-y-6">
          {/* Statistics */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">{userData.total_creations}</div>
                <div className="text-sm text-gray-600">Creations</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{userData.total_likes_received}</div>
                <div className="text-sm text-gray-600">Likes Received</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{userData.battle_wins}</div>
                <div className="text-sm text-gray-600">Battle Wins</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{userData.net_credits}</div>
                <div className="text-sm text-gray-600">Net Credits</div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="h-2 w-2 bg-blue-600 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm text-gray-900">Created a new image with "Anime Style"</p>
                  <p className="text-xs text-gray-500">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="h-2 w-2 bg-green-600 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm text-gray-900">Received 15 likes on creation</p>
                  <p className="text-xs text-gray-500">5 hours ago</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="h-2 w-2 bg-purple-600 rounded-full mt-2"></div>
                <div>
                  <p className="text-sm text-gray-900">Won a battle competition</p>
                  <p className="text-xs text-gray-500">1 day ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
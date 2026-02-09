import { useState } from 'react'
import { Plus, Search, Shield, UserCog, Eye } from 'lucide-react'
import { formatDate, getInitials } from '@/lib/utils'

export default function AdminsPage() {
  const [admins] = useState([
    {
      id: 1,
      name: 'John Doe',
      email: 'john@magicpic.app',
      role: 'super_admin',
      is_active: true,
      last_login: '2024-01-15T10:30:00Z',
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@magicpic.app',
      role: 'admin',
      is_active: true,
      last_login: '2024-01-14T15:45:00Z',
      created_at: '2024-01-05T00:00:00Z',
    },
    {
      id: 3,
      name: 'Mike Johnson',
      email: 'mike@magicpic.app',
      role: 'moderator',
      is_active: false,
      last_login: '2024-01-10T09:15:00Z',
      created_at: '2024-01-10T00:00:00Z',
    },
  ])

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'super_admin':
        return 'bg-purple-100 text-purple-800'
      case 'admin':
        return 'bg-blue-100 text-blue-800'
      case 'moderator':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'super_admin':
        return Shield
      case 'admin':
        return UserCog
      case 'moderator':
        return Eye
      default:
        return UserCog
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Admin Management</h1>
          <p className="text-gray-600">Manage administrator accounts and permissions</p>
        </div>
        <button className="btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add Admin
        </button>
      </div>

      {/* Search */}
      <div className="card p-4">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search admins..."
            className="input pl-10"
          />
        </div>
      </div>

      {/* Admins Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Admin
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {admins.map((admin) => {
                const RoleIcon = getRoleIcon(admin.role)
                return (
                  <tr key={admin.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="h-10 w-10 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                          {getInitials(admin.name)}
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {admin.name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {admin.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <RoleIcon className="h-4 w-4 mr-2 text-gray-400" />
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(admin.role)}`}>
                          {admin.role.replace('_', ' ')}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        admin.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {admin.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(admin.last_login)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button className="text-primary-600 hover:text-primary-900">
                          Edit
                        </button>
                        <button className="text-red-600 hover:text-red-900">
                          Remove
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Role Permissions Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="flex items-center mb-4">
            <Shield className="h-6 w-6 text-purple-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Super Admin</h3>
          </div>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Full system access</li>
            <li>• Manage all users and admins</li>
            <li>• System settings control</li>
            <li>• All analytics and reports</li>
          </ul>
        </div>

        <div className="card p-6">
          <div className="flex items-center mb-4">
            <UserCog className="h-6 w-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Admin</h3>
          </div>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• User management</li>
            <li>• Credits management</li>
            <li>• Styles management</li>
            <li>• Analytics access</li>
          </ul>
        </div>

        <div className="card p-6">
          <div className="flex items-center mb-4">
            <Eye className="h-6 w-6 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">Moderator</h3>
          </div>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Content moderation</li>
            <li>• View user information</li>
            <li>• Handle reports</li>
            <li>• Basic analytics</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
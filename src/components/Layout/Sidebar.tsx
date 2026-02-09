import { Link, useLocation } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { 
  LayoutDashboard, 
  Users, 
  CreditCard, 
  Palette, 
  Image, 
  BarChart3, 
  Settings, 
  UserCog,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'
import { RootState, AppDispatch } from '@/store'
import { toggleSidebar } from '@/store/slices/uiSlice'
import { cn } from '@/lib/utils'

const menuItems = [
  {
    title: 'Dashboard',
    icon: LayoutDashboard,
    path: '/admin/dashboard',
  },
  {
    title: 'Users',
    icon: Users,
    path: '/admin/users',
    subItems: [
      { title: 'All Users', path: '/admin/users' },
      { title: 'Create User', path: '/admin/users/create' },
    ],
  },
  {
    title: 'Credits',
    icon: CreditCard,
    path: '/admin/credits',
    subItems: [
      { title: 'Transactions', path: '/admin/credits/transactions' },
      { title: 'Add Credits', path: '/admin/credits/add' },
      { title: 'Statistics', path: '/admin/credits/stats' },
    ],
  },
  {
    title: 'Styles',
    icon: Palette,
    path: '/admin/styles',
    subItems: [
      { title: 'All Styles', path: '/admin/styles' },
      { title: 'Create Style', path: '/admin/styles/create' },
    ],
  },
  {
    title: 'Creations',
    icon: Image,
    path: '/admin/creations',
  },
  {
    title: 'Analytics',
    icon: BarChart3,
    path: '/admin/analytics',
  },
  {
    title: 'Settings',
    icon: Settings,
    path: '/admin/settings',
  },
  {
    title: 'Admins',
    icon: UserCog,
    path: '/admin/admins',
  },
]

export default function Sidebar() {
  const dispatch = useDispatch<AppDispatch>()
  const { sidebarCollapsed } = useSelector((state: RootState) => state.ui)
  const location = useLocation()

  const handleToggle = () => {
    dispatch(toggleSidebar())
  }

  return (
    <div
      className={cn(
        'fixed left-0 top-0 h-full bg-white border-r border-gray-200 transition-all duration-300 z-40',
        sidebarCollapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!sidebarCollapsed && (
          <h1 className="text-xl font-bold text-gray-900">MagicPic Admin</h1>
        )}
        <button
          onClick={handleToggle}
          className="p-1 rounded-md hover:bg-gray-100 transition-colors"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <ChevronLeft className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path || 
            (item.subItems && item.subItems.some(sub => location.pathname === sub.path))
          
          return (
            <div key={item.path}>
              <Link
                to={item.path}
                className={cn(
                  'flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-100 text-primary-700'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                )}
              >
                <item.icon className="h-5 w-5 flex-shrink-0" />
                {!sidebarCollapsed && (
                  <span className="ml-3">{item.title}</span>
                )}
              </Link>
              
              {/* Sub Items */}
              {!sidebarCollapsed && item.subItems && isActive && (
                <div className="ml-8 mt-2 space-y-1">
                  {item.subItems.map((subItem) => (
                    <Link
                      key={subItem.path}
                      to={subItem.path}
                      className={cn(
                        'block px-3 py-1 text-sm rounded-md transition-colors',
                        location.pathname === subItem.path
                          ? 'text-primary-700 bg-primary-50'
                          : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                      )}
                    >
                      {subItem.title}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </nav>
    </div>
  )
}
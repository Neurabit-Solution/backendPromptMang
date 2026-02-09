import { ReactNode } from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '@/store'
import Sidebar from './Sidebar'
import Header from './Header'
import { cn } from '@/lib/utils'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { sidebarCollapsed } = useSelector((state: RootState) => state.ui)

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div
        className={cn(
          'transition-all duration-300',
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        )}
      >
        <Header />
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
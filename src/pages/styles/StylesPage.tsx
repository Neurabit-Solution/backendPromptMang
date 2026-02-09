import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus, Search, Grid, List } from 'lucide-react'
import { stylesAPI } from '@/lib/api'
import { formatNumber } from '@/lib/utils'

export default function StylesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')

  const { data, isLoading } = useQuery({
    queryKey: ['styles', page, search],
    queryFn: () => stylesAPI.list({
      page,
      search: search || undefined,
    }),
  })

  const styles = data?.data.data.items || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Styles</h1>
          <p className="text-gray-600">Manage AI generation styles and prompts</p>
        </div>
        <Link to="/admin/styles/create" className="btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          Create Style
        </Link>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex items-center justify-between">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search styles..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input pl-10"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded-md ${viewMode === 'grid' ? 'bg-primary-100 text-primary-600' : 'text-gray-400'}`}
            >
              <Grid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded-md ${viewMode === 'list' ? 'bg-primary-100 text-primary-600' : 'text-gray-400'}`}
            >
              <List className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Styles Grid/List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
          {styles.map((style: any) => (
            <div key={style.id} className="card p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{style.name}</h3>
                  <p className="text-sm text-gray-500">{style.category_name}</p>
                </div>
                <div className="flex space-x-1">
                  {style.is_trending && (
                    <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
                      Trending
                    </span>
                  )}
                  {style.is_new && (
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                      New
                    </span>
                  )}
                </div>
              </div>
              
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">{style.description}</p>
              
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">
                  {formatNumber(style.usage_count)} uses
                </span>
                <span className="font-medium text-primary-600">
                  {style.credits_required} credits
                </span>
              </div>
              
              <div className="mt-4 flex justify-end">
                <Link
                  to={`/admin/styles/${style.id}`}
                  className="text-primary-600 hover:text-primary-800 text-sm font-medium"
                >
                  View Details →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter, Grid, List, Eye, Star } from 'lucide-react'
import { creationsAPI } from '@/lib/api'
import { formatDate, formatNumber } from '@/lib/utils'

export default function CreationsPage() {
  const [page, setPage] = useState(1)
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [filters, setFilters] = useState({
    is_public: undefined as boolean | undefined,
    is_featured: undefined as boolean | undefined,
  })

  const { data, isLoading } = useQuery({
    queryKey: ['creations', page, filters],
    queryFn: () => creationsAPI.list({
      page,
      ...filters,
    }),
  })

  const creations = data?.data.data.creations || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Creations</h1>
        <p className="text-gray-600">Manage user-generated content and featured creations</p>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex items-center justify-between">
          <div className="flex gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search creations..."
                className="input pl-10"
              />
            </div>
            <select
              value={filters.is_public?.toString() || ''}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                is_public: e.target.value ? e.target.value === 'true' : undefined
              }))}
              className="input"
            >
              <option value="">All Visibility</option>
              <option value="true">Public</option>
              <option value="false">Private</option>
            </select>
            <select
              value={filters.is_featured?.toString() || ''}
              onChange={(e) => setFilters(prev => ({
                ...prev,
                is_featured: e.target.value ? e.target.value === 'true' : undefined
              }))}
              className="input"
            >
              <option value="">All Status</option>
              <option value="true">Featured</option>
              <option value="false">Not Featured</option>
            </select>
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

      {/* Creations Grid/List */}
      {isLoading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6' : 'space-y-4'}>
          {creations.map((creation: any) => (
            <div key={creation.id} className="card overflow-hidden">
              {viewMode === 'grid' ? (
                <>
                  <div className="aspect-square bg-gray-200 relative">
                    {creation.image_url ? (
                      <img
                        src={creation.image_url}
                        alt="Creation"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        No Image
                      </div>
                    )}
                    {creation.is_featured && (
                      <div className="absolute top-2 right-2">
                        <Star className="h-5 w-5 text-yellow-500 fill-current" />
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-600">{creation.user_name}</span>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        creation.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {creation.is_public ? 'Public' : 'Private'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{creation.style_name}</p>
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <span>{formatNumber(creation.likes_count)} likes</span>
                      <span>{formatDate(creation.created_at)}</span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-4 flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gray-200 rounded-md flex-shrink-0">
                    {creation.image_url && (
                      <img
                        src={creation.image_url}
                        alt="Creation"
                        className="w-full h-full object-cover rounded-md"
                      />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {creation.user_name}
                      </h3>
                      {creation.is_featured && (
                        <Star className="h-4 w-4 text-yellow-500 fill-current" />
                      )}
                    </div>
                    <p className="text-sm text-gray-500">{creation.style_name}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-400">
                      <span>{formatNumber(creation.likes_count)} likes</span>
                      <span>{formatDate(creation.created_at)}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      creation.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {creation.is_public ? 'Public' : 'Private'}
                    </span>
                    <button className="text-primary-600 hover:text-primary-800">
                      <Eye className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
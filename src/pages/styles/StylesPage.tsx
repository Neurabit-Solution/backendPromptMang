import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Plus, Search, Grid, List, Palette } from 'lucide-react'
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

  // Check if data is an array (direct response) or nested in data.data.styles
  const styles = Array.isArray(data?.data) ? data?.data : (data?.data?.data?.styles || [])

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
            <div key={style.id} className="group card overflow-hidden flex flex-col hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border-gray-100 hover:border-primary-200">
              <div className="relative aspect-[4/3] overflow-hidden bg-gray-100">
                {style.preview_url ? (
                  <img
                    src={style.preview_url}
                    alt={style.name}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    <Palette className="h-10 w-10 opacity-20" />
                  </div>
                )}

                {/* Overlay with tags */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
                  <div className="flex flex-wrap gap-1">
                    {style.tags?.map((tag: string) => (
                      <span key={tag} className="px-2 py-0.5 text-[10px] uppercase font-bold bg-white/20 backdrop-blur-md text-white rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="absolute top-3 right-3 flex flex-col gap-2">
                  {style.is_trending && (
                    <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-orange-500 text-white rounded-full shadow-lg border border-orange-400/50 backdrop-blur-sm">
                      Trending
                    </span>
                  )}
                  {style.is_new && (
                    <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-emerald-500 text-white rounded-full shadow-lg border border-emerald-400/50 backdrop-blur-sm">
                      New
                    </span>
                  )}
                </div>
              </div>

              <div className="p-5 flex-1 flex flex-col">
                <div className="mb-3">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="text-lg font-bold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-1">
                      {style.name}
                    </h3>
                    <span className={`h-2 w-2 rounded-full ${style.is_active ? 'bg-green-500' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'}`}></span>
                  </div>
                  <p className="text-xs font-medium text-primary-500 uppercase tracking-wide">
                    Category ID: {style.category_id}
                  </p>
                </div>

                <p className="text-sm text-gray-500 mb-5 line-clamp-2 italic leading-relaxed">
                  "{style.description}"
                </p>

                <div className="mt-auto flex items-center justify-between bg-gray-50/80 rounded-xl p-3 border border-gray-100 group-hover:bg-white group-hover:border-primary-100 transition-colors">
                  <div className="flex flex-col">
                    <span className="text-[10px] uppercase font-bold text-gray-400 tracking-tight">Requirement</span>
                    <span className="text-sm font-extrabold text-gray-900">
                      {style.credits_required} Credits
                    </span>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-[10px] uppercase font-bold text-gray-400 tracking-tight">Popularity</span>
                    <span className="text-sm font-extrabold text-primary-600 uppercase">
                      {formatNumber(style.uses_count || 0)} Uses
                    </span>
                  </div>
                </div>

                <div className="mt-4">
                  <Link
                    to={`/admin/styles/${style.id}`}
                    className="w-full flex items-center justify-center py-2.5 rounded-xl bg-gray-900 text-white text-xs font-bold uppercase tracking-widest hover:bg-primary-600 transition-all duration-300 shadow-lg shadow-gray-200 hover:shadow-primary-200"
                  >
                    Manage Style
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
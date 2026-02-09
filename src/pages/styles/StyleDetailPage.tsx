import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Edit, Trash2 } from 'lucide-react'
import { stylesAPI } from '@/lib/api'
import { formatNumber } from '@/lib/utils'

export default function StyleDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: style, isLoading } = useQuery({
    queryKey: ['style', id],
    queryFn: () => stylesAPI.get(Number(id)),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!style?.data.data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Style not found</p>
      </div>
    )
  }

  const styleData = style.data.data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button className="p-2 hover:bg-gray-100 rounded-md">
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{styleData.name}</h1>
            <p className="text-gray-600">{styleData.category_name}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          <button className="btn-secondary">
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </button>
          <button className="btn-danger">
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Style Info */}
        <div className="lg:col-span-2 space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Description</h3>
            <p className="text-gray-600">{styleData.description}</p>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Prompt Template</h3>
            <div className="bg-gray-50 p-4 rounded-md">
              <code className="text-sm text-gray-800">{styleData.prompt_template}</code>
            </div>
          </div>

          {styleData.negative_prompt && (
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Negative Prompt</h3>
              <div className="bg-gray-50 p-4 rounded-md">
                <code className="text-sm text-gray-800">{styleData.negative_prompt}</code>
              </div>
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Usage Count</span>
                <span className="font-semibold">{formatNumber(styleData.usage_count)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Credits Required</span>
                <span className="font-semibold">{styleData.credits_required}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Status</span>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  styleData.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {styleData.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {styleData.tags?.map((tag: string, index: number) => (
                <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded-md">
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
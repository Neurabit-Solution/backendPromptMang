import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Star, Eye, Heart, Flag } from 'lucide-react'
import { creationsAPI } from '@/lib/api'
import { formatDate, formatNumber } from '@/lib/utils'

export default function CreationDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data: creation, isLoading } = useQuery({
    queryKey: ['creation', id],
    queryFn: () => creationsAPI.get(Number(id)),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!creation?.data.data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Creation not found</p>
      </div>
    )
  }

  const creationData = creation.data.data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button className="p-2 hover:bg-gray-100 rounded-md">
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Creation Details</h1>
          <p className="text-gray-600">View and manage creation</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Image */}
        <div className="card p-6">
          <div className="aspect-square bg-gray-200 rounded-lg overflow-hidden mb-4">
            {creationData.image_url ? (
              <img
                src={creationData.image_url}
                alt="Creation"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                No Image Available
              </div>
            )}
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <Heart className="h-4 w-4" />
                <span>{formatNumber(creationData.likes_count)}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Eye className="h-4 w-4" />
                <span>{formatNumber(creationData.views_count)}</span>
              </div>
              {creationData.reports_count > 0 && (
                <div className="flex items-center space-x-1 text-red-600">
                  <Flag className="h-4 w-4" />
                  <span>{creationData.reports_count}</span>
                </div>
              )}
            </div>
            {creationData.is_featured && (
              <Star className="h-5 w-5 text-yellow-500 fill-current" />
            )}
          </div>
        </div>

        {/* Details */}
        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Creation Info</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Creator</span>
                <span className="font-medium">{creationData.user_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Email</span>
                <span className="text-sm">{creationData.user_email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Style</span>
                <span className="font-medium">{creationData.style_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Credits Spent</span>
                <span className="font-medium">{creationData.credits_spent}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Processing Time</span>
                <span className="font-medium">{creationData.processing_time}s</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Created</span>
                <span className="font-medium">{formatDate(creationData.created_at)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Visibility</span>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  creationData.is_public ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {creationData.is_public ? 'Public' : 'Private'}
                </span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Prompt</h3>
            <div className="bg-gray-50 p-4 rounded-md">
              <p className="text-sm text-gray-800">{creationData.prompt}</p>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
            <div className="space-y-3">
              <button className="w-full btn-primary">
                {creationData.is_featured ? 'Remove from Featured' : 'Add to Featured'}
              </button>
              <button className="w-full btn-secondary">
                {creationData.is_public ? 'Make Private' : 'Make Public'}
              </button>
              {creationData.reports_count > 0 && (
                <button className="w-full btn-danger">
                  View Reports ({creationData.reports_count})
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
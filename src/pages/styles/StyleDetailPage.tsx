import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ArrowLeft, Edit, Trash2, Save, X, Upload, Loader2, Palette } from 'lucide-react'
import { stylesAPI, categoriesAPI } from '@/lib/api'
import { formatNumber } from '@/lib/utils'
import { toast } from 'react-hot-toast'

const updateStyleSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().min(1, 'Description is required'),
  category_id: z.number().min(1, 'Category is required'),
  prompt_template: z.string().min(1, 'Prompt template is required'),
  negative_prompt: z.string().optional(),
  credits_required: z.number().min(0, 'Credits must be positive'),
  is_active: z.boolean(),
  is_trending: z.boolean(),
  is_new: z.boolean(),
})

type UpdateStyleFormData = z.infer<typeof updateStyleSchema>

export default function StyleDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [isEditing, setIsEditing] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [categories, setCategories] = useState<any[]>([])
  const [previewImage, setPreviewImage] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  const { data: style, isLoading } = useQuery({
    queryKey: ['style', id],
    queryFn: () => stylesAPI.get(Number(id)),
    enabled: !!id,
  })

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<UpdateStyleFormData>({
    resolver: zodResolver(updateStyleSchema),
  })

  useEffect(() => {
    if (style?.data) {
      const s = style.data.data || style.data
      reset({
        name: s.name,
        description: s.description,
        category_id: s.category_id,
        prompt_template: s.prompt_template,
        negative_prompt: s.negative_prompt || '',
        credits_required: s.credits_required,
        is_active: s.is_active,
        is_trending: s.is_trending,
        is_new: s.is_new,
      })
      setPreviewUrl(s.preview_url)
    }
  }, [style, reset])

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await categoriesAPI.list()
        const cats = Array.isArray(response.data) ? response.data : (response.data?.data?.categories || [])
        setCategories(cats)
      } catch (error) {
        console.error('Error fetching categories:', error)
      }
    }
    if (isEditing) {
      fetchCategories()
    }
  }, [isEditing])

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Image size should be less than 5MB')
        return
      }
      setPreviewImage(file)
      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
    }
  }

  const onSubmit = async (data: UpdateStyleFormData) => {
    setIsSubmitting(true)
    try {
      const formData = new FormData()
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined) {
          formData.append(key, value.toString())
        }
      })
      if (previewImage) {
        formData.append('preview_image', previewImage)
      }

      await stylesAPI.update(Number(id), formData)
      toast.success('Style updated successfully')
      setIsEditing(false)
      queryClient.invalidateQueries({ queryKey: ['style', id] })
    } catch (error: any) {
      console.error('Error updating style:', error)
      toast.error(error.response?.data?.message || 'Failed to update style')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to PERMANENTLY delete this style?')) return

    try {
      await stylesAPI.delete(Number(id))
      toast.success('Style deleted successfully')
      navigate('/admin/styles')
    } catch (error) {
      console.error('Error deleting style:', error)
      toast.error('Failed to delete style')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!style?.data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Style not found</p>
        <button onClick={() => navigate('/admin/styles')} className="mt-4 text-primary-600">
          Back to Styles
        </button>
      </div>
    )
  }

  const styleData = style.data.data || style.data

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/admin/styles')}
            className="p-2 hover:bg-gray-100 rounded-md"
          >
            <ArrowLeft className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isEditing ? 'Edit Style' : styleData.name}
            </h1>
            <p className="text-gray-600">{styleData.category_name}</p>
          </div>
        </div>
        <div className="flex space-x-2">
          {isEditing ? (
            <>
              <button
                onClick={() => {
                  setIsEditing(false)
                  setPreviewUrl(styleData.preview_url)
                  setPreviewImage(null)
                  reset()
                }}
                className="btn-secondary"
                disabled={isSubmitting}
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </button>
              <button
                onClick={handleSubmit(onSubmit)}
                className="btn-primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Save className="h-4 w-4 mr-2" />
                )}
                Save Changes
              </button>
            </>
          ) : (
            <>
              <button onClick={() => setIsEditing(true)} className="btn-secondary">
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </button>
              <button onClick={handleDelete} className="btn-danger">
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </button>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {isEditing ? (
            <div className="card p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Style Name *
                  </label>
                  <input {...register('name')} className="input" />
                  {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category *
                  </label>
                  <select {...register('category_id', { valueAsNumber: true })} className="input">
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.icon} {cat.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <textarea {...register('description')} rows={3} className="input" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Prompt Template *
                </label>
                <textarea {...register('prompt_template')} rows={6} className="input" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Negative Prompt (Optional)
                </label>
                <textarea {...register('negative_prompt')} rows={3} className="input" />
              </div>
            </div>
          ) : (
            <>
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Description</h3>
                <p className="text-gray-600">{styleData.description}</p>
              </div>

              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Prompt Template</h3>
                <div className="bg-gray-50 p-4 rounded-md">
                  <code className="text-sm text-gray-800 whitespace-pre-wrap">{styleData.prompt_template}</code>
                </div>
              </div>

              {styleData.negative_prompt && (
                <div className="card p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Negative Prompt</h3>
                  <div className="bg-gray-50 p-4 rounded-md">
                    <code className="text-sm text-gray-800 whitespace-pre-wrap">{styleData.negative_prompt}</code>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        <div className="space-y-6">
          {/* Image */}
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Preview Image</h3>
            <div className="relative aspect-square rounded-lg overflow-hidden bg-gray-100 border border-gray-200">
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  <Palette className="h-12 w-12" />
                </div>
              )}
              {isEditing && (
                <label className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 opacity-0 hover:opacity-100 cursor-pointer transition-opacity">
                  <div className="text-white text-center">
                    <Upload className="h-8 w-8 mx-auto mb-2" />
                    <span className="text-sm font-medium">Change Image</span>
                  </div>
                  <input type="file" className="hidden" accept="image/*" onChange={handleImageChange} />
                </label>
              )}
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {isEditing ? 'Settings' : 'Statistics'}
            </h3>
            {isEditing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Credits Required
                  </label>
                  <input
                    type="number"
                    {...register('credits_required', { valueAsNumber: true })}
                    className="input"
                  />
                </div>
                <div className="space-y-3 pt-2">
                  <div className="flex items-center">
                    <input type="checkbox" {...register('is_active')} id="is_active" className="h-4 w-4 text-primary-600 rounded" />
                    <label htmlFor="is_active" className="ml-2 text-sm text-gray-900">Active</label>
                  </div>
                  <div className="flex items-center">
                    <input type="checkbox" {...register('is_trending')} id="is_trending" className="h-4 w-4 text-primary-600 rounded" />
                    <label htmlFor="is_trending" className="ml-2 text-sm text-gray-900">Trending</label>
                  </div>
                  <div className="flex items-center">
                    <input type="checkbox" {...register('is_new')} id="is_new" className="h-4 w-4 text-primary-600 rounded" />
                    <label htmlFor="is_new" className="ml-2 text-sm text-gray-900">New</label>
                  </div>
                </div>
              </div>
            ) : (
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
                  <span
                    className={`px-2 py-1 text-xs rounded-full ${styleData.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}
                  >
                    {styleData.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
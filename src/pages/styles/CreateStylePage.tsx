import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Upload, X, Loader2 } from 'lucide-react'
import { stylesAPI, categoriesAPI } from '@/lib/api'
import { toast } from 'react-hot-toast'

const createStyleSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().min(1, 'Description is required'),
  category_id: z.number().min(1, 'Category is required'),
  prompt_template: z.string().min(1, 'Prompt template is required'),
  negative_prompt: z.string().optional(),
  credits_required: z.number().min(0, 'Credits must be positive'),
  is_active: z.boolean().default(true),
  is_trending: z.boolean().default(false),
  is_new: z.boolean().default(true),
})

type CreateStyleFormData = z.infer<typeof createStyleSchema>

export default function CreateStylePage() {
  const navigate = useNavigate()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [categories, setCategories] = useState<any[]>([])
  const [previewImage, setPreviewImage] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateStyleFormData>({
    resolver: zodResolver(createStyleSchema),
    defaultValues: {
      credits_required: 100,
      is_active: true,
      is_trending: false,
      is_new: true,
    },
  })

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await categoriesAPI.list()
        const cats = Array.isArray(response.data) ? response.data : (response.data?.data?.categories || [])
        setCategories(cats)
      } catch (error) {
        console.error('Error fetching categories:', error)
        toast.error('Failed to load categories')
      }
    }
    fetchCategories()
  }, [])

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

  const removeImage = () => {
    setPreviewImage(null)
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl)
      setPreviewUrl(null)
    }
  }

  const onSubmit = async (data: CreateStyleFormData) => {
    if (!previewImage) {
      toast.error('Preview image is required')
      return
    }

    setIsSubmitting(true)
    try {
      const formData = new FormData()
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined) {
          formData.append(key, value.toString())
        }
      })
      formData.append('preview_image', previewImage)

      await stylesAPI.create(formData)
      toast.success('Style created successfully')
      navigate('/admin/styles')
    } catch (error: any) {
      console.error('Error creating style:', error)
      toast.error(error.response?.data?.message || 'Failed to create style')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/admin/styles')}
          className="p-2 hover:bg-gray-100 rounded-md"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Style</h1>
          <p className="text-gray-600">Add a new AI generation style</p>
        </div>
      </div>

      {/* Form */}
      <div className="max-w-4xl">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {/* Basic Information */}
              <div className="card p-6 space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Basic Information</h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Style Name *
                    </label>
                    <input
                      {...register('name')}
                      type="text"
                      className="input"
                      placeholder="e.g., Anime Style"
                    />
                    {errors.name && (
                      <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category *
                    </label>
                    <select
                      {...register('category_id', { valueAsNumber: true })}
                      className="input"
                    >
                      <option value="">Select category</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.icon} {cat.name}
                        </option>
                      ))}
                    </select>
                    {errors.category_id && (
                      <p className="mt-1 text-sm text-red-600">{errors.category_id.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <textarea
                    {...register('description')}
                    rows={3}
                    className="input"
                    placeholder="Describe this style..."
                  />
                  {errors.description && (
                    <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                  )}
                </div>
              </div>

              {/* AI Configuration */}
              <div className="card p-6 space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">AI Configuration</h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prompt Template *
                  </label>
                  <textarea
                    {...register('prompt_template')}
                    rows={6}
                    className="input"
                    placeholder="Enter the AI prompt template..."
                  />
                  {errors.prompt_template && (
                    <p className="mt-1 text-sm text-red-600">{errors.prompt_template.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Negative Prompt (Optional)
                  </label>
                  <textarea
                    {...register('negative_prompt')}
                    rows={3}
                    className="input"
                    placeholder="What to avoid in generation..."
                  />
                </div>
              </div>
            </div>

            <div className="space-y-6">
              {/* Image Upload */}
              <div className="card p-6 space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Preview Image *</h3>
                <div className="relative">
                  {previewUrl ? (
                    <div className="relative rounded-lg overflow-hidden border border-gray-200">
                      <img src={previewUrl} alt="Preview" className="w-full aspect-square object-cover" />
                      <button
                        type="button"
                        onClick={removeImage}
                        className="absolute top-2 right-2 p-1 bg-red-600 text-white rounded-full hover:bg-red-700 shadow-md transition-colors"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <label className="flex flex-col items-center justify-center w-full aspect-square rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors">
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <Upload className="h-10 w-10 text-gray-400 mb-3" />
                        <p className="text-sm text-gray-500">Click to upload</p>
                        <p className="text-xs text-gray-400 mt-1">PNG, JPG up to 5MB</p>
                      </div>
                      <input
                        type="file"
                        className="hidden"
                        accept="image/*"
                        onChange={handleImageChange}
                      />
                    </label>
                  )}
                </div>
              </div>

              {/* Settings */}
              <div className="card p-6 space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Settings</h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Credits Required *
                  </label>
                  <input
                    {...register('credits_required', { valueAsNumber: true })}
                    type="number"
                    min="0"
                    className="input"
                    placeholder="100"
                  />
                  {errors.credits_required && (
                    <p className="mt-1 text-sm text-red-600">{errors.credits_required.message}</p>
                  )}
                </div>

                <div className="space-y-3">
                  <div className="flex items-center">
                    <input
                      {...register('is_active')}
                      type="checkbox"
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      id="is_active"
                    />
                    <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900">
                      Style is active
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      {...register('is_trending')}
                      type="checkbox"
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      id="is_trending"
                    />
                    <label htmlFor="is_trending" className="ml-2 block text-sm text-gray-900">
                      Mark as trending
                    </label>
                  </div>

                  <div className="flex items-center">
                    <input
                      {...register('is_new')}
                      type="checkbox"
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      id="is_new"
                    />
                    <label htmlFor="is_new" className="ml-2 block text-sm text-gray-900">
                      Mark as new
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/admin/styles')}
              className="btn-secondary"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Style'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
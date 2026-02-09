import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

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

  const onSubmit = (data: CreateStyleFormData) => {
    console.log('Create style:', data)
    // Implementation will be added
  }

  return (
    <div className="space-y-6">
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
                  <option value={1}>Anime</option>
                  <option value={2}>Realistic</option>
                  <option value={3}>Abstract</option>
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

          <div className="card p-6 space-y-6">
            <h3 className="text-lg font-semibold text-gray-900">Settings</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
            </div>

            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  {...register('is_active')}
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Style is active
                </label>
              </div>

              <div className="flex items-center">
                <input
                  {...register('is_trending')}
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Mark as trending
                </label>
              </div>

              <div className="flex items-center">
                <input
                  {...register('is_new')}
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Mark as new
                </label>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/admin/styles')}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Style
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
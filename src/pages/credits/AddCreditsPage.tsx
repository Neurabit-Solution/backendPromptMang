import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Search } from 'lucide-react'
import { creditsAPI, usersAPI } from '@/lib/api'
import { formatCredits } from '@/lib/utils'
import toast from 'react-hot-toast'

const addCreditsSchema = z.object({
  user_id: z.number().min(1, 'Please select a user'),
  amount: z.number().min(1, 'Amount must be positive'),
  description: z.string().min(1, 'Description is required'),
  reference_id: z.string().optional(),
  notify_user: z.boolean().default(true),
})

type AddCreditsFormData = z.infer<typeof addCreditsSchema>

export default function AddCreditsPage() {
  const navigate = useNavigate()
  const [userSearch, setUserSearch] = useState('')
  const [selectedUser, setSelectedUser] = useState<any>(null)

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<AddCreditsFormData>({
    resolver: zodResolver(addCreditsSchema),
    defaultValues: {
      notify_user: true,
    },
  })

  const { data: users } = useQuery({
    queryKey: ['users-search', userSearch],
    queryFn: () => usersAPI.list({ search: userSearch, limit: 10 }),
    enabled: userSearch.length > 2,
  })

  const addCreditsMutation = useMutation({
    mutationFn: creditsAPI.add,
    onSuccess: () => {
      toast.success('Credits added successfully!')
      navigate('/admin/credits/transactions')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error?.message || 'Failed to add credits')
    },
  })

  const onSubmit = (data: AddCreditsFormData) => {
    addCreditsMutation.mutate(data)
  }

  const handleUserSelect = (user: any) => {
    setSelectedUser(user)
    setValue('user_id', user.id)
    setUserSearch('')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/admin/credits/transactions')}
          className="p-2 hover:bg-gray-100 rounded-md"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Add Credits</h1>
          <p className="text-gray-600">Grant credits to a user account</p>
        </div>
      </div>

      {/* Form */}
      <div className="max-w-2xl">
        <form onSubmit={handleSubmit(onSubmit)} className="card p-6 space-y-6">
          {/* User Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select User *
            </label>
            {selectedUser ? (
              <div className="flex items-center justify-between p-3 border border-gray-300 rounded-md bg-gray-50">
                <div>
                  <div className="font-medium">{selectedUser.name}</div>
                  <div className="text-sm text-gray-500">{selectedUser.email}</div>
                  <div className="text-sm text-gray-500">
                    Current balance: {formatCredits(selectedUser.credits)}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setSelectedUser(null)
                    setValue('user_id', 0)
                  }}
                  className="text-red-600 hover:text-red-800"
                >
                  Change
                </button>
              </div>
            ) : (
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  className="input pl-10"
                  placeholder="Search users by name or email..."
                />
                {users && userSearch.length > 2 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                    {users.data.data.items.map((user: any) => (
                      <button
                        key={user.id}
                        type="button"
                        onClick={() => handleUserSelect(user)}
                        className="w-full text-left px-4 py-2 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                      >
                        <div className="font-medium">{user.name}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                        <div className="text-sm text-gray-500">
                          {formatCredits(user.credits)}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
            {errors.user_id && (
              <p className="mt-1 text-sm text-red-600">{errors.user_id.message}</p>
            )}
          </div>

          {/* Amount */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Credits Amount *
            </label>
            <input
              {...register('amount', { valueAsNumber: true })}
              type="number"
              min="1"
              className="input"
              placeholder="Enter amount"
            />
            {errors.amount && (
              <p className="mt-1 text-sm text-red-600">{errors.amount.message}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              {...register('description')}
              rows={3}
              className="input"
              placeholder="Reason for adding credits..."
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          {/* Reference ID */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reference ID (Optional)
            </label>
            <input
              {...register('reference_id')}
              type="text"
              className="input"
              placeholder="Transaction reference"
            />
          </div>

          {/* Notify User */}
          <div className="flex items-center">
            <input
              {...register('notify_user')}
              type="checkbox"
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-900">
              Notify user about credit addition
            </label>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/admin/credits/transactions')}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={addCreditsMutation.isPending}
              className="btn-primary"
            >
              {addCreditsMutation.isPending ? 'Adding...' : 'Add Credits'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
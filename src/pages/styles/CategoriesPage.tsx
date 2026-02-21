import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2, X, Save, Upload, Loader2, ListTree } from 'lucide-react'
import { categoriesAPI } from '@/lib/api'
import { toast } from 'react-hot-toast'

export default function CategoriesPage() {
    const queryClient = useQueryClient()
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [editingCategory, setEditingCategory] = useState<any>(null)
    const [isSubmitting, setIsSubmitting] = useState(false)

    // Form state
    const [formData, setFormData] = useState({
        name: '',
        icon: '',
        description: '',
        display_order: 0,
        is_active: true,
    })
    const [previewImage, setPreviewImage] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)

    const { data, isLoading } = useQuery({
        queryKey: ['categories'],
        queryFn: () => categoriesAPI.list(),
    })

    const categories = Array.isArray(data?.data) ? data?.data : (data?.data?.data?.categories || [])

    const handleOpenModal = (category: any = null) => {
        if (category) {
            setEditingCategory(category)
            setFormData({
                name: category.name,
                icon: category.icon,
                description: category.description,
                display_order: category.display_order,
                is_active: category.is_active,
            })
            setPreviewUrl(category.preview_url)
        } else {
            setEditingCategory(null)
            setFormData({
                name: '',
                icon: '',
                description: '',
                display_order: 0,
                is_active: true,
            })
            setPreviewUrl(null)
        }
        setPreviewImage(null)
        setIsModalOpen(true)
    }

    const handleCloseModal = () => {
        setIsModalOpen(false)
        setEditingCategory(null)
        setPreviewImage(null)
        setPreviewUrl(null)
    }

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) {
            setPreviewImage(file)
            setPreviewUrl(URL.createObjectURL(file))
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSubmitting(true)

        try {
            const form = new FormData()
            form.append('name', formData.name)
            form.append('icon', formData.icon)
            form.append('description', formData.description)
            form.append('display_order', formData.display_order.toString())
            form.append('is_active', formData.is_active.toString())

            if (previewImage) {
                form.append('preview_image', previewImage)
            }

            if (editingCategory) {
                await categoriesAPI.update(editingCategory.id, form)
                toast.success('Category updated successfully')
            } else {
                await categoriesAPI.create(form)
                toast.success('Category created successfully')
            }

            queryClient.invalidateQueries({ queryKey: ['categories'] })
            handleCloseModal()
        } catch (error: any) {
            console.error('Error saving category:', error)
            toast.error(error.response?.data?.message || 'Failed to save category')
        } finally {
            setIsSubmitting(false)
        }
    }

    const handleDelete = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this category? All associated styles will also be affected.')) return

        try {
            await categoriesAPI.delete(id)
            toast.success('Category deleted successfully')
            queryClient.invalidateQueries({ queryKey: ['categories'] })
        } catch (error) {
            console.error('Error deleting category:', error)
            toast.error('Failed to delete category')
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Style Categories</h1>
                    <p className="text-gray-600">Organize your generation styles into categories</p>
                </div>
                <button onClick={() => handleOpenModal()} className="btn-primary">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Category
                </button>
            </div>

            {isLoading ? (
                <div className="flex items-center justify-center min-h-64">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {categories.map((category: any) => (
                        <div key={category.id} className="card overflow-hidden">
                            <div className="aspect-video relative bg-gray-100">
                                {category.preview_url ? (
                                    <img src={category.preview_url} alt={category.name} className="w-full h-full object-cover" />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-gray-300">
                                        <ListTree className="h-12 w-12" />
                                    </div>
                                )}
                                <div className="absolute top-2 left-2 px-2 py-1 bg-white/90 backdrop-blur-sm rounded text-lg shadow-sm">
                                    {category.icon}
                                </div>
                            </div>
                            <div className="p-6">
                                <div className="flex items-start justify-between mb-2">
                                    <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
                                    <span className={`px-2 py-0.5 text-xs rounded-full ${category.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                                        }`}>
                                        {category.is_active ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                                <p className="text-sm text-gray-500 mb-4 line-clamp-2">{category.description}</p>
                                <div className="flex items-center justify-between mt-auto">
                                    <span className="text-xs text-gray-400">Order: {category.display_order}</span>
                                    <div className="flex space-x-2">
                                        <button
                                            onClick={() => handleOpenModal(category)}
                                            className="p-1.5 text-gray-500 hover:text-primary-600 transition-colors"
                                        >
                                            <Edit className="h-4 w-4" />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(category.id)}
                                            className="p-1.5 text-gray-500 hover:text-red-600 transition-colors"
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 z-50 overflow-y-auto">
                    <div className="flex items-center justify-center min-h-screen p-4 text-center sm:block sm:p-0">
                        <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                            <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
                        </div>
                        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                            <form onSubmit={handleSubmit}>
                                <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                                    <div className="flex items-center justify-between mb-4 pb-4 border-b">
                                        <h3 className="text-lg font-medium text-gray-900">
                                            {editingCategory ? 'Edit Category' : 'Add New Category'}
                                        </h3>
                                        <button type="button" onClick={handleCloseModal} className="text-gray-400 hover:text-gray-500">
                                            <X className="h-6 w-6" />
                                        </button>
                                    </div>

                                    <div className="space-y-4">
                                        <div className="grid grid-cols-4 gap-4">
                                            <div className="col-span-3">
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                                                <input
                                                    type="text"
                                                    required
                                                    value={formData.name}
                                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                                    className="input"
                                                    placeholder="e.g. Trending"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Icon</label>
                                                <input
                                                    type="text"
                                                    required
                                                    value={formData.icon}
                                                    onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                                                    className="input text-center"
                                                    placeholder="🔥"
                                                />
                                            </div>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                            <textarea
                                                required
                                                value={formData.description}
                                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                                rows={3}
                                                className="input"
                                                placeholder="Brief category description..."
                                            />
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Display Order</label>
                                                <input
                                                    type="number"
                                                    value={formData.display_order}
                                                    onChange={(e) => setFormData({ ...formData, display_order: parseInt(e.target.value) })}
                                                    className="input"
                                                />
                                            </div>
                                            <div className="flex items-end pb-3">
                                                <label className="flex items-center cursor-pointer">
                                                    <input
                                                        type="checkbox"
                                                        checked={formData.is_active}
                                                        onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                                        className="h-4 w-4 text-primary-600 rounded"
                                                    />
                                                    <span className="ml-2 text-sm text-gray-700">Active</span>
                                                </label>
                                            </div>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Preview Image</label>
                                            <div className="relative aspect-video rounded-lg overflow-hidden border-2 border-dashed border-gray-300 bg-gray-50 flex items-center justify-center">
                                                {previewUrl ? (
                                                    <>
                                                        <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
                                                        <div className="absolute inset-0 bg-black/40 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center">
                                                            <label className="btn-secondary cursor-pointer">
                                                                Change Image
                                                                <input type="file" className="hidden" accept="image/*" onChange={handleImageChange} />
                                                            </label>
                                                        </div>
                                                    </>
                                                ) : (
                                                    <label className="flex flex-col items-center justify-center cursor-pointer p-4 w-full h-full">
                                                        <Upload className="h-8 w-8 text-gray-400 mb-2" />
                                                        <span className="text-sm text-gray-500">Upload category icon image</span>
                                                        <input type="file" className="hidden" accept="image/*" onChange={handleImageChange} />
                                                    </label>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                                    <button
                                        type="submit"
                                        className="btn-primary w-full sm:ml-3 sm:w-auto"
                                        disabled={isSubmitting}
                                    >
                                        {isSubmitting ? (
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                        ) : (
                                            <>
                                                <Save className="h-4 w-4 mr-2" />
                                                {editingCategory ? 'Update' : 'Create'}
                                            </>
                                        )}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={handleCloseModal}
                                        className="btn-secondary w-full mt-3 sm:mt-0 sm:w-auto"
                                        disabled={isSubmitting}
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

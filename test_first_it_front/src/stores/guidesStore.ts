import { defineStore } from 'pinia'
import { apiInstance } from '../api/api'
import type { defaultGuideItem, GuideItem, guideWithRelationsItem } from '../api/api'

export type GuideType = 'statuses' | 'operations' | 'categories' | 'subcategories'

interface GuideState {
    statuses: GuideItem[]
    operations: GuideItem[]
    categories: GuideItem[]
    subcategories: guideWithRelationsItem[]
    loading: boolean,
    error: string | null,
    expandedSections: Record<string, boolean>
}

export const useGuideStore = defineStore('guides', {
    state: (): GuideState => ({
        statuses: [],
        operations: [],
        categories: [],
        subcategories: [],
        loading: false,
        error: null,
        expandedSections: {
            statuses: true,
            operations: true,
            categories: true,
            subcategories: true
        }
    }),

    getters: {
        getGuideByType: (state) => (type: GuideType) => {
            switch (type) {
                case 'statuses': return state.statuses
                case 'categories': return state.categories
                case 'operations': return state.operations
                case 'subcategories': return state.subcategories
                default: return []
            }
        },

        getSubcategoriesForCategory: (state) => (categoryId: string) => {
            return state.subcategories.filter(sub =>
                sub.category && sub.category.id === categoryId // Добавляем проверку на существование category
            )
        },

        getGuideItemById: (state) => (type: GuideType, itemId: string) => {
            const guide = state[type] as GuideItem[]
            return guide.find(item => item.id === itemId)
        },

        getCategoryTree: (state) => {
            return state.categories.map(category => ({
                ...category,
                subcategories: state.subcategories.filter(sub =>
                    sub.category && sub.category.id === category.id // Проверка на существование category
                )
            }))
        }
    },

    actions: {
        toggleSection(type: GuideType) {
            this.expandedSections[type] = !this.expandedSections[type]
        },
        async fetchGuide(type: GuideType) {
            this.loading = true
            this.error = null

            try {
                // Да, any -- костыль
                const data: any = await apiInstance.get(`/guides/${type}/`).then(r => r.data.list)

                const items: any = data.map((item: any) => ({
                    id: item.id,
                    name: item.name,
                    category: item.category ? item.category : null // Для подкатегорий
                }))

                switch (type) {
                    case 'statuses':
                        this.statuses = items;
                        break
                    case 'operations':
                        this.operations = items;
                        break
                    case 'categories':
                        this.categories = items;
                        break
                    case 'subcategories':
                        this.subcategories = items;
                        break
                }

                return items
            } catch (error: any) {
                this.error = error.message || `Failed to load ${type}`
                throw error
            } finally {
                this.loading = false
            }
        },

        async createGuide(type: GuideType, name: string, category?: GuideItem) {
            this.loading = true
            this.error = null

            try {
                const payload = category || type === 'subcategories'
                    ? { name, category: category?.id }
                    : { name }
                const response = await apiInstance.post(`/guides/${type}/`, payload)

                const newItem = {
                    id: response.data.id,
                    name: response.data.name,
                    category: response.data.category || null
                }
                switch (type) {
                    case 'statuses':
                        this.statuses.push(newItem)
                        break
                    case 'operations':
                        this.operations.push(newItem)
                        break
                    case 'categories':
                        this.categories.push(newItem)
                        break
                    case 'subcategories':
                        this.subcategories.push(newItem as guideWithRelationsItem)
                        break
                }

                return newItem
            } catch (error: any) {
                this.error = error.message || `Failed to create ${type}`
                throw error
            } finally {
                this.loading = false
            }
        },

        async updateGuideItem(type: GuideType, data: GuideItem | guideWithRelationsItem) {
            this.loading = true
            this.error = null

            try {
                await apiInstance.patch(`/guides/${type}/${data.id}`, data)

                const items = this[type] as Array<GuideItem | guideWithRelationsItem>
                const index = items.findIndex(item => item.id === data.id)

                if (index !== -1) {
                    items[index] = { ...items[index], ...data }
                }
            } catch (error: any) {
                this.error = error.messgae || `Failed to update guide ${type}`
                throw error
            } finally {
                console.log(`Guide item of ${type} update successfull`)
                this.loading = false
            }
        },

        async deleteGuideItem(type: GuideType, itemId: string) {
            this.loading = true
            this.error = null

            try {
                await apiInstance.delete(`/guides/${type}/${itemId}`)

                const items = this[type] as Array<GuideItem | guideWithRelationsItem>
                const index = items.findIndex(item => item.id === itemId)

                if (index !== -1) {
                    items.splice(index, 1)
                }
            } catch (error: any) {
                this.error = error.message || `Failed to delete guide item of ${type}`
                throw error
            } finally {
                console.log(`Guide item of ${type} delete successfull`)
                this.loading = false
            }
        },

        async fetchAllGuides() {
            this.loading = true
            this.error = null

            try {
                await Promise.all([
                    this.fetchGuide('statuses'),
                    this.fetchGuide('categories'),
                    this.fetchGuide('operations'),
                    this.fetchGuide('subcategories'),
                ])
            } catch (error: any) {
                this.error = `Failed to load some guides: ${error.message}`
            } finally {
                this.loading = false
            }

        }
    }
})
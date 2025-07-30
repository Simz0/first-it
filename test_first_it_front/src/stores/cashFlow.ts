import { defineStore } from 'pinia'
import { apiInstance } from '../api/api'
import type { CashFlowItem, CashFlowItemPayload } from '../api/api'

interface CashFlowState {
  items: CashFlowItem[]
  loading: boolean
  error: string | null
  filters: {
    dateRange: [string, string] | null
    category: string | null
    subcategory: string | null
    operationType: string | null
    status: string | null
  }
  sortField: 'created_at' | 'amount' | 'type' | 'status'
  sortDirection: 'asc' | 'desc'
}

export const useCashFlowStore = defineStore('cashFlow', {
  state: (): CashFlowState => ({
    items: [],
    loading: false,
    error: null,
    filters: {
      dateRange: null,
      category: null,
      subcategory: null,
      operationType: null,
      status: null
    },
    sortField: 'created_at',
    sortDirection: 'desc'
  }),

  getters: {
    // Фильтрованные и отсортированные элементы
    filteredItems(state): CashFlowItem[] {
      let result = [...state.items]

      // Применяем фильтры
      if (state.filters.dateRange) {
        const [start, end] = state.filters.dateRange
        result = result.filter(item =>
          new Date(item.created_at) >= new Date(start) && new Date(item.created_at) <= new Date(end)
        )
      }

      if (state.filters.category) {
        result = result.filter(item =>
          item.category.category.id === state.filters.category
        )
      }

      if (state.filters.subcategory) {
        result = result.filter(item =>
          item.category.id === state.filters.subcategory
        )
      }

      if (state.filters.operationType) {
        result = result.filter(item =>
          item.type.id === state.filters.operationType
        )
      }

      if (state.filters.status) {
        result = result.filter(item =>
          item.status.id === state.filters.status
        )
      }
      return result.sort((a, b) => {
        const fieldA = a[state.sortField];
        const fieldB = b[state.sortField];

        let comparison = 0;

        // Явная проверка типов
        if (typeof fieldA === 'string' && typeof fieldB === 'string') {
          comparison = String(fieldA).localeCompare(fieldB);
        } else if (typeof fieldA === 'number' && typeof fieldB === 'number') {
          comparison = fieldA - fieldB;
        }

        return state.sortDirection === 'asc' ? comparison : -comparison;
      });
    },

// Сумма по отфильтрованным элементам
totalAmount(): number {
  return this.filteredItems.reduce((sum, item) => sum + item.amount, 0)
}
  },

actions: {
    // Загрузка денежных потоков
    async fetchCashFlows() {
    this.loading = true
    this.error = null

    try {
      const response = await apiInstance.get('/cashflows/')
      this.items = response.data.map((item: any) => ({
        ...item,
        created_at: item.created_at.split('T')[0] // Форматируем дату
      }))
    } catch (error: any) {
      this.error = error.response?.data?.msg || 'Failed to load cash flows'
      throw error
    } finally {
      this.loading = false
    }
  },

    // Создание нового денежного потока
    async createCashFlow(item: Omit<CashFlowItemPayload, 'id'>) {
    this.loading = true

    try {
      const response = await apiInstance.post('/cashflows/', item)
      const newItem = {
        ...response.data,
        created_at: response.data.created_at.split('T')[0]
      }
      this.items.unshift(newItem)
      return newItem
    } catch (error: any) {
      this.error = error.response?.data?.msg || 'Failed to create cash flow'
      throw error
    } finally {
      this.loading = false
    }
  },

    // Обновление денежного потока
    async updateCashFlow(id: string, updates: Partial<CashFlowItemPayload>) {
    this.loading = true

    try {
      const response = await apiInstance.patch(`/cashflows/${id}/`, updates)
      const updatedItem = {
        ...response.data,
        created_at: response.data.created_at.split('T')[0]
      }

      const index = this.items.findIndex(item => item.id === id)
      if (index !== -1) {
        this.items.splice(index, 1, updatedItem)
      }

      return updatedItem
    } catch (error: any) {
      this.error = error.response?.data?.msg || 'Failed to update cash flow'
      throw error
    } finally {
      this.loading = false
    }
  },

    // Удаление денежного потока
    async deleteCashFlow(id: string) {
    this.loading = true

    try {
      await apiInstance.delete(`/cashflows/${id}/`)

      const index = this.items.findIndex(item => item.id === id)
      if (index !== -1) {
        this.items.splice(index, 1)
      }
    } catch (error: any) {
      this.error = error.response?.data?.msg || 'Failed to delete cash flow'
      throw error
    } finally {
      this.loading = false
    }
  },

  // Установка фильтров
  setFilters(filters: Partial<CashFlowState['filters']>) {
    this.filters = { ...this.filters, ...filters }
  },

  // Сброс фильтров
  resetFilters() {
    this.filters = {
      dateRange: null,
      category: null,
      subcategory: null,
      operationType: null,
      status: null
    }
  },

  // Изменение сортировки
  setSort(field: CashFlowState['sortField']) {
    if (this.sortField === field) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
    } else {
      this.sortField = field
      this.sortDirection = 'asc'
    }
  }
}
})
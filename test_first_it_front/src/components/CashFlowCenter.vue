<template>
  <div class="cash-flow-center">
    <!-- Панель фильтров -->
    <div class="filter-panel">
      <div class="filter-group">
        <label>Период:</label>
        <input type="date" v-model="dateStart"> - 
        <input type="date" v-model="dateEnd">
      </div>
      
      <div class="filter-group">
        <label>Категория:</label>
        <select v-model="selectedCategory">
          <option value="">Все</option>
          <option v-for="cat in guideStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Подкатегория:</label>
        <select v-model="selectedSubcategory">
          <option value="">Все</option>
          <option v-for="sub in filteredSubcategories" :key="sub.id" :value="sub.id">
            {{ sub.name }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Тип операции:</label>
        <select v-model="selectedOperationType">
          <option value="">Все</option>
          <option v-for="op in guideStore.operations" :key="op.id" :value="op.id">
            {{ op.name }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Статус:</label>
        <select v-model="selectedStatus">
          <option value="">Все</option>
          <option v-for="status in guideStore.statuses" :key="status.id" :value="status.id">
            {{ status.name }}
          </option>
        </select>
      </div>
      
      <button @click="applyFilters">Применить</button>
      <button @click="resetFilters">Сбросить</button>
    </div>
    
    <!-- Статистика -->
    <div class="summary">
      <div>Всего операций: {{ cashFlowStore.filteredItems.length }}</div>
      <div>Общая сумма: {{ cashFlowStore.totalAmount }} руб.</div>
    </div>
    
    <!-- Таблица денежных потоков -->
    <div class="cash-flow-table">
      <table>
        <thead>
          <tr>
            <th @click="setSort('created_at')">
              Дата {{ sortIndicator('created_at') }}
            </th>
            <th>Категория / Подкатегория</th>
            <th>Описание</th>
            <th @click="setSort('amount')">
              Сумма {{ sortIndicator('amount') }}
            </th>
            <th>Тип операции</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in cashFlowStore.filteredItems" :key="item.id">
            <td>{{ item.created_at }}</td>
            <td>
              <div>{{ item.category?.category?.name }}</div>
              <div class="subcategory">{{ item.category?.name }}</div>
            </td>
            <td>{{ item.comment || '—' }}</td>
            <td :class="{'income': item.type.name === 'Пополнение', 'expense': item.type.name === 'Списание'}">
              {{ item.type.name === 'Пополнение' ? '+' : '-' }}{{ item.amount }}
            </td>
            <td>{{ item.type.name }}</td>
            <td>{{ item.status.name }}</td>
            <td class="actions">
              <button @click="editItem(item)">✏️</button>
              <button @click="deleteItem(item.id)">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="cashFlowStore.loading" class="loading">Загрузка...</div>
      <div v-if="!cashFlowStore.loading && cashFlowStore.filteredItems.length === 0" class="empty">
        Нет данных для отображения
      </div>
    </div>
    
    <!-- Форма создания/редактирования -->
    <div v-if="showForm" class="cash-flow-form">
      <h3>{{ editingItem ? 'Редактирование' : 'Новая операция' }}</h3>
      
      <div class="form-group">
        <label>Дата:</label>
        <input type="date" v-model="formData.created_at" required>
      </div>
      
      <div class="form-group">
        <label>Сумма:</label>
        <input type="number" v-model.number="formData.amount" required>
      </div>
      
      <div class="form-group">
        <label>Описание:</label>
        <input type="text" v-model="formData.comment">
      </div>
      
      <div class="form-group">
        <label>Категория:</label>
        <select v-model="formData.categoryId" @change="formData.subcategoryId = ''">
          <option v-for="cat in guideStore.categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label>Подкатегория:</label>
        <select v-model="formData.subcategoryId">
          <option v-for="sub in subcategoriesForForm" :key="sub.id" :value="sub.id">
            {{ sub.name }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label>Тип операции:</label>
        <select v-model="formData.typeId">
          <option v-for="op in guideStore.operations" :key="op.id" :value="op.id">
            {{ op.name }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label>Статус:</label>
        <select v-model="formData.statusId">
          <option v-for="status in guideStore.statuses" :key="status.id" :value="status.id">
            {{ status.name }}
          </option>
        </select>
      </div>
      
      <div class="form-actions">
        <button @click="saveItem">{{ editingItem ? 'Обновить' : 'Создать' }}</button>
        <button @click="cancelEdit">Отмена</button>
      </div>
    </div>
    
    <!-- Кнопка добавления -->
    <button v-if="!showForm" class="add-button" @click="addNewItem">
      + Добавить операцию
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useCashFlowStore } from '../stores/cashFlow'
import { useGuideStore } from '../stores/guidesStore'
import type { CashFlowItem, guideWithRelationsItem } from '../api/api'

const cashFlowStore = useCashFlowStore()
const guideStore = useGuideStore()

// Загрузка данных при монтировании
onMounted(async () => {
  await Promise.all([
    cashFlowStore.fetchCashFlows(),
    guideStore.fetchAllGuides()
  ])
})

// Фильтры
const dateStart = ref<string>('')
const dateEnd = ref<string>('')
const selectedCategory = ref<string>('')
const selectedSubcategory = ref<string>('')
const selectedOperationType = ref<string>('')
const selectedStatus = ref<string>('')

// Фильтрованные подкатегории для формы
const filteredSubcategories = computed(() => {
  if (!selectedCategory.value) return []
  return guideStore.getSubcategoriesForCategory(selectedCategory.value)
})

// Применение фильтров
const applyFilters = () => {
  cashFlowStore.setFilters({
    dateRange: dateStart.value && dateEnd.value 
      ? [dateStart.value, dateEnd.value] 
      : null,
    category: selectedCategory.value || null,
    subcategory: selectedSubcategory.value || null,
    operationType: selectedOperationType.value || null,
    status: selectedStatus.value || null
  })
}

// Сброс фильтров
const resetFilters = () => {
  dateStart.value = ''
  dateEnd.value = ''
  selectedCategory.value = ''
  selectedSubcategory.value = ''
  selectedOperationType.value = ''
  selectedStatus.value = ''
  cashFlowStore.resetFilters()
}

// Сортировка
const setSort = (field: 'created_at' | 'amount') => {
  cashFlowStore.setSort(field)
}

const sortIndicator = (field: 'created_at' | 'amount') => {
  if (cashFlowStore.sortField !== field) return ''
  return cashFlowStore.sortDirection === 'asc' ? '↑' : '↓'
}

// Форма редактирования
const showForm = ref(false)
const editingItem = ref<CashFlowItem | null>(null)
const formData = ref({
  created_at: new Date().toISOString().split('T')[0],
  amount: 0,
  comment: '',
  categoryId: '',
  subcategoryId: '',
  typeId: '',
  statusId: ''
})

// Подкатегории для формы
const subcategoriesForForm = computed(() => {
  if (!formData.value.categoryId) return []
  return guideStore.getSubcategoriesForCategory(formData.value.categoryId)
})

// Добавление новой операции
const addNewItem = () => {
  editingItem.value = null
  formData.value = {
    created_at: new Date().toISOString().split('T')[0],
    amount: 0,
    comment: '',
    categoryId: guideStore.categories[0]?.id || '',
    subcategoryId: '',
    typeId: guideStore.operations[0]?.id || '',
    statusId: guideStore.statuses[0]?.id || ''
  }
  showForm.value = true
}

// Редактирование операции
const editItem = (item: CashFlowItem) => {
  editingItem.value = item
  formData.value = {
    created_at: (item.created_at).toString(),
    amount: item.amount,
    comment: item.comment || '',
    categoryId: item.category.category.id,
    subcategoryId: item.category.id,
    typeId: item.type.id,
    statusId: item.status.id
  }
  showForm.value = true
}

// Сохранение операции
const saveItem = async () => {
  if (!formData.value.subcategoryId) {
    alert('Выберите подкатегорию!')
    return
  }

  const categoryObject = guideStore.getGuideItemById('subcategories', formData.value.subcategoryId) as guideWithRelationsItem
  if (!categoryObject || !categoryObject.category) {
    alert('Ошибка: не найдена категория для выбранной подкатегории')
    return
  }
  
  const payload = {
    created_at: new Date(formData.value.created_at),
    amount: formData.value.amount,
    comment: formData.value.comment,
    category: categoryObject,
    type: formData.value.typeId,
    status: formData.value.statusId
  }

  try {
    if (editingItem.value) {
      await cashFlowStore.updateCashFlow(editingItem.value.id, payload)
    } else {
      await cashFlowStore.createCashFlow(payload)
    }
    showForm.value = false
  } catch (error) {
    console.error('Ошибка сохранения:', error)
  }
}

// Отмена редактирования
const cancelEdit = () => {
  showForm.value = false
}

// Удаление операции
const deleteItem = async (id: string) => {
  if (confirm('Вы уверены, что хотите удалить эту операцию?')) {
    await cashFlowStore.deleteCashFlow(id)
  }
}
</script>

<style scoped>
.cash-flow-center {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  padding: 16px;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-weight: 500;
  color: var(--text-secondary);
  min-width: 100px;
}

.filter-group label {
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.filter-buttons {
  grid-column: 1 / -1;
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

input, select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: var(--card-bg);
  color: var(--text-color);
  transition: var(--transition);
  flex: 1;
}

input:focus, select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

button {
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  transition: var(--transition);
}

button:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

button:nth-child(odd):not(.actions button) {
  background: var(--info-color);
}

button:nth-child(odd):not(.actions button):hover {
  background: #a6a9ad;
}

.summary {
  display: flex;
  justify-content: space-between;
  padding: 16px;
  background-color: var(--card-bg);
  border-radius: 8px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.summary div:last-child {
  color: var(--success-color);
  font-weight: 600;
}

.cash-flow-table {
  overflow-x: auto; 
}

table {
  min-width: 1000px;
  width: 100%;
}

th, td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  background-color: rgba(64, 158, 255, 0.05);
  cursor: pointer;
  user-select: none;
  font-weight: 600;
  color: var(--text-color);
  position: sticky;
  top: 0;
}

th:hover {
  background-color: rgba(64, 158, 255, 0.1);
}

tbody tr {
  transition: var(--transition);
}

tbody tr:hover {
  background-color: rgba(64, 158, 255, 0.03);
}

.subcategory {
  font-size: 0.9em;
  color: var(--text-secondary);
}

.income {
  color: var(--success-color);
  font-weight: 600;
}

.expense {
  color: var(--danger-color);
  font-weight: 600;
}

.actions button {
  background: none;
  color: var(--text-secondary);
  padding: 6px;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.actions button:hover {
  background: rgba(64, 158, 255, 0.1);
  color: var(--primary-color);
}

.actions button:last-child:hover {
  color: var(--danger-color);
}

.loading, .empty {
  text-align: center;
  padding: 40px;
  color: var(--info-color);
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cash-flow-form {
  padding: 24px;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-top: 16px;
}

.cash-flow-form h3 {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-color);
}

.form-group {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: var(--text-secondary);
}

.form-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.add-button {
  padding: 12px 24px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  transition: var(--transition);
}

.add-button:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Анимации */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.cash-flow-form {
  animation: fadeIn 0.3s ease;
}

/* Адаптив */
@media (max-width: 1200px) {
  .filter-panel {
    flex-direction: column;
  }
  
  .filter-group {
    min-width: 100%;
  }
}

@media (max-width: 992px) {
  th, td {
    padding: 10px 12px;
    font-size: 0.9rem;
  }
}
@media (max-width: 768px) {
  .cash-flow-center {
    padding: 16px;
  }
  
  .filter-panel {
    grid-template-columns: 1fr;
  }
  
  .summary {
    flex-direction: column;
    gap: 8px;
  }
}

@media (max-width: 576px) {
  .form-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }
}
</style>
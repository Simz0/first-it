<template>
  <div class="guide-sidebar">
    <!-- Статусы -->
    <div class="guide-section">
      <div class="section-header" @click="toggleSection('statuses')">
        <h3>Статусы</h3>
        <span class="toggle-icon">{{ store.expandedSections.statuses ? '−' : '+' }}</span>
      </div>
      
      <div v-if="store.expandedSections.statuses" class="section-content">
        <ul>
          <li v-for="status in store.statuses" :key="status.id">
            {{ status.name }}
            <button @click="editItem('statuses', status)">✏️</button>
            <button @click="deleteItem('statuses', status.id)">🗑️</button>
          </li>
        </ul>
        <button @click="addItem('statuses')">+ Добавить статус</button>
      </div>
    </div>

    <!-- Типы операций -->
    <div class="guide-section">
      <div class="section-header" @click="toggleSection('operations')">
        <h3>Типы операций</h3>
        <span class="toggle-icon">{{ store.expandedSections.operations ? '−' : '+' }}</span>
      </div>
      
      <div v-if="store.expandedSections.operations" class="section-content">
        <ul>
          <li v-for="opType in store.operations" :key="opType.id">
            {{ opType.name }}
            <button @click="editItem('operations', opType)">✏️</button>
            <button @click="deleteItem('operations', opType.id)">🗑️</button>
          </li>
        </ul>
        <button @click="addItem('operations')">+ Добавить тип</button>
      </div>
    </div>

    <!-- Категории и подкатегории -->
    <div class="guide-section">
      <div class="section-header" @click="toggleSection('categories')">
        <h3>Категории</h3>
        <span class="toggle-icon">{{ store.expandedSections.categories ? '−' : '+' }}</span>
      </div>
      
      <div v-if="store.expandedSections.categories" class="section-content">
        <div v-for="category in store.getCategoryTree" :key="category.id" class="category">
          <div class="category-header">
            <strong>{{ category.name }}</strong>
            <button @click="editItem('categories', category)">✏️</button>
            <button @click="deleteItem('categories', category.id)">🗑️</button>
            <button @click="addSubcategory(category)">+ Подкатегория</button>
          </div>
          
          <ul v-if="category.subcategories.length" class="subcategories">
            <li v-for="sub in category.subcategories" :key="sub.id">
              {{ sub.name }}
              <button @click="editItem('subcategories', sub)">✏️</button>
              <button @click="deleteItem('subcategories', sub.id)">🗑️</button>
            </li>
          </ul>
        </div>
        <button @click="addItem('categories')">+ Добавить категорию</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useGuideStore } from '../stores/guidesStore.ts'
import type {
    GuideItem,
} from '../api/api.ts'
import type {
    GuideType,
} from '../stores/guidesStore.ts'

const store = useGuideStore()

// Загрузка данных при монтировании компонента
store.fetchAllGuides()

const toggleSection = (type: GuideType) => {
  store.toggleSection(type)
}

const addItem = async (type: GuideType) => {
  const name = prompt(`Введите название для нового ${getItemName(type)}:`)
  if (name) {
    await store.createGuide(type, name)
  }
}

const addSubcategory = async (category: GuideItem) => {
  const name = prompt('Введите название новой подкатегории:')
  if (name) {
    await store.createGuide('subcategories', name, category)
  }
}

const editItem = async (type: GuideType, item: GuideItem) => {
  const newName = prompt('Введите новое название:', item.name)
  if (newName && newName !== item.name) {
    await store.updateGuideItem(type, { ...item, name: newName })
  }
}

const deleteItem = async (type: GuideType, itemId: string) => {
  if (confirm('Вы уверены, что хотите удалить этот элемент?')) {
    await store.deleteGuideItem(type, itemId)
  }
}

const getItemName = (type: GuideType): string => {
  switch (type) {
    case 'statuses': return 'статуса'
    case 'operations': return 'типа операции'
    case 'categories': return 'категории'
    case 'subcategories': return 'подкатегории'
    default: return 'элемента'
  }
}
</script>

<style scoped>
.guide-sidebar {
  width: var(--sidebar-width);
  background-color: var(--card-bg);
  padding: 20px;
  border-right: 1px solid var(--border-color);
  height: 100vh;
  overflow-y: auto;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  transition: var(--transition);
}

.section-header:hover {
  background-color: rgba(64, 158, 255, 0.05);
}

.section-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-color);
}

.toggle-icon {
  font-weight: bold;
  font-size: 1.4em;
  color: var(--text-secondary);
  transition: var(--transition);
}

.section-content {
  padding: 12px 0 20px 10px;
}

.category {
  margin-bottom: 15px;
  padding: 12px;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: var(--transition);
}

.category:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
  flex-wrap: wrap;
}

.category-header strong {
  flex-grow: 1;
  font-weight: 500;
}

.subcategories {
  padding-left: 15px;
  margin-top: 8px;
  border-left: 2px solid var(--border-color);
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  padding: 8px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed var(--border-color);
}

li:last-child {
  border-bottom: none;
}

button {
  padding: 6px 10px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  transition: var(--transition);
}

button:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.section-content > button {
  margin-top: 10px;
  width: 100%;
  justify-content: center;
  padding: 8px;
  font-weight: 500;
}

/* Иконки в кнопках */
button:before {
  font-size: 1.1em;
}

@media (max-width: 992px) {
  .guide-sidebar {
    width: 100%;
    height: auto;
    max-height: 50vh;
    position: static;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }
}

@media (max-width: 768px) {
  .section-header {
    padding: 10px 0;
  }
  
  .category-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .category-header button {
    width: 100%;
    justify-content: center;
  }
}
</style>
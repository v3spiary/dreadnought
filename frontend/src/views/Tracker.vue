<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { TrendingUp, TrendingDown, MoveRight, TrendingUpDown, BarChart3, Apple, Bike, ListChecks, Target, Calendar, AlertCircle, Brain, Dumbbell } from 'lucide-vue-next';
import { api } from '@/lib/api'

const router = useRouter()
const dashboardData = ref<any>(null)
const metricsData = ref<any[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

// Типы для метрик
interface MetricType {
  id: number
  name: string
  code: string
  category: string
  unit: string
  description?: string
  is_active: boolean
  order: number
}

interface Metric {
  id?: number
  date: string
  metric_type: MetricType
  value: string | null
  notes: string
  created_at: string | null
  updated_at: string | null
}

interface ProgressItem {
  current: number | null
  target: number
  percentage: number
  trend: string
  change: number | null
  change_percent: number | null
}

// Базовые метрики (для первого таба)
const basicMetricCodes = ['calories', 'steps', 'sleep', 'water', 'pages_read']

// Получение данных с сервера
const fetchData = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Загружаем оба запроса параллельно
    const [dashboardResponse, metricsResponse] = await Promise.all([
      api.get('/tracker/dashboard/today/'),
      api.get('/tracker/metrics/today/')
    ])
    
    dashboardData.value = dashboardResponse.data
    metricsData.value = metricsResponse.data
  } catch (err: any) {
    console.error('Error fetching data:', err)
    error.value = err.response?.data?.message || 'Ошибка загрузки данных'
  } finally {
    loading.value = false
  }
}

// Получение прогресса для метрики
const getMetricProgress = (code: string): ProgressItem | null => {
  if (!dashboardData.value?.progress) return null
  return dashboardData.value.progress[code] || null
}

// Базовые метрики
const basicMetrics = computed(() => {
  return metricsData.value
    .filter(metric => basicMetricCodes.includes(metric.metric_type.code))
    .map(metric => {
      const progress = getMetricProgress(metric.metric_type.code)
      return {
        ...metric,
        progress
      }
    })
    .sort((a, b) => basicMetricCodes.indexOf(a.metric_type.code) - basicMetricCodes.indexOf(b.metric_type.code))
})

// Группировка метрик по категориям для табов
const groupedMetrics = computed(() => {
  const groups: Record<string, any[]> = {}
  
  // Инициализируем группы для существующих категорий
  metricsData.value.forEach(metric => {
    const category = metric.metric_type.category
    if (!groups[category]) {
      groups[category] = []
    }
  })
  
  // Добавляем метрики в группы, исключая базовые
  metricsData.value.forEach(metric => {
    const category = metric.metric_type.category
    if (!basicMetricCodes.includes(metric.metric_type.code)) {
      const progress = getMetricProgress(metric.metric_type.code)
      groups[category].push({
        ...metric,
        progress
      })
    }
  })
  
  // Сортируем метрики внутри групп по order
  Object.keys(groups).forEach(category => {
    groups[category].sort((a, b) => 
      (a.metric_type.order || 0) - (b.metric_type.order || 0)
    )
  })
  
  return groups
})

// Получение уникальных категорий для табов
const availableCategories = computed(() => {
  const categories = new Set<string>()
  metricsData.value.forEach(metric => {
    if (!basicMetricCodes.includes(metric.metric_type.code)) {
      categories.add(metric.metric_type.category)
    }
  })
  return Array.from(categories)
})

// Форматирование значения
const formatValue = (value: string | number | null, unit: string): string => {
  if (value === null || value === undefined || value === '') return '—'
  
  let numValue: number
  if (typeof value === 'string') {
    numValue = parseFloat(value)
  } else {
    numValue = value
  }
  
  // Округляем целые числа без дробной части
  if (numValue % 1 === 0) {
    return `${numValue}`
  }
  
  // Для дробных чисел оставляем 2 знака после запятой
  return `${numValue.toFixed(2)}`
}

// Цвет для значения
const getValueColor = (metric: any): string => {
  if (!metric.progress) {
    return metric.value ? 'uk-text-muted' : 'uk-text-muted'
  }
  
  const percentage = metric.progress.percentage
  if (percentage >= 100) return 'uk-text-success'
  if (percentage >= 80) return 'uk-text-warning'
  if (percentage >= 50) return 'uk-text-primary'
  return 'uk-text-danger'
}

// Цвет для тренда
const getTrendColor = (trend: string): string => {
  switch (trend) {
    case 'up': return 'uk-text-success'
    case 'down': return 'uk-text-danger'
    case 'stable': return 'uk-text-warning'
    default: return 'uk-text-muted'
  }
}

// Иконка тренда
const getTrendIcon = (trend: string): any => {
  switch (trend) {
    case 'up': return TrendingUp
    case 'down': return TrendingDown
    case 'stable': return MoveRight
    default: return TrendingUpDown
  }
}

// Статическая оценка дня (под замену)
const dayRating = computed(() => {
  if (!metricsData.value.length) return { rating: '—', color: 'uk-text-muted', icon: TrendingUpDown }
  
  const completed = metricsData.value.filter(m => m.value !== null && parseFloat(m.value || '0') > 0).length
  const total = metricsData.value.length
  const completionRate = total > 0 ? (completed / total) * 100 : 0
  
  if (completionRate >= 90) return { rating: 'A+', color: 'uk-text-success', icon: TrendingUp }
  if (completionRate >= 80) return { rating: 'A', color: 'uk-text-success', icon: TrendingUp }
  if (completionRate >= 70) return { rating: 'A-', color: 'uk-text-success', icon: TrendingUp }
  if (completionRate >= 60) return { rating: 'B+', color: 'uk-text-warning', icon: TrendingUp }
  if (completionRate >= 50) return { rating: 'B', color: 'uk-text-warning', icon: TrendingUp }
  if (completionRate >= 40) return { rating: 'C+', color: 'uk-text-danger', icon: TrendingDown }
  return { rating: 'C', color: 'uk-text-danger', icon: TrendingDown }
})

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div>
    <div class="uk-flex uk-flex-between uk-flex-middle uk-margin-medium-bottom">
      <h3 class="uk-margin-remove">Personal Tracker Dashboard</h3>
      <div v-if="dashboardData?.date" class="uk-text-meta">
        <Calendar :size="16" class="uk-margin-small-right" />
        {{ dashboardData.date }}
      </div>
    </div>

    <!-- Ошибка -->
    <div v-if="error" class="uk-alert-danger" uk-alert>
      <a class="uk-alert-close" uk-close></a>
      <p><AlertCircle :size="16" class="uk-margin-small-right" /> {{ error }}</p>
    </div>

    <!-- Загрузка -->
    <div v-if="loading" class="uk-text-center uk-padding-large">
      <div uk-spinner="ratio: 2"></div>
      <p class="uk-text-muted uk-margin-small-top">Загрузка данных...</p>
    </div>

    <!-- Основной контент -->
    <div v-else>
      <div class="uk-child-width-1-1@s" uk-grid>
        <div>
          <div uk-grid>
            <div class="uk-width-auto@m">
              <ul class="uk-tab-left" uk-tab="connect: #component-tab-left; animation: uk-animation-fade">
                <li><a href="#"><BarChart3 :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Базовые</a></li>
                <li><a href="#"><Apple :size="15" stroke-width="1.3"style="padding-right: 3px;" /> Питание</a></li>
                <li><a href="#"><Bike :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Спорт</a></li>
                <li><a href="#"><ListChecks :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Дисциплина</a></li>
                <li><a href="#"><Target :size="20" stroke-width="1.5" style="padding-right: 5px;" /> Саморазвитие</a></li>
              </ul>
            </div>
            
            <div class="uk-width-expand@m">
              <div id="component-tab-left" class="uk-switcher">
                <!-- Таб 1: Базовые метрики -->
                <div>
                  <div class="uk-alert-primary" uk-alert>
                    <a class="uk-alert-close" uk-close></a>
                    <p><span uk-icon="icon: warning;" style="padding-right: 5px;"></span>  Действующий форс-мажор: Восстановление после операции.</p>
                  </div>

                  <div class="uk-slider-container-offset" uk-slider>
                    <div class="uk-position-relative uk-visible-toggle" tabindex="-1">
                      <div class="uk-slider-items uk-child-width-1-1@s uk-grid">
                        <div>
                          <div class="uk-grid-small uk-child-width-1-6@s uk-text-center" uk-grid uk-height-match="target: > div > .uk-card">
                            <!-- Оценка дня -->
                            <div>
                              <div class="uk-card uk-card-default uk-card-body">
                                <h1 :class="dayRating.color + ' uk-margin-small-top'">{{ dayRating.rating }}</h1>
                                <p><component :is="dayRating.icon" :class="dayRating.color"/></p>
                                <p class="uk-text-muted">Оценка дня</p>
                              </div>
                            </div>
                            
                            <!-- Базовые метрики -->
                            <div v-for="metric in basicMetrics" :key="metric.metric_type.code">
                              <div class="uk-card uk-card-default uk-card-body">
                                <div v-if="metric.metric_type.unit" class="uk-card-badge uk-label">
                                  {{ metric.metric_type.unit === 'hours' ? 'ч' : 
                                     metric.metric_type.unit === 'steps' ? 'шагов' :
                                     metric.metric_type.unit === 'kcal' ? 'ккал' :
                                     metric.metric_type.unit === 'l' ? 'л' :
                                     metric.metric_type.unit === 'pages' ? 'страниц' :
                                     metric.metric_type.unit }}
                                </div>
                                <h1 :class="getValueColor(metric) + ' uk-margin-small-top'">
                                  {{ formatValue(metric.value, metric.metric_type.unit) }}
                                </h1>
                                <p v-if="metric.progress?.trend">
                                  <component 
                                    :is="getTrendIcon(metric.progress.trend)" 
                                    :class="getTrendColor(metric.progress.trend)"
                                  />
                                </p>
                                <p v-else-if="metric.value" class="uk-text-muted">—</p>
                                <p v-else class="uk-text-muted">нет данных</p>
                                <p class="uk-text-muted">{{ metric.metric_type.name }}</p>
                                
                                <!-- Прогресс бар для метрик с целями -->
                                <div v-if="metric.progress?.target" class="uk-progress uk-progress-small uk-margin-small-top">
                                  <div 
                                    class="uk-progress-bar" 
                                    :style="{ width: Math.min(metric.progress.percentage || 0, 100) + '%' }"
                                    :class="{
                                      'uk-background-success': metric.progress.percentage >= 100,
                                      'uk-background-warning': metric.progress.percentage >= 80 && metric.progress.percentage < 100,
                                      'uk-background-danger': metric.progress.percentage < 80
                                    }"
                                  ></div>
                                </div>
                                
                                <!-- Целевое значение -->
                                <div v-if="metric.progress?.target" class="uk-text-small uk-text-muted uk-margin-top">
                                  {{ formatValue(metric.progress.current, metric.metric_type.unit) || 0 }}/{{ metric.progress.target }}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <a class="uk-position-center-left uk-position-small uk-hidden-hover uk-dark" uk-slidenav-previous uk-slider-item="previous"></a>
                      <a class="uk-position-center-right uk-position-small uk-hidden-hover uk-dark" uk-slidenav-next uk-slider-item="next"></a>
                    </div>
                    <ul class="uk-slider-nav uk-dotnav uk-flex-center uk-position-bottom-center uk-margin"></ul>
                  </div>
                </div>

                <!-- Динамические табы по категориям -->
                <div v-for="category in availableCategories" :key="category">
                  <div class="uk-grid-small uk-child-width-1-2@s uk-child-width-1-3@m uk-child-width-1-4@l uk-text-center" 
                       uk-grid 
                       uk-height-match="target: > div > .uk-card">
                    
                    <div v-for="metric in groupedMetrics[category]" :key="metric.metric_type.code">
                      <div class="uk-card uk-card-default uk-card-body">
                        <div v-if="metric.metric_type.unit" class="uk-card-badge uk-label">
                          {{ metric.metric_type.unit === 'count' ? 'раз' : 
                             metric.metric_type.unit === 'hours' ? 'ч' :
                             metric.metric_type.unit === 'kcal' ? 'ккал' :
                             metric.metric_type.unit === 'g' ? 'г' :
                             metric.metric_type.unit === 'l' ? 'л' :
                             metric.metric_type.unit === 'steps' ? 'шагов' :
                             metric.metric_type.unit }}
                        </div>
                        
                        <h1 :class="getValueColor(metric) + ' uk-margin-small-top'">
                          {{ formatValue(metric.value, metric.metric_type.unit) }}
                        </h1>
                        
                        <p v-if="metric.progress?.trend">
                          <component 
                            :is="getTrendIcon(metric.progress.trend)" 
                            :class="getTrendColor(metric.progress.trend)"
                          />
                        </p>
                        <p v-else-if="metric.value" class="uk-text-muted">—</p>
                        <p v-else class="uk-text-muted">нет данных</p>
                        
                        <p class="uk-text-muted">{{ metric.metric_type.name }}</p>
                        
                        <!-- Прогресс бар для метрик с целями -->
                        <div v-if="metric.progress?.target" class="uk-progress uk-progress-small uk-margin-small-top">
                          <div 
                            class="uk-progress-bar" 
                            :style="{ width: Math.min(metric.progress.percentage || 0, 100) + '%' }"
                            :class="{
                              'uk-background-success': metric.progress.percentage >= 100,
                              'uk-background-warning': metric.progress.percentage >= 80 && metric.progress.percentage < 100,
                              'uk-background-danger': metric.progress.percentage < 80
                            }"
                          ></div>
                        </div>
                        
                        <!-- Целевое значение -->
                        <div v-if="metric.progress?.target" class="uk-text-small uk-text-muted uk-margin-top">
                          {{ formatValue(metric.progress.current, metric.metric_type.unit) || 0 }}/{{ metric.progress.target }}
                        </div>
                        
                        <!-- Описание метрики -->
                        <div v-if="metric.metric_type.description" class="uk-text-small uk-text-muted uk-margin-top">
                          {{ metric.metric_type.description }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
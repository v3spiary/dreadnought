<template>
  <div class="bar-chart-container">
    <div :style="{ height: height + 'px' }">
      <Bar 
        :data="processedChartData" 
        :options="chartOptions"
        :key="chartKey"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { Bar } from 'vue-chartjs'
import { 
  Chart as ChartJS, 
  Title, 
  Tooltip, 
  Legend, 
  BarElement, 
  CategoryScale, 
  LinearScale 
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: 'BarChart',
  components: { Bar },
  
  props: {
    chartData: {
      type: Object,
      required: true,
      validator: (value) => {
        return value.labels && value.datasets
      }
    },
    
    title: {
      type: String,
      default: ''
    },
    
    height: {
      type: Number,
      default: 300
    },
    
    options: {
      type: Object,
      default: () => ({})
    }
  },
  
  data() {
    return {
      chartKey: 0,
      
      defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: true,
            text: this.title
          }
        }
      }
    }
  },
  
  computed: {
    chartOptions() {
      return {
        ...this.defaultOptions,
        ...this.options
      }
    },
    
    processedChartData() {
      return {
        labels: this.chartData.labels || [],
        datasets: this.chartData.datasets || []
      }
    }
  },
  
  watch: {
    chartData: {
      handler() {
        this.chartKey += 1
      },
      deep: true
    }
  }
}
</script>

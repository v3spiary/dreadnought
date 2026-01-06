<template>
  <Navbar :activeItem="Item" />

  <BarChart 
    :chart-data="chartData"
    title="Продажи по месяцам"
  />
</template>

<script lang="ts">
import Navbar from '@/components/NavBar.vue'
import BarChart from '@/components/BarChart.vue'

export default {
  name: 'DashboardPage',
  components: {
    Navbar,
    BarChart
  },
  
  data() {
    return {
      chartData: {
        labels: ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн'],
        datasets: [
          {
            label: 'Продажи 2023',
            backgroundColor: '#42b883',
            data: [65, 59, 80, 81, 56, 55]
          },
          {
            label: 'Продажи 2024',
            backgroundColor: '#ff6b6b',
            data: [28, 48, 40, 19, 86, 27]
          }
        ]
      },
      
      customOptions: {
        plugins: {
          legend: {
            position: 'bottom'
          }
        },
        scales: {
          y: {
            ticks: {
              callback: function(value) {
                return value + 'k'
              }
            }
          }
        }
      }
    }
  }
}
</script>

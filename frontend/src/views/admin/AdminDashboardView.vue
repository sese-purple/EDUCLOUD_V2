<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import AdminSidebar from '../../components/AdminSidebar.vue'
import {
  Users, BookOpen, Database,
  UserPlus, FolderPlus, Bell
} from 'lucide-vue-next'

const router = useRouter()

const systemStats = ref([
  { name: 'Total Registered Users', value: '...', icon: Users, color: 'text-blue-500' },
  { name: 'Active Course Shells', value: '...', icon: BookOpen, color: 'text-indigo-500' },
  { name: 'Total Enrollments', value: '...', icon: Database, color: 'text-emerald-500' },
])

const recentActivity = ref<any[]>([])

const fetchDashboardData = async () => {
  try {
    const response = await api.get('dashboard/')
    const data = response.data
    systemStats.value = [
      { name: 'Total Registered Users', value: String(data.total_users), icon: Users, color: 'text-blue-500' },
      { name: 'Active Course Shells', value: String(data.total_courses), icon: BookOpen, color: 'text-indigo-500' },
      { name: 'Total Enrollments', value: String(data.total_enrollments), icon: Database, color: 'text-emerald-500' },
    ]
    recentActivity.value = data.recent_activities.map((a: any) => ({
      id: a.id,
      action: a.action,
      user: a.user,
      time: new Date(a.time).toLocaleString(),
    }))
  } catch (error) {
    console.error("Error fetching dashboard data:", error)
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <div class="flex h-screen bg-gray-100 font-sans overflow-hidden">
    
    <AdminSidebar />

    <div class="flex-1 flex flex-col overflow-hidden">
      
      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm z-10">
        <h2 class="text-xl font-bold text-gray-800">EDUCLOUD <span class="text-indigo-600">Core Network</span></h2>
        <div class="flex items-center space-x-4">
          <Bell class="h-5 w-5 text-gray-400 cursor-pointer hover:text-gray-600" />
          <div class="h-8 w-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center font-bold border border-red-200">
            AD
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">
        
        <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Infrastructure Dashboard</h2>
            <p class="text-gray-500 text-sm mt-1">Monitor system health and provision new institutional resources.</p>
          </div>
          <div class="flex space-x-3">
            <button @click="router.push('/admin/courses')" class="flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors shadow-sm">
              <FolderPlus class="h-4 w-4 mr-2 text-indigo-600" /> Provision Course
            </button>
            <button @click="router.push('/admin/users')" class="flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
              <UserPlus class="h-4 w-4 mr-2" /> Add New User
            </button>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div v-for="stat in systemStats" :key="stat.name" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center">
            <div class="p-3 rounded-lg bg-gray-50 mr-4 border border-gray-100">
              <component :is="stat.icon" :class="['h-6 w-6', stat.color]" />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-500">{{ stat.name }}</p>
              <h3 class="text-2xl font-bold text-gray-900">{{ stat.value }}</h3>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h3 class="text-sm font-bold text-gray-700 uppercase tracking-wider">System Audit Log</h3>
            <span class="text-xs text-indigo-600 font-medium cursor-pointer">View Full Log</span>
          </div>
          <ul class="divide-y divide-gray-100">
            <li v-for="log in recentActivity" :key="log.id" class="px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
              <div class="flex items-center">
                <div class="h-2 w-2 rounded-full bg-emerald-500 mr-4"></div>
                <p class="text-sm text-gray-900 font-medium">{{ log.action }}</p>
              </div>
              <div class="text-right">
                <p class="text-xs text-gray-500">{{ log.user }}</p>
                <p class="text-xs text-gray-400 mt-0.5">{{ log.time }}</p>
              </div>
            </li>
          </ul>
        </div>

      </main>
    </div>
  </div>
</template>
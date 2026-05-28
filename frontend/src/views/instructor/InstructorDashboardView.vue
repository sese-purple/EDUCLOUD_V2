<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  LayoutDashboard, BookOpen, MapPin, Users,
  FileText, Settings, Plus, Bell, Search,
  LogOut, ChevronRight
} from 'lucide-vue-next'

const router = useRouter()

const stats = ref([
  { id: 1, name: 'Total Enrolled', value: '142', change: '+12%', trend: 'up' },
  { id: 2, name: 'Active Modules', value: '4', change: 'Steady', trend: 'neutral' },
  { id: 3, name: 'Pending Logbooks', value: '28', change: '-5', trend: 'down' },
])

const courses = ref([
  { id: 1, title: 'Integrated Internship Management', code: 'SYS-400', students: 120, progress: 85, color: 'bg-indigo-500' },
  { id: 2, title: 'Advanced Web Architecture', code: 'SE-301', students: 45, progress: 40, color: 'bg-blue-500' },
])

const instructorTools = ref([
  { name: 'Generate QR Attendance', icon: MapPin, color: 'text-emerald-600', bg: 'bg-emerald-100' },
  { name: 'Agile Project Boards', icon: Users, color: 'text-blue-600', bg: 'bg-blue-100' },
  { name: 'Export Mark Sheets', icon: FileText, color: 'text-purple-600', bg: 'bg-purple-100' },
  { name: 'Draft Rich-Text Quiz', icon: BookOpen, color: 'text-amber-600', bg: 'bg-amber-100' },
])
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    
    <aside class="w-64 bg-white border-r border-gray-200 flex flex-col hidden md:flex">
      <div class="h-16 flex items-center px-6 border-b border-gray-200">
        <h1 class="text-xl font-bold text-gray-900 tracking-tight">
          EDUCLOUD <span class="text-indigo-600">2.0</span>
        </h1>
      </div>

      <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <a href="#" class="flex items-center px-3 py-2.5 bg-indigo-50 text-indigo-700 rounded-lg font-medium group">
          <LayoutDashboard class="w-5 h-5 mr-3 text-indigo-600" />
          Dashboard
        </a>
        <a href="#" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors group">
          <BookOpen class="w-5 h-5 mr-3 text-gray-400 group-hover:text-gray-600" />
          My Courses
        </a>
        <a href="#" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors group">
          <MapPin class="w-5 h-5 mr-3 text-gray-400 group-hover:text-gray-600" />
          Live Attendance
        </a>
        <a href="#" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors group">
          <Users class="w-5 h-5 mr-3 text-gray-400 group-hover:text-gray-600" />
          Agile Workspaces
        </a>
        <a href="#" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors group">
          <FileText class="w-5 h-5 mr-3 text-gray-400 group-hover:text-gray-600" />
          Mark Sheets
        </a>
      </nav>

      <div class="p-4 border-t border-gray-200">
        <a href="#" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors group">
          <Settings class="w-5 h-5 mr-3 text-gray-400 group-hover:text-gray-600" />
          Settings
        </a>
        <a href="#" class="flex items-center px-3 py-2.5 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors mt-1">
          <LogOut class="w-5 h-5 mr-3 text-red-500" />
          Sign Out
        </a>
      </div>
    </aside>

    <div class="flex-1 flex flex-col overflow-hidden">
      
      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-6 lg:px-8">
        <div class="flex items-center flex-1">
          <div class="relative w-full max-w-md hidden sm:block">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input type="text" placeholder="Search courses, students, or tasks..." class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm">
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <button class="text-gray-400 hover:text-gray-600 relative">
            <Bell class="h-6 w-6" />
            <span class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
          </button>
          <div class="h-8 w-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold shadow-md cursor-pointer">
            A
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto bg-gray-50 p-4 sm:p-6 lg:p-8">
        
        <div class="flex items-center justify-between mb-8">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Instructor Control Center</h2>
            <p class="text-sm text-gray-500 mt-1">Manage your active modules and student progress.</p>
          </div>
          <button class="hidden sm:flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
            <Plus class="h-4 w-4 mr-2" /> New Course
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div v-for="tool in instructorTools" :key="tool.name" class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center hover:shadow-md transition-all cursor-pointer group">
            <div :class="[tool.bg, tool.color, 'h-12 w-12 rounded-lg flex items-center justify-center mr-4 group-hover:scale-105 transition-transform']">
              <component :is="tool.icon" class="h-6 w-6" />
            </div>
            <div>
              <h3 class="text-sm font-bold text-gray-900">{{ tool.name }}</h3>
              <p class="text-xs text-gray-500 mt-0.5 flex items-center">Launch tool <ChevronRight class="h-3 w-3 ml-1" /></p>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-5 sm:grid-cols-3 mb-8">
          <div v-for="stat in stats" :key="stat.id" class="bg-white rounded-xl border border-gray-100 p-6 shadow-sm">
            <dt class="text-sm font-medium text-gray-500">{{ stat.name }}</dt>
            <dd class="mt-2 flex items-baseline text-3xl font-extrabold text-gray-900">
              {{ stat.value }}
            </dd>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden mb-8">
          <div class="px-6 py-5 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Active Modules</h3>
          </div>
          <ul role="list" class="divide-y divide-gray-200">
            <li v-for="course in courses" :key="course.id" 
                @click="router.push(`/course/${course.id}`)"
                class="p-6 hover:bg-gray-50 transition-colors cursor-pointer flex items-center justify-between">
              <div class="flex items-center space-x-4">
                <div :class="[course.color, 'h-12 w-12 rounded-lg flex items-center justify-center shadow-inner']">
                  <span class="text-white font-bold text-sm">{{ course.code.split('-')[0] }}</span>
                </div>
                <div>
                  <p class="text-sm font-bold text-gray-900">{{ course.title }}</p>
                  <p class="text-sm text-gray-500">{{ course.code }} • {{ course.students }} Students</p>
                </div>
              </div>
              <ChevronRight class="h-5 w-5 text-gray-400" />
            </li>
          </ul>
        </div>
        
      </main>
    </div>
  </div>
</template>

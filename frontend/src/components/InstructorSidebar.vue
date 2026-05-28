<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  LayoutDashboard, BookOpen, LogOut, 
  ClipboardCheck, GraduationCap, Settings, UserCheck
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const courseId = computed(() => Number(route.params.id) || 0)
const username = ref(localStorage.getItem('username') || 'Instructor')

const handleLogout = () => {
  localStorage.clear() // Hard clear for absolute security
  router.push('/login')
}

// Smart active state logic
const isExactActive = (path: string) => route.path === path
const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/')
</script>

<template>
  <aside class="w-64 bg-white border-r border-gray-200 flex-col hidden md:flex flex-shrink-0 z-20 shadow-sm transition-all duration-300">
    
    <div class="h-16 flex items-center px-6 border-b border-gray-100 shrink-0">
      <div class="h-8 w-8 bg-indigo-600 rounded-lg flex items-center justify-center mr-3 shadow-sm">
        <span class="text-white font-extrabold text-lg">E</span>
      </div>
      <h1 class="text-xl font-extrabold text-gray-900 tracking-tight">
        EDUCLOUD <span class="text-indigo-600">2.0</span>
      </h1>
    </div>

    <nav class="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto custom-scrollbar">
   

      <a @click="router.push('/dashboard')"
         :class="[isExactActive('/dashboard') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <LayoutDashboard :class="[isExactActive('/dashboard') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Dashboard
      </a>

      <a @click="router.push('/my-courses')"
         :class="[isActive('/my-courses') || isActive('/course/') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <BookOpen :class="[isActive('/my-courses') || isActive('/course/') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        My Modules
      </a>

      
      <a @click="router.push('/attendance')"
         :class="[isActive('/attendance') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <UserCheck :class="[isActive('/attendance') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Smart Attendance
      </a>

      <a @click="router.push('/gradebook')"
         :class="[isActive('/gradebook') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <GraduationCap :class="[isActive('/gradebook') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Master Gradebook
      </a>
      
      <a @click="router.push('/quizzes')"
         :class="[isActive('/quizzes') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <ClipboardCheck :class="[isActive('/quizzes') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Assessment Manager
      </a>
    </nav>

    <div class="border-t border-gray-100 p-4 bg-gray-50/50 shrink-0">
      

      <div class="space-y-1">
        <a @click="router.push('/instructor/settings')"
           :class="[isActive('/instructor/settings') ? 'bg-indigo-100 text-indigo-800' : 'text-gray-600 hover:bg-white hover:shadow-sm', 'flex items-center px-3 py-2 rounded-lg text-sm font-semibold transition-all cursor-pointer group']">
          <Settings :class="[isActive('/instructor/settings') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-4 h-4 mr-3 transition-colors']" /> 
          Settings
        </a>
        <a @click="handleLogout" class="flex items-center px-3 py-2 text-red-600 hover:bg-red-50 hover:shadow-sm rounded-lg text-sm font-semibold transition-all cursor-pointer group">
          <LogOut class="w-4 h-4 mr-3 text-red-400 group-hover:text-red-600 transition-colors" /> 
          Sign Out
        </a>
      </div>
    </div>

  </aside>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 10px;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: #d1d5db;
}
</style>
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  LayoutDashboard, GraduationCap, LogOut, Settings, BookOpen,
  ClipboardList, CalendarDays
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

// Fetch the user's name to personalize the bottom of the sidebar
const username = ref(localStorage.getItem('username') || 'Student User')

const handleLogout = () => {
  localStorage.clear() // Instantly wipes all tokens and user data
  router.push('/login')
}

// Smart active state logic (Dashboard needs an exact match, others can be partial)
const isExactActive = (path: string) => route.path === path
const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/')
</script>

<template>
  <aside class="w-64 bg-white border-r border-gray-200 flex-col hidden md:flex flex-shrink-0 z-20 shadow-sm transition-all duration-300">
    
    <!-- Header / Logo -->
    <div class="h-16 flex items-center px-6 border-b border-gray-100">
      <div class="h-8 w-8 bg-indigo-600 rounded-lg flex items-center justify-center mr-3 shadow-sm">
        <span class="text-white font-extrabold text-lg">E</span>
      </div>
      <h1 class="text-xl font-extrabold text-gray-900 tracking-tight">
        EDUCLOUD <span class="text-indigo-600">2.0</span>
      </h1>
    </div>

    <!-- Main Navigation Links -->
    <nav class="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto custom-scrollbar">
      

      <a @click="router.push('/student')"
         :class="[isExactActive('/student') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <LayoutDashboard :class="[isExactActive('/student') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Dashboard
      </a>

      <a @click="router.push('/student/courses')"
         :class="[isActive('/student/courses') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <BookOpen :class="[isActive('/student/courses') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        My Modules
      </a>

      <a @click="router.push('/student/assignments')"
         :class="[isActive('/student/assignments') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <ClipboardList :class="[isActive('/student/assignments') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Tasks & Assignments
      </a>

      <a @click="router.push('/student/calendar')"
         :class="[isActive('/student/calendar') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <CalendarDays :class="[isActive('/student/calendar') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Master Schedule
      </a>

     

      <a @click="router.push('/student/marksheet')"
         :class="[isActive('/student/marksheet') ? 'bg-indigo-50 text-indigo-700 relative before:absolute before:inset-y-0 before:left-0 before:w-1 before:bg-indigo-600 before:rounded-r-full' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900', 'flex items-center px-3 py-2.5 rounded-lg font-semibold transition-all cursor-pointer group']">
        <GraduationCap :class="[isActive('/student/marksheet') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Official Marksheet
      </a>
    </nav>

    <!-- Footer: User Profile & Settings -->
    <div class="border-t border-gray-100 p-4 bg-gray-50/50">
      
     

      <div class="space-y-1">
        <a @click="router.push('/student/settings')"
           :class="[isActive('/student/settings') ? 'bg-indigo-100 text-indigo-800' : 'text-gray-600 hover:bg-white hover:shadow-sm', 'flex items-center px-3 py-2 rounded-lg text-sm font-semibold transition-all cursor-pointer group']">
          <Settings :class="[isActive('/student/settings') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-4 h-4 mr-3 transition-colors']" /> 
          Account Settings
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
/* Sleek custom scrollbar for the sidebar */
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
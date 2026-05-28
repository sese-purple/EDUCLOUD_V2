<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import {
  LayoutDashboard, GraduationCap, LogOut, Settings, BookOpen
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  router.push('/login')
}

const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/')
</script>

<template>
  <aside class="w-64 bg-white border-r border-gray-200 flex flex-col hidden md:flex flex-shrink-0 z-20 shadow-sm">
    <div class="h-16 flex items-center px-6 border-b border-gray-200">
      <h1 class="text-xl font-bold text-gray-900 tracking-tight">
        EDUCLOUD <span class="text-indigo-600">2.0</span>
      </h1>
    </div>

    <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
      <p class="px-3 text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Student Portal</p>

      <a @click="router.push('/student')"
         :class="[route.path === '/student' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50', 'flex items-center px-3 py-2.5 rounded-lg font-medium transition-colors cursor-pointer group']">
        <LayoutDashboard :class="[route.path === '/student' ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Dashboard
      </a>

      <a @click="router.push('/student/marksheet')"
         :class="[isActive('/student/marksheet') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50', 'flex items-center px-3 py-2.5 rounded-lg font-medium transition-colors cursor-pointer group']">
        <GraduationCap :class="[isActive('/student/marksheet') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Marksheet
      </a>

      <a @click="router.push('/student/courses')"
         :class="[isActive('/student/courses') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50', 'flex items-center px-3 py-2.5 rounded-lg font-medium transition-colors cursor-pointer group']">
        <BookOpen :class="[isActive('/student/courses') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        My Courses
      </a>
    </nav>

    <div class="p-4 border-t border-gray-200 space-y-1">
      <a @click="router.push('/student/settings')"
         :class="[isActive('/student/settings') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50', 'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer']">
        <Settings class="w-4 h-4 mr-3 text-gray-400" /> Settings
      </a>
      <a @click="handleLogout" class="flex items-center px-3 py-2.5 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors cursor-pointer">
        <LogOut class="w-5 h-5 mr-3 text-red-500" /> Sign Out
      </a>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api'
import {
  LayoutDashboard, BookOpen, LogOut, ChevronDown,
  ClipboardCheck, GraduationCap, Settings
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const courses = ref<any[]>([])
const expanded = ref(false)

const courseId = computed(() => Number(route.params.id) || 0)

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  router.push('/login')
}

onMounted(async () => {
  try {
    const res = await api.get('instructor-dashboard/')
    courses.value = res.data.courses
  } catch (_e) { /* ignore */ }
})

const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/')

const goToFirstCourseFeature = (feature: string) => {
  if (courseId.value) {
    router.push(`/course/${courseId.value}/${feature}`)
  } else if (courses.value.length) {
    router.push(`/course/${courses.value[0].id}/${feature}`)
  } else {
    alert('Select a course first.')
  }
}
</script>

<template>
  <aside class="w-64 bg-white border-r border-gray-200 flex flex-col hidden md:flex flex-shrink-0 z-20 shadow-sm">

    <div class="h-16 flex items-center px-6 border-b border-gray-200">
      <h1 class="text-xl font-bold text-gray-900 tracking-tight">
        EDUCLOUD <span class="text-indigo-600">2.0</span>
      </h1>
    </div>

    <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
      <a @click="router.push('/dashboard')"
         :class="[isActive('/dashboard') && !isActive('/my-courses') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50', 'flex items-center px-3 py-2.5 rounded-lg font-medium transition-colors cursor-pointer group']">
        <LayoutDashboard :class="[isActive('/dashboard') && !isActive('/my-courses') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
        Dashboard
      </a>

      <div>
        <a @click="expanded = !expanded"
           :class="[isActive('/my-courses') || isActive('/course/') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50', 'flex items-center justify-between px-3 py-2.5 rounded-lg font-medium transition-colors cursor-pointer group']">
          <span class="flex items-center">
            <BookOpen :class="[isActive('/my-courses') || isActive('/course/') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-5 h-5 mr-3 transition-colors']" />
            My Courses
          </span>
          <ChevronDown :class="[expanded ? 'rotate-180' : '', 'h-4 w-4 text-gray-400 transition-transform']" />
        </a>
        <div v-if="expanded || isActive('/course/') || isActive('/my-courses')" class="ml-6 mt-1 space-y-0.5">
          <a @click="router.push('/my-courses')"
             :class="[route.path === '/my-courses' ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50', 'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer']">
            All Courses
          </a>
          <a v-for="c in courses.slice(0, 8)" :key="c.id"
             @click="router.push(`/course/${c.id}`)"
             :class="[route.params.id == c.id ? 'bg-indigo-50 text-indigo-700' : 'text-gray-600 hover:bg-gray-50', 'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer truncate']">
            {{ c.title }}
          </a>
        </div>
      </div>

      <div class="pt-4 mt-4 border-t border-gray-100">
        <p class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Course Tools</p>
        <a @click="goToFirstCourseFeature('quizzes')"
           :class="[isActive('/course/' + courseId + '/quizzes') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50', 'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer group']">
          <ClipboardCheck :class="[isActive('/course/' + courseId + '/quizzes') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-4 h-4 mr-3 transition-colors']" />
          Quiz Manager
        </a>
        <a @click="router.push('/gradebook')"
           :class="[isActive('/gradebook') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50', 'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer group']">
          <GraduationCap :class="[isActive('/gradebook') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-4 h-4 mr-3 transition-colors']" />
          Gradebook
        </a>

      </div>

      <div class="pt-4 mt-4 border-t border-gray-100">
        <p class="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">System</p>
        <a @click="router.push('/instructor/settings')"
           :class="[isActive('/instructor/settings') ? 'bg-indigo-50 text-indigo-700' : 'text-gray-700 hover:bg-gray-50', 'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer group']">
          <Settings :class="[isActive('/instructor/settings') ? 'text-indigo-600' : 'text-gray-400 group-hover:text-gray-600', 'w-4 h-4 mr-3 transition-colors']" />
          Settings
        </a>
      </div>
    </nav>

    <div class="p-4 border-t border-gray-200">
      <a @click="handleLogout" class="flex items-center px-3 py-2.5 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors cursor-pointer">
        <LogOut class="w-5 h-5 mr-3 text-red-500" />
        Sign Out
      </a>
    </div>
  </aside>
</template>

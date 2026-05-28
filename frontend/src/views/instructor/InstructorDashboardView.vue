<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  BookOpen, Users, Bell, MapPin,
  ChevronRight, FileText, LayoutDashboard
} from 'lucide-vue-next'

const router = useRouter()

const courses = ref<any[]>([])
const isLoading = ref(true)

const totalEnrolled = computed(() =>
  courses.value.reduce((sum: number, c: any) => sum + (c.students || 0), 0)
)

const quickTools = [
  { name: 'Generate QR Attendance', icon: MapPin, color: 'text-indigo-600', bg: 'bg-indigo-100', route: (c: number) => `/course/${c}/attendance` },
  { name: 'Agile Project Boards', icon: Users, color: 'text-blue-600', bg: 'bg-blue-100', route: (c: number) => `/course/${c}` },
  { name: 'Export Mark Sheets', icon: FileText, color: 'text-purple-600', bg: 'bg-purple-100', route: (c: number) => `/course/${c}/grades` },
  { name: 'Course Overview', icon: LayoutDashboard, color: 'text-amber-600', bg: 'bg-amber-100', route: (c: number) => `/course/${c}` },
]

const launchTool = (tool: (typeof quickTools)[0]) => {
  if (!courses.value.length) {
    alert('No courses assigned. Contact your admin.')
    return
  }
  router.push(tool.route(courses.value[0].id))
}

const fetchDashboard = async () => {
  isLoading.value = true
  try {
    const res = await api.get('instructor-dashboard/')
    courses.value = res.data.courses
  } catch (error) {
    console.error("Error fetching instructor dashboard:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchDashboard()
})
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">

    <InstructorSidebar />

    <div class="flex-1 flex flex-col overflow-hidden">

      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm z-10">
        <div>
          <h2 class="text-lg font-bold text-gray-800">EDUCLOUD <span class="text-indigo-600">Instructor</span></h2>
        </div>
        <div class="flex items-center space-x-4">
          <button class="text-gray-400 hover:text-gray-600">
            <Bell class="h-5 w-5" />
          </button>
          <div class="h-8 w-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold shadow-sm">
            I
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">

        <div class="flex items-center justify-between mb-8">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Instructor Control Center</h2>
            <p class="text-sm text-gray-500 mt-1">Manage your active modules and student progress.</p>
          </div>
        </div>

        <div v-if="isLoading" class="text-center py-16 text-gray-500">
          Loading dashboard data...
        </div>

        <template v-else>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div v-for="tool in quickTools" :key="tool.name" @click="launchTool(tool)"
                 class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex items-center hover:shadow-md transition-all cursor-pointer group">
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
            <div class="bg-white rounded-xl border border-gray-100 p-6 shadow-sm">
              <dt class="text-sm font-medium text-gray-500">Total Enrolled</dt>
              <dd class="mt-2 flex items-baseline text-3xl font-extrabold text-gray-900">{{ totalEnrolled }}</dd>
            </div>
            <div class="bg-white rounded-xl border border-gray-100 p-6 shadow-sm">
              <dt class="text-sm font-medium text-gray-500">Active Modules</dt>
              <dd class="mt-2 flex items-baseline text-3xl font-extrabold text-gray-900">{{ courses.length }}</dd>
            </div>
            <div class="bg-white rounded-xl border border-gray-100 p-6 shadow-sm">
              <dt class="text-sm font-medium text-gray-500">Courses</dt>
              <dd class="mt-2 flex items-baseline text-3xl font-extrabold text-gray-900">{{ courses.length }}</dd>
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
                  <div class="h-12 w-12 bg-indigo-100 rounded-lg flex items-center justify-center shadow-inner">
                    <span class="text-indigo-700 font-bold text-sm">{{ course.course_code?.split('-')[0] }}</span>
                  </div>
                  <div>
                    <p class="text-sm font-bold text-gray-900">{{ course.title }}</p>
                    <p class="text-sm text-gray-500">{{ course.course_code }} • {{ course.students }} Students</p>
                  </div>
                </div>
                <ChevronRight class="h-5 w-5 text-gray-400" />
              </li>
            </ul>
            <div v-if="courses.length === 0" class="p-12 text-center">
              <BookOpen class="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <h3 class="text-lg font-medium text-gray-900">No courses assigned</h3>
              <p class="text-sm text-gray-500 mt-1">Contact your institution admin to get assigned to a course.</p>
            </div>
          </div>

        </template>

      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  BookOpen, Users, Bell, ChevronRight, FileText, 
  LayoutDashboard, Menu, GraduationCap, Settings, LogOut,
  UserCheck, ClipboardCheck, Sparkles, TrendingUp
} from 'lucide-vue-next'

const router = useRouter()

const courses = ref<any[]>([])
const isLoading = ref(true)
const mobileMenuOpen = ref(false)
const username = ref(localStorage.getItem('username') || 'Instructor')

// Dynamic Greeting
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
})

const totalEnrolled = computed(() =>
  courses.value.reduce((sum: number, c: any) => sum + (c.students || 0), 0)
)

// UPGRADE: Clean global routes instead of hacky course[0] guessing
const quickTools = [
  { name: 'Smart Attendance', desc: 'Take roll call instantly', icon: UserCheck, color: 'text-indigo-600', bg: 'bg-indigo-100', route: '/attendance' },
  { name: 'Assessment Manager', desc: 'Grade pending quizzes', icon: ClipboardCheck, color: 'text-orange-600', bg: 'bg-orange-100', route: '/quizzes' },
  { name: 'Master Gradebook', desc: 'Export official marks', icon: GraduationCap, color: 'text-emerald-600', bg: 'bg-emerald-100', route: '/gradebook' },
  { name: 'Module Settings', desc: 'Update course syllabus', icon: Settings, color: 'text-slate-600', bg: 'bg-slate-100', route: '/my-courses' },
]

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

    <div v-if="mobileMenuOpen" class="fixed inset-0 z-50 flex md:hidden">
      <div class="fixed inset-0 bg-gray-900/80 backdrop-blur-sm" @click="mobileMenuOpen = false"></div>
      <div class="relative flex w-full max-w-xs flex-1 flex-col bg-white pt-5 pb-4 shadow-2xl">
        <div class="flex items-center justify-between px-4 mb-6">
          <h1 class="text-xl font-extrabold text-gray-900 tracking-tight">EDUCLOUD <span class="text-indigo-600">2.0</span></h1>
          <button @click="mobileMenuOpen = false" class="text-gray-400 hover:text-gray-600 bg-gray-100 rounded-full p-1"><span class="text-xl leading-none">&times;</span></button>
        </div>
        <nav class="flex-1 px-4 space-y-1">
          <a @click="mobileMenuOpen = false; router.push('/dashboard')" class="flex items-center px-3 py-3 bg-indigo-50 text-indigo-700 rounded-xl font-bold transition-colors cursor-pointer">
            <LayoutDashboard class="w-5 h-5 mr-3 text-indigo-600" /> Dashboard
          </a>
          <a @click="mobileMenuOpen = false; router.push('/my-courses')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <BookOpen class="w-5 h-5 mr-3 text-gray-400" /> My Modules
          </a>
          <a @click="mobileMenuOpen = false; router.push('/attendance')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <UserCheck class="w-5 h-5 mr-3 text-gray-400" /> Attendance
          </a>
          <a @click="mobileMenuOpen = false; router.push('/gradebook')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <GraduationCap class="w-5 h-5 mr-3 text-gray-400" /> Gradebook
          </a>
          <hr class="my-4 border-gray-100" />
          <a @click="localStorage.clear(); router.push('/login')" class="flex items-center px-3 py-3 text-red-600 hover:bg-red-50 rounded-xl font-medium transition-colors cursor-pointer">
            <LogOut class="w-5 h-5 mr-3 text-red-500" /> Sign Out
          </a>
        </nav>
      </div>
    </div>

    <div class="flex-1 flex flex-col overflow-hidden relative">

      <header class="h-16 bg-white/80 backdrop-blur-md border-b border-gray-200 flex items-center justify-between px-4 sm:px-8 z-10 sticky top-0">
        <div class="flex items-center">
          <button @click="mobileMenuOpen = true" class="mr-4 md:hidden text-gray-500 hover:text-gray-900 focus:outline-none p-1 rounded-md hover:bg-gray-100">
            <Menu class="h-6 w-6" />
          </button>
          <div class="hidden sm:block">
            <h2 class="text-sm font-bold text-gray-800 uppercase tracking-wider">Faculty Portal</h2>
          </div>
        </div>
        <div class="flex items-center space-x-5">
          <div class="relative cursor-pointer group">
            <Bell class="h-5 w-5 text-gray-400 group-hover:text-indigo-600 transition-colors" />
            <span class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
          </div>
          <div class="h-9 w-9 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 text-white flex items-center justify-center font-bold shadow-md text-sm border-2 border-white cursor-pointer hover:scale-105 transition-transform">
            {{ username.charAt(0).toUpperCase() }}
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 sm:p-8 bg-gray-50/50">

        <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 text-indigo-400">
          <Sparkles class="h-10 w-10 animate-pulse mb-4" />
          <p class="font-medium">Syncing your dashboard...</p>
        </div>

        <template v-else>

          <div class="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h1 class="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
                {{ greeting }}, <span class="text-indigo-600">Prof. {{ username.replace('prof_', '').split('_')[0] }}</span> 
              </h1>
              <p class="text-sm text-gray-500 mt-1 font-medium">{{ currentDate }}</p>
            </div>
            
            <div class="flex bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden shrink-0">
              <div class="px-5 py-3 border-r border-gray-100 flex items-center">
                <div class="h-8 w-8 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center mr-3"><Users class="h-4 w-4"/></div>
                <div>
                  <p class="text-xs font-bold text-gray-400 uppercase tracking-wider">Total Students</p>
                  <p class="text-lg font-extrabold text-gray-900 leading-none mt-0.5">{{ totalEnrolled }}</p>
                </div>
              </div>
              <div class="px-5 py-3 flex items-center">
                <div class="h-8 w-8 bg-emerald-50 text-emerald-600 rounded-lg flex items-center justify-center mr-3"><BookOpen class="h-4 w-4"/></div>
                <div>
                  <p class="text-xs font-bold text-gray-400 uppercase tracking-wider">Active Modules</p>
                  <p class="text-lg font-extrabold text-gray-900 leading-none mt-0.5">{{ courses.length }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="mb-8">
            <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wider mb-3">Quick Launch</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div v-for="tool in quickTools" :key="tool.name" @click="router.push(tool.route)"
                   class="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm flex items-center hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group">
                <div :class="[tool.bg, tool.color, 'h-12 w-12 rounded-xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform']">
                  <component :is="tool.icon" class="h-6 w-6" />
                </div>
                <div class="min-w-0">
                  <h3 class="text-sm font-bold text-gray-900 truncate">{{ tool.name }}</h3>
                  <p class="text-[11px] text-gray-500 font-medium mt-0.5 truncate">{{ tool.desc }}</p>
                </div>
              </div>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-sm font-bold text-gray-900 uppercase tracking-wider">Your Assigned Modules</h3>
              <button @click="router.push('/my-courses')" class="text-sm font-bold text-indigo-600 hover:text-indigo-800">View All</button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              <div v-for="course in courses" :key="course.id"
                   @click="router.push(`/course/${course.id}`)"
                   class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group flex flex-col">
                
                <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-purple-600"></div>
                
                <div class="p-6 flex flex-col flex-1">
                  <div class="flex items-center justify-between mb-4">
                    <div class="h-12 w-12 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center justify-center shrink-0">
                      <span class="text-indigo-700 font-extrabold text-sm">{{ course.course_code?.split('-')[0] || 'CR' }}</span>
                    </div>
                    <span class="bg-gray-100 text-gray-600 text-[10px] font-bold uppercase px-2.5 py-1 rounded-md flex items-center">
                      <Users class="h-3 w-3 mr-1" /> {{ course.students || 0 }}
                    </span>
                  </div>
                  
                  <div class="mb-4">
                    <h3 class="text-lg font-extrabold text-gray-900 line-clamp-2 group-hover:text-indigo-700 transition-colors">{{ course.title }}</h3>
                    <p class="text-xs font-bold text-gray-400 mt-1 uppercase tracking-wider">{{ course.course_code }}</p>
                  </div>

                  <div class="mt-auto pt-4 border-t border-gray-50 flex items-center justify-between text-sm font-bold text-indigo-600 group-hover:text-indigo-800">
                    Open Control Center <ChevronRight class="h-4 w-4" />
                  </div>
                </div>
              </div>

              <div v-if="courses.length === 0" class="col-span-full bg-white rounded-2xl border-2 border-dashed border-gray-200 p-12 text-center flex flex-col items-center">
                <div class="h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                  <BookOpen class="h-8 w-8 text-gray-300" />
                </div>
                <h3 class="text-base font-bold text-gray-900">No modules assigned</h3>
                <p class="text-sm text-gray-500 mt-1 max-w-sm">You do not currently have any active courses. Please contact the IT Administrator to be provisioned.</p>
              </div>
            </div>
          </div>

        </template>
      </main>
    </div>
  </div>
</template>
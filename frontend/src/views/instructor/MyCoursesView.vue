<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  BookOpen, ChevronRight, Menu, Bell, Search,
  Users, Sparkles, LayoutDashboard, UserCheck, 
  GraduationCap, ClipboardCheck, Settings, LogOut
} from 'lucide-vue-next'

const router = useRouter()
const courses = ref<any[]>([])
const isLoading = ref(true)
const searchQuery = ref('')
const mobileMenuOpen = ref(false)
const username = ref(localStorage.getItem('username') || 'Instructor')

onMounted(async () => {
  try {
    const res = await api.get('instructor-dashboard/')
    courses.value = res.data.courses
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
})

// Smart Search Logic
const filteredCourses = computed(() => {
  if (!searchQuery.value.trim()) return courses.value
  
  const q = searchQuery.value.toLowerCase()
  return courses.value.filter(c => 
    c.title.toLowerCase().includes(q) || 
    c.course_code?.toLowerCase().includes(q)
  )
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
          <a @click="mobileMenuOpen = false; router.push('/dashboard')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <LayoutDashboard class="w-5 h-5 mr-3 text-gray-400" /> Dashboard
          </a>
          <a @click="mobileMenuOpen = false; router.push('/my-courses')" class="flex items-center px-3 py-3 bg-indigo-50 text-indigo-700 rounded-xl font-bold transition-colors cursor-pointer">
            <BookOpen class="w-5 h-5 mr-3 text-indigo-600" /> My Modules
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

      <header class="h-16 bg-white/80 backdrop-blur-md border-b border-gray-200 flex items-center justify-between px-4 sm:px-8 z-10 sticky top-0 shrink-0">
        <div class="flex items-center">
          <button @click="mobileMenuOpen = true" class="mr-4 md:hidden text-gray-500 hover:text-gray-900 focus:outline-none p-1 rounded-md hover:bg-gray-100">
            <Menu class="h-6 w-6" />
          </button>
          <div class="hidden sm:flex items-center">
            <BookOpen class="h-5 w-5 text-indigo-600 mr-2" />
            <h2 class="text-sm font-bold text-gray-800 uppercase tracking-wider">Module Directory</h2>
          </div>
        </div>
        <div class="flex items-center space-x-5">
          <Bell class="h-5 w-5 text-gray-400 hover:text-indigo-600 cursor-pointer transition-colors" />
          <div class="h-9 w-9 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 text-white flex items-center justify-center font-bold shadow-md text-sm border-2 border-white cursor-pointer hover:scale-105 transition-transform">
            {{ username.charAt(0).toUpperCase() }}
          </div>
        </div>
      </header>

      <div class="bg-white border-b border-gray-200 px-4 sm:px-8 py-4 shrink-0 flex items-center justify-between">
        <h1 class="text-xl font-extrabold text-gray-900 hidden sm:block">All Modules</h1>
        
        <div class="relative w-full sm:w-80">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input v-model="searchQuery" placeholder="Search by title or course code..."
            class="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm font-medium focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all shadow-inner" />
        </div>
      </div>

      <main class="flex-1 overflow-y-auto p-4 sm:p-8 bg-gray-50/50">
        
        <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 text-indigo-400">
          <Sparkles class="h-10 w-10 animate-pulse mb-4" />
          <p class="font-medium">Loading your modules...</p>
        </div>

        <template v-else>
          <div v-if="!filteredCourses.length" class="flex flex-col items-center justify-center py-20 text-center">
            <div class="h-20 w-20 bg-white rounded-full shadow-sm flex items-center justify-center mb-4 border border-gray-100">
              <BookOpen class="h-10 w-10 text-gray-300" />
            </div>
            <h3 class="text-lg font-bold text-gray-900">No modules found</h3>
            <p class="text-gray-500 text-sm mt-1 max-w-sm">
              {{ searchQuery ? "No courses match your search criteria." : "You have not been assigned to any modules yet." }}
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <div v-for="course in filteredCourses" :key="course.id"
                 @click="router.push(`/course/${course.id}`)"
                 class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group flex flex-col">
              
              <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-purple-600"></div>
              
              <div class="p-6 flex flex-col flex-1">
                <div class="flex items-start justify-between mb-4">
                  <div class="h-12 w-12 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center justify-center shrink-0">
                    <span class="text-indigo-700 font-extrabold text-sm">{{ course.course_code?.split('-')[0] || 'CR' }}</span>
                  </div>
                  
                  <span class="bg-gray-100 text-gray-600 text-[10px] font-bold uppercase px-2.5 py-1 rounded-md flex items-center shrink-0">
                    <Users class="h-3 w-3 mr-1" /> {{ course.students || 0 }} Enrolled
                  </span>
                </div>
                
                <div class="mb-5 flex-1">
                  <h3 class="text-lg font-extrabold text-gray-900 line-clamp-2 group-hover:text-indigo-700 transition-colors">{{ course.title }}</h3>
                  <p class="text-xs font-bold text-gray-400 mt-1 uppercase tracking-wider">{{ course.course_code }}</p>
                </div>

                <div class="mt-auto pt-4 border-t border-gray-50 flex items-center justify-between text-sm font-bold text-indigo-600 group-hover:text-indigo-800 transition-colors">
                  Open Control Center <ChevronRight class="h-4 w-4" />
                </div>
              </div>
            </div>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>
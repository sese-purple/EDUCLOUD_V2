<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  BookOpen, Search, Key, CheckCircle, Lock,
  LogIn, X, ChevronRight, GraduationCap,
  Menu, Bell, Sparkles, LayoutDashboard, Settings, LogOut, CheckCircle2
} from 'lucide-vue-next'

const router = useRouter()
const courses = ref<any[]>([])
const isLoading = ref(true)
const searchQuery = ref('')
const activeTab = ref<'enrolled' | 'catalog'>('enrolled') // 🧠 New Tab State
const mobileMenuOpen = ref(false)
const username = ref(localStorage.getItem('username') || 'Student')

// Modal State
const showEnrollModal = ref(false)
const enrollKey = ref('')
const enrolling = ref(false)
const selectedCourse = ref<any>(null)
const enrollError = ref('')
const enrollSuccess = ref('')

onMounted(async () => {
  try {
    const res = await api.get('courses/')
    courses.value = res.data
  } catch (err) { 
    console.error(err) 
  } finally { 
    isLoading.value = false 
  }
})

// 🧠 UPGRADE: Computed property handles both Tabs AND Search automatically!
const filteredCourses = computed(() => {
  let result = courses.value

  // 1. Filter by Tab
  if (activeTab.value === 'enrolled') {
    result = result.filter(c => c.is_enrolled)
  } else {
    result = result.filter(c => !c.is_enrolled)
  }

  // 2. Filter by Search Query
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(c =>
      c.title.toLowerCase().includes(q) ||
      c.course_code?.toLowerCase().includes(q) ||
      c.instructor?.first_name?.toLowerCase().includes(q) ||
      c.instructor?.last_name?.toLowerCase().includes(q)
    )
  }

  return result
})

const openEnroll = (course: any) => {
  selectedCourse.value = course
  enrollKey.value = ''
  enrollError.value = ''
  enrollSuccess.value = ''
  showEnrollModal.value = true
}

const confirmEnroll = async () => {
  if (!selectedCourse.value) return
  enrolling.value = true
  enrollError.value = ''
  enrollSuccess.value = ''
  try {
    const res = await api.post(`courses/${selectedCourse.value.id}/enroll/`, {
      enrollment_key: enrollKey.value
    })
    enrollSuccess.value = res.data.detail
    
    // Update local state without refreshing the page
    const courseIndex = courses.value.findIndex(c => c.id === selectedCourse.value.id)
    if (courseIndex !== -1) {
      courses.value[courseIndex].is_enrolled = true
    }
    
    setTimeout(() => { 
      showEnrollModal.value = false
      activeTab.value = 'enrolled' // Teleport them back to their courses tab!
    }, 1200)
  } catch (err: any) {
    enrollError.value = err.response?.data?.detail || 'Invalid enrollment key.'
  } finally { 
    enrolling.value = false 
  }
}

const goToCourse = (course: any) => {
  router.push(`/student/course/${course.id}`)
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    
    <StudentSidebar />

    <div v-if="mobileMenuOpen" class="fixed inset-0 z-50 flex md:hidden">
      <div class="fixed inset-0 bg-gray-900/80 backdrop-blur-sm" @click="mobileMenuOpen = false"></div>
      <div class="relative flex w-full max-w-xs flex-1 flex-col bg-white pt-5 pb-4 shadow-2xl">
        <div class="flex items-center justify-between px-4 mb-6">
          <h1 class="text-xl font-extrabold text-gray-900 tracking-tight">EDUCLOUD <span class="text-indigo-600">2.0</span></h1>
          <button @click="mobileMenuOpen = false" class="text-gray-400 hover:text-gray-600 bg-gray-100 rounded-full p-1"><span class="text-xl leading-none">&times;</span></button>
        </div>
        <nav class="flex-1 px-4 space-y-1">
          <a @click="mobileMenuOpen = false; router.push('/student')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <LayoutDashboard class="w-5 h-5 mr-3 text-gray-400" /> Dashboard
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/courses')" class="flex items-center px-3 py-3 bg-indigo-50 text-indigo-700 rounded-xl font-bold transition-colors cursor-pointer">
            <BookOpen class="w-5 h-5 mr-3 text-indigo-600" /> My Modules
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/marksheet')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <GraduationCap class="w-5 h-5 mr-3 text-gray-400" /> Marksheet
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/settings')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <Settings class="w-5 h-5 mr-3 text-gray-400" /> Settings
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
          <div class="hidden sm:flex items-center">
            <BookOpen class="h-5 w-5 text-indigo-600 mr-2" />
            <h2 class="text-sm font-bold text-gray-800 uppercase tracking-wider">Course Management</h2>
          </div>
        </div>
        <div class="flex items-center space-x-5">
          <Bell class="h-5 w-5 text-gray-400 hover:text-indigo-600 cursor-pointer transition-colors" />
          <div class="h-9 w-9 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 text-white flex items-center justify-center font-bold shadow-md text-sm border-2 border-white cursor-pointer hover:scale-105 transition-transform">
            {{ username.charAt(0).toUpperCase() }}
          </div>
        </div>
      </header>

      <div class="bg-white border-b border-gray-200 px-4 sm:px-8 py-4 shrink-0 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div class="flex bg-gray-100 p-1 rounded-lg w-full sm:w-auto">
          <button @click="activeTab = 'enrolled'" 
            :class="[activeTab === 'enrolled' ? 'bg-white shadow-sm text-indigo-700 font-bold' : 'text-gray-500 font-medium hover:text-gray-700', 'flex-1 sm:flex-none px-4 py-2 text-sm rounded-md transition-all']">
            My Modules
          </button>
          <button @click="activeTab = 'catalog'" 
            :class="[activeTab === 'catalog' ? 'bg-white shadow-sm text-indigo-700 font-bold' : 'text-gray-500 font-medium hover:text-gray-700', 'flex-1 sm:flex-none px-4 py-2 text-sm rounded-md transition-all']">
            Browse Catalog
          </button>
        </div>

        <div class="relative w-full sm:w-72">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input v-model="searchQuery" placeholder="Search courses or professors..."
            class="w-full pl-9 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all shadow-inner" />
        </div>
      </div>

      <main class="flex-1 overflow-y-auto p-4 sm:p-8 bg-gray-50">
        
        <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 text-indigo-400">
          <Sparkles class="h-10 w-10 animate-pulse mb-4" />
          <p class="font-medium">Loading course catalog...</p>
        </div>

        <template v-else>
          
          <div v-if="!filteredCourses.length" class="flex flex-col items-center justify-center py-20 text-center">
            <div class="h-20 w-20 bg-white rounded-full shadow-sm flex items-center justify-center mb-4 border border-gray-100">
              <BookOpen class="h-10 w-10 text-gray-300" />
            </div>
            <h3 class="text-lg font-bold text-gray-900">No courses found</h3>
            <p class="text-gray-500 text-sm mt-1 max-w-sm">
              {{ activeTab === 'enrolled' ? "You aren't enrolled in any courses yet. Check the 'Browse Catalog' tab." : "No courses match your search criteria." }}
            </p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <div v-for="course in filteredCourses" :key="course.id"
                 class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg hover:border-indigo-200 transition-all group flex flex-col">

              <div class="h-3 w-full bg-gradient-to-r" 
                   :class="course.is_enrolled ? 'from-emerald-400 to-teal-500' : 'from-indigo-500 to-purple-600'">
              </div>

              <div class="p-6 flex flex-col flex-1">
                <div class="flex items-start justify-between mb-4">
                  <div class="h-12 w-12 rounded-xl flex items-center justify-center shrink-0 border"
                       :class="course.is_enrolled ? 'bg-emerald-50 border-emerald-100 text-emerald-700' : 'bg-indigo-50 border-indigo-100 text-indigo-700'">
                    <span class="font-extrabold text-sm">{{ course.course_code?.split('-')[0] || 'CR' }}</span>
                  </div>
                  
                  <span v-if="course.is_enrolled" class="shrink-0 bg-emerald-100 text-emerald-700 text-xs font-bold px-3 py-1 rounded-full flex items-center border border-emerald-200">
                    <CheckCircle2 class="h-3.5 w-3.5 mr-1" /> Enrolled
                  </span>
                </div>

                <div class="mb-4 flex-1">
                  <h3 class="text-lg font-extrabold text-gray-900 line-clamp-2 group-hover:text-indigo-700 transition-colors">{{ course.title }}</h3>
                  <p class="text-sm font-bold text-gray-400 mt-1 uppercase tracking-wider">{{ course.course_code }}</p>
                </div>

                <p class="text-sm text-gray-600 mb-5 flex items-center bg-gray-50 px-3 py-2 rounded-lg border border-gray-100">
                  <GraduationCap class="h-4 w-4 mr-2 text-gray-400" />
                  Prof. {{ course.instructor?.first_name }} {{ course.instructor?.last_name || 'Instructor' }}
                </p>

                <div class="pt-4 border-t border-gray-100 mt-auto">
                  <button v-if="course.is_enrolled" @click="goToCourse(course)"
                    class="w-full flex items-center justify-center py-2.5 bg-indigo-50 text-indigo-700 font-bold rounded-xl hover:bg-indigo-100 transition-colors">
                    Enter Classroom <ChevronRight class="h-4 w-4 ml-1" />
                  </button>
                  <button v-else @click="openEnroll(course)"
                    class="w-full flex items-center justify-center py-2.5 bg-white border-2 border-indigo-600 text-indigo-600 font-bold rounded-xl hover:bg-indigo-600 hover:text-white transition-all">
                    <Lock class="h-4 w-4 mr-2" /> Request Enrollment
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </main>

      <Teleport to="body">
        <div v-if="showEnrollModal" class="fixed inset-0 z-[100] flex items-center justify-center px-4">
          <div class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm" @click="showEnrollModal = false"></div>
          
          <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 overflow-hidden">
            <div class="absolute top-0 left-0 w-full h-2 bg-indigo-600"></div>

            <div class="flex items-start justify-between mb-6">
              <div class="flex items-center">
                <div class="h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center mr-3">
                  <Key class="h-5 w-5 text-indigo-600" />
                </div>
                <h3 class="text-xl font-extrabold text-gray-900">Enroll in Module</h3>
              </div>
              <button @click="showEnrollModal = false" class="text-gray-400 hover:text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-full p-2 transition-colors">
                <X class="h-5 w-5" />
              </button>
            </div>

            <div class="bg-gray-50 border border-gray-100 rounded-xl p-4 mb-6">
              <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">Target Course</p>
              <p class="text-base font-bold text-gray-900">{{ selectedCourse?.title }}</p>
            </div>

            <div v-if="enrollSuccess" class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-4 rounded-xl text-sm mb-4 flex items-center font-medium">
              <CheckCircle class="h-5 w-5 mr-2 shrink-0" /> {{ enrollSuccess }}
            </div>

            <template v-if="!enrollSuccess">
              <div class="mb-6">
                <label class="block text-sm font-bold text-gray-700 mb-2">Enrollment Key</label>
                <input v-model="enrollKey" type="text" placeholder="e.g., FALL2026-SEC1"
                  class="w-full border-2 border-gray-200 rounded-xl px-4 py-3 text-sm focus:ring-0 focus:border-indigo-600 outline-none transition-colors" 
                  @keyup.enter="confirmEnroll" />
                <p class="text-xs text-gray-500 mt-2 flex items-start">
                  <span class="mr-1">💡</span> Ask your professor for the 6-digit section key to unlock this module.
                </p>
              </div>

              <div v-if="enrollError" class="text-red-600 text-sm mb-4 font-medium flex items-center bg-red-50 p-3 rounded-lg">
                <X class="h-4 w-4 mr-2 shrink-0" /> {{ enrollError }}
              </div>

              <div class="flex space-x-3">
                <button @click="showEnrollModal = false" class="flex-1 py-3 bg-gray-100 text-gray-700 font-bold rounded-xl hover:bg-gray-200 transition-colors">
                  Cancel
                </button>
                <button @click="confirmEnroll" :disabled="enrolling || !enrollKey.trim()"
                  class="flex-[2] py-3 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-md flex items-center justify-center">
                  <LogIn class="h-5 w-5 mr-2" /> {{ enrolling ? 'Verifying...' : 'Confirm Enrollment' }}
                </button>
              </div>
            </template>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>
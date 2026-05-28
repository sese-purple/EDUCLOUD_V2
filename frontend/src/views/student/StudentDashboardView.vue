<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  BookOpen, Award, Clock, Bell,
  ChevronRight, Video, FileText, Calendar,
  Menu, LayoutDashboard, GraduationCap, Settings, LogOut,
  Sparkles, Megaphone, TrendingUp, CheckCircle2
} from 'lucide-vue-next'

const router = useRouter()
const data = ref<any>({ courses: [], gpa: 0, enrolled_count: 0, pending_tasks: 0, next_session: null, due_assignments: [] })
const isLoading = ref(true)
const mobileMenuOpen = ref(false)

const countdown = ref('')
const username = ref(localStorage.getItem('username') || 'Student')

// Dynamic Greeting based on time of day
const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
})

const fetchDashboard = async () => {
  isLoading.value = true
  try {
    const res = await api.get('student-dashboard/')
    data.value = res.data
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const updateCountdown = () => {
  const session = data.value.next_session
  if (!session?.scheduled_at) { countdown.value = ''; return }
  const diff = new Date(session.scheduled_at).getTime() - Date.now()
  if (diff <= 0) { countdown.value = 'Starting now!'; return }
  const h = Math.floor(diff / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  countdown.value = `${h}h ${m}m`
}

let interval: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  fetchDashboard().then(() => { updateCountdown(); interval = setInterval(updateCountdown, 10000) })
})
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
          <a @click="mobileMenuOpen = false; router.push('/student')" class="flex items-center px-3 py-3 bg-indigo-50 text-indigo-700 rounded-xl font-bold transition-colors cursor-pointer">
            <LayoutDashboard class="w-5 h-5 mr-3 text-indigo-600" /> Dashboard
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/marksheet')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <GraduationCap class="w-5 h-5 mr-3 text-gray-400" /> Marksheet
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/courses')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <BookOpen class="w-5 h-5 mr-3 text-gray-400" /> My Courses
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/settings')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <Settings class="w-5 h-5 mr-3 text-gray-400" /> Settings
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
            <h2 class="text-sm font-bold text-gray-800 uppercase tracking-wider">Student Portal</h2>
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
          <p class="font-medium">Syncing your workspace...</p>
        </div>

        <template v-else>

          <div class="mb-6">
            <h1 class="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
              {{ greeting }}, <span class="text-indigo-600">{{ username.split('_')[0] }}</span> 
            </h1>
            <p class="text-sm text-gray-500 mt-1 font-medium">{{ currentDate }}</p>
          </div>

          <div class="mb-8">
            <div v-if="data.next_session" class="bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-800 rounded-3xl p-6 sm:p-10 text-white shadow-xl relative overflow-hidden group">
              <div class="absolute top-0 right-0 w-64 h-64 bg-white rounded-full opacity-10 blur-3xl -mr-20 -mt-20 group-hover:opacity-20 transition-opacity duration-700"></div>
              <div class="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between">
                <div>
                  <div class="flex items-center space-x-2 mb-2">
                    <span class="bg-red-500/20 text-red-200 px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider border border-red-500/30 flex items-center">
                      <span class="h-2 w-2 rounded-full bg-red-400 animate-pulse mr-1.5"></span> Live Soon
                    </span>
                  </div>
                  <h2 class="text-2xl sm:text-3xl font-extrabold mt-1">{{ data.next_session.title }}</h2>
                  <p class="text-indigo-200 text-sm mt-1 sm:text-base">{{ data.next_session.course }}</p>
                  <div v-if="countdown" class="mt-4 flex items-center bg-black/20 w-fit px-4 py-2 rounded-xl backdrop-blur-sm border border-white/10">
                    <Clock class="h-5 w-5 mr-2 text-indigo-300" />
                    <span class="text-xl font-mono font-bold tracking-wider">{{ countdown }}</span>
                  </div>
                </div>
                <a v-if="data.next_session.meeting_link" :href="data.next_session.meeting_link" target="_blank"
                  class="mt-6 md:mt-0 inline-flex items-center justify-center px-8 py-3.5 bg-white text-indigo-800 rounded-xl font-extrabold text-sm hover:bg-indigo-50 hover:scale-105 transition-all shadow-xl">
                  <Video class="h-5 w-5 mr-2" /> Join Classroom
                </a>
              </div>
            </div>

            <div v-else class="bg-gradient-to-r from-slate-800 to-gray-900 rounded-3xl p-6 sm:p-10 text-white shadow-xl relative overflow-hidden">
              <div class="absolute right-0 bottom-0 opacity-10">
                <Sparkles class="w-64 h-64 -mb-10 -mr-10" />
              </div>
              <div class="relative z-10 max-w-2xl">
                <p class="text-gray-400 text-sm font-bold uppercase tracking-wider mb-2">Workspace Overview</p>
                <h2 class="text-2xl sm:text-3xl font-extrabold text-white">You're all caught up on live lectures!</h2>
                <p class="text-gray-400 text-sm mt-2 sm:text-base leading-relaxed">
                  You have {{ data.pending_tasks }} assignments pending. This is a great time to review your course materials, check your marksheet, or get a head start on next week's readings.
                </p>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-3">
                <div class="p-2.5 bg-blue-50 text-blue-600 rounded-xl"><BookOpen class="h-5 w-5" /></div>
                <TrendingUp class="h-4 w-4 text-emerald-500" />
              </div>
              <p class="text-3xl font-extrabold text-gray-900">{{ data.enrolled_count }}</p>
              <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-1">Active Courses</p>
            </div>
            
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-3">
                <div class="p-2.5 bg-amber-50 text-amber-600 rounded-xl"><Award class="h-5 w-5" /></div>
              </div>
              <p class="text-3xl font-extrabold text-gray-900">{{ data.gpa }}</p>
              <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-1">Overall GPA</p>
            </div>
            
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-3">
                <div class="p-2.5 bg-orange-50 text-orange-600 rounded-xl"><Clock class="h-5 w-5" /></div>
              </div>
              <p class="text-3xl font-extrabold text-gray-900">{{ data.pending_tasks }}</p>
              <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-1">Pending Tasks</p>
            </div>
            
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition-shadow">
              <div class="flex items-center justify-between mb-3">
                <div class="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl"><Calendar class="h-5 w-5" /></div>
              </div>
              <p class="text-3xl font-extrabold text-gray-900">{{ data.courses.length }}</p>
              <p class="text-xs font-bold text-gray-400 uppercase tracking-wider mt-1">Total Modules</p>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

            <div class="lg:col-span-2">
              <div class="flex items-center justify-between mb-5">
                <h3 class="text-lg font-extrabold text-gray-900">Current Modules</h3>
                <button @click="router.push('/student/courses')" class="text-sm font-bold text-indigo-600 hover:text-indigo-800">View All</button>
              </div>
              
              <div class="space-y-4">
                <div v-for="c in data.courses" :key="c.id" @click="router.push(`/student/course/${c.id}`)"
                  class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:border-indigo-300 hover:shadow-md transition-all cursor-pointer group">
                  <div class="flex items-start sm:items-center space-x-4">
                    <div class="h-14 w-14 bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl flex items-center justify-center shrink-0 border border-indigo-100 group-hover:scale-105 transition-transform">
                      <span class="text-indigo-700 font-extrabold text-lg">{{ c.course_code?.split('-')[0] || 'CR' }}</span>
                    </div>
                    
                    <div class="flex-1 min-w-0">
                      <h4 class="text-base font-bold text-gray-900 truncate group-hover:text-indigo-700 transition-colors">{{ c.title }}</h4>
                      <p class="text-sm text-gray-500 truncate mt-0.5">{{ c.course_code }} • Prof. {{ c.instructor_name }}</p>
                      
                      <div v-if="c.attendance_pct !== null" class="mt-3 flex items-center w-full max-w-xs">
                        <span class="text-xs font-bold text-gray-500 w-12">{{ c.attendance_pct }}%</span>
                        <div class="flex-1 bg-gray-100 rounded-full h-2 ml-2 overflow-hidden">
                          <div class="h-full rounded-full transition-all duration-1000" 
                               :class="c.attendance_pct >= 80 ? 'bg-emerald-500' : 'bg-amber-500'"
                               :style="{ width: c.attendance_pct + '%' }"></div>
                        </div>
                      </div>
                    </div>
                    
                    <div class="hidden sm:flex h-10 w-10 rounded-full bg-gray-50 items-center justify-center group-hover:bg-indigo-50 transition-colors">
                      <ChevronRight class="h-5 w-5 text-gray-400 group-hover:text-indigo-600" />
                    </div>
                  </div>
                </div>

                <div v-if="!data.courses.length" class="bg-white rounded-2xl border-2 border-dashed border-gray-200 p-10 text-center">
                  <div class="mx-auto h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                    <BookOpen class="h-8 w-8 text-gray-300" />
                  </div>
                  <h4 class="text-base font-bold text-gray-900">No active modules</h4>
                  <p class="text-sm text-gray-500 mt-1 mb-4">You haven't enrolled in any courses for this semester.</p>
                  <button @click="router.push('/student/courses')" class="px-5 py-2 bg-indigo-50 text-indigo-700 font-bold rounded-lg hover:bg-indigo-100 transition-colors">
                    Browse Catalog
                  </button>
                </div>
              </div>
            </div>

            <div class="space-y-8">
              
              <div>
                <div class="flex items-center justify-between mb-5">
                  <h3 class="text-lg font-extrabold text-gray-900 flex items-center">
                    Action Required <span v-if="data.due_assignments?.length" class="ml-2 bg-red-100 text-red-600 text-xs py-0.5 px-2 rounded-full">{{ data.due_assignments.length }}</span>
                  </h3>
                </div>
                
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                  <ul v-if="data.due_assignments?.length" class="divide-y divide-gray-50">
                    <li v-for="a in data.due_assignments" :key="a.id" @click="router.push(`/student/course/${a.course_id}/assignment/${a.id}`)" class="p-5 hover:bg-orange-50/30 transition-colors cursor-pointer group">
                      <div class="flex items-start">
                        <div class="h-10 w-10 rounded-xl bg-orange-100 flex items-center justify-center mr-4 shrink-0 border border-orange-200">
                          <FileText class="h-5 w-5 text-orange-600" />
                        </div>
                        <div class="min-w-0 flex-1">
                          <p class="text-sm font-bold text-gray-900 group-hover:text-indigo-700 transition-colors line-clamp-1">{{ a.title }}</p>
                          <p class="text-xs text-gray-500 mt-1 line-clamp-1">{{ a.course }}</p>
                          <div class="mt-2 flex items-center">
                            <Clock class="h-3.5 w-3.5 text-red-500 mr-1" />
                            <p class="text-xs text-red-600 font-bold">Due {{ new Date(a.due_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) }}</p>
                          </div>
                        </div>
                      </div>
                    </li>
                  </ul>
                  <div v-else class="p-8 text-center flex flex-col items-center">
                    <div class="h-12 w-12 bg-emerald-50 rounded-full flex items-center justify-center mb-3">
                      <CheckCircle2 class="h-6 w-6 text-emerald-500" />
                    </div>
                    <h4 class="text-sm font-bold text-gray-900">You're all caught up!</h4>
                    <p class="text-xs text-gray-500 mt-1">No assignments due in the next 7 days.</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 class="text-lg font-extrabold text-gray-900 mb-5">Notice Board</h3>
                <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-1">
                  <div class="p-4 hover:bg-gray-50 rounded-xl transition-colors flex items-start cursor-pointer border-b border-gray-50">
                    <Megaphone class="h-5 w-5 text-indigo-500 mr-3 shrink-0 mt-0.5" />
                    <div>
                      <p class="text-sm font-bold text-gray-900">Semester Registration</p>
                      <p class="text-xs text-gray-500 mt-1 line-clamp-2">Fall 2026 course enrollment officially opens next Monday. Ensure your account holds are cleared.</p>
                      <p class="text-[10px] text-gray-400 font-bold uppercase tracking-wider mt-2">Admin • 2 days ago</p>
                    </div>
                  </div>
                  <div class="p-4 hover:bg-gray-50 rounded-xl transition-colors flex items-start cursor-pointer">
                    <Megaphone class="h-5 w-5 text-gray-400 mr-3 shrink-0 mt-0.5" />
                    <div>
                      <p class="text-sm font-bold text-gray-900">Library Maintenance</p>
                      <p class="text-xs text-gray-500 mt-1 line-clamp-2">The digital research database will be offline for scheduled maintenance this Saturday night.</p>
                      <p class="text-[10px] text-gray-400 font-bold uppercase tracking-wider mt-2">IT Dept • 1 week ago</p>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  Menu, Bell, CalendarDays, Video, Clock,
  FileText, ChevronRight, LayoutDashboard, BookOpen,
  ClipboardList, GraduationCap, Settings, LogOut, Sparkles
} from 'lucide-vue-next'

const router = useRouter()
const isLoading = ref(true)
const mobileMenuOpen = ref(false)
const username = ref(localStorage.getItem('username') || 'Student')

const onlineClasses = ref<any[]>([])
const upcomingDeadlines = ref<any[]>([])

onMounted(async () => {
  isLoading.value = true
  try {
    const [dashRes, sessRes] = await Promise.allSettled([
      api.get('student-dashboard/'),
      api.get('sessions/'),
    ])

    if (dashRes.status === 'fulfilled') {
      const data = dashRes.value.data
      upcomingDeadlines.value = data.due_assignments || []
      if (data.next_session) {
        onlineClasses.value = [data.next_session]
      }
    }

    if (sessRes.status === 'fulfilled') {
      const allSessions = sessRes.value.data || []
      const enrolledCourseIds = new Set(
        dashRes.status === 'fulfilled'
          ? (dashRes.value.data.courses || []).map((c: any) => c.id)
          : []
      )
      const upcoming = allSessions
        .filter((s: any) => {
          if (!s.scheduled_at) return false
          if (enrolledCourseIds.size && !enrolledCourseIds.has(s.course)) return false
          return new Date(s.scheduled_at).getTime() > Date.now() - 7200000
        })
        .sort((a: any, b: any) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())

      const existingIds = new Set(onlineClasses.value.map((s: any) => s.id))
      for (const s of upcoming) {
        if (!existingIds.has(s.id) && onlineClasses.value.length < 10) {
          onlineClasses.value.push(s)
          existingIds.add(s.id)
        }
      }
      onlineClasses.value.sort((a: any, b: any) =>
        new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime()
      )
    }
  } catch (err) { console.error(err) } finally { isLoading.value = false }
})

const isLiveNow = (dateString: string) => {
  if (!dateString) return false
  const classTime = new Date(dateString).getTime()
  const now = Date.now()
  const diffMinutes = (classTime - now) / 1000 / 60
  return diffMinutes <= 15 && diffMinutes >= -120
}

const formatTime = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString([], { weekday: 'long', month: 'short', day: 'numeric' })
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
          <a @click="mobileMenuOpen = false; router.push('/student')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium cursor-pointer"><LayoutDashboard class="w-5 h-5 mr-3 text-gray-400" /> Dashboard</a>
          <a @click="mobileMenuOpen = false; router.push('/student/courses')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium cursor-pointer"><BookOpen class="w-5 h-5 mr-3 text-gray-400" /> My Modules</a>
          <a @click="mobileMenuOpen = false; router.push('/student/assignments')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium cursor-pointer"><ClipboardList class="w-5 h-5 mr-3 text-gray-400" /> Assignments</a>
          <a @click="mobileMenuOpen = false; router.push('/student/calendar')" class="flex items-center px-3 py-3 bg-indigo-50 text-indigo-700 rounded-xl font-bold cursor-pointer"><CalendarDays class="w-5 h-5 mr-3 text-indigo-600" /> Schedule</a>
          <a @click="mobileMenuOpen = false; router.push('/student/marksheet')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium cursor-pointer"><GraduationCap class="w-5 h-5 mr-3 text-gray-400" /> Marksheet</a>
          <a @click="mobileMenuOpen = false; router.push('/student/settings')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium cursor-pointer"><Settings class="w-5 h-5 mr-3 text-gray-400" /> Settings</a>
          <hr class="my-3 border-gray-200" />
          <a @click="localStorage.clear(); router.push('/login')" class="flex items-center px-3 py-3 text-red-600 hover:bg-red-50 rounded-xl font-medium cursor-pointer"><LogOut class="w-5 h-5 mr-3 text-red-500" /> Sign Out</a>
        </nav>
      </div>
    </div>

    <div class="flex-1 flex flex-col overflow-hidden relative">
      <header class="h-16 bg-white/80 backdrop-blur-md border-b border-gray-200 flex items-center justify-between px-4 sm:px-8 z-10 sticky top-0 shrink-0">
        <div class="flex items-center">
          <button @click="mobileMenuOpen = true" class="mr-4 md:hidden text-gray-500 hover:text-gray-900 focus:outline-none p-1 rounded-md hover:bg-gray-100"><Menu class="h-6 w-6" /></button>
          <div class="hidden sm:flex items-center">
            <CalendarDays class="h-5 w-5 text-indigo-600 mr-2" />
            <h2 class="text-sm font-bold text-gray-800 uppercase tracking-wider">Master Schedule</h2>
          </div>
        </div>
        <div class="flex items-center space-x-5">
          <Bell class="h-5 w-5 text-gray-400 hover:text-indigo-600 cursor-pointer transition-colors" />
          <div class="h-9 w-9 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 text-white flex items-center justify-center font-bold shadow-md text-sm border-2 border-white cursor-pointer hover:scale-105 transition-transform">
            {{ username.charAt(0).toUpperCase() }}
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto bg-gray-50">
        <div class="bg-white border-b border-gray-200 px-4 sm:px-8 py-8 shrink-0">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">Your Agenda</h1>
          <p class="text-sm font-medium text-gray-500 mt-1">Manage your upcoming online classes and deadlines.</p>
        </div>

        <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 text-indigo-400">
          <Sparkles class="h-10 w-10 animate-pulse mb-4" />
          <p class="font-medium">Syncing your calendar...</p>
        </div>

        <div v-else class="p-4 sm:p-8 max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">

          <!-- Online Classes -->
          <div>
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-extrabold text-gray-900 flex items-center">
                <Video class="h-5 w-5 mr-2 text-indigo-600" /> Online Classes
              </h3>
              <span class="bg-indigo-100 text-indigo-700 text-xs font-bold px-3 py-1 rounded-full">{{ onlineClasses.length }} Scheduled</span>
            </div>

            <div class="relative border-l-2 border-gray-200 ml-4 space-y-8 pb-4">
              <div v-for="(session, index) in onlineClasses" :key="session.id || index" class="relative pl-6">
                <div :class="['absolute -left-[9px] top-1.5 h-4 w-4 rounded-full border-2 border-white shadow-sm',
                  isLiveNow(session.scheduled_at) ? 'bg-red-500 ring-4 ring-red-500/20 animate-pulse' : 'bg-indigo-500']">
                </div>

                <div :class="['rounded-2xl border p-5 transition-all shadow-sm',
                  isLiveNow(session.scheduled_at) ? 'bg-white border-red-200 shadow-red-100' : 'bg-white border-gray-100 hover:border-indigo-200 hover:shadow-md']">
                  <div class="flex justify-between items-start mb-3">
                    <div>
                      <p class="text-xs font-extrabold uppercase tracking-wider mb-1"
                         :class="isLiveNow(session.scheduled_at) ? 'text-red-500' : 'text-indigo-600'">
                        {{ formatDate(session.scheduled_at) }}
                      </p>
                      <h4 class="text-lg font-extrabold text-gray-900">{{ session.title || 'Live Lecture' }}</h4>
                      <p class="text-sm font-bold text-gray-500 mt-0.5">{{ session.course_title || session.course || 'Module' }}</p>
                    </div>
                  </div>
                  <div class="flex items-center text-sm font-bold text-gray-600 bg-gray-50 w-fit px-3 py-1.5 rounded-lg mb-5 border border-gray-100">
                    <Clock class="h-4 w-4 mr-2 text-gray-400" /> {{ formatTime(session.scheduled_at) }}
                  </div>
                  <a v-if="session.meeting_link" :href="session.meeting_link" target="_blank"
                    :class="['w-full flex items-center justify-center py-2.5 rounded-xl font-bold text-sm transition-all shadow-sm',
                      isLiveNow(session.scheduled_at) ? 'bg-red-50 text-red-700 hover:bg-red-100' : 'bg-indigo-600 text-white hover:bg-indigo-700']">
                    <Video class="h-4 w-4 mr-2" /> {{ isLiveNow(session.scheduled_at) ? 'Join Live Now' : 'Join Classroom' }}
                  </a>
                </div>
              </div>

              <div v-if="!onlineClasses.length" class="relative pl-6">
                <div class="absolute -left-[9px] top-1.5 h-4 w-4 rounded-full border-2 border-white bg-gray-300"></div>
                <div class="bg-transparent border-2 border-dashed border-gray-200 rounded-2xl p-6 text-center">
                  <p class="text-sm font-bold text-gray-500">No upcoming classes.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Deadlines -->
          <div>
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-extrabold text-gray-900 flex items-center">
                <FileText class="h-5 w-5 mr-2 text-orange-500" /> Upcoming Deadlines
              </h3>
            </div>
            <div class="space-y-4">
              <div v-for="assignment in upcomingDeadlines" :key="assignment.id"
                   @click="router.push(`/student/course/${assignment.course_id}/assignment/${assignment.id}`)"
                   class="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 hover:border-orange-200 hover:shadow-md transition-all cursor-pointer group flex items-center justify-between">
                <div class="flex items-start">
                  <div class="h-12 w-12 rounded-xl bg-orange-50 flex items-center justify-center mr-4 shrink-0 border border-orange-100">
                    <FileText class="h-6 w-6 text-orange-500" />
                  </div>
                  <div>
                    <h4 class="text-base font-extrabold text-gray-900 group-hover:text-orange-600 transition-colors line-clamp-1">{{ assignment.title }}</h4>
                    <p class="text-xs font-bold text-gray-500 mt-1 uppercase tracking-wider">{{ assignment.course }}</p>
                    <div class="mt-2 flex items-center">
                      <Clock class="h-3.5 w-3.5 text-red-500 mr-1" />
                      <p class="text-xs text-red-600 font-bold">Due {{ formatDate(assignment.due_date) }}</p>
                    </div>
                  </div>
                </div>
                <div class="h-10 w-10 rounded-full bg-gray-50 flex items-center justify-center group-hover:bg-orange-50 transition-colors shrink-0">
                  <ChevronRight class="h-5 w-5 text-gray-400 group-hover:text-orange-600" />
                </div>
              </div>

              <div v-if="!upcomingDeadlines.length" class="bg-white rounded-2xl border-2 border-dashed border-gray-200 p-8 text-center flex flex-col items-center">
                <div class="h-12 w-12 bg-emerald-50 rounded-full flex items-center justify-center mb-3">
                  <Sparkles class="h-6 w-6 text-emerald-500" />
                </div>
                <h4 class="text-sm font-bold text-gray-900">Your agenda is clear!</h4>
                <p class="text-xs text-gray-500 mt-1">No deadlines approaching in the next week.</p>
              </div>
            </div>
          </div>

        </div>
      </main>
    </div>
  </div>
</template>

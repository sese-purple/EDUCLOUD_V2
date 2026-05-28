<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  ArrowLeft, BookOpen, Video, FileText, Download,
  Clock, Calendar, CheckCircle, ExternalLink,
  HelpCircle, ChevronRight, BarChart,
  Menu, LayoutDashboard, GraduationCap, Settings, LogOut,
  Bell, Sparkles, ClipboardList, CalendarDays, User
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const courseId = computed(() => Number(route.params.id))
const course = ref<any>(null)
const sessions = ref<any[]>([])
const assignments = ref<any[]>([])
const materials = ref<any[]>([])
const quizzes = ref<any[]>([])
const attempts = ref<any[]>([])
const isLoading = ref(true)
const activeTab = ref('overview')
const mobileMenuOpen = ref(false)

const username = ref(localStorage.getItem('username') || 'Student')

onMounted(async () => {
  try {
    const [courseRes, sessionsRes, assignRes, matsRes, quizzesRes, attemptsRes] = await Promise.all([
      api.get(`courses/${courseId.value}/`),
      api.get('sessions/', { params: { course: courseId.value } }),
      api.get('assignments/', { params: { course: courseId.value } }),
      api.get('materials/', { params: { course: courseId.value } }),
      api.get('quizzes/', { params: { course: courseId.value } }),
      api.get('attempts/'),
    ])
    course.value = courseRes.data
    sessions.value = sessionsRes.data
    assignments.value = assignRes.data
    materials.value = matsRes.data
    quizzes.value = quizzesRes.data
    attempts.value = attemptsRes.data
  } catch (err) { console.error(err) } finally { isLoading.value = false }
})

const getAttempt = (quizId: number) => {
  const userId = Number(localStorage.getItem('user_id'))
  return attempts.value.find((a: any) => a.quiz?.id === quizId && a.student?.id === userId)
}

const nextSession = computed(() =>
  sessions.value.find((s: any) => s.is_live) || sessions.value[0] || null
)
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
          <a @click="mobileMenuOpen = false; router.push('/student/assignments')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <ClipboardList class="w-5 h-5 mr-3 text-gray-400" /> Assignments
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/calendar')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <CalendarDays class="w-5 h-5 mr-3 text-gray-400" /> Schedule
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/marksheet')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <GraduationCap class="w-5 h-5 mr-3 text-gray-400" /> Marksheet
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
          <button @click="router.push('/student/courses')" class="hidden sm:flex items-center text-sm font-bold text-gray-500 hover:text-indigo-600 transition-colors">
            <ArrowLeft class="h-4 w-4 mr-2" /> Back to Modules
          </button>
        </div>
        <div class="flex items-center space-x-5">
          <Bell class="h-5 w-5 text-gray-400 hover:text-indigo-600 cursor-pointer transition-colors" />
          <div class="h-9 w-9 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 text-white flex items-center justify-center font-bold shadow-md text-sm border-2 border-white cursor-pointer hover:scale-105 transition-transform">
            {{ username.charAt(0).toUpperCase() }}
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto bg-gray-50/50">
        <div v-if="isLoading" class="flex flex-col items-center justify-center py-20 text-indigo-400">
          <Sparkles class="h-10 w-10 animate-pulse mb-4" />
          <p class="font-medium">Loading classroom...</p>
        </div>

        <template v-else>
          
          <div class="bg-white border-b border-gray-200 px-4 sm:px-8 pt-8 pb-4">
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6">
              <div class="flex items-center space-x-4">
                <div class="h-16 w-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl shadow-md flex items-center justify-center shrink-0">
                  <span class="text-white font-extrabold text-xl">{{ course?.course_code?.split('-')[0] || 'CR' }}</span>
                </div>
                <div>
                  <h1 class="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">{{ course?.title }}</h1>
                  <p class="text-sm font-bold text-gray-500 mt-1 uppercase tracking-wider">{{ course?.course_code }} • Prof. {{ course?.instructor?.last_name || 'Instructor' }}</p>
                </div>
              </div>
            </div>

            <div class="flex space-x-2 overflow-x-auto custom-scrollbar pb-2">
              <button v-for="tab in ['overview', 'materials', 'assignments', 'quizzes']" :key="tab"
                @click="activeTab = tab"
                :class="[activeTab === tab ? 'bg-gray-900 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200', 'px-5 py-2 rounded-full font-bold text-sm capitalize transition-all whitespace-nowrap']">
                {{ tab }}
              </button>
            </div>
          </div>

          <div class="p-4 sm:p-8 max-w-7xl mx-auto w-full">
            
            <template v-if="activeTab === 'overview'">
              <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                <div class="lg:col-span-2 space-y-6">
                  
                  <div v-if="nextSession" class="bg-gradient-to-r from-indigo-600 to-indigo-800 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden group">
                    <div class="absolute top-0 right-0 w-48 h-48 bg-white rounded-full opacity-10 blur-3xl -mr-10 -mt-10 group-hover:opacity-20 transition-opacity"></div>
                    <div class="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p class="text-indigo-200 text-xs font-bold uppercase tracking-wider mb-1 flex items-center">
                          <span class="h-2 w-2 rounded-full bg-red-400 animate-pulse mr-2"></span> Next Live Class
                        </p>
                        <h3 class="text-2xl font-extrabold mt-1">{{ nextSession.title || 'Live Session' }}</h3>
                        <p v-if="nextSession.scheduled_at" class="text-indigo-100 text-sm mt-2 flex items-center bg-black/20 w-fit px-3 py-1.5 rounded-lg backdrop-blur-sm border border-white/10">
                          <Calendar class="h-4 w-4 mr-2 text-indigo-300" /> {{ new Date(nextSession.scheduled_at).toLocaleString(undefined, { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }}
                        </p>
                      </div>
                      <a v-if="nextSession.meeting_link" :href="nextSession.meeting_link" target="_blank"
                        class="mt-5 sm:mt-0 inline-flex items-center px-6 py-3 bg-white text-indigo-800 rounded-xl font-extrabold text-sm hover:bg-indigo-50 hover:scale-105 transition-all shadow-lg">
                        <Video class="h-5 w-5 mr-2" /> Join Classroom
                      </a>
                    </div>
                  </div>

                  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 sm:p-8">
                    <h3 class="text-lg font-extrabold text-gray-900 mb-4 flex items-center"><BookOpen class="h-5 w-5 text-indigo-600 mr-2" /> Course Syllabus</h3>
                    <div v-if="course.syllabus" class="prose prose-sm max-w-none text-gray-600 whitespace-pre-wrap leading-relaxed">{{ course.syllabus }}</div>
                    <p v-else class="text-sm text-gray-400 italic">No syllabus provided by the instructor.</p>
                  </div>
                </div>

                <div class="space-y-6">
                  
                  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <h3 class="text-sm font-extrabold text-gray-900 uppercase tracking-wider mb-4">Instructor</h3>
                    <div class="flex items-center">
                      <div class="h-12 w-12 bg-gray-100 rounded-full flex items-center justify-center mr-4">
                        <User class="h-6 w-6 text-gray-400" />
                      </div>
                      <div>
                        <p class="font-bold text-gray-900">{{ course?.instructor?.first_name }} {{ course?.instructor?.last_name || 'Not Assigned' }}</p>
                        <p class="text-xs text-indigo-600 font-medium cursor-pointer hover:underline">Contact via Email</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
                    <h3 class="text-sm font-extrabold text-gray-900 uppercase tracking-wider mb-4 flex items-center">
                      <Video class="h-4 w-4 text-indigo-600 mr-2" /> Lecture Vault
                    </h3>
                    <div v-if="sessions.filter((s:any) => s.recording_url).length" class="space-y-3">
                      <div v-for="s in sessions.filter((s:any) => s.recording_url)" :key="s.id"
                        class="p-3 bg-gray-50 hover:bg-indigo-50/50 rounded-xl transition-colors group cursor-pointer border border-gray-100">
                        <p class="text-sm font-bold text-gray-900 group-hover:text-indigo-700 transition-colors line-clamp-1">{{ s.title }}</p>
                        <div class="flex items-center justify-between mt-2">
                          <p class="text-[11px] font-bold text-gray-400 uppercase">{{ new Date(s.scheduled_at || s.date).toLocaleDateString() }}</p>
                          <a :href="s.recording_url" target="_blank" class="text-xs font-bold text-indigo-600 hover:text-indigo-800 flex items-center">
                            Watch <ExternalLink class="h-3 w-3 ml-1" />
                          </a>
                        </div>
                      </div>
                    </div>
                    <p v-else class="text-xs text-gray-400 text-center py-4">No recordings available yet.</p>
                  </div>
                </div>
              </div>
            </template>

            <template v-else-if="activeTab === 'materials'">
              <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="px-6 py-5 border-b border-gray-100 bg-gray-50/50">
                  <h3 class="text-base font-extrabold text-gray-900">Course Resources</h3>
                </div>
                <ul class="divide-y divide-gray-50">
                  <li v-for="m in materials" :key="m.id" class="p-5 hover:bg-gray-50 transition-colors flex items-center justify-between group">
                    <div class="flex items-center space-x-4">
                      <div class="h-10 w-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center shrink-0">
                        <FileText class="h-5 w-5" />
                      </div>
                      <div>
                        <p class="text-sm font-bold text-gray-900 group-hover:text-indigo-700 transition-colors">{{ m.title }}</p>
                        <p class="text-xs font-medium text-gray-500 mt-0.5">{{ m.file_type || 'Document' }}</p>
                      </div>
                    </div>
                    <a v-if="m.file || m.file_url" :href="m.file || m.file_url" target="_blank"
                      class="px-4 py-2 bg-white border border-gray-200 text-gray-700 hover:text-indigo-600 hover:border-indigo-200 rounded-lg text-sm font-bold flex items-center transition-all shadow-sm">
                      <Download class="h-4 w-4 mr-2" /> Download
                    </a>
                  </li>
                  <li v-if="!materials.length" class="p-12 text-center flex flex-col items-center">
                    <div class="h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                      <FileText class="h-8 w-8 text-gray-300" />
                    </div>
                    <p class="text-sm font-bold text-gray-900">No resources yet.</p>
                    <p class="text-xs text-gray-500 mt-1">Check back later when the instructor uploads files.</p>
                  </li>
                </ul>
              </div>
            </template>

            <template v-else-if="activeTab === 'assignments'">
              <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="px-6 py-5 border-b border-gray-100 bg-gray-50/50">
                  <h3 class="text-base font-extrabold text-gray-900">Tasks & Assignments</h3>
                </div>
                <ul class="divide-y divide-gray-50">
                  <li v-for="a in assignments" :key="a.id"
                      @click="router.push(`/student/course/${courseId}/assignment/${a.id}`)"
                      class="p-5 hover:bg-indigo-50/30 transition-colors cursor-pointer flex items-center justify-between group">
                    <div class="flex items-center space-x-4 min-w-0">
                      <div class="h-10 w-10 bg-orange-50 text-orange-600 rounded-xl flex items-center justify-center shrink-0">
                        <ClipboardList class="h-5 w-5" />
                      </div>
                      <div class="min-w-0">
                        <p class="text-sm font-bold text-gray-900 truncate group-hover:text-indigo-700 transition-colors">{{ a.title }}</p>
                        <p class="text-xs font-medium text-gray-500 mt-1">{{ a.assignment_type }} • {{ a.max_points }} pts</p>
                      </div>
                    </div>
                    <div class="flex items-center shrink-0 ml-4">
                      <p v-if="a.due_date" class="hidden sm:block text-xs font-bold text-red-500 mr-4">Due {{ new Date(a.due_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) }}</p>
                      <div class="h-8 w-8 bg-gray-50 group-hover:bg-indigo-100 rounded-full flex items-center justify-center transition-colors">
                        <ChevronRight class="h-4 w-4 text-gray-400 group-hover:text-indigo-600" />
                      </div>
                    </div>
                  </li>
                  <li v-if="!assignments.length" class="p-12 text-center flex flex-col items-center">
                    <div class="h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                      <CheckCircle class="h-8 w-8 text-gray-300" />
                    </div>
                    <p class="text-sm font-bold text-gray-900">No active assignments.</p>
                    <p class="text-xs text-gray-500 mt-1">You're completely caught up for this module!</p>
                  </li>
                </ul>
              </div>
            </template>

            <template v-else-if="activeTab === 'quizzes'">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div v-for="q in quizzes" :key="q.id"
                     class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg hover:border-indigo-200 transition-all flex flex-col">
                  <div class="p-6 flex-1">
                    <div class="flex items-start justify-between mb-4">
                      <div class="min-w-0 pr-4">
                        <h3 class="text-lg font-extrabold text-gray-900 truncate">{{ q.title }}</h3>
                        <p class="text-sm font-medium text-gray-500 mt-1">{{ q.total_points }} points • {{ q.time_limit }} min limit</p>
                      </div>
                      <span v-if="getAttempt(q.id)?.is_completed" class="shrink-0 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-bold px-3 py-1.5 rounded-full flex items-center">
                        <CheckCircle class="h-3.5 w-3.5 mr-1" /> {{ getAttempt(q.id).score }}/{{ q.total_points }}
                      </span>
                      <span v-else-if="getAttempt(q.id)" class="shrink-0 bg-amber-50 text-amber-700 border border-amber-200 text-xs font-bold px-3 py-1.5 rounded-full flex items-center">
                        <Clock class="h-3.5 w-3.5 mr-1" /> In Progress
                      </span>
                    </div>
                    <p v-if="q.due_date" class="text-xs font-bold text-red-500 flex items-center mt-2">
                      <Calendar class="h-3.5 w-3.5 mr-1.5" /> Due {{ new Date(q.due_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }}
                    </p>
                  </div>
                  
                  <div class="px-6 py-4 bg-gray-50/50 border-t border-gray-100 mt-auto">
                    <button @click="router.push(`/student/course/${courseId}/quiz/${q.id}`)"
                      :class="['w-full py-2.5 rounded-xl font-bold text-sm transition-all shadow-sm flex items-center justify-center',
                        getAttempt(q.id)?.is_completed
                          ? 'text-gray-700 bg-white border border-gray-200 hover:text-indigo-600 hover:border-indigo-200'
                          : 'text-white bg-indigo-600 hover:bg-indigo-700']">
                      {{ getAttempt(q.id)?.is_completed ? 'Review Answers' : 'Begin Assessment' }} <ChevronRight class="h-4 w-4 ml-1" />
                    </button>
                  </div>
                </div>
                
                <div v-if="!quizzes.length" class="col-span-full p-12 text-center bg-white rounded-2xl border-2 border-dashed border-gray-200 flex flex-col items-center">
                  <div class="h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                    <HelpCircle class="h-8 w-8 text-gray-300" />
                  </div>
                  <h4 class="text-sm font-bold text-gray-900">No assessments scheduled.</h4>
                  <p class="text-xs text-gray-500 mt-1">Any upcoming quizzes will appear here.</p>
                </div>
              </div>
            </template>

          </div>
        </template>

      </main>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { height: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #e5e7eb; border-radius: 10px; }
.custom-scrollbar:hover::-webkit-scrollbar-thumb { background-color: #d1d5db; }
</style>
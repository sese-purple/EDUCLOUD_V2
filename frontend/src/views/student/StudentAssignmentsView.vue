<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  Menu, LayoutDashboard, GraduationCap, BookOpen, Settings, LogOut,
  Clock, AlertCircle, CheckCircle, ChevronRight, FileText,
  Calendar, Filter, ExternalLink, Upload
} from 'lucide-vue-next'

const router = useRouter()
const mobileMenuOpen = ref(false)
const isLoading = ref(true)
const assignments = ref<any[]>([])
const submissions = ref<any[]>([])
const courses = ref<any[]>([])
const selectedCourse = ref('all')

const courseColors = [
  'border-l-indigo-500', 'border-l-emerald-500', 'border-l-amber-500',
  'border-l-rose-500', 'border-l-cyan-500', 'border-l-violet-500',
  'border-l-pink-500', 'border-l-orange-500', 'border-l-teal-500',
]
const courseColorMap = computed(() => {
  const map: Record<number, string> = {}
  courses.value.forEach((c: any, i: number) => {
    map[c.id] = courseColors[i % courseColors.length]
  })
  return map
})

const courseBgMap = computed(() => {
  const bgColors = ['bg-indigo-100 text-indigo-700', 'bg-emerald-100 text-emerald-700', 'bg-amber-100 text-amber-700',
    'bg-rose-100 text-rose-700', 'bg-cyan-100 text-cyan-700', 'bg-violet-100 text-violet-700']
  const map: Record<number, string> = {}
  courses.value.forEach((c: any, i: number) => {
    map[c.id] = bgColors[i % bgColors.length]
  })
  return map
})

const courseLookup = computed(() => {
  const map: Record<number, any> = {}
  courses.value.forEach((c: any) => { map[c.id] = c })
  return map
})

onMounted(async () => {
  try {
    const results = await Promise.allSettled([
      api.get('student-dashboard/'),
      api.get('assignments/'),
      api.get('submissions/'),
    ])
    if (results[0].status === 'fulfilled') courses.value = results[0].value.data.courses || []
    else console.error('dashboard failed:', results[0].reason)
    if (results[1].status === 'fulfilled') assignments.value = results[1].value.data || []
    else console.error('assignments failed:', results[1].reason)
    if (results[2].status === 'fulfilled') submissions.value = results[2].value.data || []
    else console.error('submissions failed:', results[2].reason)
  } catch (err) { console.error(err) } finally { isLoading.value = false }
})

const filteredAssignments = computed(() => {
  let list = assignments.value
  if (selectedCourse.value !== 'all') {
    list = list.filter((a: any) => a.course === Number(selectedCourse.value))
  }
  const enrolledIds = new Set(courses.value.map((c: any) => c.id))
  list = list.filter((a: any) => enrolledIds.has(a.course))

  const now = Date.now()
  const soon = now + 48 * 60 * 60 * 1000
  const userId = Number(localStorage.getItem('user_id'))

  const overdue: any[] = []
  const dueSoon: any[] = []
  const upcoming: any[] = []
  const completed: any[] = []

  for (const a of list) {
    const sub = submissions.value.find((s: any) => s.assignment === a.id && s.student?.id === userId)
    if (sub) {
      completed.push({ ...a, _submission: sub })
    } else if (a.due_date && new Date(a.due_date).getTime() < now) {
      overdue.push(a)
    } else if (a.due_date && new Date(a.due_date).getTime() <= soon) {
      dueSoon.push(a)
    } else {
      upcoming.push(a)
    }
  }

  const sortByDate = (arr: any[]) => arr.sort((a, b) => {
    if (!a.due_date) return 1
    if (!b.due_date) return -1
    return new Date(a.due_date).getTime() - new Date(b.due_date).getTime()
  })

  return {
    overdue: sortByDate(overdue),
    dueSoon: sortByDate(dueSoon),
    upcoming: sortByDate(upcoming),
    completed: sortByDate(completed),
  }
})

const courseFilterOptions = computed(() => {
  return [{ id: 'all', title: 'All Courses' }, ...courses.value]
})

const goToSubmission = (assignmentId: number) => {
  const a = assignments.value.find((x: any) => x.id === assignmentId)
  if (a) router.push(`/student/course/${a.course}/assignment/${assignmentId}`)
}

const formatDate = (d: string) => {
  if (!d) return ''
  const date = new Date(d)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const isSoon = (d: string) => {
  if (!d) return false
  return new Date(d).getTime() <= Date.now() + 48 * 60 * 60 * 1000
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <StudentSidebar />
    <div v-if="mobileMenuOpen" class="fixed inset-0 z-50 flex md:hidden">
      <div class="fixed inset-0 bg-gray-800/75" @click="mobileMenuOpen = false"></div>
      <div class="relative flex w-full max-w-xs flex-1 flex-col bg-white pt-5 pb-4">
        <div class="flex items-center justify-between px-4 mb-6">
          <h1 class="text-xl font-bold text-gray-900 tracking-tight">EDUCLOUD <span class="text-indigo-600">2.0</span></h1>
          <button @click="mobileMenuOpen = false" class="text-gray-400 hover:text-gray-600"><span class="text-2xl">&times;</span></button>
        </div>
        <nav class="flex-1 px-4 space-y-1">
          <a @click="mobileMenuOpen = false; router.push('/student')" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium cursor-pointer"><LayoutDashboard class="w-5 h-5 mr-3 text-gray-400" /> Dashboard</a>
          <a @click="mobileMenuOpen = false; router.push('/student/marksheet')" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium cursor-pointer"><GraduationCap class="w-5 h-5 mr-3 text-gray-400" /> Marksheet</a>
          <a @click="mobileMenuOpen = false; router.push('/student/courses')" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium cursor-pointer"><BookOpen class="w-5 h-5 mr-3 text-gray-400" /> My Courses</a>
          <a @click="mobileMenuOpen = false; router.push('/student/assignments')" class="flex items-center px-3 py-2.5 bg-indigo-50 text-indigo-700 rounded-lg font-medium cursor-pointer"><FileText class="w-5 h-5 mr-3 text-indigo-600" /> Tasks</a>
          <a @click="mobileMenuOpen = false; router.push('/student/settings')" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium cursor-pointer"><Settings class="w-5 h-5 mr-3 text-gray-400" /> Settings</a>
          <hr class="my-3 border-gray-200" />
          <a @click="localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); localStorage.removeItem('user_role'); localStorage.removeItem('user_id'); localStorage.removeItem('username'); router.push('/login')" class="flex items-center px-3 py-2.5 text-red-600 hover:bg-red-50 rounded-lg font-medium cursor-pointer"><LogOut class="w-5 h-5 mr-3 text-red-500" /> Sign Out</a>
        </nav>
      </div>
    </div>

    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-6 shadow-sm z-10">
        <div class="flex items-center">
          <button @click="mobileMenuOpen = true" class="mr-3 md:hidden text-gray-500 hover:text-gray-900 focus:outline-none"><Menu class="h-6 w-6" /></button>
          <h2 class="text-lg font-bold text-gray-800">Tasks & Assignments</h2>
        </div>
        <div class="flex items-center">
          <Filter class="h-4 w-4 text-gray-400 mr-2" />
          <select v-model="selectedCourse"
            class="text-sm border border-gray-300 rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-indigo-500 outline-none bg-white">
            <option v-for="opt in courseFilterOptions" :key="opt.id" :value="opt.id">{{ opt.title }}</option>
          </select>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 sm:p-6">
        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading...</div>

        <template v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 h-full">

            <!-- Overdue -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
              <div class="px-4 py-3 bg-red-50 border-b border-red-100 flex items-center">
                <AlertCircle class="h-4 w-4 text-red-600 mr-2" />
                <h3 class="text-sm font-bold text-red-700">Overdue</h3>
                <span class="ml-auto text-xs font-bold text-red-500 bg-red-100 px-2 py-0.5 rounded-full">{{ filteredAssignments.overdue.length }}</span>
              </div>
              <div class="flex-1 p-3 space-y-2 overflow-y-auto">
                <div v-for="a in filteredAssignments.overdue" :key="a.id"
                  class="border-l-4 border-l-red-500 bg-red-50/50 rounded-lg p-3 cursor-pointer hover:bg-red-50 transition-colors"
                  @click="goToSubmission(a.id)">
                  <p class="text-sm font-bold text-gray-900 truncate">{{ a.title }}</p>
                  <p class="text-xs text-red-600 font-medium mt-0.5">{{ courseLookup[a.course]?.title || 'Course' }}</p>
                  <p class="text-xs text-gray-500 mt-1 flex items-center"><Clock class="h-3 w-3 mr-1" /> {{ formatDate(a.due_date) }}</p>
                  <div class="flex items-center justify-between mt-2">
                    <span class="text-xs text-gray-400">{{ a.max_points }} pts</span>
                    <button @click.stop="goToSubmission(a.id)" class="text-xs font-medium text-red-600 hover:text-red-800 flex items-center">
                      <Upload class="h-3 w-3 mr-1" /> Submit
                    </button>
                  </div>
                </div>
                <p v-if="!filteredAssignments.overdue.length" class="text-xs text-gray-400 text-center py-4">All caught up!</p>
              </div>
            </div>

            <!-- Due Soon -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
              <div class="px-4 py-3 bg-amber-50 border-b border-amber-100 flex items-center">
                <Clock class="h-4 w-4 text-amber-600 mr-2" />
                <h3 class="text-sm font-bold text-amber-700">Due Soon</h3>
                <span class="ml-auto text-xs font-bold text-amber-500 bg-amber-100 px-2 py-0.5 rounded-full">{{ filteredAssignments.dueSoon.length }}</span>
              </div>
              <div class="flex-1 p-3 space-y-2 overflow-y-auto">
                <div v-for="a in filteredAssignments.dueSoon" :key="a.id"
                  :class="['border-l-4 rounded-lg p-3 cursor-pointer hover:bg-gray-50 transition-colors', courseColorMap[a.course] || 'border-l-gray-300']"
                  @click="goToSubmission(a.id)">
                  <p class="text-sm font-bold text-gray-900 truncate">{{ a.title }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">{{ courseLookup[a.course]?.title || 'Course' }}</p>
                  <p class="text-xs text-amber-600 font-medium mt-1 flex items-center"><Clock class="h-3 w-3 mr-1" /> {{ formatDate(a.due_date) }}</p>
                  <div class="flex items-center justify-between mt-2">
                    <span class="text-xs text-gray-400">{{ a.max_points }} pts</span>
                    <button @click.stop="goToSubmission(a.id)" class="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center">
                      <Upload class="h-3 w-3 mr-1" /> Submit
                    </button>
                  </div>
                </div>
                <p v-if="!filteredAssignments.dueSoon.length" class="text-xs text-gray-400 text-center py-4">No tasks due in 48h</p>
              </div>
            </div>

            <!-- Upcoming -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
              <div class="px-4 py-3 bg-blue-50 border-b border-blue-100 flex items-center">
                <Calendar class="h-4 w-4 text-blue-600 mr-2" />
                <h3 class="text-sm font-bold text-blue-700">Upcoming</h3>
                <span class="ml-auto text-xs font-bold text-blue-500 bg-blue-100 px-2 py-0.5 rounded-full">{{ filteredAssignments.upcoming.length }}</span>
              </div>
              <div class="flex-1 p-3 space-y-2 overflow-y-auto">
                <div v-for="a in filteredAssignments.upcoming" :key="a.id"
                  :class="['border-l-4 rounded-lg p-3 cursor-pointer hover:bg-gray-50 transition-colors', courseColorMap[a.course] || 'border-l-gray-300']"
                  @click="goToSubmission(a.id)">
                  <p class="text-sm font-bold text-gray-900 truncate">{{ a.title }}</p>
                  <p class="text-xs text-gray-500 mt-0.5">{{ courseLookup[a.course]?.title || 'Course' }}</p>
                  <p class="text-xs text-gray-500 mt-1 flex items-center"><Calendar class="h-3 w-3 mr-1" /> {{ formatDate(a.due_date) }}</p>
                  <div class="flex items-center justify-between mt-2">
                    <span class="text-xs text-gray-400">{{ a.max_points }} pts</span>
                    <span class="text-xs text-gray-400">{{ a.assignment_type }}</span>
                  </div>
                </div>
                <p v-if="!filteredAssignments.upcoming.length" class="text-xs text-gray-400 text-center py-4">No upcoming tasks</p>
              </div>
            </div>

            <!-- Completed -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col">
              <div class="px-4 py-3 bg-emerald-50 border-b border-emerald-100 flex items-center">
                <CheckCircle class="h-4 w-4 text-emerald-600 mr-2" />
                <h3 class="text-sm font-bold text-emerald-700">Completed</h3>
                <span class="ml-auto text-xs font-bold text-emerald-500 bg-emerald-100 px-2 py-0.5 rounded-full">{{ filteredAssignments.completed.length }}</span>
              </div>
              <div class="flex-1 p-3 space-y-2 overflow-y-auto">
                <div v-for="a in filteredAssignments.completed" :key="a.id"
                  class="border-l-4 border-l-emerald-400 bg-emerald-50/30 rounded-lg p-3">
                  <div class="flex items-start justify-between">
                    <p class="text-sm font-bold text-gray-900 truncate flex-1">{{ a.title }}</p>
                    <span v-if="a._submission?.grade !== null" class="ml-2 text-xs font-bold text-emerald-700 shrink-0">{{ a._submission.grade }}/{{ a.max_points }}</span>
                  </div>
                  <p class="text-xs text-gray-500 mt-0.5">{{ courseLookup[a.course]?.title || 'Course' }}</p>
                  <p v-if="a._submission?.feedback" class="text-xs text-gray-400 mt-1 italic truncate">"{{ a._submission.feedback }}"</p>
                </div>
                <p v-if="!filteredAssignments.completed.length" class="text-xs text-gray-400 text-center py-4">No completed tasks yet</p>
              </div>
            </div>

          </div>
        </template>
      </main>
    </div>
  </div>
</template>

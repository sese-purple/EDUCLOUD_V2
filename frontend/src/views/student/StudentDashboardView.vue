<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  BookOpen, Award, Clock, Bell,
  ChevronRight, Video, FileText, Calendar
} from 'lucide-vue-next'

const router = useRouter()
const data = ref<any>({ courses: [], gpa: 0, enrolled_count: 0, pending_tasks: 0, next_session: null, due_assignments: [] })
const isLoading = ref(true)

const countdown = ref('')

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
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm z-10">
        <h2 class="text-lg font-bold text-gray-800">Student Dashboard</h2>
        <div class="flex items-center space-x-4">
          <Bell class="h-5 w-5 text-gray-400 hover:text-gray-600 cursor-pointer" />
          <div class="h-8 w-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold shadow-sm text-sm">S</div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">

        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading dashboard...</div>

        <template v-else>

          <!-- Up Next Hero Widget -->
          <div v-if="data.next_session" class="mb-8 bg-gradient-to-r from-indigo-600 to-indigo-800 rounded-2xl p-6 sm:p-8 text-white shadow-lg relative overflow-hidden">
            <div class="absolute top-0 right-0 w-48 h-48 bg-indigo-500 rounded-full opacity-30 blur-3xl -mr-12 -mt-12"></div>
            <div class="relative z-10 flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p class="text-indigo-200 text-sm font-medium uppercase tracking-wider">Up Next</p>
                <h2 class="text-xl sm:text-2xl font-bold mt-1">{{ data.next_session.title }}</h2>
                <p class="text-indigo-200 text-sm mt-1">{{ data.next_session.course }}</p>
                <div v-if="countdown" class="mt-2 flex items-center">
                  <Clock class="h-5 w-5 mr-2 text-indigo-200" />
                  <span class="text-2xl font-mono font-bold">{{ countdown }}</span>
                </div>
              </div>
              <a v-if="data.next_session.meeting_link" :href="data.next_session.meeting_link" target="_blank"
                class="mt-4 sm:mt-0 inline-flex items-center px-6 py-3 bg-white text-indigo-700 rounded-xl font-bold text-sm hover:bg-indigo-50 transition-all shadow-lg">
                <Video class="h-5 w-5 mr-2" /> Join Now
              </a>
            </div>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-5">
              <div class="flex items-center">
                <div class="p-2.5 bg-indigo-100 rounded-lg mr-3"><BookOpen class="h-5 w-5 text-indigo-600" /></div>
                <div>
                  <p class="text-xs font-medium text-gray-500">Enrolled</p>
                  <p class="text-xl font-bold text-gray-900">{{ data.enrolled_count }}</p>
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-5">
              <div class="flex items-center">
                <div class="p-2.5 bg-yellow-100 rounded-lg mr-3"><Award class="h-5 w-5 text-yellow-600" /></div>
                <div>
                  <p class="text-xs font-medium text-gray-500">GPA</p>
                  <p class="text-xl font-bold text-gray-900">{{ data.gpa }}</p>
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-5">
              <div class="flex items-center">
                <div class="p-2.5 bg-orange-100 rounded-lg mr-3"><Clock class="h-5 w-5 text-orange-600" /></div>
                <div>
                  <p class="text-xs font-medium text-gray-500">Pending</p>
                  <p class="text-xl font-bold text-gray-900">{{ data.pending_tasks }}</p>
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-4 sm:p-5">
              <div class="flex items-center">
                <div class="p-2.5 bg-emerald-100 rounded-lg mr-3"><Calendar class="h-5 w-5 text-emerald-600" /></div>
                <div>
                  <p class="text-xs font-medium text-gray-500">Courses</p>
                  <p class="text-xl font-bold text-gray-900">{{ data.courses.length }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

            <!-- Enrolled Courses -->
            <div class="lg:col-span-2">
              <h3 class="text-lg font-bold text-gray-900 mb-4">My Courses</h3>
              <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <ul class="divide-y divide-gray-200">
                  <li v-for="c in data.courses" :key="c.id"
                      @click="router.push(`/student/course/${c.id}`)"
                      class="p-4 sm:p-5 hover:bg-gray-50 transition-colors cursor-pointer flex items-center justify-between">
                    <div class="flex items-center space-x-4 min-w-0">
                      <div class="h-10 w-10 sm:h-12 sm:w-12 bg-indigo-100 rounded-lg flex items-center justify-center shrink-0">
                        <span class="text-indigo-700 font-bold text-sm">{{ c.course_code?.split('-')[0] }}</span>
                      </div>
                      <div class="min-w-0">
                        <p class="text-sm font-bold text-gray-900 truncate">{{ c.title }}</p>
                        <p class="text-xs text-gray-500 truncate">{{ c.course_code }} • {{ c.instructor_name }}</p>
                        <div v-if="c.attendance_pct !== null" class="mt-1.5 flex items-center text-xs">
                          <span class="text-gray-400 mr-2">Attendance: {{ c.attendance_pct }}%</span>
                          <div class="w-20 bg-gray-200 rounded-full h-1.5">
                            <div class="h-1.5 rounded-full" :class="c.attendance_pct >= 80 ? 'bg-emerald-500' : 'bg-red-500'"
                              :style="{ width: c.attendance_pct + '%' }"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <ChevronRight class="h-5 w-5 text-gray-400 ml-3 shrink-0" />
                  </li>
                </ul>
                <div v-if="!data.courses.length" class="p-8 text-center text-gray-400">
                  <BookOpen class="h-10 w-10 mx-auto mb-2 text-gray-300" />
                  <p class="text-sm">Not enrolled in any courses yet.</p>
                </div>
              </div>
            </div>

            <!-- Due Assignments -->
            <div>
              <h3 class="text-lg font-bold text-gray-900 mb-4">Due Soon</h3>
              <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <ul v-if="data.due_assignments?.length" class="divide-y divide-gray-200">
                  <li v-for="a in data.due_assignments" :key="a.id"
                      @click="router.push(`/student/course/${a.course_id}/assignment/${a.id}`)"
                      class="p-4 hover:bg-gray-50 transition-colors cursor-pointer">
                    <div class="flex items-start">
                      <div class="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center mr-3 shrink-0 mt-0.5">
                        <FileText class="h-4 w-4 text-orange-600" />
                      </div>
                      <div class="min-w-0">
                        <p class="text-sm font-bold text-gray-900 truncate">{{ a.title }}</p>
                        <p class="text-xs text-gray-500 mt-0.5">{{ a.course }}</p>
                        <p v-if="a.due_date" class="text-xs text-red-500 font-medium mt-1">Due {{ new Date(a.due_date).toLocaleDateString() }}</p>
                      </div>
                    </div>
                  </li>
                </ul>
                <div v-else class="p-6 text-center text-gray-400">
                  <CheckCircle class="h-8 w-8 mx-auto mb-1 text-gray-300" />
                  <p class="text-xs">All caught up!</p>
                </div>
              </div>
            </div>

          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  CheckCircle2, XCircle, Clock, AlertCircle,
  Users, Calendar, ChevronDown, Search, RefreshCw, Filter
} from 'lucide-vue-next'

const router = useRouter()

const courses = ref<any[]>([])
const selectedCourseId = ref<number | null>(null)
const sessions = ref<any[]>([])
const selectedSessionId = ref<number | null>(null)
const students = ref<any[]>([])
const allAttendanceMap = ref<Record<number, Record<number, string>>>({})
const isLoading = ref(false)
const searchQuery = ref('')
const stats = ref<any>(null)

const fetchCourses = async () => {
  try {
    const res = await api.get('instructor-dashboard/')
    courses.value = res.data.courses || []
    if (courses.value.length === 1) selectedCourseId.value = courses.value[0].id
  } catch (err) { console.error(err) }
}

const fetchSessions = async () => {
  if (!selectedCourseId.value) { sessions.value = []; return }
  try {
    const res = await api.get('sessions/', { params: { course: selectedCourseId.value } })
    sessions.value = res.data.sort((a: any, b: any) =>
      new Date(b.scheduled_at || b.date).getTime() - new Date(a.scheduled_at || a.date).getTime()
    )
    if (!selectedSessionId.value && sessions.value.length) selectedSessionId.value = sessions.value[0].id
  } catch (err) { console.error(err) }
}

const fetchAttendanceData = async () => {
  if (!selectedCourseId.value) return
  isLoading.value = true
  try {
    const [enrollRes, attendanceRes] = await Promise.all([
      api.get('enrollments/', { params: { course: selectedCourseId.value } }),
      api.get('attendance/', { params: { session__course: selectedCourseId.value } }),
    ])
    students.value = enrollRes.data.map((e: any) => e.student)
    const map: Record<number, Record<number, string>> = {}
    attendanceRes.data.forEach((a: any) => {
      if (!map[a.session]) map[a.session] = {}
      map[a.session][a.student.id] = a.status
    })
    allAttendanceMap.value = map
  } catch (err) { console.error(err) }
  finally { isLoading.value = false }
}

const getStatus = (studentId: number) => {
  if (!selectedSessionId.value) return null
  return allAttendanceMap.value[selectedSessionId.value]?.[studentId] || null
}

const cycleStatus = async (studentId: number) => {
  if (!selectedSessionId.value) return
  const current = getStatus(studentId) || 'absent'
  const order = ['present', 'absent', 'late', 'excused']
  const idx = order.indexOf(current)
  const nextStatus = order[(idx + 1) % order.length]

  if (!allAttendanceMap.value[selectedSessionId.value])
    allAttendanceMap.value[selectedSessionId.value] = {}
  allAttendanceMap.value[selectedSessionId.value][studentId] = nextStatus

  try {
    const existing = await api.get('attendance/', {
      params: { session: selectedSessionId.value, student: studentId }
    })
    if (existing.data.length) {
      await api.patch(`attendance/${existing.data[0].id}/`, { status: nextStatus })
    } else {
      await api.post('attendance/', {
        session: selectedSessionId.value,
        student: studentId,
        status: nextStatus,
      })
    }
    if (selectedSessionId.value) fetchSessionStats()
  } catch (err) { console.error(err) }
}

const markAllPresent = async () => {
  if (!selectedSessionId.value) return
  try {
    await api.post(`sessions/${selectedSessionId.value}/mark_all_present/`)
    await fetchAttendanceData()
    fetchSessionStats()
  } catch (err) { console.error(err) }
}

const fetchSessionStats = async () => {
  if (!selectedSessionId.value) { stats.value = null; return }
  try {
    const res = await api.get(`sessions/${selectedSessionId.value}/stats/`)
    stats.value = res.data
  } catch { stats.value = null }
}

const getCourseAttendancePercent = (studentId: number) => {
  let present = 0, total = 0
  const sessionsList = sessions.value
  for (const s of sessionsList) {
    const status = allAttendanceMap.value[s.id]?.[studentId]
    if (status) {
      total++
      if (status === 'present' || status === 'late' || status === 'excused') present++
    }
  }
  return total ? Math.round((present / total) * 100) : null
}

const statusIcon = (status: string) => {
  const icons: Record<string, any> = {
    present: CheckCircle2, absent: XCircle, late: Clock, excused: AlertCircle
  }
  return icons[status] || CheckCircle2
}

const statusClass = (status: string) => {
  const classes: Record<string, string> = {
    present: 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200 border-emerald-200',
    absent: 'bg-red-100 text-red-700 hover:bg-red-200 border-red-200',
    late: 'bg-amber-100 text-amber-700 hover:bg-amber-200 border-amber-200',
    excused: 'bg-blue-100 text-blue-700 hover:bg-blue-200 border-blue-200',
  }
  return classes[status] || 'bg-gray-100 text-gray-500 border-gray-200'
}

const filteredStudents = computed(() => {
  let list = students.value
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(s =>
      s.first_name?.toLowerCase().includes(q) ||
      s.last_name?.toLowerCase().includes(q) ||
      s.username?.toLowerCase().includes(q)
    )
  }
  return list
})

const selectedCourse = computed(() => courses.value.find(c => c.id === selectedCourseId.value))
const selectedSession = computed(() => sessions.value.find(s => s.id === selectedSessionId.value))

const sessionAttendanceCounts = computed(() => {
  if (!selectedSessionId.value || !students.value.length) return { present: 0, absent: 0, late: 0, excused: 0, total: 0 }
  const counts = { present: 0, absent: 0, late: 0, excused: 0, total: students.value.length }
  students.value.forEach(s => {
    const status = getStatus(s.id)
    if (status && counts.hasOwnProperty(status)) counts[status as keyof typeof counts]++
  })
  return counts
})

watch(selectedCourseId, () => {
  selectedSessionId.value = null
  allAttendanceMap.value = {}
  stats.value = null
  fetchSessions()
  fetchAttendanceData()
})

watch(selectedSessionId, () => {
  fetchAttendanceData()
  fetchSessionStats()
})

onMounted(fetchCourses)
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <InstructorSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0 shadow-sm">
        <div class="px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="flex items-center">
                <Users class="h-5 w-5 text-indigo-600 mr-2" />
                <h1 class="text-xl font-bold text-gray-900">Smart Attendance</h1>
              </div>
              <div class="h-6 w-px bg-gray-200" />
              <select v-model.number="selectedCourseId"
                class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none">
                <option :value="null" disabled>Select course...</option>
                <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.course_code }} — {{ c.title }}</option>
              </select>
              <div v-if="sessions.length" class="flex items-center gap-2">
                <Calendar class="h-4 w-4 text-gray-400" />
                <select v-model.number="selectedSessionId"
                  class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none max-w-[220px]">
                  <option v-for="s in sessions" :key="s.id" :value="s.id">
                    {{ s.title }} — {{ new Date(s.scheduled_at || s.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }}
                  </option>
                </select>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <div v-if="sessionAttendanceCounts.total" class="flex items-center gap-3 text-xs text-gray-500 mr-4">
                <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-emerald-500" />{{ sessionAttendanceCounts.present }}</span>
                <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-red-500" />{{ sessionAttendanceCounts.absent }}</span>
                <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-amber-500" />{{ sessionAttendanceCounts.late }}</span>
                <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-blue-500" />{{ sessionAttendanceCounts.excused }}</span>
              </div>
              <button @click="markAllPresent" :disabled="!selectedSessionId"
                class="flex items-center px-4 py-1.5 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm">
                <CheckCircle2 class="h-4 w-4 mr-1.5" /> Mark All Present
              </button>
            </div>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto">
        <div v-if="!selectedCourseId" class="flex flex-col items-center justify-center h-full text-gray-400">
          <div class="bg-gray-100 rounded-full p-6 mb-4">
            <Users class="h-12 w-12" />
          </div>
          <p class="text-lg font-medium text-gray-500">Select a course to start taking attendance</p>
          <p class="text-sm text-gray-400 mt-1">Choose a course from the dropdown above</p>
        </div>

        <div v-else-if="isLoading" class="flex items-center justify-center h-full">
          <div class="text-center text-gray-500">
            <RefreshCw class="h-8 w-8 mx-auto mb-2 animate-spin" />
            <p class="text-sm">Loading roster...</p>
          </div>
        </div>

        <template v-else-if="selectedSessionId">
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-3">
                <span class="text-sm text-gray-600 font-medium">{{ students.length }} enrolled</span>
                <div class="relative max-w-xs">
                  <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                  <input v-model="searchQuery" type="text" placeholder="Search student..."
                    class="w-56 pl-8 pr-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                </div>
              </div>
              <div class="text-xs text-gray-400">
                Click a status badge to cycle: <span class="font-mono">Present → Absent → Late → Excused</span>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider w-full">Student</th>
                    <th class="px-4 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider whitespace-nowrap">Attendance %</th>
                    <th class="px-4 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider whitespace-nowrap min-w-[120px]">Status</th>
                    <th class="px-4 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider whitespace-nowrap">Quick Toggle</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="s in filteredStudents" :key="s.id"
                    :class="[getCourseAttendancePercent(s.id) !== null && getCourseAttendancePercent(s.id)! < 80 ? 'bg-red-50/50' : 'hover:bg-gray-50', 'transition-colors']">
                    <td class="px-4 py-2.5">
                      <div class="flex items-center">
                        <div class="h-8 w-8 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm mr-3 shrink-0">
                          {{ s.first_name?.charAt(0) || '?' }}
                        </div>
                        <div>
                          <div class="flex items-center">
                            <p class="text-sm font-medium text-gray-900">{{ s.first_name }} {{ s.last_name }}</p>
                            <span v-if="getCourseAttendancePercent(s.id) !== null && getCourseAttendancePercent(s.id)! < 80"
                              class="ml-2 inline-flex items-center text-[10px] font-bold text-red-600 bg-red-100 px-1.5 py-0.5 rounded-full">
                              <AlertCircle class="h-3 w-3 mr-0.5" /> DANGER
                            </span>
                          </div>
                          <p class="text-xs text-gray-500">@{{ s.username }}</p>
                        </div>
                      </div>
                    </td>
                    <td class="px-4 py-2.5 text-center">
                      <div class="flex items-center justify-center gap-2">
                        <div class="w-20 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            :class="[getCourseAttendancePercent(s.id) !== null && getCourseAttendancePercent(s.id)! < 80 ? 'bg-red-500' : 'bg-emerald-500', 'h-full rounded-full transition-all']"
                            :style="{ width: (getCourseAttendancePercent(s.id) || 0) + '%' }" />
                        </div>
                        <span :class="[getCourseAttendancePercent(s.id) !== null && getCourseAttendancePercent(s.id)! < 80 ? 'text-red-600 font-bold' : 'text-gray-600', 'text-sm font-mono min-w-[3rem] text-right']">
                          {{ getCourseAttendancePercent(s.id) !== null ? getCourseAttendancePercent(s.id) + '%' : '—' }}
                        </span>
                      </div>
                    </td>
                    <td class="px-4 py-2.5 text-center">
                      <div v-if="getStatus(s.id)"
                        @click="cycleStatus(s.id)"
                        :class="[statusClass(getStatus(s.id) || ''), 'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold border cursor-pointer transition-all select-none']">
                        <component :is="statusIcon(getStatus(s.id)!)" class="h-3.5 w-3.5" />
                        {{ getStatus(s.id)?.charAt(0).toUpperCase() + getStatus(s.id)?.slice(1) }}
                      </div>
                      <span v-else
                        @click="cycleStatus(s.id)"
                        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-gray-400 bg-gray-100 border border-dashed border-gray-300 cursor-pointer hover:bg-gray-200 hover:text-gray-600 transition-all select-none">
                        Mark
                      </span>
                    </td>
                    <td class="px-4 py-2.5 text-right">
                      <div class="flex items-center justify-end gap-1">
                        <button @click="cycleStatus(s.id)"
                          class="p-1.5 rounded text-gray-400 hover:bg-emerald-50 hover:text-emerald-600 transition-colors" title="Present">
                          <CheckCircle2 class="h-4 w-4" />
                        </button>
                        <button @click="cycleStatus(s.id)"
                          class="p-1.5 rounded text-gray-400 hover:bg-red-50 hover:text-red-600 transition-colors" title="Absent">
                          <XCircle class="h-4 w-4" />
                        </button>
                        <button @click="cycleStatus(s.id)"
                          class="p-1.5 rounded text-gray-400 hover:bg-amber-50 hover:text-amber-600 transition-colors" title="Late">
                          <Clock class="h-4 w-4" />
                        </button>
                        <button @click="cycleStatus(s.id)"
                          class="p-1.5 rounded text-gray-400 hover:bg-blue-50 hover:text-blue-600 transition-colors" title="Excused">
                          <AlertCircle class="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="!students.length" class="p-8 text-center text-gray-500">
                <Users class="h-10 w-10 mx-auto mb-2 text-gray-300" />
                <p class="text-sm">No students enrolled in this course.</p>
              </div>
            </div>
          </div>
        </template>

        <div v-else class="flex flex-col items-center justify-center h-full text-gray-400">
          <Calendar class="h-12 w-12 mb-3" />
          <p class="text-base font-medium text-gray-500">No sessions available</p>
          <p class="text-sm mt-1 mb-4">Schedule a class session to start taking attendance.</p>
          <button @click="router.push(`/course/${selectedCourseId}/live`)"
            class="flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
            <Calendar class="h-4 w-4 mr-1.5" /> Schedule Session Now
          </button>
        </div>
      </main>
    </div>
  </div>
</template>

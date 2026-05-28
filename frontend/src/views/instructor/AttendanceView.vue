<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  ArrowLeft, CheckCircle2, XCircle, Clock, AlertCircle,
  Users, Calendar
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const courseId = computed(() => Number(route.params.id))
const course = ref<any>(null)
const students = ref<any[]>([])
const sessions = ref<any[]>([])
const attendanceMap = ref<Record<string, Record<number, string>>>({})
const isLoading = ref(true)

const fetchAttendanceData = async () => {
  isLoading.value = true
  try {
    const [courseRes, enrollmentsRes, sessionsRes, attendanceRes] = await Promise.all([
      api.get(`courses/${courseId.value}/`),
      api.get('enrollments/', { params: { course: courseId.value } }),
      api.get('sessions/', { params: { course: courseId.value } }),
      api.get('attendance/', { params: { session__course: courseId.value } }),
    ])
    course.value = courseRes.data
    students.value = enrollmentsRes.data.map((e: any) => e.student)
    sessions.value = sessionsRes.data

    const map: Record<string, Record<number, string>> = {}
    attendanceRes.data.forEach((a: any) => {
      if (!map[a.session]) map[a.session] = {}
      map[a.session][a.student.id] = a.status
    })
    attendanceMap.value = map
  } catch (error) {
    console.error("Error loading attendance data:", error)
  } finally {
    isLoading.value = false
  }
}

const cycleStatus = async (sessionId: number, studentId: number, current: string) => {
  const order = ['present', 'absent', 'late', 'excused']
  const idx = order.indexOf(current)
  const nextStatus = order[(idx + 1) % order.length]

  if (!attendanceMap.value[sessionId]) attendanceMap.value[sessionId] = {}
  attendanceMap.value[sessionId][studentId] = nextStatus

  try {
    const existing = await api.get('attendance/', {
      params: { session: sessionId, student: studentId }
    })
    if (existing.data.length) {
      await api.patch(`attendance/${existing.data[0].id}/`, { status: nextStatus })
    } else {
      await api.post('attendance/', {
        session: sessionId,
        student: studentId,
        status: nextStatus,
      })
    }
  } catch (error) {
    console.error("Error updating attendance:", error)
  }
}

const getStatusIcon = (status: string) => {
  const map: Record<string, any> = {
    present: CheckCircle2,
    absent: XCircle,
    late: Clock,
    excused: AlertCircle,
  }
  return map[status] || CheckCircle2
}

const statusColor = (status: string) => {
  const map: Record<string, string> = {
    present: 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200',
    absent: 'bg-red-100 text-red-700 hover:bg-red-200',
    late: 'bg-amber-100 text-amber-700 hover:bg-amber-200',
    excused: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

const getStudentAttendance = (studentId: number) => {
  let present = 0, total = 0
  sessions.value.forEach((s: any) => {
    const status = attendanceMap.value[s.id]?.[studentId]
    if (status) {
      total++
      if (status === 'present' || status === 'late' || status === 'excused') present++
    }
  })
  return total ? Math.round((present / total) * 100) : null
}

const handleMarkAllPresent = async (sessionId: number) => {
  try {
    await api.post(`sessions/${sessionId}/mark_all_present/`)
    await fetchAttendanceData()
  } catch (error) {
    console.error("Error marking all present:", error)
  }
}

const sortedSessions = computed(() =>
  [...sessions.value].sort((a: any, b: any) =>
    new Date(a.scheduled_at || a.date).getTime() - new Date(b.scheduled_at || b.date).getTime()
  )
)

onMounted(() => {
  fetchAttendanceData()
})
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">

    <InstructorSidebar />

    <div class="flex-1 flex flex-col overflow-hidden">

      <header class="bg-white border-b border-gray-200 flex-shrink-0">
        <div class="px-6">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center">
              <button @click="router.push(`/course/${courseId}`)" class="mr-4 text-gray-400 hover:text-indigo-600 transition-colors">
                <ArrowLeft class="h-6 w-6" />
              </button>
              <div>
                <h1 class="text-xl font-bold text-gray-900 leading-tight">Attendance Tracker</h1>
                <p v-if="course" class="text-xs text-gray-500 font-medium">{{ course.title }} — {{ students.length }} students</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">

        <div v-if="isLoading" class="text-center py-16 text-gray-500">
          Loading attendance data...
        </div>

        <template v-else>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10 min-w-[180px]">
                      <div class="flex items-center">
                        <Users class="h-4 w-4 mr-2 text-gray-400" /> Student
                      </div>
                    </th>
                    <th class="px-4 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider min-w-[60px]">%</th>
                    <th v-for="s in sortedSessions" :key="s.id"
                      class="px-3 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider min-w-[90px]">
                      <div class="flex flex-col items-center">
                        <span>{{ new Date(s.scheduled_at || s.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }}</span>
                        <button @click.stop="handleMarkAllPresent(s.id)"
                          class="mt-1 text-[10px] text-indigo-600 hover:text-indigo-800 hover:underline font-medium">
                          Mark All
                        </button>
                      </div>
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="s in students" :key="s.id"
                    :class="[getStudentAttendance(s.id) !== null && getStudentAttendance(s.id)! < 80 ? 'bg-red-50' : 'hover:bg-gray-50', 'transition-colors']">
                    <td class="px-4 py-2.5 whitespace-nowrap sticky left-0 bg-white z-10"
                      :class="getStudentAttendance(s.id) !== null && getStudentAttendance(s.id)! < 80 ? '!bg-red-50' : ''">
                      <div class="flex items-center">
                        <div class="h-8 w-8 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm mr-3">
                          {{ s.first_name?.charAt(0) || '?' }}
                        </div>
                        <div>
                          <p class="text-sm font-medium text-gray-900 flex items-center">
                            {{ s.first_name }} {{ s.last_name }}
                            <span v-if="getStudentAttendance(s.id) !== null && getStudentAttendance(s.id)! < 80"
                              class="ml-2 text-[10px] text-red-600 font-bold flex items-center">
                              <AlertCircle class="h-3 w-3 mr-0.5" /> Warning
                            </span>
                          </p>
                          <p class="text-xs text-gray-500">@{{ s.username }}</p>
                        </div>
                      </div>
                    </td>
                    <td class="px-4 py-2.5 text-center">
                      <span :class="[getStudentAttendance(s.id) !== null && getStudentAttendance(s.id)! < 80 ? 'text-red-600 font-bold' : 'text-gray-600', 'text-sm font-mono']">
                        {{ getStudentAttendance(s.id) !== null ? getStudentAttendance(s.id) + '%' : '—' }}
                      </span>
                    </td>
                    <td v-for="session in sortedSessions" :key="session.id"
                      class="px-3 py-2.5 text-center cursor-pointer">
                      <div v-if="attendanceMap[session.id]?.[s.id]"
                        @click="cycleStatus(session.id, s.id, attendanceMap[session.id][s.id])"
                        :class="[statusColor(attendanceMap[session.id][s.id]), 'inline-flex items-center justify-center w-8 h-8 rounded-full transition-colors']"
                        :title="attendanceMap[session.id][s.id]">
                        <component :is="getStatusIcon(attendanceMap[session.id][s.id])" class="h-4 w-4" />
                      </div>
                      <div v-else
                        @click="cycleStatus(session.id, s.id, 'present')"
                        class="inline-flex items-center justify-center w-8 h-8 rounded-full text-gray-300 hover:bg-gray-100 transition-colors cursor-pointer">
                        <span class="text-xs">—</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="!sessions.length" class="text-center py-12 text-gray-400">
            <Calendar class="h-10 w-10 mx-auto mb-2" />
            <p class="text-sm">No sessions yet. Schedule a class first to track attendance.</p>
          </div>

        </template>

      </main>
    </div>
  </div>
</template>

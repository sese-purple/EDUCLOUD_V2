<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  ArrowLeft, Video, Plus, Clock,
  ExternalLink, Upload, Trash2,
  Calendar, Monitor, CheckCircle2, AlertCircle
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const courseId = computed(() => Number(route.params.id))
const course = ref<any>(null)
const sessions = ref<any[]>([])
const isLoading = ref(true)
const showScheduleForm = ref(false)
const scheduleError = ref('')
const scheduleSuccess = ref(false)

const newSession = ref({
  title: '',
  scheduled_at: '',
  ends_at: '',
  meeting_link: '',
})

const fetchSessions = async () => {
  isLoading.value = true
  try {
    const params: any = { course: courseId.value }
    const [courseRes, sessionsRes] = await Promise.all([
      api.get(`courses/${courseId.value}/`),
      api.get('sessions/', { params }),
    ])
    course.value = courseRes.data
    sessions.value = sessionsRes.data
  } catch (error) {
    console.error("Error loading sessions:", error)
  } finally {
    isLoading.value = false
  }
}

const upcomingSessions = computed(() =>
  sessions.value.filter((s: any) => !s.recording_url && new Date(s.scheduled_at) > new Date())
    .sort((a: any, b: any) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())
)

const pastSessions = computed(() =>
  sessions.value.filter((s: any) => s.recording_url || new Date(s.scheduled_at) < new Date())
    .sort((a: any, b: any) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime())
)

const nextSession = computed(() => upcomingSessions.value[0] || null)

const countdown = ref('')
const countdownRef = ref<ReturnType<typeof setInterval> | null>(null)

const updateCountdown = () => {
  if (!nextSession.value) {
    countdown.value = ''
    return
  }
  const now = new Date().getTime()
  const target = new Date(nextSession.value.scheduled_at).getTime()
  const diff = target - now
  if (diff <= 0) {
    countdown.value = 'Starting now!'
    return
  }
  const h = Math.floor(diff / (1000 * 60 * 60))
  const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  countdown.value = `${h}h ${m}m until next session`
}

onMounted(() => {
  fetchSessions()
  countdownRef.value = setInterval(updateCountdown, 1000)
})

onUnmounted(() => {
  if (countdownRef.value) clearInterval(countdownRef.value)
})

const parseDate = (str: string): string => {
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(str)) return str + ':00'
  const dmy = str.match(/^(\d{2})\/(\d{2})\/(\d{4})[\sT](\d{2}:\d{2})/)
  if (dmy) return `${dmy[3]}-${dmy[2]}-${dmy[1]}T${dmy[4]}:00`
  const mdy = str.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})[\sT](\d{2}:\d{2})/)
  if (mdy) return `${mdy[3]}-${mdy[1]}-${mdy[2]}T${mdy[4]}:00`
  return str
}

const handleSchedule = async () => {
  scheduleError.value = ''
  scheduleSuccess.value = false

  if (!newSession.value.scheduled_at) {
    scheduleError.value = 'Date & Time is required'
    return
  }

  try {
    await api.post('sessions/', {
      course: courseId.value,
      title: newSession.value.title || 'Live Session',
      scheduled_at: parseDate(newSession.value.scheduled_at),
      ends_at: newSession.value.ends_at ? parseDate(newSession.value.ends_at) : null,
      meeting_link: newSession.value.meeting_link || '',
    })
    scheduleSuccess.value = true
    setTimeout(() => scheduleSuccess.value = false, 3000)
    showScheduleForm.value = false
    newSession.value = { title: '', scheduled_at: '', ends_at: '', meeting_link: '' }
    await fetchSessions()
  } catch (error: any) {
    scheduleError.value = error.response?.data?.scheduled_at?.[0] || 'Failed to schedule. Check your input and try again.'
  }
}

const handleDeleteSession = async (id: number) => {
  try {
    await api.delete(`sessions/${id}/`)
    await fetchSessions()
  } catch (error) {
    console.error("Error deleting session:", error)
  }
}

const handleAddRecording = async (sessionId: number) => {
  const url = prompt('Enter recording URL:')
  if (!url) return
  try {
    await api.patch(`sessions/${sessionId}/`, { recording_url: url })
    await fetchSessions()
  } catch (error) {
    console.error("Error adding recording:", error)
  }
}
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
                <h1 class="text-xl font-bold text-gray-900 leading-tight">Virtual Classroom</h1>
                <p v-if="course" class="text-xs text-gray-500 font-medium">{{ course.title }}</p>
              </div>
            </div>
            <button @click="showScheduleForm = !showScheduleForm"
              class="flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
              <Plus class="h-4 w-4 mr-2" /> Schedule Class
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">

        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading sessions...</div>

        <template v-else>

          <div v-if="nextSession" class="bg-indigo-900 rounded-2xl shadow-lg overflow-hidden relative mb-8">
            <div class="absolute top-0 right-0 -mt-4 -mr-4 w-32 h-32 bg-indigo-700 rounded-full opacity-50 blur-2xl"></div>
            <div class="p-8 relative z-10 text-white flex flex-col md:flex-row items-center justify-between">
              <div>
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-500 text-white mb-4">
                  <Clock class="h-3 w-3 mr-1" /> {{ countdown }}
                </span>
                <h2 class="text-2xl font-bold mb-1">{{ nextSession.title }}</h2>
                <p class="text-indigo-200 text-sm mb-2">{{ new Date(nextSession.scheduled_at).toLocaleString() }}</p>
                <p v-if="nextSession.meeting_link" class="text-indigo-200 text-xs mb-6 max-w-md truncate">{{ nextSession.meeting_link }}</p>
                <div class="flex gap-3">
                  <a v-if="nextSession.meeting_link" :href="nextSession.meeting_link" target="_blank"
                    class="bg-white text-indigo-900 px-6 py-3 rounded-lg font-bold shadow-md hover:bg-gray-50 transition-colors flex items-center">
                    <Video class="h-5 w-5 mr-2 text-indigo-600" /> Join Live Class
                  </a>
                </div>
              </div>
              <div class="hidden md:block">
                <Monitor class="h-32 w-32 text-indigo-800 opacity-50" />
              </div>
            </div>
          </div>

          <div v-if="showScheduleForm" class="bg-white p-6 rounded-xl shadow-sm border border-indigo-200 mb-8">
            <h3 class="text-lg font-bold text-gray-900 mb-4 border-b pb-2">Schedule New Class</h3>

            <div v-if="scheduleSuccess" class="mb-4 flex items-center gap-2 text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 px-4 py-3 rounded-lg">
              <CheckCircle2 class="h-4 w-4 shrink-0" /> Session scheduled successfully!
            </div>
            <div v-if="scheduleError" class="mb-4 flex items-center gap-2 text-sm text-red-700 bg-red-50 border border-red-200 px-4 py-3 rounded-lg">
              <AlertCircle class="h-4 w-4 shrink-0" /> {{ scheduleError }}
            </div>

            <form @submit.prevent="handleSchedule" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">Session Title</label>
                <input v-model="newSession.title" type="text" placeholder="e.g. Lecture 5: Database Design"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500">
              </div>
              <div>
                <label class="block text-sm font-medium text-red-600 mb-1">Date & Time <span class="text-red-500">*</span></label>
                <input v-model="newSession.scheduled_at" type="datetime-local"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">End Time (optional)</label>
                <input v-model="newSession.ends_at" type="datetime-local"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500">
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">Meeting Link</label>
                <input v-model="newSession.meeting_link" type="text" placeholder="https://zoom.us/j/... or https://meet.google.com/..."
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500">
              </div>
              <div class="md:col-span-2 flex justify-end pt-2">
                <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-6 rounded-lg transition-colors shadow-sm">
                  Schedule Class
                </button>
              </div>
            </form>
          </div>

          <div v-if="upcomingSessions.length > 1" class="mb-8">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Upcoming Classes</h3>
            <div class="space-y-3">
              <div v-for="s in upcomingSessions.slice(1)" :key="s.id"
                class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex items-center justify-between hover:shadow-md transition-shadow">
                <div class="flex items-center">
                  <div class="h-10 w-10 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center mr-4">
                    <Calendar class="h-5 w-5" />
                  </div>
                  <div>
                    <p class="text-sm font-bold text-gray-900">{{ s.title }}</p>
                    <p class="text-xs text-gray-500">{{ new Date(s.scheduled_at).toLocaleString() }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <a v-if="s.meeting_link" :href="s.meeting_link" target="_blank"
                    class="text-indigo-600 hover:text-indigo-800 p-2 rounded hover:bg-indigo-50">
                    <ExternalLink class="h-4 w-4" />
                  </a>
                  <button @click="handleDeleteSession(s.id)" class="text-red-400 hover:text-red-600 p-2 rounded hover:bg-red-50">
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 class="text-lg font-bold text-gray-900 mb-4">Past Classes</h3>
            <div class="space-y-3">
              <div v-for="s in pastSessions" :key="s.id"
                class="bg-white rounded-xl shadow-sm border border-gray-200 p-5 flex items-center justify-between hover:shadow-md transition-shadow">
                <div class="flex items-center">
                  <div class="h-10 w-10 bg-gray-100 text-gray-500 rounded-lg flex items-center justify-center mr-4">
                    <Video class="h-5 w-5" />
                  </div>
                  <div>
                    <p class="text-sm font-bold text-gray-900">{{ s.title }}</p>
                    <p class="text-xs text-gray-500">{{ new Date(s.scheduled_at).toLocaleString() }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <button v-if="!s.recording_url" @click="handleAddRecording(s.id)"
                    class="text-indigo-600 hover:text-indigo-800 text-xs font-medium flex items-center px-3 py-1.5 rounded hover:bg-indigo-50">
                    <Upload class="h-3 w-3 mr-1" /> Add Recording
                  </button>
                  <a v-else :href="s.recording_url" target="_blank"
                    class="text-indigo-600 hover:text-indigo-800 text-xs font-medium flex items-center px-3 py-1.5 rounded hover:bg-indigo-50">
                    <Video class="h-3 w-3 mr-1" /> Recording
                  </a>
                </div>
              </div>
              <div v-if="!pastSessions.length" class="text-center py-8 text-gray-400 text-sm">
                No past classes yet.
              </div>
            </div>
          </div>

        </template>

      </main>
    </div>
  </div>
</template>

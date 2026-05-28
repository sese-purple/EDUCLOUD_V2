<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  ArrowLeft, BookOpen, Video, FileText, Download,
  Clock, Calendar, CheckCircle, ExternalLink,
  HelpCircle, ChevronRight, BarChart
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
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0">
        <div class="px-6">
          <div class="flex items-center h-16">
            <button @click="router.push('/student')" class="mr-4 text-gray-400 hover:text-indigo-600"><ArrowLeft class="h-6 w-6" /></button>
            <div v-if="course">
              <h1 class="text-lg font-bold text-gray-900">{{ course.title }}</h1>
              <p class="text-xs text-gray-500">{{ course.course_code }}</p>
            </div>
          </div>
        </div>
        <div class="px-6 border-t border-gray-100">
          <div class="flex space-x-6 -mb-px">
            <button v-for="tab in ['overview', 'materials', 'assignments', 'quizzes']" :key="tab"
              @click="activeTab = tab"
              :class="[activeTab === tab ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700', 'pb-3 px-1 border-b-2 font-medium text-sm capitalize transition-colors']">
              {{ tab }}
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-6">
        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading...</div>

        <template v-else-if="activeTab === 'overview'">

          <!-- Syllabus -->
          <div v-if="course.syllabus" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h3 class="text-base font-bold text-gray-900 mb-3 flex items-center"><BookOpen class="h-5 w-5 text-indigo-600 mr-2" /> Syllabus</h3>
            <div class="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">{{ course.syllabus }}</div>
          </div>

          <!-- Next Live Session -->
          <div v-if="nextSession" class="bg-gradient-to-r from-indigo-600 to-indigo-800 rounded-xl p-6 text-white shadow-md mb-6">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p class="text-indigo-200 text-xs uppercase tracking-wider font-medium">Next Class</p>
                <h3 class="text-lg font-bold mt-1">{{ nextSession.title || 'Live Session' }}</h3>
                <p v-if="nextSession.scheduled_at" class="text-indigo-200 text-sm mt-1 flex items-center">
                  <Calendar class="h-4 w-4 mr-1.5" /> {{ new Date(nextSession.scheduled_at).toLocaleString() }}
                </p>
              </div>
              <a v-if="nextSession.meeting_link" :href="nextSession.meeting_link" target="_blank"
                class="mt-3 sm:mt-0 inline-flex items-center px-5 py-2.5 bg-white text-indigo-700 rounded-xl font-bold text-sm hover:bg-indigo-50 transition-all shadow">
                <Video class="h-4 w-4 mr-2" /> Join Class
              </a>
            </div>
          </div>

          <!-- Past Sessions Recordings -->
          <div v-if="sessions.filter((s:any) => s.recording_url).length" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h3 class="text-base font-bold text-gray-900 mb-4 flex items-center"><Video class="h-5 w-5 text-indigo-600 mr-2" /> Recordings</h3>
            <div class="space-y-3">
              <div v-for="s in sessions.filter((s:any) => s.recording_url)" :key="s.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ s.title }}</p>
                  <p class="text-xs text-gray-500">{{ new Date(s.scheduled_at || s.date).toLocaleDateString() }}</p>
                </div>
                <a :href="s.recording_url" target="_blank" class="text-indigo-600 hover:text-indigo-800 flex items-center text-sm font-medium">
                  <ExternalLink class="h-4 w-4 mr-1" /> Watch
                </a>
              </div>
            </div>
          </div>

          <!-- Assignments List -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100">
              <h3 class="text-base font-bold text-gray-900">Assignments</h3>
            </div>
            <ul class="divide-y divide-gray-200">
              <li v-for="a in assignments" :key="a.id"
                  @click="router.push(`/student/course/${courseId}/assignment/${a.id}`)"
                  class="p-4 hover:bg-gray-50 transition-colors cursor-pointer flex items-center justify-between">
                <div class="flex items-center space-x-3 min-w-0">
                  <FileText class="h-5 w-5 text-gray-400 shrink-0" />
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">{{ a.title }}</p>
                    <p class="text-xs text-gray-500">{{ a.assignment_type }} • {{ a.max_points }} pts</p>
                  </div>
                </div>
                <ChevronRight class="h-4 w-4 text-gray-400 shrink-0 ml-3" />
              </li>
              <li v-if="!assignments.length" class="p-6 text-center text-gray-400 text-sm">No assignments yet.</li>
            </ul>
          </div>

        </template>

        <template v-else-if="activeTab === 'materials'">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100">
              <h3 class="text-base font-bold text-gray-900">Course Materials</h3>
            </div>
            <ul class="divide-y divide-gray-200">
              <li v-for="m in materials" :key="m.id" class="p-4 flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <FileText class="h-5 w-5 text-indigo-600" />
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ m.title }}</p>
                    <p class="text-xs text-gray-500">{{ m.file_type || 'Document' }}</p>
                  </div>
                </div>
                <a v-if="m.file || m.file_url" :href="m.file || m.file_url" target="_blank"
                  class="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center">
                  <Download class="h-4 w-4 mr-1" /> Download
                </a>
              </li>
              <li v-if="!materials.length" class="p-6 text-center text-gray-400 text-sm">No materials uploaded.</li>
            </ul>
          </div>
        </template>

        <template v-else-if="activeTab === 'assignments'">
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100">
              <h3 class="text-base font-bold text-gray-900">Assignments</h3>
            </div>
            <ul class="divide-y divide-gray-200">
              <li v-for="a in assignments" :key="a.id"
                  @click="router.push(`/student/course/${courseId}/assignment/${a.id}`)"
                  class="p-4 hover:bg-gray-50 transition-colors cursor-pointer flex items-center justify-between">
                <div class="flex items-center space-x-3 min-w-0">
                  <FileText class="h-5 w-5 text-gray-400 shrink-0" />
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">{{ a.title }}</p>
                    <p class="text-xs text-gray-500">{{ a.assignment_type }} • {{ a.max_points }} pts • Due {{ a.due_date ? new Date(a.due_date).toLocaleDateString() : 'No due date' }}</p>
                  </div>
                </div>
                <ChevronRight class="h-4 w-4 text-gray-400 shrink-0 ml-3" />
              </li>
              <li v-if="!assignments.length" class="p-6 text-center text-gray-400 text-sm">No assignments yet.</li>
            </ul>
          </div>
        </template>

        <template v-else-if="activeTab === 'quizzes'">
          <div class="space-y-3">
            <div v-for="q in quizzes" :key="q.id"
                 class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all">
              <div class="p-5">
                <div class="flex items-start justify-between">
                  <div class="min-w-0 flex-1">
                    <h3 class="text-sm font-bold text-gray-900 truncate">{{ q.title }}</h3>
                    <p class="text-xs text-gray-500 mt-0.5">{{ q.total_points }} points • {{ q.time_limit }} min</p>
                  </div>
                  <span v-if="getAttempt(q.id)?.is_completed"
                    class="ml-3 shrink-0 bg-emerald-50 text-emerald-700 text-xs font-medium px-2.5 py-1 rounded-full flex items-center">
                    <CheckCircle class="h-3 w-3 mr-1" /> {{ getAttempt(q.id).score }}/{{ q.total_points }}
                  </span>
                  <span v-else-if="getAttempt(q.id)"
                    class="ml-3 shrink-0 bg-amber-50 text-amber-700 text-xs font-medium px-2.5 py-1 rounded-full flex items-center">
                    <Clock class="h-3 w-3 mr-1" /> In Progress
                  </span>
                </div>
                <div class="flex items-center justify-between mt-4 pt-3 border-t border-gray-100">
                  <p v-if="q.due_date" class="text-xs text-gray-400 flex items-center">
                    <Calendar class="h-3 w-3 mr-1" /> Due {{ new Date(q.due_date).toLocaleDateString() }}
                  </p>
                  <p v-else class="text-xs text-gray-400">No due date</p>
                  <button @click="router.push(`/student/course/${courseId}/quiz/${q.id}`)"
                    :class="['text-sm font-medium px-4 py-1.5 rounded-lg transition-colors',
                      getAttempt(q.id)?.is_completed
                        ? 'text-indigo-600 bg-indigo-50 hover:bg-indigo-100'
                        : 'text-white bg-indigo-600 hover:bg-indigo-700']">
                    {{ getAttempt(q.id)?.is_completed ? 'Review' : 'Start Quiz' }}
                  </button>
                </div>
              </div>
            </div>
            <div v-if="!quizzes.length" class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
              <HelpCircle class="h-10 w-10 text-gray-300 mx-auto mb-2" />
              <p class="text-sm text-gray-400">No quizzes available yet.</p>
            </div>
          </div>
        </template>

      </main>
    </div>
  </div>
</template>

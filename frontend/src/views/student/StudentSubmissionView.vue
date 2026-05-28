<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  ArrowLeft, FileText, Upload, Clock, CheckCircle,
  X, AlertCircle, Download, Trash2,
  Menu, LayoutDashboard, GraduationCap, BookOpen, Settings, LogOut
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const courseId = computed(() => Number(route.params.id))
const assignId = computed(() => Number(route.params.task_id))

const assignment = ref<any>(null)
const submission = ref<any>(null)
const course = ref<any>(null)
const isLoading = ref(true)
const submitting = ref(false)
const dragOver = ref(false)
const selectedFile = ref<File | null>(null)
const textContent = ref('')
const submissionType = ref<'file' | 'text'>('file')
const successMsg = ref('')
const errorMsg = ref('')
const countdown = ref('')
const mobileMenuOpen = ref(false)

const deadlinePassed = computed(() => {
  if (!assignment.value?.due_date) return false
  return new Date(assignment.value.due_date).getTime() < Date.now()
})

const fetchData = async () => {
  isLoading.value = true
  try {
    const [courseRes, assignRes] = await Promise.all([
      api.get(`courses/${courseId.value}/`),
      api.get(`assignments/${assignId.value}/`),
    ])
    course.value = courseRes.data
    assignment.value = assignRes.data

    const subRes = await api.get('submissions/', { params: { assignment: assignId.value } })
    const mySub = subRes.data.find((s: any) => s.student?.id === JSON.parse(localStorage.getItem('user_id') || '0'))
    if (mySub) {
      submission.value = mySub
      if (mySub.text_response) {
        submissionType.value = 'text'
        textContent.value = mySub.text_response
      }
    }
  } catch (err) { console.error(err) } finally { isLoading.value = false }
}

const updateCountdown = () => {
  if (!assignment.value?.due_date) { countdown.value = ''; return }
  const diff = new Date(assignment.value.due_date).getTime() - Date.now()
  if (diff <= 0) { countdown.value = 'Deadline passed'; return }
  const h = Math.floor(diff / 3600000)
  const m = Math.floor((diff % 3600000) / 60000)
  const s = Math.floor((diff % 60000) / 1000)
  countdown.value = `${h}h ${m}m ${s}s`
}

let interval: ReturnType<typeof setInterval> | null = null
onMounted(() => {
  fetchData().then(() => { updateCountdown(); interval = setInterval(updateCountdown, 1000) })
})
onUnmounted(() => { if (interval) clearInterval(interval) })

const handleDrop = (e: DragEvent) => {
  dragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) selectedFile.value = file
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) selectedFile.value = input.files[0]
}

const removeFile = () => { selectedFile.value = null }

const submitWork = async () => {
  if (submissionType.value === 'file' && !selectedFile.value) { errorMsg.value = 'Please select a file.'; return }
  if (submissionType.value === 'text' && !textContent.value.trim()) { errorMsg.value = 'Please enter your response.'; return }
  if (deadlinePassed.value) { errorMsg.value = 'Deadline has passed. Submissions are closed.'; return }
  submitting.value = true
  errorMsg.value = ''
  successMsg.value = ''
  try {
    const userId = JSON.parse(localStorage.getItem('user_id') || '0')
    const payload: any = {
      assignment: assignId.value,
      student: userId,
      is_late: deadlinePassed.value,
    }

    if (submissionType.value === 'file' && selectedFile.value) {
      const form = new FormData()
      form.append('assignment', String(assignId.value))
      form.append('student', String(userId))
      form.append('file', selectedFile.value)
      form.append('is_late', String(deadlinePassed.value))
      if (submission.value?.id) {
        await api.patch(`submissions/${submission.value.id}/`, form, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      } else {
        const res = await api.post('submissions/', form, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        submission.value = res.data
      }
    } else {
      payload.text_response = textContent.value
      if (submission.value?.id) {
        const res = await api.patch(`submissions/${submission.value.id}/`, payload)
        submission.value = res.data
      } else {
        const res = await api.post('submissions/', payload)
        submission.value = res.data
      }
    }
    successMsg.value = 'Submitted successfully!'
    selectedFile.value = null
    setTimeout(() => successMsg.value = '', 4000)
    await fetchData()
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Submission failed.'
  } finally { submitting.value = false }
}

const unsubmit = async () => {
  if (!submission.value?.id) return
  try {
    await api.delete(`submissions/${submission.value.id}/`)
    submission.value = null
    successMsg.value = 'Submission withdrawn.'
    setTimeout(() => successMsg.value = '', 3000)
  } catch (err) { console.error(err) }
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <StudentSidebar />

    <!-- Mobile Menu Overlay -->
    <div v-if="mobileMenuOpen" class="fixed inset-0 z-50 flex md:hidden">
      <div class="fixed inset-0 bg-gray-800/75" @click="mobileMenuOpen = false"></div>
      <div class="relative flex w-full max-w-xs flex-1 flex-col bg-white pt-5 pb-4">
        <div class="flex items-center justify-between px-4 mb-6">
          <h1 class="text-xl font-bold text-gray-900 tracking-tight">EDUCLOUD <span class="text-indigo-600">2.0</span></h1>
          <button @click="mobileMenuOpen = false" class="text-gray-400 hover:text-gray-600"><span class="text-2xl">&times;</span></button>
        </div>
        <nav class="flex-1 px-4 space-y-1">
          <a @click="mobileMenuOpen = false; router.push('/student')"
             class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors cursor-pointer">
            <LayoutDashboard class="w-5 h-5 mr-3 text-gray-400" /> Dashboard
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/marksheet')"
             class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors cursor-pointer">
            <GraduationCap class="w-5 h-5 mr-3 text-gray-400" /> Marksheet
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/courses')"
             class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors cursor-pointer">
            <BookOpen class="w-5 h-5 mr-3 text-gray-400" /> My Courses
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/settings')"
             class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors cursor-pointer">
            <Settings class="w-5 h-5 mr-3 text-gray-400" /> Settings
          </a>
          <hr class="my-3 border-gray-200" />
          <a @click="localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); localStorage.removeItem('user_role'); localStorage.removeItem('user_id'); localStorage.removeItem('username'); router.push('/login')"
             class="flex items-center px-3 py-2.5 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors cursor-pointer">
            <LogOut class="w-5 h-5 mr-3 text-red-500" /> Sign Out
          </a>
        </nav>
      </div>
    </div>

    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0">
        <div class="px-4 sm:px-6 h-16 flex items-center">
          <button @click="mobileMenuOpen = true" class="mr-3 md:hidden text-gray-500 hover:text-gray-900 focus:outline-none">
            <Menu class="h-6 w-6" />
          </button>
          <button @click="router.push(`/student/course/${courseId}`)" class="mr-4 text-gray-400 hover:text-indigo-600 hidden sm:block"><ArrowLeft class="h-6 w-6" /></button>
          <div>
            <h1 class="text-lg font-bold text-gray-900">Submission Desk</h1>
            <p v-if="course" class="text-xs text-gray-500">{{ course.title }}</p>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 sm:p-6 max-w-3xl mx-auto w-full">

        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading...</div>

        <template v-else>

          <!-- Countdown Banner -->
          <div v-if="assignment?.due_date && !deadlinePassed"
            class="bg-gradient-to-r from-amber-500 to-orange-600 rounded-xl p-4 text-white shadow-md mb-6 flex items-center justify-between">
            <div class="flex items-center">
              <Clock class="h-5 w-5 mr-3" />
              <div>
                <p class="text-sm font-bold">Time Remaining</p>
                <p class="text-2xl font-mono font-bold">{{ countdown }}</p>
              </div>
            </div>
          </div>

          <div v-if="deadlinePassed" class="bg-red-100 border border-red-300 text-red-700 rounded-xl p-4 mb-6 flex items-center">
            <AlertCircle class="h-5 w-5 mr-3" /> Deadline has passed. Submissions are closed.
          </div>

          <!-- Success/Error -->
          <div v-if="successMsg" class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-lg text-sm flex items-center mb-6">
            <CheckCircle class="h-4 w-4 mr-2" /> {{ successMsg }}
          </div>
          <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-6">{{ errorMsg }}</div>

          <!-- Assignment Prompt -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <div class="flex items-start justify-between mb-4">
              <div>
                <h2 class="text-xl font-bold text-gray-900">{{ assignment?.title }}</h2>
                <p class="text-sm text-gray-500 mt-1">{{ assignment?.assignment_type }} • {{ assignment?.max_points }} points</p>
              </div>
            </div>
            <p class="text-sm text-gray-700 whitespace-pre-wrap">{{ assignment?.description }}</p>
            <a v-if="assignment?.file" :href="assignment.file" target="_blank"
              class="mt-4 inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-800">
              <Download class="h-4 w-4 mr-1" /> Download assignment file
            </a>
          </div>

          <!-- Existing Submission -->
          <div v-if="submission" class="bg-emerald-50 border border-emerald-200 rounded-xl p-5 mb-6">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <CheckCircle class="h-5 w-5 text-emerald-600 mr-3" />
                <div>
                  <p class="text-sm font-bold text-emerald-900">Submitted</p>
                  <p class="text-xs text-emerald-700">{{ new Date(submission.submitted_at).toLocaleString() }}</p>
                  <a v-if="submission.file" :href="submission.file" target="_blank"
                    class="text-xs text-emerald-800 underline mt-1 inline-block">View file</a>
                  <p v-if="submission.text_response" class="text-xs text-emerald-800 mt-1 italic">"{{ submission.text_response.substring(0, 100) }}{{ submission.text_response.length > 100 ? '...' : '' }}"</p>
                </div>
              </div>
              <div class="text-right">
                <div v-if="submission.grade !== null" class="text-sm">
                  <span class="font-bold text-emerald-900">{{ submission.grade }}</span>
                  <span class="text-emerald-700"> / {{ assignment?.max_points }}</span>
                </div>
                <p v-if="submission.feedback" class="text-xs text-emerald-700 mt-1 italic">"{{ submission.feedback }}"</p>
                <button v-if="!deadlinePassed" @click="unsubmit"
                  class="mt-2 text-xs text-red-600 hover:text-red-800 font-medium">Unsubmit</button>
              </div>
            </div>
          </div>

          <!-- Upload Zone -->
          <div v-if="!deadlinePassed" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base font-bold text-gray-900">Submit Your Work</h3>
              <div class="flex bg-gray-100 p-0.5 rounded-lg">
                <button @click="submissionType = 'file'" :class="[submissionType === 'file' ? 'bg-white shadow-sm text-indigo-700' : 'text-gray-500', 'px-3 py-1.5 text-xs font-medium rounded-md transition-all']">
                  File Upload
                </button>
                <button @click="submissionType = 'text'" :class="[submissionType === 'text' ? 'bg-white shadow-sm text-indigo-700' : 'text-gray-500', 'px-3 py-1.5 text-xs font-medium rounded-md transition-all']">
                  Text Entry
                </button>
              </div>
            </div>

            <!-- File Upload -->
            <div v-if="submissionType === 'file'">
              <div @drop.prevent="handleDrop" @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false"
                @click="($refs.fileInput as HTMLInputElement)?.click()"
                :class="[dragOver ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-gray-50', 'border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer mb-4']">
                <template v-if="!selectedFile">
                  <Upload class="h-10 w-10 text-gray-300 mx-auto mb-3" />
                  <p class="text-sm font-medium text-gray-700">Drop your file here, or <span class="text-indigo-600">browse</span></p>
                  <p class="text-xs text-gray-400 mt-1">PDF, DOCX, images — up to 50MB</p>
                </template>
                <template v-else>
                  <FileText class="h-8 w-8 text-indigo-600 mx-auto mb-2" />
                  <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
                  <p class="text-xs text-gray-400">{{ (selectedFile.size / 1024 / 1024).toFixed(1) }} MB</p>
                  <button @click.stop="removeFile" class="mt-2 text-xs text-red-600 hover:text-red-800 font-medium">Remove</button>
                </template>
                <input ref="fileInput" type="file" class="hidden" @change="handleFileSelect" accept=".pdf,.docx,.doc,.ppt,.pptx,.xlsx,.xls,.txt,.png,.jpg,.jpeg,.zip" />
              </div>
            </div>

            <!-- Text Entry -->
            <div v-if="submissionType === 'text'" class="mb-4">
              <textarea v-model="textContent" rows="6" placeholder="Type your response or paste a link here..."
                class="w-full border border-gray-300 rounded-xl p-4 text-sm focus:ring-2 focus:ring-indigo-500 outline-none resize-none"></textarea>
            </div>

            <button @click="submitWork" :disabled="submitting || (submissionType === 'file' && !selectedFile) || (submissionType === 'text' && !textContent.trim())"
              class="w-full py-3 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-sm text-sm flex items-center justify-center">
              <Upload class="h-5 w-5 mr-2" /> {{ submitting ? 'Uploading...' : submission ? 'Resubmit' : 'Submit Assignment' }}
            </button>
          </div>

        </template>
      </main>
    </div>
  </div>
</template>

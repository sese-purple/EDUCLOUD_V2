<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  ArrowLeft, FileText, Users,
  BookOpen, UploadCloud, Download, GraduationCap,
  Video, ClipboardCheck, X, File as FileIcon,
  FolderOpen, Settings, Key, CheckCircle, Copy, RefreshCw
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const courseId = computed(() => Number(route.params.id))
const activeTab = ref('materials')
const course = ref<any>(null)
const materials = ref<any[]>([])
const students = ref<any[]>([])
const isLoading = ref(true)
const showAddMaterial = ref(false)
const uploading = ref(false)
const dragOver = ref(false)
const selectedFile = ref<File | null>(null)
const uploadTitle = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const keyCopied = ref(false)
const generatingKey = ref(false)

const generateKey = async () => {
  generatingKey.value = true
  try {
    const res = await api.post(`courses/${courseId.value}/generate_key/`)
    course.value.enrollment_key = res.data.enrollment_key
  } catch (err) { console.error(err) } finally { generatingKey.value = false }
}

const copyKey = () => {
  if (course.value?.enrollment_key) {
    navigator.clipboard.writeText(course.value.enrollment_key)
    keyCopied.value = true
    setTimeout(() => keyCopied.value = false, 2000)
  }
}

const tabs = [
  { id: 'materials', name: 'Materials', icon: FileText },
  { id: 'roster', name: 'Roster', icon: Users },
  { id: 'live', name: 'Live Class', icon: Video },
  { id: 'attendance', name: 'Attendance', icon: ClipboardCheck },
  { id: 'assignments', name: 'Assignments', icon: FolderOpen },
  { id: 'grades', name: 'Grades', icon: GraduationCap },
  { id: 'quizzes', name: 'Quizzes', icon: BookOpen },
  { id: 'settings', name: 'Settings', icon: Settings },
]

const fetchCourseData = async () => {
  isLoading.value = true
  try {
    const [courseRes, materialsRes, enrollmentsRes] = await Promise.all([
      api.get(`courses/${courseId.value}/`),
      api.get('materials/', { params: { course: courseId.value } }),
      api.get('enrollments/', { params: { course: courseId.value } }),
    ])
    course.value = courseRes.data
    materials.value = materialsRes.data
    students.value = enrollmentsRes.data.map((e: any) => e.student)
  } catch (error) {
    console.error("Error loading course data:", error)
  } finally {
    isLoading.value = false
  }
}

const handleDrop = (e: DragEvent) => {
  dragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) {
    selectedFile.value = file
    if (!uploadTitle.value) uploadTitle.value = file.name.replace(/\.[^/.]+$/, '')
  }
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    selectedFile.value = file
    if (!uploadTitle.value) uploadTitle.value = file.name.replace(/\.[^/.]+$/, '')
  }
}

const removeSelectedFile = () => {
  selectedFile.value = null
}

const handleUpload = async () => {
  if (!selectedFile.value || !uploadTitle.value.trim()) return
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('course', String(courseId.value))
    formData.append('title', uploadTitle.value)
    formData.append('file', selectedFile.value)
    formData.append('file_type', selectedFile.value.name.split('.').pop()?.toLowerCase() || '')
    await api.post('materials/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    uploadTitle.value = ''
    selectedFile.value = null
    showAddMaterial.value = false
    const res = await api.get('materials/', { params: { course: courseId.value } })
    materials.value = res.data
  } catch (error) {
    console.error("Error uploading material:", error)
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchCourseData()
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
              <button @click="router.push({ name: 'dashboard' })" class="mr-4 text-gray-400 hover:text-indigo-600 transition-colors">
                <ArrowLeft class="h-6 w-6" />
              </button>
              <div v-if="course">
                <h1 class="text-xl font-bold text-gray-900 leading-tight">{{ course.title }}</h1>
                <p class="text-xs text-gray-500 font-medium">{{ course.course_code }} • {{ students.length }} Students</p>
              </div>
              <div v-else>
                <h1 class="text-xl font-bold text-gray-900 leading-tight">Loading...</h1>
              </div>
            </div>
          </div>

          <div class="flex space-x-8">
            <button v-for="tab in tabs" :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                activeTab === tab.id
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                'whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors'
              ]">
              <component :is="tab.icon" :class="[activeTab === tab.id ? 'text-indigo-600' : 'text-gray-400', 'h-4 w-4 mr-2']" />
              {{ tab.name }}
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">

        <div v-if="isLoading" class="text-center py-16 text-gray-500">
          Loading course data...
        </div>

        <template v-else>

          <!-- MATERIALS TAB -->
          <div v-show="activeTab === 'materials'" class="animate-fade-in max-w-4xl">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-lg font-bold text-gray-900">Course Materials</h2>
              <button @click="showAddMaterial = !showAddMaterial"
                class="flex items-center text-sm font-medium text-white bg-indigo-600 px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-colors">
                <UploadCloud class="h-4 w-4 mr-2" /> Upload Material
              </button>
            </div>

            <div v-if="showAddMaterial" class="bg-white rounded-xl shadow-sm border border-indigo-200 mb-6 overflow-hidden">
              <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
                <h3 class="text-sm font-bold text-gray-900">Upload Material</h3>
                <button @click="showAddMaterial = false" class="text-gray-400 hover:text-gray-600">
                  <X class="h-4 w-4" />
                </button>
              </div>
              <div class="p-5 space-y-4">

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
                  <input v-model="uploadTitle" type="text" placeholder="e.g. Lecture 1 Notes"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">File</label>
                  <div @drop.prevent="handleDrop" @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false"
                    :class="[dragOver ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-gray-50 hover:border-indigo-400', 'border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer']"
                    @click="fileInput?.click()">

                    <template v-if="!selectedFile">
                      <UploadCloud class="h-10 w-10 text-gray-300 mx-auto mb-3" />
                      <p class="text-sm font-medium text-gray-700">Drop a file here, or <span class="text-indigo-600">browse</span></p>
                      <p class="text-xs text-gray-400 mt-1">PDF, DOCX, PPT, images — up to 50MB</p>
                    </template>

                    <template v-else>
                      <FileIcon class="h-8 w-8 text-indigo-600 mx-auto mb-2" />
                      <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
                      <p class="text-xs text-gray-400">{{ (selectedFile.size / 1024 / 1024).toFixed(1) }} MB</p>
                      <button @click.stop="removeSelectedFile" class="mt-2 text-xs text-red-600 hover:text-red-800 font-medium">
                        Remove file
                      </button>
                    </template>

                    <input ref="fileInput" type="file" class="hidden" @change="handleFileSelect" accept=".pdf,.docx,.doc,.ppt,.pptx,.xlsx,.xls,.txt,.png,.jpg,.jpeg,.zip" />
                  </div>
                </div>

                <div class="flex justify-end space-x-3">
                  <button @click="showAddMaterial = false" class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">Cancel</button>
                  <button @click="handleUpload" :disabled="uploading || !selectedFile || !uploadTitle.trim()"
                    class="px-6 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg transition-colors shadow-sm">
                    {{ uploading ? 'Uploading...' : 'Upload' }}
                  </button>
                </div>

              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <ul v-if="materials.length" class="divide-y divide-gray-200">
                <li v-for="mat in materials" :key="mat.id" class="p-4 hover:bg-gray-50 flex items-center justify-between">
                  <div class="flex items-center">
                    <div class="h-10 w-10 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center mr-4">
                      <FileText class="h-5 w-5" />
                    </div>
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ mat.title }}</p>
                      <p class="text-xs text-gray-500">{{ mat.file_type || 'Document' }} • Added {{ new Date(mat.uploaded_at).toLocaleDateString() }}</p>
                    </div>
                  </div>
                  <a v-if="mat.file_url" :href="mat.file_url" target="_blank" class="text-indigo-600 hover:text-indigo-800">
                    <Download class="h-4 w-4" />
                  </a>
                </li>
              </ul>
              <div v-else class="p-8 text-center text-gray-500">
                <FileText class="h-10 w-10 text-gray-300 mx-auto mb-2" />
                <p class="text-sm">No materials uploaded yet.</p>
              </div>
            </div>
          </div>

          <!-- ROSTER TAB -->
          <div v-show="activeTab === 'roster'" class="animate-fade-in max-w-4xl">
            <div class="flex justify-between items-center mb-6">
              <h2 class="text-lg font-bold text-gray-900">Enrolled Students ({{ students.length }})</h2>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Student</th>
                    <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Email</th>
                    <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Username</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="s in students" :key="s.id" class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-3 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="h-8 w-8 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm mr-3">
                          {{ s.first_name?.charAt(0) || '?' }}
                        </div>
                        <span class="text-sm font-medium text-gray-900">{{ s.first_name }} {{ s.last_name }}</span>
                      </div>
                    </td>
                    <td class="px-6 py-3 text-sm text-gray-600">{{ s.email }}</td>
                    <td class="px-6 py-3 text-sm text-gray-500">@{{ s.username }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-if="!students.length" class="p-8 text-center text-gray-500">
                <Users class="h-10 w-10 text-gray-300 mx-auto mb-2" />
                <p class="text-sm">No students enrolled yet.</p>
              </div>
            </div>
          </div>

          <!-- ASSIGNMENTS TAB -->
          <div v-show="activeTab === 'assignments'" class="animate-fade-in max-w-4xl">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
              <FolderOpen class="h-12 w-12 text-indigo-400 mx-auto mb-3" />
              <h3 class="text-lg font-bold text-gray-900 mb-2">Assignments</h3>
              <p class="text-sm text-gray-500 mb-6">Create and manage individual & group assignments. Review submissions and grade student work.</p>
              <button @click="router.push(`/course/${courseId}/assignments`)"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm">
                Open Assignments
              </button>
            </div>
          </div>

          <!-- LIVE CLASS TAB -->
          <div v-show="activeTab === 'live'" class="animate-fade-in max-w-4xl">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
              <Video class="h-12 w-12 text-indigo-400 mx-auto mb-3" />
              <h3 class="text-lg font-bold text-gray-900 mb-2">Virtual Classroom</h3>
              <p class="text-sm text-gray-500 mb-6">Schedule live classes, share meeting links, and upload recordings.</p>
              <button @click="router.push(`/course/${courseId}/live`)"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm">
                Open Virtual Classroom
              </button>
            </div>
          </div>

          <!-- ATTENDANCE TAB -->
          <div v-show="activeTab === 'attendance'" class="animate-fade-in max-w-4xl">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
              <ClipboardCheck class="h-12 w-12 text-indigo-400 mx-auto mb-3" />
              <h3 class="text-lg font-bold text-gray-900 mb-2">Attendance Tracker</h3>
              <p class="text-sm text-gray-500 mb-6">Take digital attendance with one-click status toggles and auto-warnings for low attendance.</p>
              <button @click="router.push(`/course/${courseId}/attendance`)"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm">
                Open Attendance Grid
              </button>
            </div>
          </div>

          <!-- GRADES TAB -->
          <div v-show="activeTab === 'grades'" class="animate-fade-in max-w-4xl">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
              <GraduationCap class="h-12 w-12 text-indigo-400 mx-auto mb-3" />
              <h3 class="text-lg font-bold text-gray-900 mb-2">Gradebook & Marksheet</h3>
              <p class="text-sm text-gray-500 mb-6">Manage final marks, track attendance, and export grades.</p>
              <button @click="router.push(`/course/${courseId}/grades`)"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm">
                Open Gradebook
              </button>
            </div>
          </div>

          <!-- QUIZZES TAB -->
          <div v-show="activeTab === 'quizzes'" class="animate-fade-in max-w-4xl">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
              <BookOpen class="h-12 w-12 text-indigo-400 mx-auto mb-3" />
              <h3 class="text-lg font-bold text-gray-900 mb-2">Quiz Manager</h3>
              <p class="text-sm text-gray-500 mb-6">Create and manage quizzes with multiple-choice questions, time limits, and auto-grading.</p>
              <button @click="router.push(`/course/${courseId}/quizzes`)"
                class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-lg font-medium transition-colors shadow-sm">
                Open Quiz Manager
              </button>
            </div>
          </div>

          <!-- SETTINGS TAB -->
          <div v-show="activeTab === 'settings'" class="animate-fade-in max-w-4xl">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div class="px-6 py-5 border-b border-gray-100 flex items-center">
                <Key class="h-5 w-5 text-indigo-600 mr-2" />
                <h3 class="text-base font-bold text-gray-900">Enrollment Key</h3>
              </div>
              <div class="p-6 space-y-5">
                <p class="text-sm text-gray-600">Students must enter this key to enroll in your course. Share it with your class.</p>

                <div v-if="course?.enrollment_key" class="flex items-center space-x-3">
                  <div class="flex-1 bg-gray-100 border border-gray-300 rounded-lg px-4 py-3 font-mono text-lg font-bold tracking-widest text-center text-indigo-700 select-all">
                    {{ course.enrollment_key }}
                  </div>
                  <button @click="copyKey"
                    class="flex items-center px-4 py-3 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700">
                    <Copy class="h-4 w-4 mr-2" />
                    {{ keyCopied ? 'Copied!' : 'Copy' }}
                  </button>
                  <button @click="generateKey" :disabled="generatingKey"
                    class="flex items-center px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors text-sm font-medium">
                    <RefreshCw :class="['h-4 w-4 mr-2', generatingKey ? 'animate-spin' : '']" />
                    Regenerate
                  </button>
                </div>

                <div v-else>
                  <div class="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 text-sm text-amber-800 mb-4">
                    No enrollment key set. Generate one to control student enrollment.
                  </div>
                  <button @click="generateKey" :disabled="generatingKey"
                    class="flex items-center px-5 py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors text-sm font-medium">
                    <Key class="h-4 w-4 mr-2" /> Generate Key
                  </button>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mt-6">
              <div class="px-6 py-5 border-b border-gray-100 flex items-center">
                <FileText class="h-5 w-5 text-indigo-600 mr-2" />
                <h3 class="text-base font-bold text-gray-900">Course Info</h3>
              </div>
              <div class="p-6 space-y-4">
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Title</label>
                  <p class="text-sm text-gray-900 font-medium">{{ course?.title }}</p>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Course Code</label>
                  <p class="text-sm text-gray-900 font-medium">{{ course?.course_code }}</p>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Description</label>
                  <p class="text-sm text-gray-700">{{ course?.description || 'No description' }}</p>
                </div>
              </div>
            </div>
          </div>

        </template>

      </main>
    </div>
  </div>
</template>

<style>
.animate-fade-in {
  animation: fadeIn 0.25s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

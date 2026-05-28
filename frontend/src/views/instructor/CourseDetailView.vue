<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  ArrowLeft, FileText, Users, Menu, Bell, LogOut,
  BookOpen, UploadCloud, Download, GraduationCap, LayoutDashboard,
  Video, ClipboardCheck, X, File as FileIcon, Sparkles, UserCheck,
  FolderOpen, Settings, Key, Copy, RefreshCw, ChevronRight
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const courseId = computed(() => Number(route.params.id))
const activeTab = ref('overview') // Default to the new Overview tab
const course = ref<any>(null)
const materials = ref<any[]>([])
const students = ref<any[]>([])
const isLoading = ref(true)
const mobileMenuOpen = ref(false)
const username = ref(localStorage.getItem('username') || 'Instructor')

// Upload State
const showAddMaterial = ref(false)
const uploading = ref(false)
const dragOver = ref(false)
const selectedFile = ref<File | null>(null)
const uploadTitle = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

// Key State
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

// UPGRADE: Consolidated Tabs!
const tabs = [
  { id: 'overview', name: 'Control Center', icon: LayoutDashboard },
  { id: 'materials', name: 'Materials', icon: FileText },
  { id: 'roster', name: 'Roster', icon: Users },
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

onMounted(() => { fetchCourseData() })
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">

    <InstructorSidebar />

    <div v-if="mobileMenuOpen" class="fixed inset-0 z-50 flex md:hidden">
      <div class="fixed inset-0 bg-gray-900/80 backdrop-blur-sm" @click="mobileMenuOpen = false"></div>
      <div class="relative flex w-full max-w-xs flex-1 flex-col bg-white pt-5 pb-4 shadow-2xl">
        <div class="flex items-center justify-between px-4 mb-6">
          <h1 class="text-xl font-extrabold text-gray-900 tracking-tight">EDUCLOUD <span class="text-indigo-600">2.0</span></h1>
          <button @click="mobileMenuOpen = false" class="text-gray-400 hover:text-gray-600 bg-gray-100 rounded-full p-1"><span class="text-xl leading-none">&times;</span></button>
        </div>
        <nav class="flex-1 px-4 space-y-1">
          <a @click="mobileMenuOpen = false; router.push('/dashboard')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <LayoutDashboard class="w-5 h-5 mr-3 text-gray-400" /> Dashboard
          </a>
          <a @click="mobileMenuOpen = false; router.push('/my-courses')" class="flex items-center px-3 py-3 bg-indigo-50 text-indigo-700 rounded-xl font-bold transition-colors cursor-pointer">
            <BookOpen class="w-5 h-5 mr-3 text-indigo-600" /> My Modules
          </a>
          <a @click="mobileMenuOpen = false; router.push('/attendance')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <UserCheck class="w-5 h-5 mr-3 text-gray-400" /> Attendance
          </a>
          <a @click="mobileMenuOpen = false; router.push('/gradebook')" class="flex items-center px-3 py-3 text-gray-600 hover:bg-gray-50 rounded-xl font-medium transition-colors cursor-pointer">
            <GraduationCap class="w-5 h-5 mr-3 text-gray-400" /> Gradebook
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
          <button @click="router.push('/my-courses')" class="hidden sm:flex items-center text-sm font-bold text-gray-500 hover:text-indigo-600 transition-colors">
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
          <p class="font-medium">Loading classroom environment...</p>
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
                  <p class="text-sm font-bold text-gray-500 mt-1 uppercase tracking-wider">{{ course?.course_code }} • {{ students.length }} Enrolled Students</p>
                </div>
              </div>
            </div>

            <div class="flex space-x-2 overflow-x-auto custom-scrollbar pb-2">
              <button v-for="tab in tabs" :key="tab.id"
                @click="activeTab = tab.id"
                :class="[activeTab === tab.id ? 'bg-gray-900 text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200', 'px-5 py-2 rounded-full font-bold text-sm capitalize transition-all whitespace-nowrap flex items-center']">
                <component :is="tab.icon" :class="[activeTab === tab.id ? 'text-indigo-400' : 'text-gray-400', 'h-4 w-4 mr-2']" />
                {{ tab.name }}
              </button>
            </div>
          </div>

          <div class="p-4 sm:p-8 max-w-6xl mx-auto w-full">

            <div v-show="activeTab === 'overview'" class="animate-fade-in">
              <h2 class="text-lg font-extrabold text-gray-900 mb-4">Module Toolset</h2>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                
                <div @click="router.push(`/course/${courseId}/assignments`)" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group flex flex-col">
                  <div class="h-12 w-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"><FolderOpen class="h-6 w-6"/></div>
                  <h3 class="text-base font-bold text-gray-900">Assignments</h3>
                  <p class="text-xs text-gray-500 mt-1 mb-4">Create dropboxes and grade student project submissions.</p>
                  <div class="mt-auto text-sm font-bold text-indigo-600 flex items-center">Manage <ChevronRight class="h-4 w-4 ml-1" /></div>
                </div>

                <div @click="router.push(`/course/${courseId}/live`)" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group flex flex-col">
                  <div class="h-12 w-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"><Video class="h-6 w-6"/></div>
                  <h3 class="text-base font-bold text-gray-900">Virtual Classroom</h3>
                  <p class="text-xs text-gray-500 mt-1 mb-4">Schedule live lectures and upload video recordings.</p>
                  <div class="mt-auto text-sm font-bold text-indigo-600 flex items-center">Launch <ChevronRight class="h-4 w-4 ml-1" /></div>
                </div>

                <div @click="router.push(`/course/${courseId}/quizzes`)" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group flex flex-col">
                  <div class="h-12 w-12 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"><BookOpen class="h-6 w-6"/></div>
                  <h3 class="text-base font-bold text-gray-900">Assessments</h3>
                  <p class="text-xs text-gray-500 mt-1 mb-4">Build auto-graded quizzes and monitor class performance.</p>
                  <div class="mt-auto text-sm font-bold text-indigo-600 flex items-center">Configure <ChevronRight class="h-4 w-4 ml-1" /></div>
                </div>

                <div @click="router.push(`/course/${courseId}/attendance`)" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group flex flex-col">
                  <div class="h-12 w-12 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"><ClipboardCheck class="h-6 w-6"/></div>
                  <h3 class="text-base font-bold text-gray-900">Attendance Roster</h3>
                  <p class="text-xs text-gray-500 mt-1 mb-4">Track daily presence with one-click toggles.</p>
                  <div class="mt-auto text-sm font-bold text-indigo-600 flex items-center">Record <ChevronRight class="h-4 w-4 ml-1" /></div>
                </div>

                <div @click="router.push(`/course/${courseId}/grades`)" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 hover:shadow-md hover:border-indigo-200 transition-all cursor-pointer group flex flex-col">
                  <div class="h-12 w-12 bg-rose-50 text-rose-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform"><GraduationCap class="h-6 w-6"/></div>
                  <h3 class="text-base font-bold text-gray-900">Master Gradebook</h3>
                  <p class="text-xs text-gray-500 mt-1 mb-4">Calculate final marks and export official spreadsheets.</p>
                  <div class="mt-auto text-sm font-bold text-indigo-600 flex items-center">Review <ChevronRight class="h-4 w-4 ml-1" /></div>
                </div>
              </div>
            </div>

            <div v-show="activeTab === 'materials'" class="animate-fade-in max-w-4xl">
              <div class="flex justify-between items-center mb-6">
                <h2 class="text-lg font-extrabold text-gray-900">Course Resources</h2>
                <button @click="showAddMaterial = !showAddMaterial"
                  class="flex items-center text-sm font-bold text-white bg-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
                  <UploadCloud class="h-4 w-4 mr-2" /> Upload Material
                </button>
              </div>

              <div v-if="showAddMaterial" class="bg-white rounded-2xl shadow-sm border border-indigo-200 mb-6 overflow-hidden">
                <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between bg-indigo-50/50">
                  <h3 class="text-sm font-bold text-indigo-900">Upload New File</h3>
                  <button @click="showAddMaterial = false" class="text-gray-400 hover:text-gray-600 bg-white rounded-full p-1"><X class="h-4 w-4" /></button>
                </div>
                <div class="p-5">
                  <div class="mb-4">
                    <label class="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-1">Display Title</label>
                    <input v-model="uploadTitle" type="text" placeholder="e.g. Chapter 1 Slides"
                      class="w-full border-2 border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:ring-0 focus:border-indigo-600 outline-none transition-colors" />
                  </div>

                  <div class="mb-5">
                    <label class="block text-xs font-bold text-gray-600 uppercase tracking-wider mb-1">File Attachment</label>
                    <div @drop.prevent="handleDrop" @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false"
                      :class="[dragOver ? 'border-indigo-500 bg-indigo-50' : 'border-gray-200 bg-gray-50 hover:border-indigo-400', 'border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer']"
                      @click="fileInput?.click()">
                      <template v-if="!selectedFile">
                        <UploadCloud class="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <p class="text-sm font-bold text-gray-700">Drag & drop or <span class="text-indigo-600">click to browse</span></p>
                        <p class="text-xs text-gray-400 mt-1">PDF, DOCX, PPT, XLSX, ZIP (Max 50MB)</p>
                      </template>
                      <template v-else>
                        <FileIcon class="h-8 w-8 text-indigo-600 mx-auto mb-2" />
                        <p class="text-sm font-bold text-gray-900">{{ selectedFile.name }}</p>
                        <p class="text-xs text-gray-500 mt-1">{{ (selectedFile.size / 1024 / 1024).toFixed(1) }} MB</p>
                        <button @click.stop="selectedFile = null" class="mt-3 px-3 py-1 bg-red-50 text-xs text-red-600 rounded-md font-bold hover:bg-red-100">Remove</button>
                      </template>
                      <input ref="fileInput" type="file" class="hidden" @change="handleFileSelect" />
                    </div>
                  </div>

                  <div class="flex justify-end space-x-3 pt-4 border-t border-gray-100">
                    <button @click="showAddMaterial = false" class="px-5 py-2.5 text-sm font-bold text-gray-700 hover:bg-gray-100 rounded-xl transition-colors">Cancel</button>
                    <button @click="handleUpload" :disabled="uploading || !selectedFile || !uploadTitle.trim()"
                      class="px-6 py-2.5 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-xl transition-all shadow-sm">
                      {{ uploading ? 'Uploading...' : 'Publish to Class' }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <ul v-if="materials.length" class="divide-y divide-gray-50">
                  <li v-for="mat in materials" :key="mat.id" class="p-4 hover:bg-gray-50 flex items-center justify-between group transition-colors">
                    <div class="flex items-center space-x-4">
                      <div class="h-10 w-10 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center shrink-0">
                        <FileText class="h-5 w-5" />
                      </div>
                      <div>
                        <p class="text-sm font-bold text-gray-900 group-hover:text-indigo-700 transition-colors">{{ mat.title }}</p>
                        <p class="text-xs font-medium text-gray-500 mt-0.5">{{ mat.file_type || 'Document' }} • Uploaded {{ new Date(mat.uploaded_at).toLocaleDateString() }}</p>
                      </div>
                    </div>
                    <a v-if="mat.file_url" :href="mat.file_url" target="_blank" class="px-3 py-1.5 bg-white border border-gray-200 text-gray-600 hover:text-indigo-600 hover:border-indigo-200 rounded-lg text-xs font-bold flex items-center transition-all shadow-sm">
                      <Download class="h-3.5 w-3.5 mr-1.5" /> Download
                    </a>
                  </li>
                </ul>
                <div v-else class="p-12 text-center text-gray-500 flex flex-col items-center">
                  <div class="h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                    <FileText class="h-8 w-8 text-gray-300" />
                  </div>
                  <p class="text-sm font-bold text-gray-900">No materials uploaded.</p>
                  <p class="text-xs text-gray-500 mt-1">Students cannot see any files for this module yet.</p>
                </div>
              </div>
            </div>

            <div v-show="activeTab === 'roster'" class="animate-fade-in max-w-5xl">
              <div class="flex justify-between items-center mb-6">
                <h2 class="text-lg font-extrabold text-gray-900">Official Roster</h2>
                <span class="bg-indigo-100 text-indigo-700 text-xs font-bold px-3 py-1 rounded-full">{{ students.length }} Enrolled</span>
              </div>
              
              <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-100">
                    <thead class="bg-gray-50/50">
                      <tr>
                        <th class="px-6 py-4 text-left text-[11px] font-extrabold text-gray-500 uppercase tracking-wider">Student Name</th>
                        <th class="px-6 py-4 text-left text-[11px] font-extrabold text-gray-500 uppercase tracking-wider">University Email</th>
                        <th class="px-6 py-4 text-left text-[11px] font-extrabold text-gray-500 uppercase tracking-wider">System ID</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-50">
                      <tr v-for="s in students" :key="s.id" class="hover:bg-gray-50/50 transition-colors">
                        <td class="px-6 py-3 whitespace-nowrap">
                          <div class="flex items-center">
                            <div class="h-8 w-8 bg-gradient-to-tr from-indigo-500 to-purple-500 text-white rounded-full flex items-center justify-center font-bold text-xs mr-3 shadow-sm border border-white">
                              {{ s.first_name?.charAt(0) || '?' }}
                            </div>
                            <span class="text-sm font-bold text-gray-900">{{ s.first_name }} {{ s.last_name }}</span>
                          </div>
                        </td>
                        <td class="px-6 py-3 text-sm font-medium text-gray-600">{{ s.email }}</td>
                        <td class="px-6 py-3 text-sm font-medium text-gray-400">@{{ s.username }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div v-if="!students.length" class="p-12 text-center text-gray-500 flex flex-col items-center">
                  <div class="h-16 w-16 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                    <Users class="h-8 w-8 text-gray-300" />
                  </div>
                  <p class="text-sm font-bold text-gray-900">Roster is empty.</p>
                  <p class="text-xs text-gray-500 mt-1">Students need your Enrollment Key to join.</p>
                </div>
              </div>
            </div>

            <div v-show="activeTab === 'settings'" class="animate-fade-in max-w-3xl">
              
              <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden mb-6">
                <div class="px-6 py-5 border-b border-gray-50 bg-gray-50/50 flex items-center">
                  <Key class="h-5 w-5 text-indigo-600 mr-2" />
                  <h3 class="text-base font-extrabold text-gray-900">Security & Enrollment Key</h3>
                </div>
                <div class="p-6">
                  <p class="text-sm font-medium text-gray-600 mb-5">Students must enter this exact key to officially register for this section. Do not post this publicly.</p>

                  <div v-if="course?.enrollment_key" class="flex flex-col sm:flex-row items-center gap-3">
                    <div class="w-full sm:flex-1 bg-gray-50 border-2 border-gray-200 rounded-xl px-4 py-3 font-mono text-xl font-bold tracking-widest text-center text-indigo-700 select-all">
                      {{ course.enrollment_key }}
                    </div>
                    <div class="flex w-full sm:w-auto gap-2">
                      <button @click="copyKey" class="flex-1 sm:flex-none flex items-center justify-center px-5 py-3 bg-white border-2 border-gray-200 rounded-xl hover:bg-gray-50 hover:border-indigo-300 transition-colors text-sm font-bold text-gray-700">
                        <Copy class="h-4 w-4 mr-2" /> {{ keyCopied ? 'Copied!' : 'Copy' }}
                      </button>
                      <button @click="generateKey" :disabled="generatingKey" class="flex-1 sm:flex-none flex items-center justify-center px-5 py-3 bg-red-50 text-red-700 border-2 border-transparent rounded-xl hover:bg-red-100 disabled:opacity-50 transition-colors text-sm font-bold">
                        <RefreshCw :class="['h-4 w-4 mr-2', generatingKey ? 'animate-spin' : '']" /> Reset
                      </button>
                    </div>
                  </div>

                  <div v-else class="text-center bg-gray-50 border border-gray-200 rounded-xl p-8">
                    <div class="bg-amber-100 text-amber-800 text-xs font-bold px-3 py-1 rounded-full inline-block mb-3">Action Required</div>
                    <h4 class="text-sm font-bold text-gray-900 mb-1">No Enrollment Key Set</h4>
                    <p class="text-xs text-gray-500 mb-4 max-w-sm mx-auto">Generate a key to lock this course and control who can access your materials and roster.</p>
                    <button @click="generateKey" :disabled="generatingKey" class="inline-flex items-center px-6 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors text-sm font-bold shadow-sm">
                      <Key class="h-4 w-4 mr-2" /> Generate Secure Key
                    </button>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="px-6 py-5 border-b border-gray-50 bg-gray-50/50 flex items-center">
                  <FileText class="h-5 w-5 text-indigo-600 mr-2" />
                  <h3 class="text-base font-extrabold text-gray-900">Module Configuration</h3>
                </div>
                <div class="p-6 space-y-5">
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                      <label class="block text-[11px] font-extrabold text-gray-400 uppercase tracking-wider mb-1">Official Title</label>
                      <p class="text-sm text-gray-900 font-bold bg-gray-50 p-3 rounded-xl border border-gray-100">{{ course?.title }}</p>
                    </div>
                    <div>
                      <label class="block text-[11px] font-extrabold text-gray-400 uppercase tracking-wider mb-1">System Code</label>
                      <p class="text-sm text-gray-900 font-bold bg-gray-50 p-3 rounded-xl border border-gray-100">{{ course?.course_code }}</p>
                    </div>
                  </div>
                  <div>
                    <label class="block text-[11px] font-extrabold text-gray-400 uppercase tracking-wider mb-1">Syllabus / Description</label>
                    <div class="text-sm text-gray-700 font-medium bg-gray-50 p-4 rounded-xl border border-gray-100 min-h-[100px] whitespace-pre-wrap">{{ course?.syllabus || course?.description || 'No syllabus text provided.' }}</div>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.custom-scrollbar::-webkit-scrollbar { height: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #e5e7eb; border-radius: 10px; }
.custom-scrollbar:hover::-webkit-scrollbar-thumb { background-color: #d1d5db; }
</style>
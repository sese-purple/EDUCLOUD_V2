<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  BookOpen, Search, Key, CheckCircle, Lock,
  LogIn, X, ChevronRight, GraduationCap, Users
} from 'lucide-vue-next'

const router = useRouter()
const courses = ref<any[]>([])
const isLoading = ref(true)
const searchQuery = ref('')
const showEnrollModal = ref(false)
const enrollKey = ref('')
const enrolling = ref(false)
const selectedCourse = ref<any>(null)
const enrollError = ref('')
const enrollSuccess = ref('')

const filteredCourses = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await api.get('courses/')
    courses.value = res.data
    filteredCourses.value = res.data
  } catch (err) { console.error(err) } finally { isLoading.value = false }
})

const search = () => {
  const q = searchQuery.value.toLowerCase()
  filteredCourses.value = courses.value.filter(c =>
    c.title.toLowerCase().includes(q) ||
    c.course_code?.toLowerCase().includes(q) ||
    c.instructor?.first_name?.toLowerCase().includes(q) ||
    c.instructor?.last_name?.toLowerCase().includes(q)
  )
}

const openEnroll = (course: any) => {
  selectedCourse.value = course
  enrollKey.value = ''
  enrollError.value = ''
  enrollSuccess.value = ''
  showEnrollModal.value = true
}

const confirmEnroll = async () => {
  if (!selectedCourse.value) return
  enrolling.value = true
  enrollError.value = ''
  enrollSuccess.value = ''
  try {
    const res = await api.post(`courses/${selectedCourse.value.id}/enroll/`, {
      enrollment_key: enrollKey.value
    })
    enrollSuccess.value = res.data.detail
    selectedCourse.value.is_enrolled = true
    setTimeout(() => { showEnrollModal.value = false }, 1200)
  } catch (err: any) {
    enrollError.value = err.response?.data?.detail || 'Enrollment failed.'
  } finally { enrolling.value = false }
}

const goToCourse = (course: any) => {
  router.push(`/student/course/${course.id}`)
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <StudentSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0">
        <div class="px-6 h-16 flex items-center justify-between">
          <div class="flex items-center">
            <BookOpen class="h-6 w-6 text-indigo-600 mr-3" />
            <h1 class="text-xl font-bold text-gray-900">My Courses</h1>
          </div>
          <div class="relative w-72">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input v-model="searchQuery" @input="search" placeholder="Search courses..."
              class="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-6">
        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading...</div>

        <template v-else>
          <div v-if="!filteredCourses.length" class="text-center py-16">
            <BookOpen class="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <p class="text-gray-500 font-medium">No courses available</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="course in filteredCourses" :key="course.id"
                 class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all">

              <div class="h-2 bg-gradient-to-r from-indigo-500 to-indigo-700" />

              <div class="p-5">
                <div class="flex items-start justify-between mb-3">
                  <div class="min-w-0 flex-1">
                    <h3 class="text-sm font-bold text-gray-900 truncate">{{ course.title }}</h3>
                    <p class="text-xs text-gray-500 mt-0.5">{{ course.course_code }}</p>
                  </div>
                  <span v-if="course.is_enrolled"
                    class="ml-2 shrink-0 bg-emerald-50 text-emerald-700 text-xs font-medium px-2 py-0.5 rounded-full flex items-center">
                    <CheckCircle class="h-3 w-3 mr-1" /> Enrolled
                  </span>
                </div>

                <p class="text-xs text-gray-500 mb-3 truncate">
                  <GraduationCap class="h-3 w-3 inline mr-1" />
                  {{ course.instructor?.first_name }} {{ course.instructor?.last_name || 'Instructor' }}
                </p>

                <div class="flex items-center justify-between pt-3 border-t border-gray-100">
                  <button v-if="course.is_enrolled"
                    @click="goToCourse(course)"
                    class="text-sm font-medium text-indigo-600 hover:text-indigo-800 flex items-center">
                    Open <ChevronRight class="h-3.5 w-3.5 ml-0.5" />
                  </button>
                  <button v-else
                    @click="openEnroll(course)"
                    class="text-sm font-medium text-amber-600 hover:text-amber-800 flex items-center">
                    <Lock class="h-3.5 w-3.5 mr-1" /> Enroll
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </main>

      <!-- Enroll Modal -->
      <Teleport to="body">
        <div v-if="showEnrollModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
             @click.self="showEnrollModal = false">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 mx-4">
            <div class="flex items-center justify-between mb-5">
              <h3 class="text-lg font-bold text-gray-900 flex items-center">
                <Key class="h-5 w-5 text-indigo-600 mr-2" /> Enroll in Course
              </h3>
              <button @click="showEnrollModal = false" class="text-gray-400 hover:text-gray-600">
                <X class="h-5 w-5" />
              </button>
            </div>

            <p class="text-sm text-gray-600 mb-1">Course:</p>
            <p class="text-base font-bold text-gray-900 mb-4">{{ selectedCourse?.title }}</p>

            <div v-if="enrollSuccess" class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-lg text-sm mb-4">
              <CheckCircle class="h-4 w-4 inline mr-1.5" /> {{ enrollSuccess }}
            </div>

            <template v-if="!enrollSuccess">
              <label class="block text-xs font-medium text-gray-600 mb-1.5">Enrollment Key</label>
              <input v-model="enrollKey" type="text" placeholder="Enter the key provided by your instructor"
                class="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 outline-none mb-1" />
              <p class="text-xs text-gray-400 mb-4">Ask your instructor for the enrollment key to join this course.</p>

              <p v-if="enrollError" class="text-red-600 text-sm mb-3">{{ enrollError }}</p>

              <button @click="confirmEnroll" :disabled="enrolling || !enrollKey.trim()"
                class="w-full py-2.5 bg-indigo-600 text-white font-bold rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-all text-sm flex items-center justify-center">
                <LogIn class="h-4 w-4 mr-2" /> {{ enrolling ? 'Enrolling...' : 'Enroll Now' }}
              </button>
            </template>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

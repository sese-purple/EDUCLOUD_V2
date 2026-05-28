<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  Menu, LayoutDashboard, GraduationCap, BookOpen, TrendingUp, Download,
  ChevronDown, ChevronRight, Star, FileText, Settings, LogOut
} from 'lucide-vue-next'

const router = useRouter()
const courses = ref<any[]>([])
const isLoading = ref(true)
const selectedCourse = ref<number | null>(null)
const grades = ref<any[]>([])
const mobileMenuOpen = ref(false)

onMounted(async () => {
  try {
    const dashRes = await api.get('student-dashboard/')
    courses.value = dashRes.data.courses
  } catch (err) { console.error(err) } finally { isLoading.value = false }
})

const gpa = computed(() => {
  const numeric = courses.value
    .map(c => c.average_grade)
    .filter(g => g !== null && g !== undefined)
  if (!numeric.length) return '0.0'
  const avg = numeric.reduce((a: number, b: number) => a + b, 0) / numeric.length
  return avg.toFixed(2)
})

const loadGrades = async (courseId: number) => {
  selectedCourse.value = courseId
  try {
    const [gradesRes, assignRes] = await Promise.all([
      api.get('grades/', { params: { course: courseId } }),
      api.get('assignments/', { params: { course: courseId } }),
    ])
    grades.value = gradesRes.data
    if (assignRes.data.length) {
      const gradeMap = new Map(grades.value.map((g: any) => [g.student?.id, g]))
      const userId = JSON.parse(localStorage.getItem('user_id') || '0')
      const myGrade = gradeMap.get(userId)
      if (myGrade) {
        grades.value = [myGrade, ...assignRes.data.filter(() => false)]
      }
    }
    grades.value = gradesRes.data
  } catch (err) { console.error(err) }
}

const getGradeForAssignment = (assignmentId: number) => {
  return grades.value.find((g: any) => g.assignment === assignmentId)
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
          <button @click="mobileMenuOpen = true" class="mr-3 md:hidden text-gray-500 hover:text-gray-900 focus:outline-none"><Menu class="h-6 w-6" /></button>
          <GraduationCap class="h-6 w-6 text-indigo-600 mr-3" />
          <h1 class="text-xl font-bold text-gray-900">Marksheet</h1>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-6">
        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading...</div>

        <template v-else>
          <!-- GPA Overview -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-xl p-5 text-white shadow-md">
              <p class="text-indigo-200 text-xs uppercase tracking-wider font-medium">Overall GPA</p>
              <p class="text-3xl font-bold mt-1">{{ gpa }}</p>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <p class="text-xs text-gray-500 uppercase tracking-wider font-medium">Courses Enrolled</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">{{ courses.length }}</p>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <p class="text-xs text-gray-500 uppercase tracking-wider font-medium">Average Attendance</p>
              <p class="text-2xl font-bold text-gray-900 mt-1">
                {{ courses.length ? Math.round(courses.reduce((s: number, c: any) => s + (c.attendance_pct || 0), 0) / courses.length) : 0 }}%
              </p>
            </div>
          </div>

          <!-- Per-Course Grade Cards -->
          <div class="space-y-4">
            <div v-for="course in courses" :key="course.id"
                 class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div @click="loadGrades(course.id)"
                   class="p-5 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors">
                <div class="flex items-center min-w-0">
                  <BookOpen class="h-5 w-5 text-indigo-600 mr-3 shrink-0" />
                  <div class="min-w-0">
                    <p class="text-sm font-bold text-gray-900 truncate">{{ course.title }}</p>
                    <p class="text-xs text-gray-500">{{ course.course_code }} • {{ course.instructor_name }}</p>
                  </div>
                </div>
                <div class="flex items-center space-x-4 shrink-0">
                  <div class="text-right">
                    <p class="text-sm font-bold text-gray-900">{{ course.average_grade ?? '—' }}</p>
                    <p class="text-xs text-gray-500">{{ course.attendance_pct ?? '—' }}% attendance</p>
                  </div>
                  <ChevronRight class="h-4 w-4 text-gray-400" />
                </div>
              </div>

              <!-- Grade Details (expandable) -->
              <div v-if="selectedCourse === course.id" class="border-t border-gray-100">
                <div v-if="grades.length" class="divide-y divide-gray-50">
                  <div v-for="g in grades.filter((g:any) => g.course === course.id || !g.course)" :key="g.id"
                       class="px-5 py-3 flex items-center justify-between text-sm">
                    <div class="flex items-center">
                      <FileText class="h-4 w-4 text-gray-400 mr-2" />
                      <span class="text-gray-700">{{ g.assignment_title || `Grade #${g.id}` }}</span>
                    </div>
                    <div class="flex items-center space-x-3">
                      <span :class="[g.grade !== null && g.grade >= 0 ? 'text-emerald-600 font-bold' : 'text-gray-400']">
                        {{ g.grade !== null ? g.grade : '—' }}
                        <span class="text-gray-400 font-normal">/ {{ g.max_points || '?' }}</span>
                      </span>
                      <Star v-if="g.grade !== null && g.max_points && g.grade >= g.max_points * 0.9"
                            class="h-3.5 w-3.5 text-amber-400" />
                    </div>
                  </div>
                </div>
                <div v-else class="px-5 py-4 text-sm text-gray-400 text-center">No grades available yet.</div>
              </div>
            </div>

            <div v-if="!courses.length" class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-400">
              <GraduationCap class="h-10 w-10 mx-auto mb-2 text-gray-300" />
              <p class="text-sm">You are not enrolled in any courses yet.</p>
            </div>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

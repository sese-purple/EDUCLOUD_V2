<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  GraduationCap, BookOpen, TrendingUp, Download,
  ChevronDown, ChevronRight, Star, FileText
} from 'lucide-vue-next'

const router = useRouter()
const courses = ref<any[]>([])
const isLoading = ref(true)
const selectedCourse = ref<number | null>(null)
const grades = ref<any[]>([])

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
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0">
        <div class="px-6 h-16 flex items-center">
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

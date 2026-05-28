<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import { GraduationCap, BookOpen, Users, ChevronRight, FileText, Download } from 'lucide-vue-next'

const router = useRouter()
const courses = ref<any[]>([])
const isLoading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('instructor-dashboard/')
    courses.value = res.data.courses
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
})

const exportAllGrades = async (courseId: number, courseCode: string) => {
  try {
    const [enrollRes, gradeRes] = await Promise.all([
      api.get('enrollments/', { params: { course: courseId } }),
      api.get('grades/', { params: { course: courseId } }),
    ])
    const students = enrollRes.data.map((e: any) => e.student)
    const grades = gradeRes.data
    const gradeMap = new Map(grades.map((g: any) => [g.student?.id, g.grade]))
    let csv = 'Student,Username,Email,Grade\n'
    students.forEach((s: any) => {
      csv += `${s.first_name} ${s.last_name},${s.username},${s.email},${gradeMap.get(s.id) || ''}\n`
    })
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.setAttribute('download', `${courseCode}_grades.csv`)
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error(err)
  }
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <InstructorSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white border-b border-gray-200 flex items-center px-6 shadow-sm">
        <GraduationCap class="h-5 w-5 text-indigo-600 mr-3" />
        <h2 class="text-lg font-bold text-gray-800">Gradebook Overview</h2>
      </header>
      <main class="flex-1 overflow-y-auto p-8">
        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading courses...</div>
        <template v-else>
          <div v-if="courses.length === 0" class="text-center py-16">
            <BookOpen class="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p class="text-sm text-gray-500">No courses assigned.</p>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            <div v-for="c in courses" :key="c.id"
              class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all">
              <div class="p-5">
                <div class="flex items-center justify-between mb-3">
                  <div class="h-10 w-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                    <span class="text-indigo-700 font-bold text-sm">{{ c.course_code?.split('-')[0] }}</span>
                  </div>
                  <span class="text-xs text-gray-400 flex items-center"><Users class="h-3 w-3 mr-1" />{{ c.students }}</span>
                </div>
                <h3 class="text-sm font-bold text-gray-900 mb-1">{{ c.title }}</h3>
                <p class="text-xs text-gray-500 mb-4">{{ c.course_code }}</p>
                <div class="flex flex-col space-y-2">
                  <button @click="router.push(`/course/${c.id}/grades`)"
                    class="w-full flex items-center justify-between px-3 py-2 bg-indigo-50 text-indigo-700 rounded-lg text-sm font-medium hover:bg-indigo-100 transition-colors">
                    <span class="flex items-center"><GraduationCap class="h-4 w-4 mr-2" />Gradebook</span>
                    <ChevronRight class="h-4 w-4" />
                  </button>
                  <button @click="router.push(`/course/${c.id}/assignments`)"
                    class="w-full flex items-center justify-between px-3 py-2 bg-gray-50 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors">
                    <span class="flex items-center"><FileText class="h-4 w-4 mr-2" />Assignments</span>
                    <ChevronRight class="h-4 w-4" />
                  </button>
                  <button @click="exportAllGrades(c.id, c.course_code)"
                    class="w-full flex items-center justify-between px-3 py-2 bg-gray-50 text-gray-600 rounded-lg text-sm hover:bg-gray-100 transition-colors">
                    <span class="flex items-center"><Download class="h-4 w-4 mr-2" />Export CSV</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

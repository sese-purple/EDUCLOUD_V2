<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  ArrowLeft, GraduationCap, Search, Download,
  Save, Users, FileText
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const courseId = computed(() => Number(route.params.id))
const course = ref<any>(null)
const students = ref<any[]>([])
const grades = ref<any[]>([])
const assignments = ref<any[]>([])
const allSubmissions = ref<any[]>([])
const isLoading = ref(true)
const searchQuery = ref('')
const editingGrades = ref<Record<number, string>>({})

const filteredStudents = computed(() => {
  let list = students.value
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(s =>
      s.first_name?.toLowerCase().includes(q) ||
      s.last_name?.toLowerCase().includes(q) ||
      s.username?.toLowerCase().includes(q)
    )
  }
  return list
})

const getGrade = (studentId: number) => {
  const g = grades.value.find((g: any) => g.student?.id === studentId)
  return g ? g.grade : ''
}

const getAssignmentScore = (studentId: number, assignId: number) => {
  const sub = allSubmissions.value.find(
    (s: any) => s.assignment === assignId && s.student?.id === studentId
  )
  return sub?.grade ?? null
}

const getTotalAssignmentScore = (studentId: number) => {
  let total = 0
  for (const a of assignments.value) {
    const score = getAssignmentScore(studentId, a.id)
    if (score !== null) total += score
  }
  return total
}

const getMaxAssignmentScore = computed(() =>
  assignments.value.reduce((sum, a) => sum + (a.max_points || 0), 0)
)

const fetchGradebook = async () => {
  isLoading.value = true
  try {
    const [courseRes, enrollmentsRes, gradesRes, assignRes, subRes] = await Promise.all([
      api.get(`courses/${courseId.value}/`),
      api.get('enrollments/', { params: { course: courseId.value } }),
      api.get('grades/', { params: { course: courseId.value } }),
      api.get('assignments/', { params: { course: courseId.value } }),
      api.get('submissions/', { params: {} }),
    ])
    course.value = courseRes.data
    students.value = enrollmentsRes.data.map((e: any) => e.student)
    grades.value = gradesRes.data
    assignments.value = assignRes.data
    const assignmentIds = new Set(assignRes.data.map((a: any) => a.id))
    allSubmissions.value = subRes.data.filter((s: any) => assignmentIds.has(s.assignment))

    grades.value.forEach((g: any) => {
      editingGrades.value[g.student.id] = g.grade
    })
  } catch (error) {
    console.error("Error loading gradebook:", error)
  } finally {
    isLoading.value = false
  }
}

const saveGrade = async (studentId: number) => {
  const gradeValue = editingGrades.value[studentId]
  if (!gradeValue) return

  const existing = grades.value.find((g: any) => g.student?.id === studentId)
  try {
    if (existing) {
      await api.patch(`grades/${existing.id}/`, {
        student_id: studentId,
        course_id: courseId.value,
        grade: gradeValue,
      })
    } else {
      const res = await api.post('grades/', {
        student_id: studentId,
        course_id: courseId.value,
        grade: gradeValue,
      })
      grades.value.push(res.data)
    }
  } catch (error) {
    console.error("Error saving grade:", error)
  }
}

const exportGrades = () => {
  let csv = 'Student,Username,Email'
  for (const a of assignments.value) csv += `,${a.title}`
  csv += ',Total,Grade\n'

  filteredStudents.value.forEach((s: any) => {
    let row = `${s.first_name} ${s.last_name},${s.username},${s.email}`
    for (const a of assignments.value) {
      const score = getAssignmentScore(s.id, a.id)
      row += `,${score !== null ? score : ''}`
    }
    row += `,${getTotalAssignmentScore(s.id)},${getGrade(s.id)}\n`
    csv += row
  })

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.setAttribute('download', `${course.value?.course_code || 'grades'}_marksheet.csv`)
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

onMounted(fetchGradebook)
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <InstructorSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0">
        <div class="px-6">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center">
              <button @click="router.push(`/course/${courseId}`)" class="mr-4 text-gray-400 hover:text-indigo-600">
                <ArrowLeft class="h-6 w-6" />
              </button>
              <div>
                <h1 class="text-xl font-bold text-gray-900">Gradebook & Marksheet</h1>
                <p v-if="course" class="text-xs text-gray-500">{{ course.title }} — {{ course.course_code }}</p>
              </div>
            </div>
            <button @click="exportGrades"
              class="flex items-center px-3 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 shadow-sm">
              <Download class="h-4 w-4 mr-2" /> Export CSV
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">
        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading gradebook...</div>

        <template v-else>
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-3">
              <Users class="h-5 w-5 text-gray-400" />
              <span class="text-sm text-gray-600">{{ students.length }} students</span>
              <span class="text-sm text-gray-400 mx-2">|</span>
              <FileText class="h-4 w-4 text-gray-400" />
              <span class="text-sm text-gray-600">{{ assignments.length }} assignments</span>
            </div>
            <div class="relative max-w-xs">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input v-model="searchQuery" type="text" placeholder="Search students..."
                class="w-full pl-9 pr-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500">
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10 min-w-[160px]">Student</th>
                  <th v-for="a in assignments" :key="'a-'+a.id"
                    class="px-3 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider min-w-[80px] border-l border-gray-100">
                    <div class="text-[10px]">{{ a.title }}</div>
                    <div class="text-[10px] text-gray-400">/{{ a.max_points }}</div>
                  </th>
                  <th class="px-3 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider min-w-[60px] border-l border-gray-100">Total</th>
                  <th class="px-3 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider min-w-[80px] border-l border-gray-200">Final Grade</th>
                  <th class="px-3 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider min-w-[60px] border-l border-gray-200"></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="s in filteredStudents" :key="s.id" class="hover:bg-gray-50 transition-colors">
                  <td class="px-4 py-2.5 whitespace-nowrap sticky left-0 bg-white z-10">
                    <div class="flex items-center">
                      <div class="h-8 w-8 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm mr-3 shrink-0">
                        {{ s.first_name?.charAt(0) || '?' }}
                      </div>
                      <div>
                        <p class="text-sm font-medium text-gray-900">{{ s.first_name }} {{ s.last_name }}</p>
                        <p class="text-xs text-gray-500">@{{ s.username }}</p>
                      </div>
                    </div>
                  </td>
                  <td v-for="a in assignments" :key="'s-'+s.id+'-'+a.id"
                    class="px-3 py-2.5 text-center text-sm border-l border-gray-100">
                    <span v-if="getAssignmentScore(s.id, a.id) !== null"
                      class="font-mono text-gray-900">{{ getAssignmentScore(s.id, a.id) }}</span>
                    <span v-else class="text-gray-300">—</span>
                  </td>
                  <td class="px-3 py-2.5 text-center text-sm font-bold font-mono border-l border-gray-100">
                    {{ getTotalAssignmentScore(s.id) }}
                    <span v-if="getMaxAssignmentScore" class="text-gray-400 font-normal">/{{ getMaxAssignmentScore }}</span>
                  </td>
                  <td class="px-3 py-2.5 text-center border-l border-gray-200">
                    <input v-model="editingGrades[s.id]"
                      type="text" placeholder="—"
                      class="w-20 px-2 py-1 border border-gray-300 rounded text-sm text-center font-mono focus:ring-indigo-500 focus:border-indigo-500"
                      :class="getGrade(s.id) ? 'border-gray-300' : 'border-dashed border-gray-400'" />
                  </td>
                  <td class="px-3 py-2.5 text-right border-l border-gray-200">
                    <button @click="saveGrade(s.id)"
                      class="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center ml-auto">
                      <Save class="h-4 w-4 mr-1" /> Save
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="!students.length" class="p-8 text-center text-gray-500">
              <GraduationCap class="h-10 w-10 text-gray-300 mx-auto mb-2" />
              <p class="text-sm">No students enrolled in this course.</p>
            </div>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

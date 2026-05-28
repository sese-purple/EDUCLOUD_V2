<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  GraduationCap, Search, Download, Users, FileText, BookOpen, ChevronDown, Check, X
} from 'lucide-vue-next'

const router = useRouter()

const courses = ref<any[]>([])
const selectedCourseId = ref<number | null>(null)
const students = ref<any[]>([])
const assignments = ref<any[]>([])
const allSubmissions = ref<any[]>([])
const isLoading = ref(false)
const searchQuery = ref('')
const savingCells = ref<Set<string>>(new Set())
const editedCells = ref<Record<string, string>>({})
const editFocus = ref<{ studentId: number; assignId: number } | null>(null)

const fetchCourses = async () => {
  try {
    const res = await api.get('instructor-dashboard/')
    courses.value = res.data.courses || []
    if (courses.value.length === 1) selectedCourseId.value = courses.value[0].id
  } catch { }
}

const fetchGradebook = async () => {
  if (!selectedCourseId.value) { students.value = []; assignments.value = []; allSubmissions.value = []; return }
  isLoading.value = true
  try {
    const [enrollRes, assignRes, subRes] = await Promise.all([
      api.get('enrollments/', { params: { course: selectedCourseId.value } }),
      api.get('assignments/', { params: { course: selectedCourseId.value } }),
      api.get('submissions/', { params: {} }),
    ])
    students.value = enrollRes.data.map((e: any) => e.student)
    assignments.value = assignRes.data
    const assignIds = new Set(assignRes.data.map((a: any) => a.id))
    allSubmissions.value = subRes.data.filter((s: any) => assignIds.has(s.assignment))
  } catch { }
  finally { isLoading.value = false }
}

const getSubmission = (studentId: number, assignId: number) =>
  allSubmissions.value.find((s: any) => s.assignment === assignId && s.student?.id === studentId)

const getScore = (studentId: number, assignId: number) => {
  const sub = getSubmission(studentId, assignId)
  return sub?.grade ?? null
}

const cellKey = (studentId: number, assignId: number) => `${studentId}_${assignId}`

const editingValue = (studentId: number, assignId: number) => {
  const key = cellKey(studentId, assignId)
  return editedCells.value[key] !== undefined ? editedCells.value[key] : getScore(studentId, assignId)?.toString() ?? ''
}

const startEdit = (studentId: number, assignId: number) => {
  editFocus.value = { studentId, assignId }
}

const handleCellKeydown = async (e: KeyboardEvent, studentId: number, assignId: number) => {
  if (e.key === 'Enter' || e.key === 'Tab') {
    e.preventDefault()
    await saveCell(studentId, assignId)
    if (e.key === 'Tab') {
      const idx = assignments.value.findIndex((a: any) => a.id === assignId)
      if (idx < assignments.value.length - 1) {
        editFocus.value = { studentId, assignId: assignments.value[idx + 1].id }
        await nextTick()
        document.getElementById(`cell-${studentId}-${assignments.value[idx + 1].id}`)?.focus()
      } else {
        editFocus.value = null
      }
    } else {
      editFocus.value = null
    }
  }
  if (e.key === 'Escape') {
    const key = cellKey(studentId, assignId)
    delete editedCells.value[key]
    editFocus.value = null
  }
}

const saveCell = async (studentId: number, assignId: number) => {
  const key = cellKey(studentId, assignId)
  const value = editedCells.value[key]
  if (value === undefined || value === getScore(studentId, assignId)?.toString()) {
    delete editedCells.value[key]
    return
  }
  savingCells.value.add(key)
  try {
    const sub = getSubmission(studentId, assignId)
    const payload = { grade: Number(value), assignment: assignId, student_id: studentId }
    if (sub) {
      await api.patch(`submissions/${sub.id}/`, payload)
      sub.grade = Number(value)
    } else {
      const res = await api.post('submissions/', payload)
      allSubmissions.value.push(res.data)
    }
    delete editedCells.value[key]
  } catch { }
  finally { savingCells.value.delete(key) }
}

const handleInput = (studentId: number, assignId: number, val: string) => {
  editedCells.value[cellKey(studentId, assignId)] = val
}

const getTotalScore = (studentId: number) => {
  let total = 0
  for (const a of assignments.value) {
    const score = getScore(studentId, a.id)
    if (score !== null) total += score
  }
  return total
}

const maxPoints = computed(() =>
  assignments.value.reduce((sum, a) => sum + (a.max_points || 0), 0)
)

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

const selectedCourse = computed(() => courses.value.find(c => c.id === selectedCourseId.value))

const exportGrades = () => {
  let csv = 'Student,Username,Email'
  for (const a of assignments.value) csv += `,${a.title}`
  csv += ',Total,Grade\n'
  filteredStudents.value.forEach((s: any) => {
    let row = `${s.first_name} ${s.last_name},${s.username},${s.email}`
    for (const a of assignments.value) {
      const score = getScore(s.id, a.id)
      row += `,${score !== null ? score : ''}`
    }
    row += `,${getTotalScore(s.id)},${getTotalScore(s.id)}${maxPoints.value ? '/' + maxPoints.value : ''}\n`
    csv += row
  })
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.setAttribute('download', `${selectedCourse.value?.course_code || 'gradebook'}_marksheet.csv`)
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

watch(selectedCourseId, fetchGradebook)
onMounted(fetchCourses)
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <InstructorSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0 shadow-sm">
        <div class="px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <GraduationCap class="h-5 w-5 text-indigo-600" />
              <h1 class="text-xl font-bold text-gray-900">Master Gradebook</h1>
              <div class="h-6 w-px bg-gray-200" />
              <select v-model.number="selectedCourseId"
                class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none min-w-[200px]">
                <option :value="null" disabled>Select a course...</option>
                <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.course_code }} — {{ c.title }}</option>
              </select>
            </div>
            <div class="flex items-center gap-3">
              <div class="text-sm text-gray-500 flex items-center gap-3">
                <span class="flex items-center"><Users class="h-3.5 w-3.5 mr-1" />{{ students.length }} students</span>
                <span class="flex items-center"><FileText class="h-3.5 w-3.5 mr-1" />{{ assignments.length }} items</span>
              </div>
              <button @click="exportGrades" :disabled="!assignments.length"
                class="flex items-center px-4 py-1.5 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm">
                <Download class="h-4 w-4 mr-1.5" /> Export CSV
              </button>
            </div>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-hidden flex flex-col">
        <div v-if="!selectedCourseId" class="flex flex-col items-center justify-center h-full text-gray-400">
          <div class="bg-gray-100 rounded-full p-6 mb-4">
            <GraduationCap class="h-12 w-12" />
          </div>
          <p class="text-lg font-medium text-gray-500">Select a course to view gradebook</p>
          <p class="text-sm text-gray-400 mt-1">Choose from the dropdown above</p>
        </div>

        <div v-else-if="isLoading" class="flex items-center justify-center h-full text-gray-500">
          Loading gradebook...
        </div>

        <template v-else>
          <div class="px-6 py-3 flex items-center justify-between bg-white border-b border-gray-200">
            <div class="relative max-w-xs">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
              <input v-model="searchQuery" type="text" placeholder="Search students..."
                class="w-64 pl-8 pr-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
            </div>
            <div class="text-xs text-gray-400">
              <kbd class="px-1.5 py-0.5 bg-gray-100 border border-gray-200 rounded text-[10px] font-mono">Enter</kbd> save &amp; next
              <kbd class="px-1.5 py-0.5 bg-gray-100 border border-gray-200 rounded text-[10px] font-mono ml-2">Tab</kbd> next column
              <kbd class="px-1.5 py-0.5 bg-gray-100 border border-gray-200 rounded text-[10px] font-mono ml-2">Esc</kbd> undo
            </div>
          </div>

          <div class="flex-1 overflow-auto p-0">
            <div class="bg-white border-t border-gray-200 inline-block min-w-full">
              <table class="min-w-full divide-y divide-gray-200" style="table-layout: fixed;">
                <thead class="bg-gray-50 sticky top-0 z-20">
                  <tr>
                    <th class="px-3 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-30 min-w-[200px] w-[200px] border-r border-gray-200">Student</th>
                    <th v-for="a in assignments" :key="a.id"
                      class="px-2 py-3 text-center text-[10px] font-bold text-gray-500 uppercase tracking-wider min-w-[90px] w-[90px] border-r border-gray-100">
                      <div class="truncate" :title="a.title">{{ a.title }}</div>
                      <div class="text-[9px] text-gray-400 font-normal">/{{ a.max_points || '—' }}</div>
                    </th>
                    <th class="px-3 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider min-w-[100px] w-[100px] bg-gray-50 sticky right-0 z-30 border-l-2 border-gray-300">
                      Total
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="s in filteredStudents" :key="s.id" class="hover:bg-blue-50/30 transition-colors">
                    <td class="px-3 py-1.5 whitespace-nowrap text-sm sticky left-0 bg-white z-10 border-r border-gray-200">
                      <div class="flex items-center gap-2">
                        <div class="h-7 w-7 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-xs shrink-0">
                          {{ s.first_name?.charAt(0) || '?' }}
                        </div>
                        <div class="truncate">
                          <p class="text-sm font-medium text-gray-900 truncate">{{ s.first_name }} {{ s.last_name }}</p>
                          <p class="text-[10px] text-gray-500 truncate">@{{ s.username }}</p>
                        </div>
                      </div>
                    </td>
                    <td v-for="a in assignments" :key="a.id"
                      class="px-2 py-1 text-center border-r border-gray-100 relative">
                      <div v-if="editFocus?.studentId === s.id && editFocus?.assignId === a.id">
                        <input
                          :id="`cell-${s.id}-${a.id}`"
                          :value="editingValue(s.id, a.id)"
                          @input="handleInput(s.id, a.id, ($event.target as HTMLInputElement).value)"
                          @keydown="handleCellKeydown($event, s.id, a.id)"
                          @blur="saveCell(s.id, a.id)"
                          type="number" step="0.5"
                          class="w-full px-1 py-0.5 text-sm text-center font-mono border-2 border-indigo-500 rounded outline-none bg-white shadow-sm"
                          autofocus />
                      </div>
                      <div v-else
                        @click="startEdit(s.id, a.id)"
                        class="w-full px-1 py-1.5 cursor-pointer rounded transition-colors min-h-[2rem] flex items-center justify-center">
                        <span v-if="getScore(s.id, a.id) !== null"
                          class="font-mono text-sm text-gray-900">{{ getScore(s.id, a.id) }}</span>
                        <span v-else class="text-gray-300 text-xs">—</span>
                      </div>
                      <div v-if="savingCells.has(cellKey(s.id, a.id))"
                        class="absolute inset-0 bg-white/60 flex items-center justify-center z-10">
                        <div class="h-4 w-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
                      </div>
                    </td>
                    <td class="px-3 py-1.5 text-center sticky right-0 bg-white z-10 border-l-2 border-gray-300 font-bold">
                      <div class="text-sm font-mono text-gray-900">{{ getTotalScore(s.id) }}</div>
                      <div v-if="maxPoints" class="text-[10px] text-gray-400">/{{ maxPoints }}</div>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="!students.length" class="p-8 text-center text-gray-500">
                <GraduationCap class="h-10 w-10 mx-auto mb-2 text-gray-300" />
                <p class="text-sm">No students enrolled in this course.</p>
              </div>
              <div v-if="students.length && !assignments.length" class="p-8 text-center text-gray-400">
                <FileText class="h-10 w-10 mx-auto mb-2" />
                <p class="text-sm">No assignments yet. Create assignments from the course page to populate the gradebook.</p>
              </div>
            </div>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

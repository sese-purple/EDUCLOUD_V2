<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  ArrowLeft, Plus, Pencil, Trash2, X,
  BookOpen, Clock, Download, CheckCircle,
  User, Users, Shuffle, FolderOpen
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const courseId = computed(() => Number(route.params.id))

interface Submission {
  id: number
  student: { id: number; first_name: string; last_name: string; username: string }
  group: number | null
  file: string
  submitted_at: string
  grade: number | null
  feedback: string
  is_late: boolean
  graded_at: string | null
  student_name: string | null
}

interface Assignment {
  id: number
  title: string
  description: string
  due_date: string | null
  max_points: number
  assignment_type: string
  file: string
  created_by: number
  created_at: string
  submissions: Submission[]
}

const assignments = ref<Assignment[]>([])
const course = ref<any>(null)
const students = ref<any[]>([])
const groups = ref<any[]>([])
const isLoading = ref(true)
const showForm = ref(false)
const editingAssignment = ref<Assignment | null>(null)
const saving = ref(false)
const selectedFile = ref<File | null>(null)
const uploadTitle = ref('')

const form = ref({
  title: '',
  description: '',
  due_date: '',
  max_points: 100,
  assignment_type: 'individual',
  groups: [] as number[],
})

const openCreate = () => {
  editingAssignment.value = null
  form.value = { title: '', description: '', due_date: '', max_points: 100, assignment_type: 'individual', groups: [] }
  selectedFile.value = null
  uploadTitle.value = ''
  showForm.value = true
}

const openEdit = (a: Assignment) => {
  editingAssignment.value = a
  form.value = {
    title: a.title,
    description: a.description,
    due_date: a.due_date ? a.due_date.slice(0, 16) : '',
    max_points: a.max_points,
    assignment_type: a.assignment_type,
    groups: (a as any).groups || [],
  }
  selectedFile.value = null
  uploadTitle.value = ''
  showForm.value = true
}

const onFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) selectedFile.value = input.files[0]
}

const saveAssignment = async () => {
  if (!form.value.title.trim()) return
  saving.value = true
  try {
    const data = new FormData()
    data.append('course', String(courseId.value))
    data.append('title', form.value.title)
    data.append('description', form.value.description)
    data.append('max_points', String(form.value.max_points))
    data.append('assignment_type', form.value.assignment_type)
    if (form.value.due_date) data.append('due_date', form.value.due_date)
    if (selectedFile.value) data.append('file', selectedFile.value)
    if (form.value.assignment_type === 'group' && form.value.groups.length) {
      for (const gid of form.value.groups) data.append('groups', String(gid))
    }

    if (editingAssignment.value?.id) {
      await api.patch(`assignments/${editingAssignment.value.id}/`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } else {
      await api.post('assignments/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    showForm.value = false
    await fetchData()
  } catch (err) {
    console.error(err)
  } finally {
    saving.value = false
  }
}

const deleteAssignment = async (a: Assignment) => {
  try {
    await api.delete(`assignments/${a.id}/`)
    await fetchData()
  } catch (err) {
    console.error(err)
  }
}

const confirmDelete = ref<number | null>(null)
const expandedSubmissions = ref<Record<number, boolean>>({})

const fetchData = async () => {
  isLoading.value = true
  try {
    const [courseRes, assignRes, enrollRes, groupsRes] = await Promise.all([
      api.get(`courses/${courseId.value}/`),
      api.get('assignments/', { params: { course: courseId.value } }),
      api.get('enrollments/', { params: { course: courseId.value } }),
      api.get('groups/', { params: { course: courseId.value } }),
    ])
    course.value = courseRes.data
    assignments.value = assignRes.data
    groups.value = groupsRes.data
    students.value = enrollRes.data.map((e: any) => e.student)

    for (const a of assignments.value) {
      const subRes = await api.get('submissions/', { params: { assignment: a.id } })
      a.submissions = subRes.data
    }
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const submitGrade = async (sub: Submission) => {
  try {
    await api.patch(`submissions/${sub.id}/`, {
      grade: sub.grade,
      feedback: sub.feedback,
      graded_at: new Date().toISOString(),
    })
  } catch (err) {
    console.error(err)
  }
}

const nGroups = ref(2)
const newGroupName = ref('')
const showGroups = ref(false)

const createRandomGroups = async () => {
  if (!students.value.length) return alert('No students enrolled.')
  try {
    const res = await api.post('groups/random_groups/', {
      course: courseId.value,
      n_groups: nGroups.value,
    })
    groups.value = res.data
  } catch (err) { console.error(err) }
}

const addGroup = async () => {
  if (!newGroupName.value.trim()) return
  try {
    const res = await api.post('groups/', { course: courseId.value, name: newGroupName.value })
    groups.value.push(res.data)
    newGroupName.value = ''
  } catch (err) { console.error(err) }
}

const deleteGroup = async (g: any) => {
  try {
    await api.delete(`groups/${g.id}/`)
    groups.value = groups.value.filter((x: any) => x.id !== g.id)
  } catch (err) { console.error(err) }
}

const unassignedStudents = computed(() => {
  const assigned = new Set<number>()
  for (const g of groups.value) {
    for (const m of g.members || []) assigned.add(m.id)
  }
  return students.value.filter(s => !assigned.has(s.id))
})

onMounted(fetchData)
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <InstructorSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0">
        <div class="px-6">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center">
              <button @click="router.push(`/course/${courseId}`)" class="mr-4 text-gray-400 hover:text-indigo-600"><ArrowLeft class="h-6 w-6" /></button>
              <div>
                <h1 class="text-xl font-bold text-gray-900">Assignments</h1>
                <p v-if="course" class="text-xs text-gray-500">{{ course.title }}</p>
              </div>
            </div>
            <button @click="openCreate" class="flex items-center text-sm font-medium text-white bg-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-700">
              <Plus class="h-4 w-4 mr-2" /> New Assignment
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">

        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading...</div>

        <template v-else>

          <!-- Form -->
          <div v-if="showForm" class="mb-8 bg-white rounded-xl shadow-sm border border-indigo-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
              <h3 class="text-lg font-bold text-gray-900">{{ editingAssignment ? 'Edit' : 'New' }} Assignment</h3>
              <button @click="showForm = false"><X class="h-5 w-5 text-gray-400" /></button>
            </div>
            <div class="p-6 space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
                  <input v-model="form.title" type="text" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select v-model="form.assignment_type" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none">
                    <option value="individual">Individual</option>
                    <option value="group">Group</option>
                  </select>
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea v-model="form.description" rows="3" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                  <input v-model="form.due_date" type="datetime-local" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Max Points</label>
                  <input v-model.number="form.max_points" type="number" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                </div>
              </div>
              <div v-if="form.assignment_type === 'group'" class="bg-indigo-50 rounded-lg p-4">
                <label class="block text-sm font-bold text-indigo-900 mb-2">Assign to Groups</label>
                <div v-if="groups.length" class="grid grid-cols-2 md:grid-cols-3 gap-2">
                  <label v-for="g in groups" :key="g.id"
                    class="flex items-center space-x-2 text-sm text-gray-700 cursor-pointer p-2 rounded hover:bg-indigo-100 transition-colors">
                    <input type="checkbox" :value="g.id" v-model="form.groups"
                      class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                    <span>{{ g.name }}</span>
                  </label>
                </div>
                <p v-else class="text-sm text-indigo-400 italic">No groups yet. Create groups first.</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Attachment (optional)</label>
                <input @change="onFileSelect" type="file" class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100" />
              </div>
              <div class="flex justify-end space-x-3 pt-2">
                <button @click="showForm = false" class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button @click="saveAssignment" :disabled="saving || !form.title.trim()"
                  class="px-6 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg shadow-sm">
                  {{ saving ? 'Saving...' : editingAssignment ? 'Update' : 'Create' }}
                </button>
              </div>
            </div>
          </div>

          <!-- List -->
          <div v-if="!assignments.length && !showForm" class="text-center py-16">
            <BookOpen class="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p class="text-sm text-gray-500">No assignments yet. Create one to get started.</p>
          </div>

          <div v-for="a in assignments" :key="a.id" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-4">
            <div class="px-6 py-4 flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <h3 class="text-base font-bold text-gray-900">{{ a.title }}</h3>
                  <span class="text-xs font-medium px-2 py-0.5 rounded-full"
                    :class="a.assignment_type === 'group' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'">
                    {{ a.assignment_type }}
                  </span>
                  <span v-if="a.submissions" class="text-xs text-gray-400">{{ a.submissions.length }} submissions</span>
                </div>
                <p v-if="a.description" class="text-sm text-gray-500 mt-1">{{ a.description }}</p>
                <div class="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                  <span><Clock class="h-3 w-3 inline mr-1" />{{ a.max_points }} pts</span>
                  <span v-if="a.due_date"><Clock class="h-3 w-3 inline mr-1" />Due {{ new Date(a.due_date).toLocaleString() }}</span>
                </div>
              </div>
              <div class="flex items-center space-x-2 ml-4">
                <a v-if="a.file" :href="a.file" target="_blank" class="p-2 text-gray-400 hover:text-indigo-600 rounded-lg"><Download class="h-4 w-4" /></a>
                <button @click="openEdit(a)" class="p-2 text-gray-400 hover:text-indigo-600 rounded-lg"><Pencil class="h-4 w-4" /></button>
                <button @click="confirmDelete = a.id" class="p-2 text-gray-400 hover:text-red-600 rounded-lg"><Trash2 class="h-4 w-4" /></button>
              </div>
            </div>
            <div v-if="confirmDelete === a.id" class="px-6 py-3 bg-red-50 border-t border-red-200 flex items-center justify-between">
              <span class="text-sm text-red-700 font-medium">Delete this assignment?</span>
              <div class="flex space-x-2">
                <button @click="confirmDelete = null" class="px-3 py-1.5 text-sm text-gray-600 hover:bg-white rounded-lg">Cancel</button>
                <button @click="deleteAssignment(a); confirmDelete = null" class="px-3 py-1.5 text-sm font-medium text-white bg-red-600 rounded-lg">Delete</button>
              </div>
            </div>

            <!-- Submissions -->
            <div v-if="a.submissions?.length" class="border-t border-gray-100">
              <button @click="expandedSubmissions[a.id] = !expandedSubmissions[a.id]"
                class="w-full px-6 py-2.5 text-sm font-medium text-gray-600 hover:bg-gray-50 flex items-center justify-between">
                <span>Submissions ({{ a.submissions.length }})</span>
                <span>{{ expandedSubmissions[a.id] ? '▲' : '▼' }}</span>
              </button>
              <div v-if="expandedSubmissions[a.id]" class="divide-y divide-gray-100">
                <div v-for="sub in a.submissions" :key="sub.id" class="px-6 py-3 flex items-center gap-4 text-sm">
                  <div class="flex-1 flex items-center">
                    <component :is="a.assignment_type === 'group' ? Users : User" class="h-4 w-4 text-gray-400 mr-2" />
                    <span class="font-medium text-gray-900">{{ sub.student_name || sub.student?.first_name + ' ' + sub.student?.last_name }}</span>
                    <span v-if="sub.is_late" class="ml-2 text-xs text-red-600 font-medium">LATE</span>
                    <a v-if="sub.file" :href="sub.file" target="_blank" class="ml-2 text-indigo-600 hover:text-indigo-800"><Download class="h-3 w-3 inline" /></a>
                  </div>
                  <span class="text-xs text-gray-400">{{ new Date(sub.submitted_at).toLocaleDateString() }}</span>
                  <div class="flex items-center space-x-2">
                    <input v-model.number="sub.grade" type="number" :max="a.max_points" placeholder="Grade"
                      class="w-16 border border-gray-300 rounded px-2 py-1 text-xs focus:ring-2 focus:ring-indigo-500 outline-none text-center" />
                    <span class="text-xs text-gray-400">/ {{ a.max_points }}</span>
                  </div>
                  <button @click="submitGrade(sub)" class="text-indigo-600 hover:text-indigo-800">
                    <CheckCircle class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Project Groups Section -->
          <div class="mt-10 pt-8 border-t-2 border-gray-200">
            <button @click="showGroups = !showGroups"
              class="flex items-center text-base font-bold text-gray-900 mb-4 hover:text-indigo-600 transition-colors">
              <FolderOpen class="h-5 w-5 mr-2 text-indigo-600" />
              Project Groups
              <span class="ml-2 text-xs font-normal text-gray-400">({{ groups.length }} groups, {{ unassignedStudents.length }} unassigned)</span>
              <span class="ml-auto text-gray-400">{{ showGroups ? '▲' : '▼' }}</span>
            </button>

            <div v-if="showGroups" class="animate-fade-in space-y-6">

              <!-- Random Group Generator -->
              <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                <h4 class="text-sm font-bold text-gray-900 mb-3 flex items-center"><Shuffle class="h-4 w-4 mr-2 text-indigo-600" /> Random Group Generator</h4>
                <div class="flex items-end space-x-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-600 mb-1">Number of groups</label>
                    <input v-model.number="nGroups" type="number" min="2" max="10"
                      class="w-24 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                  </div>
                  <button @click="createRandomGroups"
                    class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 shadow-sm flex items-center">
                    <Shuffle class="h-4 w-4 mr-1.5" /> Generate
                  </button>
                </div>
                <p class="text-xs text-gray-400 mt-2">{{ students.length }} students evenly split into {{ nGroups }} groups.</p>
              </div>

              <!-- Manual Group Creator -->
              <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                <h4 class="text-sm font-bold text-gray-900 mb-3 flex items-center"><Plus class="h-4 w-4 mr-2 text-indigo-600" /> Add Group Manually</h4>
                <div class="flex items-center space-x-3">
                  <input v-model="newGroupName" @keyup.enter="addGroup" placeholder="Group name"
                    class="flex-1 max-w-xs border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                  <button @click="addGroup" class="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-900">
                    <Plus class="h-4 w-4 inline mr-1" /> Add
                  </button>
                </div>
              </div>

              <!-- Group Cards -->
              <div v-if="groups.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="g in groups" :key="g.id"
                  class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                  <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                    <h4 class="text-sm font-bold text-gray-900 flex items-center">
                      <Users class="h-4 w-4 text-indigo-600 mr-2" /> {{ g.name }}
                    </h4>
                    <button @click="deleteGroup(g)" class="text-gray-300 hover:text-red-600 transition-colors">
                      <Trash2 class="h-3.5 w-3.5" />
                    </button>
                  </div>
                  <ul class="divide-y divide-gray-50">
                    <li v-for="m in g.members" :key="m.id"
                      class="px-4 py-2 text-sm text-gray-700 flex items-center">
                      <div class="h-5 w-5 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-xs font-bold mr-2">
                        {{ m.first_name?.charAt(0) || '?' }}
                      </div>
                      {{ m.first_name }} {{ m.last_name }}
                    </li>
                    <li v-if="!g.members?.length" class="px-4 py-2.5 text-sm text-gray-400 italic">No members</li>
                  </ul>
                </div>
              </div>
              <div v-else class="text-center py-8 text-gray-400">
                <Users class="h-10 w-10 mx-auto mb-2 text-gray-300" />
                <p class="text-sm">No groups yet.</p>
              </div>

              <!-- Unassigned -->
              <div v-if="unassignedStudents.length" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div class="px-5 py-3 border-b border-gray-100">
                  <h4 class="text-sm font-bold text-gray-900">Unassigned Students ({{ unassignedStudents.length }})</h4>
                </div>
                <div class="px-5 py-3 flex flex-wrap gap-2">
                  <span v-for="s in unassignedStudents" :key="s.id"
                    class="inline-flex items-center px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
                    {{ s.first_name }} {{ s.last_name }}
                  </span>
                </div>
              </div>

            </div>
          </div>

        </template>
      </main>
    </div>
  </div>
</template>

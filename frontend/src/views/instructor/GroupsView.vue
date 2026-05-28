<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  ArrowLeft, Users, Plus, Shuffle, Trash2,
  FolderOpen, Download
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const courseId = computed(() => Number(route.params.id))

const course = ref<any>(null)
const groups = ref<any[]>([])
const students = ref<any[]>([])
const groupAssignments = ref<any[]>([])
const submissions = ref<any[]>([])
const isLoading = ref(true)
const nGroups = ref(2)
const newGroupName = ref('')

const fetchData = async () => {
  isLoading.value = true
  try {
    const [courseRes, groupsRes, enrollRes, assignRes, subRes] = await Promise.all([
      api.get(`courses/${courseId.value}/`),
      api.get('groups/', { params: { course: courseId.value } }),
      api.get('enrollments/', { params: { course: courseId.value } }),
      api.get('assignments/', { params: { course: courseId.value } }),
      api.get('submissions/', { params: {} }),
    ])
    course.value = courseRes.data
    groups.value = groupsRes.data
    students.value = enrollRes.data.map((e: any) => e.student)
    groupAssignments.value = assignRes.data.filter((a: any) => a.assignment_type === 'group')
    const assignIds = new Set(groupAssignments.value.map((a: any) => a.id))
    submissions.value = subRes.data.filter((s: any) => assignIds.has(s.assignment))
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
}

const createRandomGroups = async () => {
  if (!students.value.length) return alert('No students enrolled.')
  try {
    const res = await api.post('groups/random_groups/', {
      course: courseId.value,
      n_groups: nGroups.value,
    })
    groups.value = res.data
  } catch (err) {
    console.error(err)
  }
}

const addGroup = async () => {
  if (!newGroupName.value.trim()) return
  try {
    const res = await api.post('groups/', { course: courseId.value, name: newGroupName.value })
    groups.value.push(res.data)
    newGroupName.value = ''
  } catch (err) {
    console.error(err)
  }
}

const deleteGroup = async (g: any) => {
  try {
    await api.delete(`groups/${g.id}/`)
    groups.value = groups.value.filter((x: any) => x.id !== g.id)
  } catch (err) {
    console.error(err)
  }
}

const unassignedStudents = computed(() => {
  const assigned = new Set<number>()
  for (const g of groups.value) {
    for (const m of g.members || []) {
      assigned.add(m.id)
    }
  }
  return students.value.filter(s => !assigned.has(s.id))
})

const getSubmission = (groupId: number, assignId: number) => {
  return submissions.value.find(
    (s: any) => s.group === groupId && s.assignment === assignId
  ) || null
}

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
                <h1 class="text-xl font-bold text-gray-900">Project Groups</h1>
                <p v-if="course" class="text-xs text-gray-500">{{ course.title }} • {{ students.length }} students • {{ groupAssignments.length }} group assignments</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">

        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading...</div>

        <template v-else>

          <!-- Random Group Creator -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h3 class="text-base font-bold text-gray-900 mb-4 flex items-center"><Shuffle class="h-5 w-5 mr-2 text-indigo-600" /> Random Group Generator</h3>
            <div class="flex items-end space-x-3">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Number of groups</label>
                <input v-model.number="nGroups" type="number" min="2" max="10"
                  class="w-24 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
              </div>
              <button @click="createRandomGroups"
                class="bg-indigo-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm flex items-center">
                <Shuffle class="h-4 w-4 mr-2" /> Generate Groups
              </button>
            </div>
            <p class="text-xs text-gray-400 mt-2">{{ students.length }} students will be evenly split into {{ nGroups }} groups.</p>
          </div>

          <!-- Manual Group Creator -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
            <h3 class="text-base font-bold text-gray-900 mb-4 flex items-center"><Plus class="h-5 w-5 mr-2 text-indigo-600" /> Add Group Manually</h3>
            <div class="flex items-center space-x-3">
              <input v-model="newGroupName" @keyup.enter="addGroup" placeholder="Group name"
                class="flex-1 max-w-xs border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
              <button @click="addGroup" class="bg-gray-800 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-900 transition-colors">
                <Plus class="h-4 w-4 inline mr-1" /> Add
              </button>
            </div>
          </div>

          <!-- Group Assignments Progress -->
          <div v-if="groupAssignments.length" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
            <div class="px-6 py-4 border-b border-gray-100 flex items-center">
              <FolderOpen class="h-5 w-5 text-indigo-600 mr-2" />
              <h3 class="text-base font-bold text-gray-900">Group Assignments Progress</h3>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50 z-10 min-w-[140px]">Group</th>
                    <th v-for="a in groupAssignments" :key="a.id"
                      class="px-3 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider min-w-[120px] border-l border-gray-100">
                      {{ a.title }}<br /><span class="text-[10px] font-normal text-gray-400">/{{ a.max_points }}</span>
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="g in groups" :key="g.id" class="hover:bg-gray-50 transition-colors">
                    <td class="px-4 py-3 whitespace-nowrap sticky left-0 bg-white z-10 font-medium text-sm text-gray-900 flex items-center">
                      <Users class="h-4 w-4 text-indigo-600 mr-2 shrink-0" /> {{ g.name }}
                      <span class="ml-2 text-xs text-gray-400">({{ g.members?.length || 0 }})</span>
                    </td>
                    <td v-for="a in groupAssignments" :key="a.id"
                      class="px-3 py-3 text-center border-l border-gray-100">
                      <template v-if="getSubmission(g.id, a.id)">
                        <div class="flex flex-col items-center">
                          <a v-if="getSubmission(g.id, a.id).file" :href="getSubmission(g.id, a.id).file" target="_blank"
                            class="text-indigo-600 hover:text-indigo-800 mb-1">
                            <Download class="h-4 w-4 inline" />
                          </a>
                          <span v-if="getSubmission(g.id, a.id).grade !== null"
                            class="text-sm font-bold font-mono text-gray-900">{{ getSubmission(g.id, a.id).grade }}</span>
                          <span v-else class="text-xs text-amber-600 font-medium">Pending</span>
                        </div>
                      </template>
                      <span v-else class="text-xs text-gray-400">—</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Groups List -->
          <div v-if="groups.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            <div v-for="g in groups" :key="g.id"
              class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
                <h3 class="text-sm font-bold text-gray-900 flex items-center">
                  <Users class="h-4 w-4 text-indigo-600 mr-2" /> {{ g.name }}
                </h3>
                <button @click="deleteGroup(g)" class="text-gray-300 hover:text-red-600 transition-colors">
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
              <ul class="divide-y divide-gray-50">
                <li v-for="m in g.members" :key="m.id"
                  class="px-5 py-2.5 text-sm text-gray-700 flex items-center">
                  <div class="h-6 w-6 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-xs font-bold mr-2.5">
                    {{ m.first_name?.charAt(0) || '?' }}
                  </div>
                  {{ m.first_name }} {{ m.last_name }}
                </li>
                <li v-if="!g.members?.length" class="px-5 py-3 text-sm text-gray-400 italic">No members</li>
              </ul>
            </div>
          </div>

          <div v-else class="text-center py-16">
            <Users class="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <p class="text-sm text-gray-500">No groups yet. Create random groups or add them manually.</p>
          </div>

          <!-- Unassigned Students -->
          <div v-if="unassignedStudents.length" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-3 border-b border-gray-100">
              <h3 class="text-sm font-bold text-gray-900">Unassigned Students ({{ unassignedStudents.length }})</h3>
            </div>
            <div class="px-6 py-3 flex flex-wrap gap-2">
              <span v-for="s in unassignedStudents" :key="s.id"
                class="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
                {{ s.first_name }} {{ s.last_name }}
              </span>
            </div>
          </div>

        </template>
      </main>
    </div>
  </div>
</template>

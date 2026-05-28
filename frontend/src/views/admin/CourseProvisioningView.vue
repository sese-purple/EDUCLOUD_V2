<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import AdminSidebar from '../../components/AdminSidebar.vue'
import {
  BookOpen, Plus, FolderPlus, MoreVertical,
  Users, CheckCircle2, AlertCircle
} from 'lucide-vue-next'

const router = useRouter()

const courses = ref<any[]>([])
const availableInstructors = ref<any[]>([])
const showCreateForm = ref(false)
const isLoading = ref(true)

const newCourse = ref({
  title: '',
  course_code: '',
  description: '',
  instructor_id: ''
})

const loadData = async () => {
  isLoading.value = true
  try {
    const [coursesRes, usersRes] = await Promise.all([
      api.get('courses/'),
      api.get('users/')
    ])

    courses.value = coursesRes.data
    availableInstructors.value = usersRes.data
  } catch (error) {
    console.error("Error loading provisioning data:", error)
  } finally {
    isLoading.value = false
  }
}

const handleCreateCourse = async () => {
  try {
    await api.post('courses/', {
      title: newCourse.value.title,
      course_code: newCourse.value.course_code,
      description: newCourse.value.description,
      instructor_id: newCourse.value.instructor_id
    })

    showCreateForm.value = false
    newCourse.value = { title: '', course_code: '', description: '', instructor_id: '' }

    await loadData()
  } catch (error) {
    console.error("Failed to provision course:", error)
    alert("Error creating course. Check console.")
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">

    <AdminSidebar />

    <div class="flex-1 flex flex-col overflow-hidden">

      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm z-10">
        <h2 class="text-xl font-bold text-gray-800">EDUCLOUD <span class="text-indigo-600">Core Network</span></h2>
        <div class="flex items-center space-x-4">
          <div class="h-8 w-8 rounded-full bg-red-100 text-red-600 flex items-center justify-center font-bold border border-red-200">
            AD
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">

        <div class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">Course Provisioning</h2>
            <p class="text-gray-500 text-sm mt-1">Create official institutional modules and assign faculty.</p>
          </div>
          <button @click="showCreateForm = !showCreateForm" class="flex items-center px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
            <FolderPlus class="h-4 w-4 mr-2" /> {{ showCreateForm ? 'Cancel' : 'Provision New Course' }}
          </button>
        </div>

        <div v-if="showCreateForm" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
          <h3 class="text-lg font-bold text-gray-900 mb-4 border-b pb-2">Module Details</h3>
          <form @submit.prevent="handleCreateCourse" class="space-y-4">

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Official Module Title</label>
                <input v-model="newCourse.title" type="text" required placeholder="e.g. Integrated Internship Management"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Course Code</label>
                <input v-model="newCourse.course_code" type="text" required placeholder="e.g. CS-301"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Assign Lead Instructor</label>
                <select v-model="newCourse.instructor_id" required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm bg-white">
                  <option value="" disabled>Select a faculty member...</option>
                  <option v-for="user in availableInstructors" :key="user.id" :value="user.id">
                    {{ user.first_name }} {{ user.last_name }} (@{{ user.username }})
                  </option>
                </select>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Module Description (Optional)</label>
              <textarea v-model="newCourse.description" rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm"></textarea>
            </div>

            <div class="flex justify-end pt-2">
              <button type="submit" class="bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 px-6 rounded-lg transition-colors shadow-sm">
                Deploy Course to Network
              </button>
            </div>
          </form>
        </div>

        <div v-if="isLoading" class="text-center py-10 text-gray-500">
          Syncing with database...
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          <div v-for="course in courses" :key="course.id" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow group cursor-pointer">
            <div class="h-2 w-full bg-indigo-500"></div>
            <div class="p-6">
              <div class="flex justify-between items-start mb-4">
                <div class="h-10 w-10 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center font-bold">
                  <BookOpen class="h-5 w-5" />
                </div>
                <button class="text-gray-400 hover:text-gray-600">
                  <MoreVertical class="h-5 w-5" />
                </button>
              </div>

              <h3 class="text-lg font-bold text-gray-900 mb-1 truncate">{{ course.title }}</h3>
              <p class="text-xs text-gray-400 font-mono mb-1">{{ course.course_code }}</p>
              <p class="text-xs text-gray-500 mb-4 line-clamp-2 h-8">
                {{ course.description || 'No description provided.' }}
              </p>

              <div class="flex items-center text-sm text-gray-600 bg-gray-50 p-2 rounded border border-gray-100">
                <Users class="h-4 w-4 mr-2 text-gray-400" />
                <span v-if="course.instructor">Instructor: {{ course.instructor.username }}</span>
                <span v-else class="text-red-500 text-xs flex items-center">
                  <AlertCircle class="h-3 w-3 mr-1" /> Unassigned
                </span>
              </div>

              <div class="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
                <span class="text-xs font-medium text-emerald-600 flex items-center">
                  <CheckCircle2 class="h-3 w-3 mr-1" /> Active
                </span>
                <span class="text-xs text-gray-400">ID: {{ course.id }}</span>
              </div>
            </div>
          </div>

          <div v-if="courses.length === 0" class="col-span-full bg-white rounded-xl border border-dashed border-gray-300 p-12 text-center">
            <BookOpen class="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <h3 class="text-lg font-medium text-gray-900">No modules provisioned</h3>
            <p class="text-sm text-gray-500 mt-1">Click "Provision New Course" to get started.</p>
          </div>

        </div>

      </main>
    </div>
  </div>
</template>

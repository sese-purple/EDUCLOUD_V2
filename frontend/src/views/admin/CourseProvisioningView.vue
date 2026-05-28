<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import AdminSidebar from '../../components/AdminSidebar.vue'
import {
  BookOpen, FolderPlus, MoreVertical,
  Users, CheckCircle2, AlertCircle,
  Pencil, Trash2, X, Search
} from 'lucide-vue-next'

const courses = ref<any[]>([])
const availableInstructors = ref<any[]>([])
const showCreateForm = ref(false)
const isLoading = ref(true)
const searchQuery = ref('')

const newCourse = ref({
  title: '',
  course_code: '',
  description: '',
  instructor_id: ''
})

const editingCourse = ref<any | null>(null)
const showEditForm = ref(false)
const editCourseData = ref({
  title: '',
  course_code: '',
  description: '',
  instructor_id: ''
})

const showDeleteConfirm = ref(false)
const deletingCourse = ref<any | null>(null)
const openActionId = ref<number | null>(null)

const loadData = async () => {
  isLoading.value = true
  try {
    const params: any = {}
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    const [coursesRes, usersRes] = await Promise.all([
      api.get('courses/', { params }),
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

const openEditForm = (course: any) => {
  editingCourse.value = course
  editCourseData.value = {
    title: course.title,
    course_code: course.course_code,
    description: course.description || '',
    instructor_id: course.instructor?.id || ''
  }
  showEditForm.value = true
  openActionId.value = null
}

const handleUpdateCourse = async () => {
  if (!editingCourse.value) return
  try {
    await api.patch(`courses/${editingCourse.value.id}/`, {
      title: editCourseData.value.title,
      course_code: editCourseData.value.course_code,
      description: editCourseData.value.description,
      instructor_id: editCourseData.value.instructor_id
    })

    showEditForm.value = false
    editingCourse.value = null
    await loadData()
  } catch (error) {
    console.error("Failed to update course:", error)
    alert("Error updating course. Check console.")
  }
}

const confirmDelete = (course: any) => {
  deletingCourse.value = course
  showDeleteConfirm.value = true
  openActionId.value = null
}

const handleDeleteCourse = async () => {
  if (!deletingCourse.value) return
  try {
    await api.delete(`courses/${deletingCourse.value.id}/`)
    showDeleteConfirm.value = false
    deletingCourse.value = null
    await loadData()
  } catch (error) {
    console.error("Failed to delete course:", error)
    alert("Error deleting course. Check console.")
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

        <div v-if="showEditForm && editingCourse" class="bg-white p-6 rounded-xl shadow-sm border border-indigo-200 border-2 mb-8">
          <div class="flex items-center justify-between mb-4 border-b pb-2">
            <h3 class="text-lg font-bold text-gray-900">Edit Module</h3>
            <button @click="showEditForm = false" class="text-gray-400 hover:text-gray-600">
              <X class="h-5 w-5" />
            </button>
          </div>
          <form @submit.prevent="handleUpdateCourse" class="space-y-4">

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Official Module Title</label>
                <input v-model="editCourseData.title" type="text" required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Course Code</label>
                <input v-model="editCourseData.course_code" type="text" required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Assign Lead Instructor</label>
                <select v-model="editCourseData.instructor_id" required
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
              <textarea v-model="editCourseData.description" rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm"></textarea>
            </div>

            <div class="flex justify-end gap-3 pt-2">
              <button type="button" @click="showEditForm = false"
                class="bg-white border border-gray-300 text-gray-700 font-medium py-2 px-6 rounded-lg hover:bg-gray-50 transition-colors">
                Cancel
              </button>
              <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-6 rounded-lg transition-colors shadow-sm">
                Save Changes
              </button>
            </div>
          </form>
        </div>

        <div class="flex items-center justify-between mb-6">
          <div class="relative w-full max-w-md">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input v-model="searchQuery" @input="loadData" type="text" placeholder="Search courses by title or code..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm shadow-sm">
          </div>
        </div>

        <div v-if="isLoading" class="text-center py-10 text-gray-500">
          Syncing with database...
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

          <div v-for="course in courses" :key="course.id" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow group">
            <div class="h-2 w-full" :class="course.instructor ? 'bg-indigo-500' : 'bg-red-400'"></div>
            <div class="p-6">
              <div class="flex justify-between items-start mb-4">
                <div class="h-10 w-10 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center font-bold">
                  <BookOpen class="h-5 w-5" />
                </div>
                <div class="relative">
                  <button @click="openActionId = openActionId === course.id ? null : course.id" class="text-gray-400 hover:text-gray-600 p-1 rounded hover:bg-gray-100 transition-colors">
                    <MoreVertical class="h-5 w-5" />
                  </button>
                  <div v-if="openActionId === course.id" class="absolute right-0 top-8 w-40 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                    <button @click="openEditForm(course)" class="flex items-center w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                      <Pencil class="h-4 w-4 mr-2 text-indigo-500" /> Edit
                    </button>
                    <button @click="confirmDelete(course)" class="flex items-center w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">
                      <Trash2 class="h-4 w-4 mr-2 text-red-500" /> Delete
                    </button>
                  </div>
                </div>
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
                <span v-if="course.instructor" class="text-xs font-medium text-emerald-600 flex items-center">
                  <CheckCircle2 class="h-3 w-3 mr-1" /> Active
                </span>
                <span v-else class="text-xs font-medium text-red-500 flex items-center">
                  <AlertCircle class="h-3 w-3 mr-1" /> Unassigned
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

    <div v-if="showDeleteConfirm && deletingCourse" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showDeleteConfirm = false">
      <div class="bg-white rounded-xl shadow-2xl border border-gray-200 p-6 w-full max-w-md mx-4">
        <div class="flex items-center mb-4">
          <div class="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center mr-3">
            <Trash2 class="h-5 w-5 text-red-600" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900">Delete Module</h3>
            <p class="text-sm text-gray-500">This action cannot be undone.</p>
          </div>
        </div>
        <p class="text-sm text-gray-700 mb-6">
          Are you sure you want to permanently delete <strong>{{ deletingCourse.title }}</strong> ({{ deletingCourse.course_code }})?
        </p>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteConfirm = false"
            class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors">
            Cancel
          </button>
          <button @click="handleDeleteCourse"
            class="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors shadow-sm">
            Delete Permanently
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

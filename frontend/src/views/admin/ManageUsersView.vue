<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import AdminSidebar from '../../components/AdminSidebar.vue'
import {
  ArrowLeft, Search, UserPlus, MoreVertical,
  Mail, Pencil, Trash2, X,
  FileUp, Upload, Download, CheckCircle2, XCircle, AlertTriangle
} from 'lucide-vue-next'

const router = useRouter()

const users = ref<any[]>([])
const isLoading = ref(true)
const showAddUserForm = ref(false)
const searchQuery = ref('')
const isCreating = ref(false)
const openActionId = ref<number | null>(null)

const newUser = ref({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  role: 'student'
})

const editingUser = ref<any | null>(null)
const showEditForm = ref(false)
const editUserData = ref({
  first_name: '',
  last_name: '',
  email: '',
  role: '',
  password: ''
})

const showDeleteConfirm = ref(false)
const deletingUser = ref<any | null>(null)

const showBulkImport = ref(false)
const dragOver = ref(false)
const selectedFile = ref<File | null>(null)
const isUploading = ref(false)
const importResult = ref<{ created: number; skipped: number; errors: string[] } | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const fetchUsers = async () => {
  isLoading.value = true
  try {
    const params: any = {}
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    const response = await api.get('users/', { params })
    users.value = response.data
  } catch (error) {
    console.error("Error fetching users:", error)
  } finally {
    isLoading.value = false
  }
}

const handleCreateUser = async () => {
  isCreating.value = true
  try {
    await api.post('users/', {
      username: newUser.value.username,
      email: newUser.value.email,
      password: newUser.value.password,
      first_name: newUser.value.first_name,
      last_name: newUser.value.last_name,
      role: newUser.value.role
    })

    showAddUserForm.value = false
    newUser.value = { username: '', email: '', password: '', first_name: '', last_name: '', role: 'student' }
    await fetchUsers()
  } catch (error) {
    console.error("Error creating user:", error)
    alert("Failed to create user. Check the console for details.")
  } finally {
    isCreating.value = false
  }
}

const openEditForm = (user: any) => {
  editingUser.value = user
  editUserData.value = {
    first_name: user.first_name,
    last_name: user.last_name,
    email: user.email,
    role: user.role,
    password: ''
  }
  showEditForm.value = true
  openActionId.value = null
}

const handleUpdateUser = async () => {
  if (!editingUser.value) return
  try {
    const payload: any = {
      first_name: editUserData.value.first_name,
      last_name: editUserData.value.last_name,
      email: editUserData.value.email,
      role: editUserData.value.role
    }
    if (editUserData.value.password) {
      payload.password = editUserData.value.password
    }

    await api.patch(`users/${editingUser.value.id}/`, payload)
    showEditForm.value = false
    editingUser.value = null
    await fetchUsers()
  } catch (error) {
    console.error("Error updating user:", error)
    alert("Failed to update user. Check the console for details.")
  }
}

const confirmDelete = (user: any) => {
  deletingUser.value = user
  showDeleteConfirm.value = true
  openActionId.value = null
}

const handleDeleteUser = async () => {
  if (!deletingUser.value) return
  try {
    await api.delete(`users/${deletingUser.value.id}/`)
    showDeleteConfirm.value = false
    deletingUser.value = null
    await fetchUsers()
  } catch (error) {
    console.error("Error deleting user:", error)
    alert("Failed to delete user. Check the console for details.")
  }
}

const onDragOver = (e: DragEvent) => {
  e.preventDefault()
  dragOver.value = true
}

const onDragLeave = () => {
  dragOver.value = false
}

const onDrop = (e: DragEvent) => {
  e.preventDefault()
  dragOver.value = false
  const file = e.dataTransfer?.files[0]
  if (file) {
    selectedFile.value = file
    importResult.value = null
  }
}

const onFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    selectedFile.value = file
    importResult.value = null
  }
}

const downloadTemplate = async () => {
  try {
    const res = await api.get('download-template/', { responseType: 'blob' })
    const url = URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'bulk_import_template.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  } catch (error) {
    console.error("Error downloading template:", error)
  }
}

const handleBulkImport = async () => {
  if (!selectedFile.value) return
  isUploading.value = true
  importResult.value = null

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await api.post('bulk-import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    importResult.value = res.data
    selectedFile.value = null
    await fetchUsers()
  } catch (error) {
    console.error("Error importing users:", error)
    alert("Bulk import failed. Check the file format and try again.")
  } finally {
    isUploading.value = false
  }
}

const closeBulkImport = () => {
  showBulkImport.value = false
  selectedFile.value = null
  importResult.value = null
}

const roleDisplay = (role: string) => {
  const map: Record<string, string> = {
    'super_admin': 'Super Admin',
    'inst_admin': 'Institution Admin',
    'instructor': 'Instructor',
    'student': 'Student',
  }
  return map[role] || role
}

const roleBadgeColor = (role: string) => {
  const map: Record<string, string> = {
    'super_admin': 'bg-purple-100 text-purple-800',
    'inst_admin': 'bg-red-100 text-red-800',
    'instructor': 'bg-blue-100 text-blue-800',
    'student': 'bg-green-100 text-green-800',
  }
  return map[role] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="flex h-screen bg-gray-100 font-sans overflow-hidden">

    <AdminSidebar />

    <div class="flex-1 flex flex-col overflow-hidden">

    <header class="bg-white border-b border-gray-200 flex-shrink-0">
      <div class="px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <button @click="router.push({ name: 'admin-dashboard' })" class="mr-4 text-gray-400 hover:text-indigo-600 transition-colors">
              <ArrowLeft class="h-6 w-6" />
            </button>
            <div>
              <h1 class="text-xl font-bold text-gray-900 leading-tight">User Management</h1>
              <p class="text-xs text-gray-500 font-medium">Provision and manage institutional accounts</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <button @click="showBulkImport = !showBulkImport; if (showBulkImport) showAddUserForm = false"
              class="bg-white border border-indigo-300 text-indigo-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-50 transition-colors shadow-sm flex items-center">
              <Upload class="h-4 w-4 mr-2" /> {{ showBulkImport ? 'Cancel' : 'Bulk Import' }}
            </button>
            <button @click="showAddUserForm = !showAddUserForm; if (showAddUserForm) showBulkImport = false"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center">
              <UserPlus class="h-4 w-4 mr-2" /> {{ showAddUserForm ? 'Cancel' : 'Add New User' }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-8">

      <div v-if="showBulkImport" class="bg-white p-6 rounded-xl shadow-sm border border-indigo-200 mb-8 bg-indigo-50/30 animate-fade-in">
        <div class="flex justify-between items-center mb-4 border-b border-indigo-100 pb-3">
          <h3 class="text-lg font-bold text-indigo-900">Bulk Provision Users (CSV)</h3>
        </div>

        <div v-if="!selectedFile && !importResult"
          @dragover="onDragOver"
          @dragleave="onDragLeave"
          @drop="onDrop"
          :class="['border-2 border-dashed rounded-xl p-8 text-center bg-white hover:bg-indigo-50 transition-colors cursor-pointer group', dragOver ? 'border-indigo-500 bg-indigo-50' : 'border-indigo-300']">
          <div class="h-12 w-12 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
            <FileUp class="h-6 w-6" />
          </div>
          <p class="text-sm font-bold text-gray-700">Click to upload or drag and drop</p>
          <p class="text-xs text-gray-500 mt-1">CSV, XLS, or XLSX files only (Max. 5000 rows)</p>
          <input type="file" accept=".csv,.xls,.xlsx" class="hidden" ref="fileInputRef" @change="onFileSelect" />
          <button @click="fileInputRef?.click()" class="mt-4 text-sm text-indigo-600 hover:text-indigo-800 font-medium underline">
            Browse Files
          </button>
          <div class="mt-4 flex justify-center">
            <a @click.prevent="downloadTemplate" href="#" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium underline flex items-center">
              <Download class="h-3 w-3 mr-1" /> Download CSV Template
            </a>
          </div>
        </div>

        <div v-else-if="selectedFile && !importResult" class="border-2 border-indigo-300 rounded-xl p-6 bg-white">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="h-10 w-10 bg-indigo-100 text-indigo-600 rounded-lg flex items-center justify-center mr-3">
                <FileUp class="h-5 w-5" />
              </div>
              <div>
                <p class="text-sm font-bold text-gray-900">{{ selectedFile.name }}</p>
                <p class="text-xs text-gray-500">{{ (selectedFile.size / 1024).toFixed(1) }} KB</p>
              </div>
            </div>
            <button @click="selectedFile = null" class="text-gray-400 hover:text-gray-600">
              <X class="h-5 w-5" />
            </button>
          </div>
          <div class="mt-4 flex justify-end">
            <button @click="handleBulkImport" :disabled="isUploading"
              class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-6 rounded-lg transition-colors shadow-sm disabled:opacity-70 flex items-center">
              <Upload class="h-4 w-4 mr-2" /> {{ isUploading ? 'Importing...' : 'Process & Import Data' }}
            </button>
          </div>
        </div>

        <div v-else-if="importResult" class="border-2 rounded-xl p-6 bg-white" :class="importResult.errors.length ? 'border-amber-200' : 'border-emerald-200'">
          <div class="flex items-center mb-4">
            <CheckCircle2 v-if="importResult.created > 0" class="h-8 w-8 text-emerald-500 mr-3" />
            <AlertTriangle v-else class="h-8 w-8 text-amber-500 mr-3" />
            <div>
              <p class="text-sm font-bold text-gray-900">Import Complete</p>
              <p class="text-xs text-gray-500">
                {{ importResult.created }} created, {{ importResult.skipped }} skipped
              </p>
            </div>
          </div>
          <div v-if="importResult.errors.length" class="max-h-32 overflow-y-auto bg-red-50 border border-red-200 rounded-lg p-3">
            <p v-for="(err, i) in importResult.errors" :key="i" class="text-xs text-red-700 flex items-start mb-1">
              <XCircle class="h-3 w-3 mr-1 mt-0.5 flex-shrink-0" /> {{ err }}
            </p>
          </div>
          <div class="mt-4 flex justify-end">
            <button @click="closeBulkImport" class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors">
              Done
            </button>
          </div>
        </div>
      </div>

      <div v-if="showAddUserForm" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8 animate-fade-in">
        <h2 class="text-lg font-bold text-gray-900 mb-4 border-b pb-2">Provision New Account</h2>
        <form @submit.prevent="handleCreateUser" class="grid grid-cols-1 md:grid-cols-2 gap-4">

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input v-model="newUser.username" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
            <input v-model="newUser.email" type="email" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
            <input v-model="newUser.first_name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
            <input v-model="newUser.last_name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Temporary Password</label>
            <input v-model="newUser.password" type="password" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">System Role</label>
            <select v-model="newUser.role" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              <option value="student">Student</option>
              <option value="instructor">Instructor</option>
              <option value="inst_admin">Institution Admin</option>
              <option value="super_admin">Super Admin</option>
            </select>
          </div>

          <div class="md:col-span-2 mt-2">
            <button type="submit" :disabled="isCreating" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-medium py-2 rounded-lg transition-colors shadow-sm disabled:opacity-70">
              {{ isCreating ? 'Creating Account...' : 'Create Account' }}
            </button>
          </div>
        </form>
      </div>

      <div v-if="showEditForm && editingUser" class="bg-white p-6 rounded-xl shadow-sm border-2 border-indigo-200 mb-8 animate-fade-in">
        <div class="flex items-center justify-between mb-4 border-b pb-2">
          <h2 class="text-lg font-bold text-gray-900">Edit User — {{ editingUser.username }}</h2>
          <button @click="showEditForm = false" class="text-gray-400 hover:text-gray-600">
            <X class="h-5 w-5" />
          </button>
        </div>
        <form @submit.prevent="handleUpdateUser" class="grid grid-cols-1 md:grid-cols-2 gap-4">

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
            <input v-model="editUserData.first_name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
            <input v-model="editUserData.last_name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
            <input v-model="editUserData.email" type="email" required class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">System Role</label>
            <select v-model="editUserData.role" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              <option value="student">Student</option>
              <option value="instructor">Instructor</option>
              <option value="inst_admin">Institution Admin</option>
              <option value="super_admin">Super Admin</option>
            </select>
          </div>

          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-1">Reset Password <span class="text-gray-400 font-normal">(leave blank to keep current)</span></label>
            <input v-model="editUserData.password" type="password" placeholder="Enter new password" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
          </div>

          <div class="md:col-span-2 flex justify-end gap-3 mt-2">
            <button type="button" @click="showEditForm = false"
              class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors">
              Cancel
            </button>
            <button type="submit"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm">
              Save Changes
            </button>
          </div>
        </form>
      </div>

      <div class="flex items-center justify-between mb-4">
        <div class="relative w-full max-w-md">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input v-model="searchQuery" @input="fetchUsers" type="text" placeholder="Search by name, username, or email..." class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm shadow-sm">
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div v-if="isLoading" class="p-10 text-center text-gray-500">
          Loading system users...
        </div>
        <table v-else class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">User</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">Contact</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">System Role</th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 transition-colors">

              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center font-bold">
                    {{ user.username.charAt(0).toUpperCase() }}
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ user.first_name }} {{ user.last_name }}</div>
                    <div class="text-sm text-gray-500">@{{ user.username }}</div>
                  </div>
                </div>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center text-sm text-gray-900">
                  <Mail class="h-4 w-4 mr-2 text-gray-400" />
                  {{ user.email || 'No email provided' }}
                </div>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="roleBadgeColor(user.role)">
                  {{ roleDisplay(user.role) }}
                </span>
              </td>

              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium relative">
                <button @click="openActionId = openActionId === user.id ? null : user.id" class="text-gray-400 hover:text-indigo-600 transition-colors p-1 rounded hover:bg-gray-100">
                  <MoreVertical class="h-5 w-5 inline" />
                </button>
                <div v-if="openActionId === user.id" class="absolute right-0 top-12 w-40 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-20">
                  <button @click="openEditForm(user)" class="flex items-center w-full px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                    <Pencil class="h-4 w-4 mr-2 text-indigo-500" /> Edit
                  </button>
                  <button @click="confirmDelete(user)" class="flex items-center w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors">
                    <Trash2 class="h-4 w-4 mr-2 text-red-500" /> Delete
                  </button>
                </div>
              </td>

            </tr>
          </tbody>
        </table>
      </div>

    </main>
    </div>

    <div v-if="showDeleteConfirm && deletingUser" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showDeleteConfirm = false">
      <div class="bg-white rounded-xl shadow-2xl border border-gray-200 p-6 w-full max-w-md mx-4">
        <div class="flex items-center mb-4">
          <div class="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center mr-3">
            <Trash2 class="h-5 w-5 text-red-600" />
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900">Delete User</h3>
            <p class="text-sm text-gray-500">This action cannot be undone.</p>
          </div>
        </div>
        <p class="text-sm text-gray-700 mb-6">
          Are you sure you want to permanently delete <strong>{{ deletingUser.first_name }} {{ deletingUser.last_name }}</strong> (@{{ deletingUser.username }})?
        </p>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteConfirm = false"
            class="px-4 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors">
            Cancel
          </button>
          <button @click="handleDeleteUser"
            class="px-4 py-2 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 transition-colors shadow-sm">
            Delete Permanently
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

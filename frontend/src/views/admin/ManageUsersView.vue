<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import AdminSidebar from '../../components/AdminSidebar.vue'
import {
  ArrowLeft, Search, UserPlus, MoreVertical,
  Mail
} from 'lucide-vue-next'

const router = useRouter()

// State Management
const users = ref<any[]>([])
const isLoading = ref(true)
const showAddUserForm = ref(false)
const searchQuery = ref('')
const isCreating = ref(false)

// New User Form State
const newUser = ref({
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  role: 'student'
})

// Fetch all users from Django when the page loads
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

// Send the new user data to Django
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
    
    // Reset form and hide it
    showAddUserForm.value = false
    newUser.value = { username: '', email: '', password: '', first_name: '', last_name: '', role: 'student' }
    
    // Refresh the table to show the new user
    await fetchUsers()
    
  } catch (error) {
    console.error("Error creating user:", error)
    alert("Failed to create user. Check the console for details.")
  } finally {
    isCreating.value = false
  }
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

// Run the fetch function as soon as the component loads
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
          <button @click="showAddUserForm = !showAddUserForm" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center">
            <UserPlus class="h-4 w-4 mr-2" /> {{ showAddUserForm ? 'Cancel' : 'Add New User' }}
          </button>
        </div>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-8">
      
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
              
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button class="text-gray-400 hover:text-indigo-600 transition-colors">
                  <MoreVertical class="h-5 w-5 inline" />
                </button>
              </td>

            </tr>
          </tbody>
        </table>
      </div>

    </main>
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
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  Settings, User, Mail, Save, Key,
  CheckCircle, Eye, EyeOff, Bell
} from 'lucide-vue-next'

const user = ref<any>({})
const saving = ref(false)
const passwordSaving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const profileForm = ref({ first_name: '', last_name: '', email: '' })
const passwordForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const showOld = ref(false)
const showNew = ref(false)
const showConfirm = ref(false)

onMounted(async () => {
  try {
    const res = await api.get('profile/')
    user.value = res.data
    profileForm.value = {
      first_name: res.data.first_name || '',
      last_name: res.data.last_name || '',
      email: res.data.email || '',
    }
  } catch (err) { console.error(err) }
})

const saveProfile = async () => {
  saving.value = true; successMsg.value = ''; errorMsg.value = ''
  try {
    const res = await api.patch('profile/', profileForm.value)
    user.value = res.data
    successMsg.value = 'Profile updated successfully.'
    setTimeout(() => successMsg.value = '', 3000)
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Failed to update profile.'
  } finally { saving.value = false }
}

const changePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    errorMsg.value = 'New passwords do not match.'; return
  }
  if (passwordForm.value.new_password.length < 6) {
    errorMsg.value = 'Password must be at least 6 characters.'; return
  }
  passwordSaving.value = true; successMsg.value = ''; errorMsg.value = ''
  try {
    await api.post('profile/', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    })
    successMsg.value = 'Password changed successfully.'
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
    setTimeout(() => successMsg.value = '', 3000)
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail || 'Failed to change password.'
  } finally { passwordSaving.value = false }
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <StudentSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white border-b border-gray-200 flex items-center px-6 shadow-sm">
        <Settings class="h-5 w-5 text-indigo-600 mr-3" />
        <h2 class="text-lg font-bold text-gray-800">Settings</h2>
      </header>

      <main class="flex-1 overflow-y-auto p-8">
        <div class="max-w-2xl mx-auto space-y-6">
          <div v-if="successMsg" class="bg-emerald-50 border border-emerald-200 text-emerald-700 px-4 py-3 rounded-lg text-sm flex items-center">
            <CheckCircle class="h-4 w-4 mr-2 shrink-0" /> {{ successMsg }}
          </div>
          <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">{{ errorMsg }}</div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-5 border-b border-gray-100 flex items-center">
              <User class="h-5 w-5 text-indigo-600 mr-2" />
              <h3 class="text-base font-bold text-gray-900">Profile</h3>
            </div>
            <div class="p-6 space-y-5">
              <div class="flex items-center mb-2">
                <div class="h-16 w-16 bg-indigo-600 text-white rounded-full flex items-center justify-center text-2xl font-bold shadow-sm mr-4">
                  {{ (profileForm.first_name?.charAt(0) || '?').toUpperCase() }}{{ (profileForm.last_name?.charAt(0) || '').toUpperCase() }}
                </div>
                <div>
                  <p class="text-lg font-bold text-gray-900">{{ user.first_name }} {{ user.last_name }}</p>
                  <p class="text-sm text-gray-500">@{{ user.username }} • {{ user.role }}</p>
                </div>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">First Name</label>
                  <input v-model="profileForm.first_name" type="text"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Last Name</label>
                  <input v-model="profileForm.last_name" type="text"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1"><Mail class="h-3 w-3 inline mr-1" /> Email</label>
                <input v-model="profileForm.email" type="email"
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none" />
              </div>
              <div class="flex justify-end">
                <button @click="saveProfile" :disabled="saving"
                  class="flex items-center px-5 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 shadow-sm transition-colors">
                  <Save class="h-4 w-4 mr-2" /> {{ saving ? 'Saving...' : 'Save Profile' }}
                </button>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-5 border-b border-gray-100 flex items-center">
              <Key class="h-5 w-5 text-indigo-600 mr-2" />
              <h3 class="text-base font-bold text-gray-900">Change Password</h3>
            </div>
            <div class="p-6 space-y-4">
              <div>
                <label class="block text-xs font-medium text-gray-600 mb-1">Current Password</label>
                <div class="relative">
                  <input :type="showOld ? 'text' : 'password'" v-model="passwordForm.old_password"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none pr-10" />
                  <button @click="showOld = !showOld" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                    <component :is="showOld ? EyeOff : Eye" class="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">New Password</label>
                  <div class="relative">
                    <input :type="showNew ? 'text' : 'password'" v-model="passwordForm.new_password"
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none pr-10" />
                    <button @click="showNew = !showNew" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                      <component :is="showNew ? EyeOff : Eye" class="h-4 w-4" />
                    </button>
                  </div>
                </div>
                <div>
                  <label class="block text-xs font-medium text-gray-600 mb-1">Confirm New Password</label>
                  <div class="relative">
                    <input :type="showConfirm ? 'text' : 'password'" v-model="passwordForm.confirm_password"
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none pr-10" />
                    <button @click="showConfirm = !showConfirm" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                      <component :is="showConfirm ? EyeOff : Eye" class="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
              <div class="flex justify-end">
                <button @click="changePassword" :disabled="passwordSaving"
                  class="flex items-center px-5 py-2 bg-gray-800 text-white text-sm font-medium rounded-lg hover:bg-gray-900 disabled:opacity-50 shadow-sm transition-colors">
                  <Key class="h-4 w-4 mr-2" /> {{ passwordSaving ? 'Changing...' : 'Change Password' }}
                </button>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-5 border-b border-gray-100 flex items-center">
              <Bell class="h-5 w-5 text-indigo-600 mr-2" />
              <h3 class="text-base font-bold text-gray-900">Notifications</h3>
            </div>
            <div class="p-6 space-y-4">
              <label class="flex items-center justify-between">
                <span class="text-sm text-gray-700">Email reminders for upcoming assignments</span>
                <input type="checkbox" checked class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
              </label>
              <label class="flex items-center justify-between">
                <span class="text-sm text-gray-700">Class session reminders</span>
                <input type="checkbox" checked class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
              </label>
              <label class="flex items-center justify-between">
                <span class="text-sm text-gray-700">Grade posting notifications</span>
                <input type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
              </label>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

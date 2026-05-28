<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import AdminSidebar from '../../components/AdminSidebar.vue'
import {
  ArrowLeft, Save, Building2, Globe, Image,
  Shield, Key, Clock, RefreshCw, SaveAll
} from 'lucide-vue-next'

const router = useRouter()

const institution = ref({
  name: '',
  domain: '',
  logo_url: '',
  security_policies: {
    password_min_length: 8,
    session_timeout_minutes: 60,
    require_complex_password: true,
    max_login_attempts: 5,
    two_factor_required: false
  }
})

const isLoading = ref(true)
const isSaving = ref(false)
const saveSuccess = ref(false)

const fetchSettings = async () => {
  isLoading.value = true
  try {
    const res = await api.get('my-institution/')
    const data = res.data
    institution.value = {
      name: data.name || '',
      domain: data.domain || '',
      logo_url: data.logo_url || '',
      security_policies: {
        password_min_length: data.security_policies?.password_min_length ?? 8,
        session_timeout_minutes: data.security_policies?.session_timeout_minutes ?? 60,
        require_complex_password: data.security_policies?.require_complex_password ?? true,
        max_login_attempts: data.security_policies?.max_login_attempts ?? 5,
        two_factor_required: data.security_policies?.two_factor_required ?? false
      }
    }
  } catch (error) {
    console.error("Error fetching institution settings:", error)
  } finally {
    isLoading.value = false
  }
}

const handleSave = async () => {
  isSaving.value = true
  saveSuccess.value = false
  try {
    await api.patch('my-institution/', {
      name: institution.value.name,
      domain: institution.value.domain,
      logo_url: institution.value.logo_url,
      security_policies: institution.value.security_policies
    })
    saveSuccess.value = true
    setTimeout(() => { saveSuccess.value = false }, 3000)
  } catch (error) {
    console.error("Error saving institution settings:", error)
    alert("Failed to save settings. Check console for details.")
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  fetchSettings()
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
                <h1 class="text-xl font-bold text-gray-900 leading-tight">Security & Settings</h1>
                <p class="text-xs text-gray-500 font-medium">Manage institution profile and global policies</p>
              </div>
            </div>
            <button @click="handleSave" :disabled="isSaving"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center disabled:opacity-70">
              <SaveAll class="h-4 w-4 mr-2" /> {{ isSaving ? 'Saving...' : 'Save All Changes' }}
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-8">

        <div v-if="saveSuccess" class="mb-6 px-4 py-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-sm font-medium rounded-lg flex items-center">
          <Save class="h-4 w-4 mr-2 text-emerald-600" /> Settings saved successfully.
        </div>

        <div v-if="isLoading" class="text-center py-10 text-gray-500">
          Loading institution settings...
        </div>

        <template v-else>

          <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
            <div class="flex items-center mb-4 border-b pb-3">
              <Building2 class="h-5 w-5 text-indigo-600 mr-2" />
              <h2 class="text-lg font-bold text-gray-900">University Profile</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Institution Name</label>
                <input v-model="institution.name" type="text" required
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Domain</label>
                <div class="relative">
                  <Globe class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input v-model="institution.domain" type="text" required placeholder="e.g. university.edu"
                    class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                </div>
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 mb-1">Logo URL</label>
                <div class="relative">
                  <Image class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input v-model="institution.logo_url" type="url" placeholder="https://example.com/logo.png"
                    class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
                </div>
                <p class="text-xs text-gray-400 mt-1">Provide a URL to your institution's logo image.</p>
              </div>
            </div>
          </div>

          <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8">
            <div class="flex items-center mb-4 border-b pb-3">
              <Shield class="h-5 w-5 text-indigo-600 mr-2" />
              <h2 class="text-lg font-bold text-gray-900">Security Policies</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  <Key class="h-4 w-4 inline mr-1 text-gray-400" /> Minimum Password Length
                </label>
                <input v-model.number="institution.security_policies.password_min_length" type="number" min="4" max="128"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  <Clock class="h-4 w-4 inline mr-1 text-gray-400" /> Session Timeout (minutes)
                </label>
                <input v-model.number="institution.security_policies.session_timeout_minutes" type="number" min="5" max="1440"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  <RefreshCw class="h-4 w-4 inline mr-1 text-gray-400" /> Max Login Attempts
                </label>
                <input v-model.number="institution.security_policies.max_login_attempts" type="number" min="1" max="20"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 text-sm">
              </div>
            </div>
            <div class="mt-4 space-y-3 pt-4 border-t border-gray-100">
              <label class="flex items-center cursor-pointer">
                <input type="checkbox" v-model="institution.security_policies.require_complex_password"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500">
                <span class="ml-2 text-sm text-gray-700">Require complex passwords (uppercase, lowercase, number, special character)</span>
              </label>
              <label class="flex items-center cursor-pointer">
                <input type="checkbox" v-model="institution.security_policies.two_factor_required"
                  class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500">
                <span class="ml-2 text-sm text-gray-700">Require two-factor authentication for all users</span>
              </label>
            </div>
          </div>

        </template>

      </main>
    </div>
  </div>
</template>

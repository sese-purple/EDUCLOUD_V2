<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import { User, Lock, Loader2, GraduationCap } from 'lucide-vue-next'

const router = useRouter()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await api.post('token/', {
      username: username.value,
      password: password.value
    })

    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)

    let userRole = 'student'

    const uname = username.value.toLowerCase()

    if (uname === 'admin' || uname.includes('admin')) {
      userRole = 'admin'
    } else if (uname.includes('prof') || uname.includes('dr') || uname === 'instructor') {
      userRole = 'instructor'
    }

    switch (userRole) {
      case 'admin':
        router.push({ name: 'admin-dashboard' })
        break
      case 'instructor':
        router.push({ name: 'dashboard' })
        break
      case 'student':
        router.push({ name: 'student-dashboard' })
        break
      default:
        router.push({ name: 'login' })
    }

  } catch (error) {
    errorMessage.value = 'Invalid username or password. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-10 rounded-2xl shadow-xl border border-slate-100 relative overflow-hidden">

      <div class="absolute top-0 left-0 w-full h-1.5 bg-indigo-600"></div>

      <div class="text-center">
        <div class="mx-auto h-12 w-12 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mb-4 shadow-sm">
          <GraduationCap class="h-7 w-7" />
        </div>
        <h2 class="text-3xl font-extrabold text-slate-900 tracking-tight">
          EDUCLOUD <span class="text-indigo-600">2.0</span>
        </h2>
        <p class="mt-2 text-sm text-slate-500 font-medium">Sign in to your institutional workspace</p>
      </div>

      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div v-if="errorMessage" class="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-md transition-all">
          <p class="text-sm text-red-700 font-medium">{{ errorMessage }}</p>
        </div>

        <div class="space-y-5">
          <div>
            <label for="username" class="block text-sm font-medium text-slate-700 mb-1">Username</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User class="h-5 w-5 text-slate-400" />
              </div>
              <input id="username" v-model="username" type="text" required
                class="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-colors"
                placeholder="Enter your username">
            </div>
            <p class="text-[10px] text-slate-400 mt-1">Hint: Use 'admin', 'prof_smith', or 'student_john' to test routing.</p>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock class="h-5 w-5 text-slate-400" />
              </div>
              <input id="password" v-model="password" type="password" required
                class="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-colors"
                placeholder="••••••••">
            </div>
          </div>
        </div>

        <div>
          <button type="submit" :disabled="isLoading"
            class="group relative w-full flex justify-center items-center py-2.5 px-4 border border-transparent text-sm font-semibold rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-70 disabled:cursor-not-allowed transition-all shadow-md">
            <Loader2 v-if="isLoading" class="animate-spin h-5 w-5 mr-2" />
            <span v-if="isLoading">Authenticating...</span>
            <span v-else>Sign In</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

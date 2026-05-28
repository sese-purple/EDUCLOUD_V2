<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  BookOpen, ClipboardList, CheckCircle,
  Award, Bell, Search, LogOut,
  ChevronRight, Clock, FileText
} from 'lucide-vue-next'

const router = useRouter()

const studentStats = ref([
  { name: 'Current GPA', value: '3.8', icon: Award, color: 'text-yellow-600', bg: 'bg-yellow-100' },
  { name: 'Enrolled Modules', value: '4', icon: BookOpen, color: 'text-indigo-600', bg: 'bg-indigo-100' },
  { name: 'Pending Tasks', value: '3', icon: Clock, color: 'text-orange-600', bg: 'bg-orange-100' },
])

const enrolledCourses = ref([
  { id: 1, title: 'Integrated Internship Management', code: 'SYS-400', instructor: 'Dr. Smith', progress: 85, color: 'bg-indigo-500' },
  { id: 2, title: 'Advanced Web Architecture', code: 'SE-301', instructor: 'Prof. Davis', progress: 40, color: 'bg-blue-500' },
])

const pendingTasks = ref([
  { id: 1, title: 'Submit Week 4 Logbook Entry', course: 'SYS-400', due: 'Today, 11:59 PM', type: 'Logbook' },
  { id: 2, title: 'API Security Quiz', course: 'SE-301', due: 'Tomorrow', type: 'Quiz' },
])
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">

    <aside class="w-64 bg-white border-r border-gray-200 flex flex-col hidden md:flex flex-shrink-0 z-20">
      <div class="h-16 flex items-center px-6 border-b border-gray-200">
        <h1 class="text-xl font-bold text-gray-900 tracking-tight">
          EDUCLOUD <span class="text-indigo-600">2.0</span>
        </h1>
      </div>

      <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
        <p class="px-3 text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">My Workspace</p>

        <a href="#" class="flex items-center px-3 py-2.5 bg-indigo-50 text-indigo-700 rounded-lg font-medium group">
          <BookOpen class="w-5 h-5 mr-3 text-indigo-600" /> My Courses
        </a>
        <a href="#" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors group">
          <ClipboardList class="w-5 h-5 mr-3 text-gray-400 group-hover:text-indigo-600 transition-colors" /> Digital Logbook
        </a>
        <a href="#" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors group">
          <CheckCircle class="w-5 h-5 mr-3 text-gray-400 group-hover:text-indigo-600 transition-colors" /> Assignments
        </a>
        <a href="#" class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors group">
          <Award class="w-5 h-5 mr-3 text-gray-400 group-hover:text-indigo-600 transition-colors" /> Official Marksheet
        </a>
      </nav>

      <div class="p-4 border-t border-gray-200">
        <a @click="router.push('/login')" class="flex items-center px-3 py-2.5 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors mt-1 cursor-pointer">
          <LogOut class="w-5 h-5 mr-3 text-red-500" /> Sign Out
        </a>
      </div>
    </aside>

    <div class="flex-1 flex flex-col overflow-hidden">

      <header class="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shadow-sm z-10">
        <div class="flex items-center flex-1">
          <div class="relative w-full max-w-md hidden sm:block">
            <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input type="text" placeholder="Search courses or materials..." class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm">
          </div>
        </div>
        <div class="flex items-center space-x-4">
          <Bell class="h-6 w-6 text-gray-400 hover:text-gray-600 cursor-pointer" />
          <div class="h-8 w-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold shadow-md cursor-pointer">
            S </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">

        <div class="mb-8 bg-indigo-900 rounded-2xl p-8 text-white shadow-lg relative overflow-hidden">
          <div class="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-indigo-600 rounded-full opacity-50 blur-3xl"></div>
          <h2 class="text-2xl font-bold relative z-10">Welcome back, Student</h2>
          <p class="text-indigo-200 mt-2 max-w-xl relative z-10">You have 1 pending logbook entry due today. Keep up the great work on your internship modules!</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div v-for="stat in studentStats" :key="stat.name" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center">
            <div :class="[stat.bg, 'p-3 rounded-lg mr-4']">
              <component :is="stat.icon" :class="['h-6 w-6', stat.color]" />
            </div>
            <div>
              <p class="text-sm font-medium text-gray-500">{{ stat.name }}</p>
              <h3 class="text-2xl font-bold text-gray-900">{{ stat.value }}</h3>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

          <div class="lg:col-span-2">
            <h3 class="text-lg font-bold text-gray-900 mb-4">My Official Modules</h3>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <ul class="divide-y divide-gray-200">
                <li v-for="course in enrolledCourses" :key="course.id" class="p-6 hover:bg-gray-50 transition-colors cursor-pointer flex items-center justify-between">
                  <div class="flex items-center space-x-4 w-full">
                    <div :class="[course.color, 'h-12 w-12 rounded-lg flex items-center justify-center shadow-inner flex-shrink-0']">
                      <span class="text-white font-bold text-sm">{{ course.code.split('-')[0] }}</span>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-bold text-gray-900 truncate">{{ course.title }}</p>
                      <p class="text-sm text-gray-500 truncate">{{ course.code }} • Prof: {{ course.instructor }}</p>
                    </div>
                    <div class="hidden sm:block w-32">
                      <div class="flex justify-between text-xs mb-1">
                        <span class="text-gray-500">Progress</span>
                        <span class="font-medium text-gray-900">{{ course.progress }}%</span>
                      </div>
                      <div class="w-full bg-gray-200 rounded-full h-1.5">
                        <div class="bg-indigo-600 h-1.5 rounded-full" :style="{ width: course.progress + '%' }"></div>
                      </div>
                    </div>
                  </div>
                  <ChevronRight class="h-5 w-5 text-gray-400 ml-4 flex-shrink-0" />
                </li>
              </ul>
            </div>
          </div>

          <div>
            <h3 class="text-lg font-bold text-gray-900 mb-4">Action Required</h3>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <ul class="space-y-4">
                <li v-for="task in pendingTasks" :key="task.id" class="flex items-start">
                  <div class="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center mr-3 flex-shrink-0 mt-0.5">
                    <FileText v-if="task.type === 'Logbook'" class="h-4 w-4 text-orange-600" />
                    <CheckCircle v-else class="h-4 w-4 text-orange-600" />
                  </div>
                  <div>
                    <p class="text-sm font-bold text-gray-900">{{ task.title }}</p>
                    <p class="text-xs text-gray-500 mt-0.5">{{ task.course }} • Due: {{ task.due }}</p>
                  </div>
                </li>
              </ul>
              <button class="w-full mt-6 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-100 transition-colors">
                View All Tasks
              </button>
            </div>
          </div>

        </div>
      </main>
    </div>
  </div>
</template>

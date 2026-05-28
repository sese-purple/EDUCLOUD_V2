<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  ArrowLeft, Users, FileText, BookOpen, 
  Video, UploadCloud, Plus, Calendar, FileBadge2
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute() // This will eventually grab the course ID from the URL

// State for our Tabbed Navigation
const activeTab = ref('documents')

const tabs = [
  { id: 'documents', name: 'Materials', icon: FileText },
  { id: 'students', name: 'Roster', icon: Users },
  { id: 'assignments', name: 'Assignments', icon: FileBadge2 },
  { id: 'quizzes', name: 'Quizzes', icon: BookOpen },
  { id: 'live', name: 'Live Classes', icon: Video },
]

// Mock Data for the different tabs
const materials = ref([
  { id: 1, name: 'Syllabus & Grading Rubric.pdf', type: 'PDF', size: '2.4 MB', date: 'Oct 12' },
  { id: 2, name: 'Lecture 1: Intro to Web Architecture.pptx', type: 'Slides', size: '15 MB', date: 'Oct 14' },
])

const assignments = ref([
  { id: 1, title: 'Individual: API Design Draft', type: 'Individual', submitted: 42, total: 45, due: 'Tomorrow' },
  { id: 2, title: 'Group: Kanban Sprint 1', type: 'Group', submitted: 8, total: 10, due: 'In 3 days' },
])
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col font-sans">
    
    <header class="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <button @click="router.push({ name: 'dashboard' })" class="mr-4 text-gray-400 hover:text-indigo-600 transition-colors">
              <ArrowLeft class="h-6 w-6" />
            </button>
            <div>
              <h1 class="text-xl font-bold text-gray-900 leading-tight">Advanced Web Architecture</h1>
              <p class="text-xs text-gray-500 font-medium">SE-301 • 45 Students Enrolled</p>
            </div>
          </div>
          
          <button class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center">
            <Settings class="h-4 w-4 mr-2" /> Manage Course
          </button>
        </div>

        <div class="flex space-x-8 mt-2 overflow-x-auto">
          <button 
            v-for="tab in tabs" :key="tab.id"
            @click="activeTab = tab.id"
            :class="[
              activeTab === tab.id 
                ? 'border-indigo-500 text-indigo-600' 
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm flex items-center transition-colors'
            ]"
          >
            <component :is="tab.icon" :class="[activeTab === tab.id ? 'text-indigo-600' : 'text-gray-400', 'h-4 w-4 mr-2']" />
            {{ tab.name }}
          </button>
        </div>
      </div>
    </header>

    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      <div v-show="activeTab === 'documents'" class="animate-fade-in">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-gray-900">Course Materials</h2>
          <button class="flex items-center text-sm font-medium text-indigo-600 bg-indigo-50 px-3 py-1.5 rounded-lg hover:bg-indigo-100 transition-colors">
            <UploadCloud class="h-4 w-4 mr-2" /> Upload File
          </button>
        </div>
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <ul class="divide-y divide-gray-200">
            <li v-for="doc in materials" :key="doc.id" class="p-4 hover:bg-gray-50 flex items-center justify-between cursor-pointer">
              <div class="flex items-center">
                <div class="h-10 w-10 bg-red-100 text-red-600 rounded-lg flex items-center justify-center mr-4">
                  <FileText class="h-5 w-5" />
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ doc.name }}</p>
                  <p class="text-xs text-gray-500">{{ doc.type }} • {{ doc.size }} • Added {{ doc.date }}</p>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div v-show="activeTab === 'assignments'" class="animate-fade-in">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-gray-900">Student Submissions</h2>
          <button class="flex items-center text-sm font-medium text-white bg-indigo-600 px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-colors">
            <Plus class="h-4 w-4 mr-2" /> New Assignment
          </button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div v-for="task in assignments" :key="task.id" class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
            <div class="flex justify-between items-start mb-4">
              <span :class="[task.type === 'Group' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700', 'text-xs font-bold px-2.5 py-0.5 rounded-full']">
                {{ task.type }} Project
              </span>
              <span class="text-xs text-gray-500 flex items-center">
                <Calendar class="h-3 w-3 mr-1" /> Due: {{ task.due }}
              </span>
            </div>
            <h3 class="text-md font-bold text-gray-900 mb-1">{{ task.title }}</h3>
            <div class="mt-4">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-gray-500">Submitted</span>
                <span class="font-medium text-gray-900">{{ task.submitted }} / {{ task.total }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-emerald-500 h-2 rounded-full" :style="{ width: (task.submitted / task.total) * 100 + '%' }"></div>
              </div>
            </div>
            <button class="mt-5 w-full py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
              Grade Submissions
            </button>
          </div>
        </div>
      </div>

      <div v-show="activeTab === 'live'" class="animate-fade-in">
        <div class="bg-indigo-900 rounded-2xl shadow-lg overflow-hidden relative">
          <div class="absolute top-0 right-0 -mt-4 -mr-4 w-32 h-32 bg-indigo-700 rounded-full opacity-50 blur-2xl"></div>
          <div class="p-8 relative z-10 text-white flex flex-col md:flex-row items-center justify-between">
            <div>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-500 text-white mb-4 animate-pulse">
                • Live Session Available
              </span>
              <h2 class="text-2xl font-bold mb-2">Lecture 4: Database ORMs</h2>
              <p class="text-indigo-200 text-sm mb-6 max-w-md">Host your secure online class. Attendance is automatically tracked via GPS and system logs.</p>
              <button class="bg-white text-indigo-900 px-6 py-3 rounded-lg font-bold shadow-md hover:bg-gray-50 transition-colors flex items-center">
                <Video class="h-5 w-5 mr-2 text-indigo-600" /> Launch Virtual Classroom
              </button>
            </div>
            <div class="hidden md:block">
              <Video class="h-32 w-32 text-indigo-800 opacity-50" />
            </div>
          </div>
        </div>
      </div>

      <div v-show="activeTab === 'quizzes' || activeTab === 'students'" class="text-center py-20 animate-fade-in">
        <component :is="activeTab === 'quizzes' ? BookOpen : Users" class="mx-auto h-12 w-12 text-gray-300 mb-4" />
        <h3 class="text-lg font-medium text-gray-900">Module under development</h3>
        <p class="text-sm text-gray-500">Connect this to your Django backend to see real data.</p>
      </div>

    </main>
  </div>
</template>

<style>
/* A tiny CSS animation to make tab switching feel smooth */
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(5px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
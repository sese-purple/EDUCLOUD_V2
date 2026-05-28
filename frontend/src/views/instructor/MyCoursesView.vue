<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import { BookOpen, ChevronRight, ClipboardList } from 'lucide-vue-next'

const router = useRouter()
const courses = ref<any[]>([])
const isLoading = ref(true)

onMounted(async () => {
  try {
    const res = await api.get('instructor-dashboard/')
    courses.value = res.data.courses
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <InstructorSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-16 bg-white border-b border-gray-200 flex items-center px-6 shadow-sm z-10">
        <ClipboardList class="h-5 w-5 text-indigo-600 mr-3" />
        <h2 class="text-lg font-bold text-gray-800">My Courses</h2>
      </header>
      <main class="flex-1 overflow-y-auto p-8">
        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading courses...</div>
        <div v-else-if="courses.length === 0" class="text-center py-16">
          <BookOpen class="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900">No courses assigned</h3>
          <p class="text-sm text-gray-500 mt-1">Contact your institution admin to get assigned to a course.</p>
        </div>
        <div v-else class="max-w-4xl mx-auto space-y-4">
          <div v-for="course in courses" :key="course.id"
               @click="router.push(`/course/${course.id}`)"
               class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 hover:shadow-md transition-all cursor-pointer flex items-center justify-between group">
            <div class="flex items-center space-x-4">
              <div class="h-14 w-14 bg-indigo-100 rounded-xl flex items-center justify-center shadow-inner">
                <span class="text-indigo-700 font-bold text-base">{{ course.course_code?.split('-')[0] }}</span>
              </div>
              <div>
                <p class="text-base font-bold text-gray-900">{{ course.title }}</p>
                <p class="text-sm text-gray-500">{{ course.course_code }} • {{ course.students }} enrolled</p>
              </div>
            </div>
            <ChevronRight class="h-5 w-5 text-gray-300 group-hover:text-gray-500 transition-colors" />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

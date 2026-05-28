<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  ArrowLeft, Plus, Pencil, Trash2,
  BookOpen, Clock, ListChecks, X, Check,
  AlertCircle
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const courseId = computed(() => Number(route.params.id))

interface Question {
  id?: number
  question_text: string
  options: string[]
  correct_answer_index: number
  points: number
}

interface Quiz {
  id?: number
  title: string
  description: string
  time_limit: number
  total_points: number
  is_active: boolean
  due_date: string | null
  allow_multiple_attempts: boolean
  questions: Question[]
}

const quizzes = ref<Quiz[]>([])
const course = ref<any>(null)
const isLoading = ref(true)
const showForm = ref(false)
const editingQuiz = ref<Quiz | null>(null)
const saving = ref(false)

const emptyQuiz = (): Quiz => ({
  title: '',
  description: '',
  time_limit: 60,
  total_points: 0,
  is_active: true,
  due_date: null,
  allow_multiple_attempts: false,
  questions: [{ question_text: '', options: ['', ''], correct_answer_index: 0, points: 1 }],
})

const form = ref<Quiz>(emptyQuiz())

onMounted(async () => {
  try {
    const [courseRes, quizRes] = await Promise.all([
      api.get(`courses/${courseId.value}/`),
      api.get('quizzes/', { params: { course: courseId.value } }),
    ])
    course.value = courseRes.data
    quizzes.value = quizRes.data
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
})

const openCreate = () => {
  form.value = emptyQuiz()
  editingQuiz.value = null
  showForm.value = true
}

const openEdit = (quiz: Quiz) => {
  form.value = {
    ...quiz,
    due_date: quiz.due_date ? quiz.due_date.slice(0, 16) : null,
    questions: quiz.questions.length ? quiz.questions.map(q => ({ ...q })) : [{ question_text: '', options: ['', ''], correct_answer_index: 0, points: 1 }],
  }
  editingQuiz.value = quiz
  showForm.value = true
}

const cancelForm = () => {
  showForm.value = false
  form.value = emptyQuiz()
  editingQuiz.value = null
}

const addQuestion = () => {
  form.value.questions.push({ question_text: '', options: ['', ''], correct_answer_index: 0, points: 1 })
}

const removeQuestion = (idx: number) => {
  form.value.questions.splice(idx, 1)
}

const addOption = (qIdx: number) => {
  form.value.questions[qIdx].options.push('')
}

const removeOption = (qIdx: number, oIdx: number) => {
  if (form.value.questions[qIdx].options.length <= 2) return
  form.value.questions[qIdx].options.splice(oIdx, 1)
  if (form.value.questions[qIdx].correct_answer_index >= form.value.questions[qIdx].options.length) {
    form.value.questions[qIdx].correct_answer_index = 0
  }
}

const totalPoints = computed(() =>
  form.value.questions.reduce((sum, q) => sum + (q.points || 0), 0)
)

const saveQuiz = async () => {
  if (!form.value.title.trim()) return
  saving.value = true
  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      course: courseId.value,
      time_limit: form.value.time_limit,
      is_active: form.value.is_active,
      due_date: form.value.due_date || null,
      allow_multiple_attempts: form.value.allow_multiple_attempts,
      total_points: totalPoints.value,
    }
    if (editingQuiz.value?.id) {
      await api.patch(`quizzes/${editingQuiz.value.id}/`, payload)
      for (const q of form.value.questions) {
        if (q.id) {
          await api.patch(`questions/${q.id}/`, { ...q, quiz: editingQuiz.value.id })
        } else {
          await api.post('questions/', { ...q, quiz: editingQuiz.value.id })
        }
      }
    } else {
      const quizRes = await api.post('quizzes/', payload)
      const quizId = quizRes.data.id
      for (const q of form.value.questions) {
        await api.post('questions/', { ...q, quiz: quizId })
      }
    }
    const res = await api.get('quizzes/', { params: { course: courseId.value } })
    quizzes.value = res.data
    showForm.value = false
  } catch (err) {
    console.error(err)
  } finally {
    saving.value = false
  }
}

const deleteQuiz = async (quiz: Quiz) => {
  if (!confirm(`Delete quiz "${quiz.title}"?`)) return
  try {
    await api.delete(`quizzes/${quiz.id}/`)
    quizzes.value = quizzes.value.filter(q => q.id !== quiz.id)
  } catch (err) {
    console.error(err)
  }
}

const confirmDelete = ref<number | null>(null)
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <InstructorSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0">
        <div class="px-6">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center">
              <button @click="router.push(`/course/${courseId}`)" class="mr-4 text-gray-400 hover:text-indigo-600 transition-colors">
                <ArrowLeft class="h-6 w-6" />
              </button>
              <div>
                <h1 class="text-xl font-bold text-gray-900 leading-tight">Quiz Manager</h1>
                <p v-if="course" class="text-xs text-gray-500 font-medium">{{ course.title }}</p>
              </div>
            </div>
            <button @click="openCreate"
              class="flex items-center text-sm font-medium text-white bg-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
              <Plus class="h-4 w-4 mr-2" /> New Quiz
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-8">

        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading quizzes...</div>

        <template v-else>

          <!-- Quiz Form Slide-down -->
          <div v-if="showForm" class="mb-8 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-fade-in">
            <div class="px-6 py-5 border-b border-gray-200 flex items-center justify-between">
              <h3 class="text-lg font-bold text-gray-900">{{ editingQuiz ? 'Edit Quiz' : 'Create New Quiz' }}</h3>
              <button @click="cancelForm" class="text-gray-400 hover:text-gray-600 transition-colors">
                <X class="h-5 w-5" />
              </button>
            </div>
            <div class="p-6 space-y-6">
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-1">Quiz Title</label>
                  <input v-model="form.title" type="text" placeholder="e.g. Midterm Assessment"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Time Limit (min)</label>
                  <input v-model.number="form.time_limit" type="number" min="1"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea v-model="form.description" rows="2" placeholder="Optional description..."
                  class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none"></textarea>
              </div>
              <div class="flex items-center space-x-6">
                <label class="flex items-center space-x-2 text-sm text-gray-700">
                  <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  <span>Active</span>
                </label>
                <label class="flex items-center space-x-2 text-sm text-gray-700">
                  <input v-model="form.allow_multiple_attempts" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  <span>Allow multiple attempts</span>
                </label>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Due date</label>
                  <input v-model="form.due_date" type="datetime-local"
                    class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                </div>
              </div>

              <div class="border-t border-gray-200 pt-6">
                <div class="flex items-center justify-between mb-4">
                  <h4 class="text-base font-bold text-gray-900 flex items-center"><ListChecks class="h-4 w-4 mr-2" /> Questions</h4>
                  <div class="text-sm text-gray-500">Total: <strong>{{ totalPoints }}</strong> points</div>
                </div>

                <div v-for="(q, qi) in form.questions" :key="qi" class="mb-6 p-4 bg-gray-50 rounded-xl border border-gray-200">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-bold text-gray-700">Question {{ qi + 1 }}</span>
                    <button v-if="form.questions.length > 1" @click="removeQuestion(qi)" class="text-red-400 hover:text-red-600 transition-colors">
                      <Trash2 class="h-4 w-4" />
                    </button>
                  </div>
                  <div class="mb-3">
                    <input v-model="q.question_text" type="text" placeholder="Enter question text"
                      class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                  </div>
                  <div class="mb-3">
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-medium text-gray-500">Options</span>
                      <button @click="addOption(qi)" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium">+ Add option</button>
                    </div>
                    <div v-for="(_, oi) in q.options" :key="oi" class="flex items-center space-x-2 mb-1.5">
                      <input type="radio" :name="'correct-' + qi" :checked="q.correct_answer_index === oi"
                        @change="q.correct_answer_index = oi" class="text-indigo-600 focus:ring-indigo-500" />
                      <input v-model="q.options[oi]" type="text" :placeholder="'Option ' + (oi + 1)"
                        class="flex-1 border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                      <button v-if="q.options.length > 2" @click="removeOption(qi, oi)" class="text-gray-300 hover:text-red-500 transition-colors">
                        <X class="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2 text-sm">
                    <label class="text-gray-600">Points:</label>
                    <input v-model.number="q.points" type="number" min="1"
                      class="w-20 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                  </div>
                </div>

                <button @click="addQuestion" class="flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors">
                  <Plus class="h-4 w-4 mr-1.5" /> Add Question
                </button>
              </div>

              <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                <button @click="cancelForm" class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">Cancel</button>
                <button @click="saveQuiz" :disabled="saving || !form.title.trim()"
                  class="px-6 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg transition-colors shadow-sm">
                  {{ saving ? 'Saving...' : editingQuiz ? 'Update Quiz' : 'Create Quiz' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Quiz List -->
          <div v-if="quizzes.length === 0 && !showForm" class="text-center py-16">
            <BookOpen class="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900">No quizzes yet</h3>
            <p class="text-sm text-gray-500 mt-1">Create your first quiz to assess student learning.</p>
          </div>

          <div v-for="quiz in quizzes" :key="quiz.id" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-4">
            <div class="px-6 py-5 flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <h3 class="text-base font-bold text-gray-900">{{ quiz.title }}</h3>
                  <span :class="[quiz.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500', 'text-xs font-medium px-2 py-0.5 rounded-full']">
                    {{ quiz.is_active ? 'Active' : 'Draft' }}
                  </span>
                </div>
                <p v-if="quiz.description" class="text-sm text-gray-500 mt-1">{{ quiz.description }}</p>
                <div class="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                  <span class="flex items-center"><Clock class="h-3 w-3 mr-1" /> {{ quiz.time_limit }} min</span>
                  <span class="flex items-center"><ListChecks class="h-3 w-3 mr-1" /> {{ quiz.questions?.length || 0 }} questions</span>
                  <span class="flex items-center"><Check class="h-3 w-3 mr-1" /> {{ quiz.total_points || 0 }} points</span>
                  <span v-if="quiz.due_date" class="flex items-center"><AlertCircle class="h-3 w-3 mr-1" /> Due {{ new Date(quiz.due_date).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }}</span>
                </div>
              </div>
              <div class="flex items-center space-x-2 ml-4">
                <button @click="openEdit(quiz)" class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                  <Pencil class="h-4 w-4" />
                </button>
                <button @click="confirmDelete = quiz.id!" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                  <Trash2 class="h-4 w-4" />
                </button>
              </div>
            </div>
            <div v-if="confirmDelete === quiz.id" class="px-6 py-3 bg-red-50 border-t border-red-200 flex items-center justify-between">
              <span class="text-sm text-red-700 font-medium">Delete this quiz?</span>
              <div class="flex items-center space-x-2">
                <button @click="confirmDelete = null" class="px-3 py-1.5 text-sm text-gray-600 hover:bg-white rounded-lg transition-colors">Cancel</button>
                <button @click="deleteQuiz(quiz); confirmDelete = null" class="px-3 py-1.5 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors">Delete</button>
              </div>
            </div>
          </div>

        </template>

      </main>
    </div>
  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.25s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

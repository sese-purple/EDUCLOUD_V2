<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'
import InstructorSidebar from '../../components/InstructorSidebar.vue'
import {
  Plus, Pencil, Trash2, BookOpen, Clock, ListChecks, X, Check,
  AlertCircle, BarChart3, ClipboardList, GraduationCap, Users,
  ChevronDown, Award, TrendingUp, TrendingDown, Minus, Eye, Search
} from 'lucide-vue-next'

const router = useRouter()
const activeTab = ref<'builder' | 'queue' | 'analytics'>('builder')
const courses = ref<any[]>([])
const selectedCourseId = ref<number | null>(null)
const quizzes = ref<any[]>([])
const attempts = ref<any[]>([])
const isLoading = ref(false)

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
  course: number
  questions: Question[]
}

const showForm = ref(false)
const editingQuiz = ref<Quiz | null>(null)
const saving = ref(false)
const confirmDelete = ref<number | null>(null)

const emptyQuiz = (): Quiz => ({
  title: '',
  description: '',
  time_limit: 60,
  total_points: 0,
  is_active: true,
  due_date: null,
  allow_multiple_attempts: false,
  course: 0,
  questions: [{ question_text: '', options: ['', ''], correct_answer_index: 0, points: 1 }],
})

const form = ref<Quiz>(emptyQuiz())

const fetchCourses = async () => {
  try {
    const res = await api.get('instructor-dashboard/')
    courses.value = res.data.courses || []
    if (courses.value.length === 1) selectedCourseId.value = courses.value[0].id
  } catch { }
}

const fetchData = async () => {
  if (!selectedCourseId.value) { quizzes.value = []; attempts.value = []; return }
  isLoading.value = true
  try {
    const [quizRes, attemptRes] = await Promise.all([
      api.get('quizzes/', { params: { course: selectedCourseId.value } }),
      api.get('attempts/', { params: { quiz__course: selectedCourseId.value } }),
    ])
    quizzes.value = quizRes.data
    attempts.value = attemptRes.data
  } catch { }
  finally { isLoading.value = false }
}

watch(selectedCourseId, fetchData)
onMounted(fetchCourses)

// ---- Builder ----
const openCreate = () => {
  form.value = { ...emptyQuiz(), course: selectedCourseId.value || 0 }
  editingQuiz.value = null
  showForm.value = true
}

const openEdit = (quiz: Quiz) => {
  form.value = {
    ...quiz,
    due_date: quiz.due_date ? quiz.due_date.slice(0, 16) : null,
    questions: quiz.questions.length
      ? quiz.questions.map(q => ({ ...q }))
      : [{ question_text: '', options: ['', ''], correct_answer_index: 0, points: 1 }],
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
  if (!form.value.title.trim() || !selectedCourseId.value) return
  saving.value = true
  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      course: selectedCourseId.value,
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
    const res = await api.get('quizzes/', { params: { course: selectedCourseId.value } })
    quizzes.value = res.data
    showForm.value = false
  } catch (err) { console.error(err) }
  finally { saving.value = false }
}

const deleteQuiz = async (quiz: Quiz) => {
  if (!confirm(`Delete quiz "${quiz.title}"?`)) return
  try {
    await api.delete(`quizzes/${quiz.id}/`)
    quizzes.value = quizzes.value.filter(q => q.id !== quiz.id)
  } catch { }
}

// ---- Grading Queue ----
const queueSearch = ref('')

const gradedAttempts = computed(() => {
  let list = attempts.value.filter(a => a.is_completed)
  if (queueSearch.value.trim()) {
    const q = queueSearch.value.toLowerCase()
    list = list.filter(a => a.student?.first_name?.toLowerCase().includes(q) ||
      a.student?.last_name?.toLowerCase().includes(q) ||
      a.quiz?.title?.toLowerCase().includes(q))
  }
  return list.sort((a: any, b: any) => new Date(b.submitted_at || b.started_at).getTime() - new Date(a.submitted_at || a.started_at).getTime())
})

// ---- Analytics ----
const quizAnalytics = computed(() => {
  return quizzes.value.map(quiz => {
    const quizAttempts = attempts.value.filter((a: any) => a.quiz?.id === quiz.id && a.is_completed)
    const count = quizAttempts.length
    const avgScore = count ? quizAttempts.reduce((sum: number, a: any) => sum + (a.percentage || 0), 0) / count : 0
    const avgPoints = count ? quizAttempts.reduce((sum: number, a: any) => sum + (a.score || 0), 0) / count : 0
    const passCount = quizAttempts.filter((a: any) => (a.percentage || 0) >= 50).length
    const passRate = count ? (passCount / count) * 100 : 0

    let hardestQuestion: any = null
    let lowestCorrectRate = 1
    if (quiz.questions?.length && quizAttempts.length) {
      for (const q of quiz.questions) {
        let correct = 0
        let total = 0
        for (const a of quizAttempts) {
          const answer = a.answers?.find((ans: any) => ans.question === q.id)
          if (answer) {
            total++
            if (answer.is_correct) correct++
          }
        }
        const rate = total ? correct / total : 1
        if (rate < lowestCorrectRate) {
          lowestCorrectRate = rate
          hardestQuestion = { question: q, correctRate: rate, total }
        }
      }
    }

    return { quiz, count, avgScore, avgPoints, passRate, hardestQuestion }
  })
})

const overallAverage = computed(() => {
  const all = quizAnalytics.value.filter(a => a.count > 0)
  if (!all.length) return 0
  return all.reduce((s, a) => s + a.avgScore, 0) / all.length
})

const totalAttempts = computed(() =>
  attempts.value.filter((a: any) => a.is_completed).length
)
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <InstructorSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0 shadow-sm">
        <div class="px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <ClipboardList class="h-5 w-5 text-indigo-600" />
              <h1 class="text-xl font-bold text-gray-900">Assessment Manager</h1>
              <div class="h-6 w-px bg-gray-200" />
              <select v-model.number="selectedCourseId"
                class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm font-medium text-gray-700 bg-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none min-w-[200px]">
                <option :value="null" disabled>Select course...</option>
                <option v-for="c in courses" :key="c.id" :value="c.id">{{ c.course_code }} — {{ c.title }}</option>
              </select>
            </div>
          </div>
          <div class="flex items-center gap-1 mt-3 border-b border-gray-200 -mb-4">
            <button @click="activeTab = 'builder'"
              :class="[activeTab === 'builder' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-500 hover:text-gray-700', 'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5']">
              <ListChecks class="h-4 w-4" /> Builder
            </button>
            <button @click="activeTab = 'queue'"
              :class="[activeTab === 'queue' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-500 hover:text-gray-700', 'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5']">
              <ClipboardList class="h-4 w-4" /> Grading Queue
              <span v-if="gradedAttempts.length" class="ml-1 text-[10px] bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded-full font-bold">{{ gradedAttempts.length }}</span>
            </button>
            <button @click="activeTab = 'analytics'"
              :class="[activeTab === 'analytics' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-500 hover:text-gray-700', 'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5']">
              <BarChart3 class="h-4 w-4" /> Analytics
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-6">
        <div v-if="!selectedCourseId" class="flex flex-col items-center justify-center h-full text-gray-400">
          <div class="bg-gray-100 rounded-full p-6 mb-4">
            <ClipboardList class="h-12 w-12" />
          </div>
          <p class="text-lg font-medium text-gray-500">Select a course to manage assessments</p>
          <p class="text-sm text-gray-400 mt-1">Choose from the dropdown above</p>
        </div>

        <div v-else-if="isLoading" class="text-center py-16 text-gray-500">Loading...</div>

        <!-- ============ BUILDER TAB ============ -->
        <template v-else-if="activeTab === 'builder'">
          <div class="flex items-center justify-between mb-4">
            <p class="text-sm text-gray-500">{{ quizzes.length }} quiz{{ quizzes.length !== 1 ? 'zes' : '' }}</p>
            <button @click="openCreate"
              class="flex items-center text-sm font-medium text-white bg-indigo-600 px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm">
              <Plus class="h-4 w-4 mr-1.5" /> New Quiz
            </button>
          </div>

          <div v-if="showForm" class="mb-8 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden animate-fade-in">
            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 class="text-lg font-bold text-gray-900">{{ editingQuiz ? 'Edit Quiz' : 'Create New Quiz' }}</h3>
              <button @click="cancelForm" class="text-gray-400 hover:text-gray-600"><X class="h-5 w-5" /></button>
            </div>
            <div class="p-6 space-y-5">
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
              <div class="flex items-center gap-6">
                <label class="flex items-center gap-2 text-sm text-gray-700">
                  <input v-model="form.is_active" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  <span>Active</span>
                </label>
                <label class="flex items-center gap-2 text-sm text-gray-700">
                  <input v-model="form.allow_multiple_attempts" type="checkbox" class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  <span>Allow multiple attempts</span>
                </label>
                <div>
                  <label class="block text-xs font-medium text-gray-700 mb-1">Due date</label>
                  <input v-model="form.due_date" type="datetime-local"
                    class="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                </div>
              </div>

              <div class="border-t border-gray-200 pt-5">
                <div class="flex items-center justify-between mb-4">
                  <h4 class="text-base font-bold text-gray-900 flex items-center gap-2"><ListChecks class="h-4 w-4" /> Questions</h4>
                  <div class="text-sm text-gray-500">Total: <strong>{{ totalPoints }}</strong> points</div>
                </div>
                <div v-for="(q, qi) in form.questions" :key="qi" class="mb-4 p-4 bg-gray-50 rounded-xl border border-gray-200">
                  <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-bold text-gray-700">Question {{ qi + 1 }}</span>
                    <button v-if="form.questions.length > 1" @click="removeQuestion(qi)" class="text-red-400 hover:text-red-600"><Trash2 class="h-4 w-4" /></button>
                  </div>
                  <input v-model="q.question_text" type="text" placeholder="Enter question text"
                    class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none mb-3" />
                  <div class="mb-2">
                    <div class="flex items-center justify-between mb-2">
                      <span class="text-xs font-medium text-gray-500">Options</span>
                      <button @click="addOption(qi)" class="text-xs text-indigo-600 hover:text-indigo-800 font-medium">+ Add option</button>
                    </div>
                    <div v-for="(_, oi) in q.options" :key="oi" class="flex items-center gap-2 mb-1.5">
                      <input type="radio" :name="'correct-' + qi" :checked="q.correct_answer_index === oi"
                        @change="q.correct_answer_index = oi" class="text-indigo-600 focus:ring-indigo-500 shrink-0" />
                      <input v-model="q.options[oi]" type="text" :placeholder="'Option ' + (oi + 1)"
                        class="flex-1 border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                      <button v-if="q.options.length > 2" @click="removeOption(qi, oi)" class="text-gray-300 hover:text-red-500"><X class="h-3.5 w-3.5" /></button>
                    </div>
                  </div>
                  <div class="flex items-center gap-2 text-sm">
                    <label class="text-gray-600">Points:</label>
                    <input v-model.number="q.points" type="number" min="1"
                      class="w-20 border border-gray-300 rounded-lg px-2 py-1 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
                  </div>
                </div>
                <button @click="addQuestion" class="flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-800">
                  <Plus class="h-4 w-4 mr-1.5" /> Add Question
                </button>
              </div>
              <div class="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button @click="cancelForm" class="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">Cancel</button>
                <button @click="saveQuiz" :disabled="saving || !form.title.trim()"
                  class="px-6 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 rounded-lg shadow-sm">
                  {{ saving ? 'Saving...' : editingQuiz ? 'Update Quiz' : 'Create Quiz' }}
                </button>
              </div>
            </div>
          </div>

          <div v-if="!quizzes.length && !showForm" class="text-center py-16">
            <BookOpen class="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h3 class="text-lg font-medium text-gray-900">No quizzes yet</h3>
            <p class="text-sm text-gray-500 mt-1">Create your first quiz to assess student learning.</p>
          </div>

          <div v-for="quiz in quizzes" :key="quiz.id" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-4">
            <div class="px-6 py-4 flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3">
                  <h3 class="text-base font-bold text-gray-900 truncate">{{ quiz.title }}</h3>
                  <span :class="[quiz.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-500', 'text-xs font-medium px-2 py-0.5 rounded-full whitespace-nowrap']">
                    {{ quiz.is_active ? 'Active' : 'Draft' }}
                  </span>
                </div>
                <p v-if="quiz.description" class="text-sm text-gray-500 mt-1 truncate">{{ quiz.description }}</p>
                <div class="flex items-center gap-4 mt-2 text-xs text-gray-400">
                  <span class="flex items-center gap-1"><Clock class="h-3 w-3" /> {{ quiz.time_limit }} min</span>
                  <span class="flex items-center gap-1"><ListChecks class="h-3 w-3" /> {{ quiz.questions?.length || 0 }} questions</span>
                  <span class="flex items-center gap-1"><Check class="h-3 w-3" /> {{ quiz.total_points || 0 }} pts</span>
                  <span v-if="quiz.due_date" class="flex items-center gap-1"><AlertCircle class="h-3 w-3" /> Due {{ new Date(quiz.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }}</span>
                </div>
              </div>
              <div class="flex items-center gap-2 ml-4 shrink-0">
                <button @click="openEdit(quiz)" class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg"><Pencil class="h-4 w-4" /></button>
                <button @click="confirmDelete = quiz.id!" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"><Trash2 class="h-4 w-4" /></button>
              </div>
            </div>
            <div v-if="confirmDelete === quiz.id" class="px-6 py-3 bg-red-50 border-t border-red-200 flex items-center justify-between">
              <span class="text-sm text-red-700 font-medium">Delete this quiz and all its attempts?</span>
              <div class="flex items-center gap-2">
                <button @click="confirmDelete = null" class="px-3 py-1.5 text-sm text-gray-600 hover:bg-white rounded-lg">Cancel</button>
                <button @click="deleteQuiz(quiz); confirmDelete = null" class="px-3 py-1.5 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg">Delete</button>
              </div>
            </div>
          </div>
        </template>

        <!-- ============ GRADING QUEUE TAB ============ -->
        <template v-else-if="activeTab === 'queue'">
          <div class="flex items-center justify-between mb-4">
            <div class="relative max-w-sm">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
              <input v-model="queueSearch" type="text" placeholder="Search by student or quiz..."
                class="w-full pl-8 pr-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-indigo-500 focus:border-indigo-500 outline-none" />
            </div>
            <span class="text-sm text-gray-500">{{ gradedAttempts.length }} submission{{ gradedAttempts.length !== 1 ? 's' : '' }}</span>
          </div>

          <div v-if="!gradedAttempts.length" class="text-center py-16 text-gray-400">
            <ClipboardList class="h-12 w-12 mx-auto mb-3" />
            <p class="text-base font-medium text-gray-500">No submissions yet</p>
            <p class="text-sm mt-1">Student quiz submissions will appear here for review.</p>
          </div>

          <div class="space-y-3">
            <div v-for="a in gradedAttempts" :key="a.id"
              class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all">
              <div class="px-5 py-4">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3 min-w-0">
                    <div class="h-9 w-9 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center font-bold text-sm shrink-0">
                      {{ a.student?.first_name?.charAt(0) || '?' }}
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm font-bold text-gray-900 truncate">{{ a.student?.first_name }} {{ a.student?.last_name }}</p>
                      <p class="text-xs text-gray-500 truncate">{{ a.quiz?.title }}</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-4 ml-4 shrink-0">
                    <div class="text-right">
                      <div class="text-sm font-bold font-mono"
                        :class="a.percentage >= 50 ? 'text-emerald-600' : 'text-red-600'">
                        {{ a.percentage?.toFixed(1) || '0' }}%
                      </div>
                      <div class="text-[10px] text-gray-400">{{ a.score }}/{{ a.total_points }} pts</div>
                    </div>
                    <div class="text-xs text-gray-400 text-right whitespace-nowrap">
                      <div>{{ a.submitted_at ? new Date(a.submitted_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '—' }}</div>
                      <div>{{ Math.floor((a.time_spent || 0) / 60) }}m {{ (a.time_spent || 0) % 60 }}s</div>
                    </div>
                    <button class="px-3 py-1.5 text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors flex items-center gap-1">
                      <Eye class="h-3 w-3" /> Review
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- ============ ANALYTICS TAB ============ -->
        <template v-else-if="activeTab === 'analytics'">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs font-medium text-gray-500 uppercase tracking-wider">Overall Average</p>
                  <p class="text-2xl font-bold text-gray-900 mt-1">{{ overallAverage.toFixed(1) }}%</p>
                </div>
                <div class="h-10 w-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                  <TrendingUp class="h-5 w-5 text-indigo-600" />
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs font-medium text-gray-500 uppercase tracking-wider">Total Attempts</p>
                  <p class="text-2xl font-bold text-gray-900 mt-1">{{ totalAttempts }}</p>
                </div>
                <div class="h-10 w-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                  <Users class="h-5 w-5 text-emerald-600" />
                </div>
              </div>
            </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs font-medium text-gray-500 uppercase tracking-wider">Quizzes Created</p>
                  <p class="text-2xl font-bold text-gray-900 mt-1">{{ quizzes.length }}</p>
                </div>
                <div class="h-10 w-10 bg-amber-100 rounded-lg flex items-center justify-center">
                  <ListChecks class="h-5 w-5 text-amber-600" />
                </div>
              </div>
            </div>
          </div>

          <div v-if="!quizAnalytics.filter(a => a.count > 0).length" class="text-center py-16 text-gray-400">
            <BarChart3 class="h-12 w-12 mx-auto mb-3" />
            <p class="text-base font-medium text-gray-500">No data yet</p>
            <p class="text-sm mt-1">Analytics will appear once students complete quizzes.</p>
          </div>

          <div v-for="qa in quizAnalytics" :key="qa.quiz.id" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-4">
            <div class="px-6 py-4 border-b border-gray-100">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-base font-bold text-gray-900">{{ qa.quiz.title }}</h3>
                  <p class="text-xs text-gray-500">{{ qa.count }} attempt{{ qa.count !== 1 ? 's' : '' }} &middot; {{ qa.quiz.questions?.length || 0 }} questions</p>
                </div>
                <div class="flex items-center gap-3">
                  <div class="text-right">
                    <p class="text-xs text-gray-500">Avg Score</p>
                    <p class="text-lg font-bold font-mono" :class="qa.avgScore >= 50 ? 'text-emerald-600' : 'text-red-600'">
                      {{ qa.avgScore.toFixed(1) }}%
                    </p>
                  </div>
                  <div class="text-right">
                    <p class="text-xs text-gray-500">Pass Rate</p>
                    <p class="text-lg font-bold font-mono" :class="qa.passRate >= 50 ? 'text-emerald-600' : 'text-amber-600'">
                      {{ qa.passRate.toFixed(0) }}%
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="qa.hardestQuestion && qa.hardestQuestion.correctRate < 0.8" class="px-6 py-4">
              <div class="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-xl">
                <AlertCircle class="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
                <div>
                  <p class="text-sm font-bold text-red-700">Hardest Question — {{ (qa.hardestQuestion.correctRate * 100).toFixed(0) }}% correct</p>
                  <p class="text-sm text-red-600 mt-0.5">{{ qa.hardestQuestion.question.question_text }}</p>
                  <p class="text-xs text-red-400 mt-1">{{ qa.hardestQuestion.correctRate <= 0.2 ? 'Critical: Most students got this wrong' : qa.hardestQuestion.correctRate <= 0.5 ? 'Needs Review: Less than half answered correctly' : 'Flagged: Could be improved' }}</p>
                </div>
              </div>
            </div>
            <div class="px-6 py-3 bg-gray-50 flex items-center justify-between text-xs text-gray-500">
              <span>Average points: <strong>{{ qa.avgPoints.toFixed(1) }}</strong> / {{ qa.quiz.total_points }}</span>
              <div class="flex items-center gap-1">
                <div class="h-2 w-24 bg-gray-200 rounded-full overflow-hidden">
                  <div class="h-full bg-indigo-500 rounded-full" :style="{ width: qa.avgScore + '%' }" />
                </div>
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

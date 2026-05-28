<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../../services/api'
import StudentSidebar from '../../components/StudentSidebar.vue'
import {
  Menu, LayoutDashboard, GraduationCap, ArrowLeft, Clock, CheckCircle, XCircle,
  HelpCircle, BookOpen, AlertTriangle, BarChart, Settings, LogOut
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const courseId = computed(() => Number(route.params.id))
const quizId = computed(() => Number(route.params.quizId))

const quiz = ref<any>(null)
const attempt = ref<any>(null)
const isLoading = ref(true)
const starting = ref(false)
const submitting = ref(false)
const answers = ref<Record<number, number>>({})
const hasStarted = ref(false)
const timeRemaining = ref(0)
const timerInterval = ref<any>(null)
const mobileMenuOpen = ref(false)

const userId = computed(() => Number(localStorage.getItem('user_id')))

const filteredQuestions = computed(() => {
  if (!quiz.value?.questions) return []
  if (attempt.value?.is_completed) return quiz.value.questions
  return quiz.value.questions.map((q: any) => ({
    ...q,
    correct_answer_index: undefined,
  }))
})

onMounted(async () => {
  try {
    const [quizRes, attemptsRes] = await Promise.all([
      api.get(`quizzes/${quizId.value}/`),
      api.get('attempts/', { params: { quiz: quizId.value } }),
    ])
    quiz.value = quizRes.data
    const myAttempts = attemptsRes.data.filter((a: any) => a.student?.id === userId.value)
    if (myAttempts.length) {
      attempt.value = myAttempts[0]
      if (attempt.value.is_completed) {
        hasStarted.value = true
        const reviewRes = await api.get(`quizzes/${quizId.value}/`, { params: { review: '1' } })
        quiz.value = reviewRes.data
      } else if (attempt.value.answers?.length) {
        hasStarted.value = true
        for (const a of attempt.value.answers) {
          answers.value[a.question] = a.selected_answer_index
        }
      }
    }
  } catch (err) {
    console.error(err)
  } finally {
    isLoading.value = false
  }
})

const startQuiz = async () => {
  starting.value = true
  try {
    const res = await api.post('attempts/', {
      quiz_id: quizId.value,
      student_id: userId.value,
    })
    attempt.value = res.data
    hasStarted.value = true
    if (quiz.value?.time_limit) {
      timeRemaining.value = quiz.value.time_limit * 60
      timerInterval.value = setInterval(() => {
        timeRemaining.value--
        if (timeRemaining.value <= 0) submitQuiz()
      }, 1000)
    }
  } catch (err) {
    console.error(err)
  } finally {
    starting.value = false
  }
}

const selectAnswer = (questionId: number, index: number) => {
  answers.value[questionId] = index
}

const submitQuiz = async () => {
  if (!attempt.value?.id) return
  submitting.value = true
  if (timerInterval.value) clearInterval(timerInterval.value)
  try {
    const quizWithAnswers = await api.get(`quizzes/${quizId.value}/`, { params: { review: '1' } })
    const questions = quizWithAnswers.data.questions || []

    for (const [qId, ansIdx] of Object.entries(answers.value)) {
      const question = questions.find((q: any) => q.id === Number(qId))
      const isCorrect = question ? ansIdx === question.correct_answer_index : false
      await api.post('answers/', {
        attempt: attempt.value.id,
        question: Number(qId),
        selected_answer_index: ansIdx,
        is_correct: isCorrect,
      })
    }

    const totalPoints = quiz.value?.total_points || 0
    const pointsPerQ = questions.length ? Math.round(totalPoints / questions.length) : 0
    const correctCount = questions.filter((q: any) => answers.value[q.id] === q.correct_answer_index).length
    const score = correctCount * pointsPerQ
    const percentage = totalPoints ? Math.round((score / totalPoints) * 100) : 0

    const res = await api.patch(`attempts/${attempt.value.id}/`, {
      score,
      total_points: totalPoints,
      percentage,
      is_completed: true,
      time_spent: quiz.value?.time_limit ? (quiz.value.time_limit * 60) - timeRemaining.value : 0,
      submitted_at: new Date().toISOString(),
    })
    attempt.value = res.data

    const refreshed = await api.get(`quizzes/${quizId.value}/`, { params: { review: '1' } })
    quiz.value = refreshed.data
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 font-sans overflow-hidden">
    <StudentSidebar />
    <!-- Mobile Menu Overlay -->
    <div v-if="mobileMenuOpen" class="fixed inset-0 z-50 flex md:hidden">
      <div class="fixed inset-0 bg-gray-800/75" @click="mobileMenuOpen = false"></div>
      <div class="relative flex w-full max-w-xs flex-1 flex-col bg-white pt-5 pb-4">
        <div class="flex items-center justify-between px-4 mb-6">
          <h1 class="text-xl font-bold text-gray-900 tracking-tight">EDUCLOUD <span class="text-indigo-600">2.0</span></h1>
          <button @click="mobileMenuOpen = false" class="text-gray-400 hover:text-gray-600"><span class="text-2xl">&times;</span></button>
        </div>
        <nav class="flex-1 px-4 space-y-1">
          <a @click="mobileMenuOpen = false; router.push('/student')"
             class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors cursor-pointer">
            <LayoutDashboard class="w-5 h-5 mr-3 text-gray-400" /> Dashboard
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/marksheet')"
             class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors cursor-pointer">
            <GraduationCap class="w-5 h-5 mr-3 text-gray-400" /> Marksheet
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/courses')"
             class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors cursor-pointer">
            <BookOpen class="w-5 h-5 mr-3 text-gray-400" /> My Courses
          </a>
          <a @click="mobileMenuOpen = false; router.push('/student/settings')"
             class="flex items-center px-3 py-2.5 text-gray-700 hover:bg-gray-50 rounded-lg font-medium transition-colors cursor-pointer">
            <Settings class="w-5 h-5 mr-3 text-gray-400" /> Settings
          </a>
          <hr class="my-3 border-gray-200" />
          <a @click="localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token'); localStorage.removeItem('user_role'); localStorage.removeItem('user_id'); localStorage.removeItem('username'); router.push('/login')"
             class="flex items-center px-3 py-2.5 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors cursor-pointer">
            <LogOut class="w-5 h-5 mr-3 text-red-500" /> Sign Out
          </a>
        </nav>
      </div>
    </div>
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-200 flex-shrink-0">
        <div class="px-4 sm:px-6 h-16 flex items-center">
          <button @click="mobileMenuOpen = true" class="mr-3 md:hidden text-gray-500 hover:text-gray-900 focus:outline-none"><Menu class="h-6 w-6" /></button>
          <button @click="router.push(`/student/course/${courseId}`)" class="mr-4 text-gray-400 hover:text-indigo-600">
            <ArrowLeft class="h-6 w-6" />
          </button>
          <div class="flex-1 min-w-0">
            <h1 class="text-lg font-bold text-gray-900 truncate">{{ quiz?.title || 'Quiz' }}</h1>
            <p class="text-xs text-gray-500">{{ quiz?.total_points }} points</p>
          </div>
          <div v-if="hasStarted && !attempt?.is_completed && quiz?.time_limit"
               :class="['flex items-center px-3 py-1.5 rounded-lg text-sm font-bold',
                 timeRemaining < 60 ? 'bg-red-100 text-red-700 animate-pulse' : 'bg-gray-100 text-gray-700']">
            <Clock class="h-4 w-4 mr-1.5" /> {{ formatTime(timeRemaining) }}
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-6 max-w-3xl mx-auto w-full">
        <div v-if="isLoading" class="text-center py-16 text-gray-500">Loading quiz...</div>

        <!-- Not started yet -->
        <template v-else-if="!hasStarted">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center max-w-lg mx-auto mt-12">
            <div class="h-16 w-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <HelpCircle class="h-8 w-8 text-indigo-600" />
            </div>
            <h2 class="text-xl font-bold text-gray-900 mb-2">{{ quiz?.title }}</h2>
            <p class="text-sm text-gray-500 mb-2">{{ quiz?.description }}</p>
            <div class="flex justify-center space-x-6 text-sm text-gray-500 mb-6 mt-4">
              <span>{{ quiz?.questions?.length || 0 }} questions</span>
              <span>{{ quiz?.total_points }} points</span>
              <span v-if="quiz?.time_limit">{{ quiz.time_limit }} min</span>
            </div>
            <button @click="startQuiz" :disabled="starting"
              class="px-8 py-3 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-md text-sm">
              {{ starting ? 'Starting...' : 'Start Quiz' }}
            </button>
          </div>
        </template>

        <!-- Results -->
        <template v-else-if="attempt?.is_completed">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center max-w-lg mx-auto mt-8">
            <div :class="['h-20 w-20 rounded-full flex items-center justify-center mx-auto mb-4',
              (attempt.percentage || 0) >= 70 ? 'bg-emerald-100' : 'bg-red-100']">
              <BarChart :class="['h-10 w-10', (attempt.percentage || 0) >= 70 ? 'text-emerald-600' : 'text-red-600']" />
            </div>
            <h2 class="text-2xl font-bold text-gray-900 mb-1">{{ attempt.score }} / {{ attempt.total_points }}</h2>
            <p :class="['text-lg font-semibold', (attempt.percentage || 0) >= 70 ? 'text-emerald-600' : 'text-red-600']">
              {{ Math.round(attempt.percentage || 0) }}%
            </p>
            <p class="text-sm text-gray-500 mt-4">
              {{ (attempt.percentage || 0) >= 70 ? 'Great job!' : 'Keep practicing!' }}
            </p>
          </div>

          <!-- Question Review -->
          <div class="space-y-3 mt-6">
            <div v-for="(q, i) in quiz?.questions" :key="q.id"
                 class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <div class="flex items-start justify-between mb-3">
                <p class="text-sm font-bold text-gray-900">Q{{ i + 1 }}. {{ q.question_text }}</p>
                <span v-if="answers[q.id] === q.correct_answer_index">
                  <CheckCircle class="h-5 w-5 text-emerald-500 shrink-0 ml-2" />
                </span>
                <span v-else>
                  <XCircle class="h-5 w-5 text-red-500 shrink-0 ml-2" />
                </span>
              </div>
              <div class="space-y-1.5">
                <div v-for="(opt, oi) in q.options" :key="oi"
                     :class="['px-3 py-2 rounded-lg text-sm border',
                       oi === q.correct_answer_index
                         ? 'bg-emerald-50 border-emerald-300 text-emerald-800 font-medium'
                         : oi === answers[q.id] && oi !== q.correct_answer_index
                           ? 'bg-red-50 border-red-300 text-red-700'
                           : 'bg-gray-50 border-gray-200 text-gray-700']">
                  {{ opt }}
                  <span v-if="oi === q.correct_answer_index" class="text-emerald-600 font-bold ml-1">✓</span>
                </div>
                <p v-if="answers[q.id] !== undefined && answers[q.id] !== q.correct_answer_index"
                   class="text-xs text-red-600 mt-1">You selected option {{ (answers[q.id] || 0) + 1 }}</p>
              </div>
            </div>
          </div>

          <div class="text-center mt-6">
            <button @click="router.push(`/student/course/${courseId}`)"
              class="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-all text-sm">
              Back to Course
            </button>
          </div>
        </template>

        <!-- Taking Quiz -->
        <template v-else>
          <div class="space-y-3">
            <div v-for="(q, i) in filteredQuestions" :key="q.id"
                 class="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
              <p class="text-sm font-bold text-gray-900 mb-3">Q{{ i + 1 }}. {{ q.question_text }}</p>
              <div class="space-y-2">
                <label v-for="(opt, oi) in q.options" :key="oi"
                       :class="['flex items-center px-3 py-2.5 rounded-lg border cursor-pointer transition-colors text-sm',
                         answers[q.id] === oi
                           ? 'border-indigo-500 bg-indigo-50 text-indigo-800 font-medium'
                           : 'border-gray-200 bg-gray-50 hover:border-gray-300 text-gray-700']">
                  <input type="radio" :name="'q_' + q.id" :value="oi"
                         :checked="answers[q.id] === oi"
                         @change="selectAnswer(q.id, oi)"
                         class="mr-3 accent-indigo-600" />
                  {{ opt }}
                </label>
              </div>
            </div>
          </div>

          <div class="sticky bottom-0 bg-white border-t border-gray-200 p-4 mt-6 -mx-6 -mb-6 flex items-center justify-between">
            <p class="text-sm text-gray-500">
              {{ Object.keys(answers).length }} / {{ quiz?.questions?.length || 0 }} answered
            </p>
            <button @click="submitQuiz" :disabled="submitting"
              class="px-8 py-2.5 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-sm text-sm">
              {{ submitting ? 'Submitting...' : 'Submit Quiz' }}
            </button>
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/auth/LoginView.vue'
import InstructorDashboardView from '../views/instructor/InstructorDashboardView.vue'
import MyCoursesView from '../views/instructor/MyCoursesView.vue'
import CourseDetailView from '../views/instructor/CourseDetailView.vue'
import GradebookOverviewView from '../views/instructor/GradebookOverviewView.vue'
import GradebookView from '../views/instructor/GradebookView.vue'
import LiveSessionView from '../views/instructor/LiveSessionView.vue'
import AttendanceView from '../views/instructor/AttendanceView.vue'
import QuizView from '../views/instructor/QuizView.vue'
import AssignmentView from '../views/instructor/AssignmentView.vue'
import GroupsView from '../views/instructor/GroupsView.vue'
import InstructorSettingsView from '../views/instructor/InstructorSettingsView.vue'
import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import ManageUsersView from '../views/admin/ManageUsersView.vue'
import CourseProvisioningView from '../views/admin/CourseProvisioningView.vue'
import AdminSettingsView from '../views/admin/AdminSettingsView.vue'
import StudentDashboardView from '../views/student/StudentDashboardView.vue'
import StudentCourseView from '../views/student/StudentCourseView.vue'
import StudentCourseListView from '../views/student/StudentCourseListView.vue'
import StudentSubmissionView from '../views/student/StudentSubmissionView.vue'
import StudentSettingsView from '../views/student/StudentSettingsView.vue'
import StudentMarksheetView from '../views/student/StudentMarksheetView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: InstructorDashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/my-courses',
      name: 'my-courses',
      component: MyCoursesView,
      meta: { requiresAuth: true }
    },
    {
      path: '/gradebook',
      name: 'gradebook',
      component: GradebookOverviewView,
      meta: { requiresAuth: true }
    },
    {
      path: '/course/:id',
      name: 'course-detail',
      component: CourseDetailView,
      meta: { requiresAuth: true }
    },
    {
      path: '/course/:id/grades',
      name: 'course-grades',
      component: GradebookView,
      meta: { requiresAuth: true }
    },
    {
      path: '/course/:id/live',
      name: 'course-live',
      component: LiveSessionView,
      meta: { requiresAuth: true }
    },
    {
      path: '/course/:id/attendance',
      name: 'course-attendance',
      component: AttendanceView,
      meta: { requiresAuth: true }
    },
    {
      path: '/course/:id/quizzes',
      name: 'course-quizzes',
      component: QuizView,
      meta: { requiresAuth: true }
    },
    {
      path: '/course/:id/assignments',
      name: 'course-assignments',
      component: AssignmentView,
      meta: { requiresAuth: true }
    },
    {
      path: '/course/:id/groups',
      name: 'course-groups',
      component: GroupsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: AdminDashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/users',
      name: 'manage-users',
      component: ManageUsersView,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/courses',
      name: 'course-provisioning',
      component: CourseProvisioningView,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/settings',
      name: 'admin-settings',
      component: AdminSettingsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/instructor/settings',
      name: 'instructor-settings',
      component: InstructorSettingsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/student',
      name: 'student-dashboard',
      component: StudentDashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/student/courses',
      name: 'student-courses',
      component: StudentCourseListView,
      meta: { requiresAuth: true }
    },
    {
      path: '/student/course/:id',
      name: 'student-course',
      component: StudentCourseView,
      meta: { requiresAuth: true }
    },
    {
      path: '/student/course/:id/assignment/:task_id',
      name: 'student-submission',
      component: StudentSubmissionView,
      meta: { requiresAuth: true }
    },
    {
      path: '/student/marksheet',
      name: 'student-marksheet',
      component: StudentMarksheetView,
      meta: { requiresAuth: true }
    },
    {
      path: '/student/settings',
      name: 'student-settings',
      component: StudentSettingsView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router

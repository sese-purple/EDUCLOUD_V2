import { createRouter, createWebHistory } from 'vue-router'
import InstructorDashboardView from '../views/instructor/InstructorDashboardView.vue'
import LoginView from '../views/auth/LoginView.vue'
import CourseDetailView from '../views/instructor/CourseDetailView.vue'
import AdminDashboardView from '../views/admin/AdminDashboardView.vue'
import ManageUsersView from '../views/admin/ManageUsersView.vue'
import CourseProvisioningView from '../views/admin/CourseProvisioningView.vue'
import StudentDashboardView from '../views/student/StudentDashboardView.vue'

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
      component: InstructorDashboardView
    },
    {
      path: '/course/:id',
      name: 'course-detail',
      component: CourseDetailView
    },
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: AdminDashboardView
    },
    {
      path: '/admin/users',
      name: 'manage-users',
      component: ManageUsersView
    },
    {
      path: '/admin/courses',
      name: 'course-provisioning',
      component: CourseProvisioningView
    },
    {
      path: '/student',
      name: 'student-dashboard',
      component: StudentDashboardView
    }
  ]
})

export default router

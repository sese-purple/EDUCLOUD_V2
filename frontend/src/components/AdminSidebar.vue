<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import {
  ShieldAlert, Users, BookOpen, Database,
  Settings, LogOut
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<template>
  <aside class="w-64 bg-slate-900 text-slate-300 flex flex-col hidden md:flex flex-shrink-0 z-20 shadow-xl border-r border-slate-800">
    
    <div class="h-16 flex items-center px-6 border-b border-slate-800 bg-slate-950/50">
      <div class="h-8 w-8 rounded-lg bg-indigo-500/20 flex items-center justify-center mr-3 border border-indigo-500/30">
        <ShieldAlert class="w-5 h-5 text-indigo-400" />
      </div>
      <div>
        <h1 class="text-sm font-bold text-white tracking-wider uppercase">System Admin</h1>
        <p class="text-[10px] text-indigo-400 font-medium tracking-widest uppercase mt-0.5">Core Network</p>
      </div>
    </div>

    <nav class="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
      
      
      <a @click="router.push('/admin')"
         :class="[route.path === '/admin' ? 'bg-indigo-600 text-white shadow-md' : 'hover:bg-slate-800 hover:text-white', 'flex items-center px-3 py-2.5 rounded-lg font-medium transition-all cursor-pointer group']">
        <Database :class="[route.path === '/admin' ? 'text-white' : 'text-slate-400 group-hover:text-indigo-400', 'w-5 h-5 mr-3 transition-colors']" /> 
        System Overview
      </a>

      <a @click="router.push('/admin/users')"
         :class="[route.path === '/admin/users' ? 'bg-indigo-600 text-white shadow-md' : 'hover:bg-slate-800 hover:text-white', 'flex items-center px-3 py-2.5 rounded-lg font-medium transition-all cursor-pointer group']">
        <Users :class="[route.path === '/admin/users' ? 'text-white' : 'text-slate-400 group-hover:text-indigo-400', 'w-5 h-5 mr-3 transition-colors']" /> 
        Manage Users
      </a>

      <a @click="router.push('/admin/courses')"
         :class="[route.path === '/admin/courses' ? 'bg-indigo-600 text-white shadow-md' : 'hover:bg-slate-800 hover:text-white', 'flex items-center px-3 py-2.5 rounded-lg font-medium transition-all cursor-pointer group']">
        <BookOpen :class="[route.path === '/admin/courses' ? 'text-white' : 'text-slate-400 group-hover:text-indigo-400', 'w-5 h-5 mr-3 transition-colors']" />
        Course Provisioning
      </a>
    </nav>

    <div class="p-4 border-t border-slate-800 bg-slate-950/30">
      <a href="#" class="flex items-center px-3 py-2.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg font-medium transition-all cursor-pointer group">
        <Settings class="w-5 h-5 mr-3 text-slate-400 group-hover:text-white transition-colors" /> 
        Security Settings
      </a>
      <a @click="handleLogout" class="flex items-center px-3 py-2.5 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg font-medium transition-all mt-1 cursor-pointer">
        <LogOut class="w-5 h-5 mr-3 text-red-400" /> 
        Force Logout
      </a>
    </div>
  </aside>
</template>

<template>
<main class="max-w-4xl mx-auto px-4 py-8">
  <div class="mb-8">
    <div class="flex items-center mb-2">
      <div class="w-10 h-10 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center mr-3 shadow-md">
        <i class="fa fa-user text-white text-lg"></i>
      </div>
      <div><h1 class="text-2xl font-bold text-slate-800">个人信息</h1><p class="text-slate-500 text-sm">管理您的账号信息，保障账号安全</p></div>
    </div>
  </div>

  <div v-if="msg" :class="mt === 'success' ? 'bg-emerald-50 border-emerald-100 text-emerald-600' : 'bg-red-50 border-red-100 text-red-600'" class="mb-6 px-6 py-4 rounded-2xl flex items-center text-sm">
    <i :class="mt === 'success' ? 'fa fa-check-circle' : 'fa fa-exclamation-circle'" class="mr-3 text-lg"></i><span>{{ msg }}</span>
  </div>

  <!-- 基本信息 -->
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 mb-6">
    <h3 class="text-base font-semibold text-slate-800 mb-4 flex items-center"><i class="fa fa-id-card-o text-indigo-500 mr-2"></i>账号基本信息</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-slate-50 rounded-xl p-4"><label class="text-xs text-slate-500 mb-1 block">账号（不可修改）</label><div class="text-base font-medium text-slate-800">{{ p.username }}</div></div>
      <div class="bg-slate-50 rounded-xl p-4"><label class="text-xs text-slate-500 mb-1 block">绑定邮箱</label><div class="text-base font-medium text-slate-800">{{ p.email }}</div></div>
    </div>
  </div>

  <!-- 修改邮箱 -->
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 mb-4 overflow-hidden">
    <div @click="showEmail = !showEmail" class="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-slate-50 transition-colors">
      <div class="flex items-center gap-3"><div class="w-9 h-9 bg-indigo-50 rounded-xl flex items-center justify-center"><i class="fa fa-envelope-o text-indigo-500 text-sm"></i></div><span class="text-base font-semibold text-slate-700">修改绑定邮箱</span></div>
      <i :class="showEmail ? 'fa fa-chevron-up' : 'fa fa-chevron-down'" class="text-slate-400 transition-transform duration-200"></i>
    </div>
    <div v-show="showEmail" class="px-6 pb-6">
      <form @submit.prevent="chEmail" class="space-y-4">
        <div><label class="block text-sm font-medium text-slate-500 mb-1">当前密码（验证身份）</label><input v-model="ef.pw" type="password" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入当前账号密码"></div>
        <div><label class="block text-sm font-medium text-slate-500 mb-1">新邮箱地址</label><input v-model="ef.ne" type="email" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入新的邮箱地址"></div>
        <div><label class="block text-sm font-medium text-slate-500 mb-1">确认新邮箱</label><input v-model="ef.ce" type="email" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="再次输入新邮箱地址"></div>
        <button type="submit" class="w-full py-3 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm"><i class="fa fa-save mr-2"></i>保存新邮箱</button>
      </form>
    </div>
  </div>

  <!-- 修改密码 -->
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 mb-4 overflow-hidden">
    <div @click="showPw = !showPw" class="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-slate-50 transition-colors">
      <div class="flex items-center gap-3"><div class="w-9 h-9 bg-emerald-50 rounded-xl flex items-center justify-center"><i class="fa fa-lock text-emerald-500 text-sm"></i></div><span class="text-base font-semibold text-slate-700">修改账号密码</span></div>
      <i :class="showPw ? 'fa fa-chevron-up' : 'fa fa-chevron-down'" class="text-slate-400 transition-transform duration-200"></i>
    </div>
    <div v-show="showPw" class="px-6 pb-6">
      <form @submit.prevent="chPw" class="space-y-4">
        <div><label class="block text-sm font-medium text-slate-500 mb-1">当前密码（验证身份）</label><input v-model="pf.pw" type="password" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入当前账号密码"></div>
        <div><label class="block text-sm font-medium text-slate-500 mb-1">新密码</label><input v-model="pf.np" type="password" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="8-50位，不能包含空格"></div>
        <div><label class="block text-sm font-medium text-slate-500 mb-1">确认新密码</label><input v-model="pf.cp" type="password" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="再次输入新密码"></div>
        <button type="submit" class="w-full py-3 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm"><i class="fa fa-save mr-2"></i>保存新密码</button>
      </form>
    </div>
  </div>

  <!-- 修改安全问题 -->
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 overflow-hidden">
    <div @click="showSec = !showSec" class="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-slate-50 transition-colors">
      <div class="flex items-center gap-3"><div class="w-9 h-9 bg-amber-50 rounded-xl flex items-center justify-center"><i class="fa fa-shield text-amber-500 text-sm"></i></div><span class="text-base font-semibold text-slate-700">修改安全问题</span></div>
      <i :class="showSec ? 'fa fa-chevron-up' : 'fa fa-chevron-down'" class="text-slate-400 transition-transform duration-200"></i>
    </div>
    <div v-show="showSec" class="px-6 pb-6">
      <form @submit.prevent="chSec" class="space-y-4">
        <div><label class="block text-sm font-medium text-slate-500 mb-1">安全问题 1</label><input v-model="sf.q1" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="例如：您母亲的姓名是？"></div>
        <div><label class="block text-sm font-medium text-slate-500 mb-1">答案 1</label><input v-model="sf.a1" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入答案"></div>
        <div><label class="block text-sm font-medium text-slate-500 mb-1">安全问题 2</label><input v-model="sf.q2" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="例如：您的小学名称是？"></div>
        <div><label class="block text-sm font-medium text-slate-500 mb-1">答案 2</label><input v-model="sf.a2" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入答案"></div>
        <div><label class="block text-sm font-medium text-slate-500 mb-1">当前密码（验证身份）</label><input v-model="sf.pw" type="password" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入当前账号密码"></div>
        <button type="submit" class="w-full py-3 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm"><i class="fa fa-save mr-2"></i>保存安全问题</button>
      </form>
    </div>
  </div>
</main>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import api from '../api'
const p = ref({ username: '', email: '' }); const msg = ref(''); const mt = ref('success')
const showEmail = ref(false); const showPw = ref(false); const showSec = ref(false)
const ef = reactive({ pw: '', ne: '', ce: '' }); const pf = reactive({ pw: '', np: '', cp: '' }); const sf = reactive({ q1: '', a1: '', q2: '', a2: '', pw: '' })
onMounted(async () => { try { const r = await api.get('/api/profile'); if (r.data.code === 200) { p.value = r.data.data; sf.q1 = r.data.data.question1; sf.q2 = r.data.data.question2 } } catch (e) {} })
async function chEmail() { try { const r = await api.put('/api/profile/email', { current_password: ef.pw, new_email: ef.ne, confirm_new_email: ef.ce }); if (r.data.code === 200) { msg.value = '邮箱修改成功！'; mt.value = 'success'; ef.pw = ''; ef.ne = ''; ef.ce = ''; const r2 = await api.get('/api/profile'); if (r2.data.code === 200) p.value = r2.data.data } else { msg.value = r.data.message; mt.value = 'error' } } catch (e) { msg.value = e.response?.data?.message || '修改失败'; mt.value = 'error' } }
async function chPw() { try { const r = await api.put('/api/profile/password', { current_password: pf.pw, new_password: pf.np, confirm_new_password: pf.cp }); if (r.data.code === 200) { msg.value = '密码修改成功！'; mt.value = 'success'; pf.pw = ''; pf.np = ''; pf.cp = '' } else { msg.value = r.data.message; mt.value = 'error' } } catch (e) { msg.value = e.response?.data?.message || '修改失败'; mt.value = 'error' } }
async function chSec() { try { const r = await api.put('/api/profile/security', { current_password: sf.pw, question1: sf.q1, answer1: sf.a1, question2: sf.q2, answer2: sf.a2 }); if (r.data.code === 200) { msg.value = '安全问题修改成功！'; mt.value = 'success'; sf.a1 = ''; sf.a2 = ''; sf.pw = '' } else { msg.value = r.data.message; mt.value = 'error' } } catch (e) { msg.value = e.response?.data?.message || '修改失败'; mt.value = 'error' } }
</script>

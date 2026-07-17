<template>
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-blue-50 to-indigo-50 py-8 px-4">
  <div class="w-full max-w-5xl bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden flex flex-col md:flex-row border border-white/50">

    <!-- 左栏 -->
    <div class="w-full md:w-2/5 bg-gradient-to-br from-slate-900 via-blue-950 to-indigo-950 p-8 md:p-10 flex flex-col justify-between relative overflow-hidden">
      <div class="absolute -top-32 -right-32 w-80 h-80 bg-indigo-500/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-32 -left-32 w-80 h-80 bg-blue-400/10 rounded-full blur-3xl"></div>

      <div class="relative z-10 flex-1 flex flex-col">
        <div class="flex-shrink-0">
          <div class="flex items-center gap-3 text-white/90 mb-6">
            <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center backdrop-blur-sm">
              <i class="fa fa-book text-white text-lg"></i>
            </div>
            <span class="text-base font-semibold tracking-wide">学术文献检索</span>
          </div>
          <h2 class="text-3xl font-bold text-white leading-tight">加入我们</h2>
          <p class="text-indigo-200/80 text-sm mt-2 leading-relaxed max-w-xs">注册后即可免费检索海量文献、收藏重要成果、追踪研究趋势。</p>
        </div>

        <div class="flex-1 flex items-center py-6">
          <div class="w-full bg-white/5 backdrop-blur-sm rounded-2xl p-5 border border-white/10">
            <div class="flex items-center gap-2 mb-3">
              <span class="text-white/40 text-[11px] tracking-[0.15em] uppercase font-medium">演进简史</span>
              <span class="flex-1 border-t border-white/10"></span>
              <span class="text-white/20 text-[10px]">从竹简到云端</span>
            </div>
            <div class="grid grid-cols-[52px_1fr] gap-x-3 gap-y-1.5 text-sm">
              <div class="text-yellow-300/60 text-[13px] font-mono font-bold text-right pt-0.5">古代</div><div><p class="text-white/90 text-[15px] font-medium leading-tight">目录学萌芽</p><p class="text-white/50 text-[12px] leading-relaxed">刘向《别录》开创中国古典目录学传统</p></div>
              <div class="text-yellow-300/60 text-[13px] font-mono font-bold text-right pt-0.5">15世纪</div><div><p class="text-white/90 text-[15px] font-medium leading-tight">印刷术革命</p><p class="text-white/50 text-[12px] leading-relaxed">古登堡印刷术推动知识大规模复制传播</p></div>
              <div class="text-yellow-300/60 text-[13px] font-mono font-bold text-right pt-0.5">1876年</div><div><p class="text-white/90 text-[15px] font-medium leading-tight">分类法诞生</p><p class="text-white/50 text-[12px] leading-relaxed">杜威十进分类法奠定现代文献组织体系</p></div>
              <div class="text-yellow-300/60 text-[13px] font-mono font-bold text-right pt-0.5">1945年</div><div><p class="text-white/90 text-[15px] font-medium leading-tight">信息科学先驱</p><p class="text-white/50 text-[12px] leading-relaxed">Vannevar Bush 预见信息检索未来</p></div>
              <div class="text-yellow-300/60 text-[13px] font-mono font-bold text-right pt-0.5">1990年代</div><div><p class="text-white/90 text-[15px] font-medium leading-tight">互联网检索兴起</p><p class="text-white/50 text-[12px] leading-relaxed">搜索引擎普及，学术资源全球互联</p></div>
              <div class="text-yellow-300/60 text-[13px] font-mono font-bold text-right pt-0.5">今日</div><div><p class="text-white/90 text-[15px] font-medium leading-tight">智能学术检索</p><p class="text-white/50 text-[12px] leading-relaxed">AI驱动、知识图谱赋能学术探索新高度</p></div>
            </div>
            <p class="text-white/20 text-[11px] italic mt-3 pt-2 border-t border-white/10 text-center tracking-wide">"知识的历史，就是人类不断寻找、组织与传承的历史"</p>
          </div>
        </div>
      </div>

      <div class="relative z-10 flex-shrink-0">
        <div class="grid grid-cols-3 gap-3 pt-3 border-t border-white/10">
          <div class="text-center group cursor-default">
            <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center mx-auto mb-1.5 group-hover:bg-white/20 transition-colors">
              <i class="fa fa-search text-yellow-300 text-sm"></i>
            </div>
            <span class="text-xs text-indigo-200/80">智能检索</span>
          </div>
          <div class="text-center group cursor-default">
            <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center mx-auto mb-1.5 group-hover:bg-white/20 transition-colors">
              <i class="fa fa-star text-yellow-300 text-sm"></i>
            </div>
            <span class="text-xs text-indigo-200/80">收藏管理</span>
          </div>
          <div class="text-center group cursor-default">
            <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center mx-auto mb-1.5 group-hover:bg-white/20 transition-colors">
              <i class="fa fa-link text-yellow-300 text-sm"></i>
            </div>
            <span class="text-xs text-indigo-200/80">引用分析</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右栏 -->
    <div class="w-full md:w-3/5 p-8 md:p-12 flex items-center justify-center bg-white/50">
      <div class="w-full max-w-sm">
        <div class="md:hidden text-center mb-6">
          <h2 class="text-3xl font-bold text-slate-800">创建账户</h2>
          <p class="text-slate-500 text-sm mt-1">填写信息，立即加入学术社区</p>
        </div>

        <div v-if="err" class="mb-5 bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-2xl flex items-center text-sm backdrop-blur-sm">
          <i class="fa fa-exclamation-circle mr-2.5 flex-shrink-0"></i><span>{{ err }}</span>
        </div>

        <form @submit.prevent="go" class="space-y-3.5">
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1.5">用户名 <span class="text-red-400">*</span></label>
            <input v-model="un" type="text" class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="2-20个字符" required>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1.5">邮箱 <span class="text-red-400">*</span></label>
            <input v-model="em" type="email" class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入您的邮箱地址" required>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1.5">密码 <span class="text-red-400">*</span></label>
            <input v-model="pw" type="password" class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="8-50个字符，不含空格" required>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-1.5">确认密码 <span class="text-red-400">*</span></label>
            <input v-model="cp" type="password" class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请再次输入密码" required>
          </div>

          <div class="border-t border-slate-100 pt-4 mt-2">
            <p class="text-sm font-medium text-slate-600 mb-2.5"><i class="fa fa-shield mr-1.5 text-indigo-500"></i>安全问题 <span class="text-red-400">*</span><span class="text-xs text-slate-400 font-normal ml-1">（用于找回密码）</span></p>
            <div class="space-y-2.5">
              <div>
                <label class="block text-xs font-medium text-slate-500 mb-1">安全问题 1 <span class="text-red-400">*</span></label>
                <input v-model="q1" type="text" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="例如：您母亲的姓名是？" required>
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-500 mb-1">答案 1 <span class="text-red-400">*</span></label>
                <input v-model="a1" type="text" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入答案" required>
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-500 mb-1">安全问题 2 <span class="text-red-400">*</span></label>
                <input v-model="q2" type="text" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="例如：您的小学名称是？" required>
              </div>
              <div>
                <label class="block text-xs font-medium text-slate-500 mb-1">答案 2 <span class="text-red-400">*</span></label>
                <input v-model="a2" type="text" class="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入答案" required>
              </div>
            </div>
          </div>

          <button type="submit" class="w-full bg-gradient-to-r from-slate-800 to-indigo-900 hover:from-slate-700 hover:to-indigo-800 text-white py-3.5 rounded-2xl font-medium transition-all duration-300 shadow-lg shadow-indigo-900/10 hover:shadow-indigo-900/20 hover:-translate-y-0.5 text-sm tracking-wide mt-3" :disabled="ld">
            <span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>注册中...</span>
            <span v-else><i class="fa fa-user-plus mr-2"></i>注 册</span>
          </button>
        </form>

        <div class="mt-7 text-center text-sm text-slate-500">
          已有账户？<router-link to="/login" class="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors">立即登录 →</router-link>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFlashStore } from '../stores/flash'
import api from '../api'

const router = useRouter(); const flash = useFlashStore()
const un = ref(''); const em = ref(''); const pw = ref(''); const cp = ref('')
const q1 = ref(''); const a1 = ref(''); const q2 = ref(''); const a2 = ref('')
const err = ref(''); const ld = ref(false)

async function go() {
  err.value = ''; ld.value = true
  try {
    const r = await api.post('/api/register', {
      username: un.value, email: em.value, password: pw.value, confirm_password: cp.value,
      question1: q1.value, answer1: a1.value, question2: q2.value, answer2: a2.value
    })
    if (r.data.code === 200) { flash.show('注册成功，请登录', 'success'); router.push('/login') }
    else err.value = r.data.message
  } catch (e) { err.value = e.response?.data?.message || '网络错误' } finally { ld.value = false }
}
</script>

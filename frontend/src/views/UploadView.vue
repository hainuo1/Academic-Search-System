<template>
<div class="max-w-3xl mx-auto px-4 py-10">
  <div class="mb-8">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center shadow-md">
        <i class="fa fa-upload text-white text-base"></i>
      </div>
      <div>
        <h1 class="text-2xl font-bold text-slate-800">上传文献</h1>
        <p class="text-slate-500 text-sm">上传PDF文献，系统将自动提取全文用于检索</p>
      </div>
    </div>
  </div>

  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg border border-slate-100 p-8">
    <div v-if="err" class="mb-6 bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-xl flex items-center text-sm backdrop-blur-sm">
      <i class="fa fa-exclamation-circle mr-2.5 flex-shrink-0"></i><span>{{ err }}</span>
    </div>

    <form @submit.prevent="go" enctype="multipart/form-data" class="space-y-5">
      <div>
        <label class="block text-sm font-medium text-slate-600 mb-2">PDF文件 <span class="text-red-400">*</span></label>
        <input type="file" accept=".pdf" @change="onF" required
          class="w-full border border-slate-200 rounded-xl p-3 text-sm text-slate-600 file:mr-4 file:py-2 file:px-5 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100 transition-all">
        <p class="text-slate-400 text-xs mt-1.5">支持PDF格式，单个文件最大50MB</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-600 mb-2">标题 <span class="text-red-400">*</span></label>
        <input v-model="t" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2">作者 <span class="text-red-400">*</span></label>
          <input v-model="a" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2">分类 <span class="text-red-400">*</span></label>
          <input v-model="c" type="text" placeholder="例如：人工智能、数据库" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-600 mb-2">发表日期 <span class="text-red-400">*</span></label>
        <input v-model="pd" type="date" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-700 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-600 mb-2">关键词 <span class="text-red-400">*</span></label>
        <input v-model="kw" type="text" placeholder="例如：AI;机器学习;知识图谱" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
        <p class="text-slate-400 text-xs mt-1.5">多个关键词用分号分隔</p>
      </div>

      <div>
        <label class="block text-sm font-medium text-slate-600 mb-2">摘要 <span class="text-red-400">*</span></label>
        <textarea v-model="ab" rows="5" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none resize-none"></textarea>
      </div>

      <button type="submit" :disabled="ld"
        class="w-full bg-gradient-to-r from-slate-800 to-indigo-900 hover:from-slate-700 hover:to-indigo-800 text-white py-3.5 rounded-2xl font-medium transition-all duration-300 shadow-lg shadow-indigo-900/10 hover:shadow-indigo-900/20 hover:-translate-y-0.5 text-sm tracking-wide flex items-center justify-center gap-2">
        <span v-if="ld"><i class="fa fa-spinner fa-spin"></i>上传中...</span>
        <span v-else><i class="fa fa-upload"></i>上传文献</span>
      </button>
    </form>
  </div>
</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useFlashStore } from '../stores/flash'
import api from '../api'

const router = useRouter(); const flash = useFlashStore()
const t = ref(''); const a = ref(''); const c = ref(''); const pd = ref(''); const kw = ref(''); const ab = ref('')
const file = ref(null); const err = ref(''); const ld = ref(false)

function onF(e) { file.value = e.target.files[0] }

async function go() {
  if (!file.value) { err.value = '请选择PDF文件'; return }
  err.value = ''; ld.value = true
  try {
    const fd = new FormData()
    fd.append('title', t.value); fd.append('author', a.value)
    fd.append('category', c.value); fd.append('publish_date', pd.value)
    fd.append('keywords', kw.value); fd.append('abstract', ab.value)
    fd.append('pdf_file', file.value)
    const r = await api.post('/api/upload', fd)
    if (r.data.code === 200) { flash.show('文献上传成功', 'success'); router.push(`/document/${r.data.data.document_id}`) }
    else err.value = r.data.message
  } catch (e) { err.value = e.response?.data?.message || '网络错误' } finally { ld.value = false }
}
</script>

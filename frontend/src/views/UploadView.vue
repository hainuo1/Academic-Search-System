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
        <div v-if="!file" class="relative">
          <input ref="fileInputRef" type="file" accept=".pdf" @change="onF"
            class="w-full border border-slate-200 rounded-xl p-3 text-sm text-slate-600 file:mr-4 file:py-2 file:px-5 file:rounded-xl file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100 transition-all">
          <p class="text-slate-400 text-xs mt-1.5">支持PDF格式，单个文件最大50MB</p>
        </div>
        <div v-else class="flex items-center gap-3 p-3 bg-indigo-50 border border-indigo-200 rounded-xl">
          <div class="w-9 h-9 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <i class="fa fa-file-pdf-o text-indigo-500 text-lg"></i>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm text-slate-700 font-medium truncate">{{ fileName }}</p>
            <p class="text-xs text-indigo-500">PDF 文件已就绪</p>
          </div>
          <button type="button" @click="onReSelect"
            class="px-4 py-1.5 bg-white border border-indigo-300 text-indigo-600 rounded-lg text-xs font-medium hover:bg-indigo-100 transition flex-shrink-0">
            <i class="fa fa-refresh mr-1"></i>重新选择
          </button>
        </div>
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
          <div class="relative">
            <div v-if="selectedCategoryNames" class="flex flex-wrap gap-1.5 mb-2">
              <span v-for="cn in selectedCategoryNames" :key="cn"
                class="bg-indigo-50 text-indigo-600 px-2.5 py-0.5 rounded-lg text-xs font-medium inline-flex items-center gap-1">
                {{ cn }}
                <i class="fa fa-times cursor-pointer hover:text-indigo-800" @click="removeCategory(cn)"></i>
              </span>
            </div>
            <button type="button" @click="goToCategorySelect"
              class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-600 hover:bg-indigo-50 hover:border-indigo-300 transition-all text-left flex items-center justify-between">
              <span :class="selectedCategoryNames ? 'text-slate-800' : 'text-slate-400'">
                {{ selectedCategoryNames ? selectedCategoryNames.join(', ') : '点击选择分类标签...' }}
              </span>
              <i class="fa fa-tags text-indigo-400"></i>
            </button>
          </div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useFlashStore } from '../stores/flash'
import api from '../api'

const router = useRouter(); const route = useRoute(); const flash = useFlashStore()
const t = ref(''); const a = ref(''); const c = ref(''); const pd = ref(''); const kw = ref(''); const ab = ref('')
const file = ref(null); const fileName = ref(''); const err = ref(''); const ld = ref(false)
const fileInputRef = ref(null)

const STORAGE_KEY = 'upload_draft'

// 保存草稿到 sessionStorage
function saveDraft() {
  const draft = {
    title: t.value, author: a.value, category: c.value,
    publishDate: pd.value, keywords: kw.value, abstract: ab.value,
    fileName: fileName.value,
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(draft))
}

// 从 sessionStorage 恢复草稿
function loadDraft() {
  const raw = sessionStorage.getItem(STORAGE_KEY)
  if (!raw) return
  try {
    const draft = JSON.parse(raw)
    t.value = draft.title || ''
    a.value = draft.author || ''
    pd.value = draft.publishDate || ''
    kw.value = draft.keywords || ''
    ab.value = draft.abstract || ''
    fileName.value = draft.fileName || ''
    // 分类优先从 URL query 取（刚从分类页返回），否则用草稿
    const cats = route.query.categories
    if (cats) {
      c.value = cats
    } else if (draft.category) {
      c.value = draft.category
    }
  } catch (e) { /* ignore */ }
}

// 清除草稿
function clearDraft() {
  sessionStorage.removeItem(STORAGE_KEY)
}

const selectedCategoryNames = computed(() => {
  return c.value ? c.value.split(',').map(s => s.trim()).filter(Boolean) : null
})

onMounted(() => {
  const cats = route.query.categories
  if (cats) {
    c.value = cats
  }
  // 从分类页返回时恢复其他字段（不含文件，File 对象无法序列化）
  if (cats || route.query.fromCategory === '1') {
    loadDraft()
  }
})

// 跳转分类选择前保存表单，并清除文件（File 对象无法跨页面保持）
function goToCategorySelect() {
  saveDraft()
  router.push({ path: '/select_category', query: { returnTo: 'upload', selected: c.value } })
}

function removeCategory(name) {
  const names = c.value.split(',').map(s => s.trim()).filter(s => s && s !== name)
  c.value = names.join(',')
}

function onF(e) {
  const f = e.target.files[0]
  if (f) {
    file.value = f
    fileName.value = f.name
  }
}

function onReSelect() {
  file.value = null
  fileName.value = ''
  // 延迟一帧等 DOM 重新渲染出 input，再触发点击
  setTimeout(() => {
    fileInputRef.value?.click()
  }, 0)
}

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
    if (r.data.code === 200) {
      clearDraft()
      flash.show('文献上传成功', 'success')
      router.push(`/document/${r.data.data.document_id}`)
    }
    else err.value = r.data.message
  } catch (e) { err.value = e.response?.data?.message || '网络错误' } finally { ld.value = false }
}
</script>

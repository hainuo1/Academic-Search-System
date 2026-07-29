<template>
<div class="max-w-4xl mx-auto px-4 py-12">
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-8">
    <div class="flex items-center gap-3 mb-6">
      <div class="w-10 h-10 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center">
        <i class="fa fa-pencil-square-o text-white text-lg"></i>
      </div>
      <div>
        <h2 class="text-2xl font-bold text-slate-800">编辑文献</h2>
        <p class="text-slate-500 text-sm">修改文献的元数据信息</p>
      </div>
    </div>

    <div v-if="err" class="mb-6 bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-xl flex items-center text-sm">
      <i class="fa fa-exclamation-circle mr-2"></i>{{ err }}
    </div>

    <div v-if="loading" class="text-center py-16">
      <div class="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4"></div>
      <p class="text-slate-500">加载中...</p>
    </div>

    <form v-else @submit.prevent="go">
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">标题 <span class="text-red-500">*</span></label>
        <input v-model="t" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">作者 <span class="text-red-500">*</span></label>
        <input v-model="a" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">分类 <span class="text-red-500">*</span></label>
        <div v-if="selectedCategoryNames" class="flex flex-wrap gap-1.5 mb-2">
          <span v-for="cn in selectedCategoryNames" :key="cn"
            class="bg-indigo-50 text-indigo-600 px-2.5 py-0.5 rounded-lg text-xs font-medium inline-flex items-center gap-1">
            {{ cn }}
            <i class="fa fa-times cursor-pointer hover:text-indigo-800" @click="removeCategory(cn)"></i>
          </span>
        </div>
        <button type="button" @click="goToCategorySelect"
          class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm hover:bg-indigo-50 hover:border-indigo-300 transition-all text-left flex items-center justify-between">
          <span :class="selectedCategoryNames ? 'text-slate-800' : 'text-slate-400'">
            {{ selectedCategoryNames ? selectedCategoryNames.join(', ') : '点击选择分类标签...' }}
          </span>
          <i class="fa fa-tags text-indigo-400"></i>
        </button>
      </div>
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">发表日期 <span class="text-red-500">*</span></label>
        <input v-model="pd" type="date" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">关键词 <span class="text-red-500">*</span></label>
        <input v-model="kw" type="text" placeholder="例如：AI;机器学习;知识图谱" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
        <p class="text-slate-500 text-sm mt-1">多个关键词用分号分隔</p>
      </div>
      <div class="mb-8">
        <label class="block mb-2 font-medium text-slate-700 text-sm">摘要 <span class="text-red-500">*</span></label>
        <textarea v-model="ab" rows="6" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none"></textarea>
      </div>

      <div class="flex gap-4">
        <button type="submit" :disabled="ld"
          class="px-8 py-3 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2">
          <span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>保存中...</span>
          <span v-else><i class="fa fa-save mr-2"></i>保存修改</span>
        </button>
        <router-link to="/my_documents" class="px-8 py-3 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-2xl font-medium transition-all">取消</router-link>
      </div>
    </form>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashStore } from '../stores/flash'
import api from '../api'

const route = useRoute(); const router = useRouter(); const flash = useFlashStore()
const t = ref(''); const a = ref(''); const c = ref(''); const pd = ref(''); const kw = ref(''); const ab = ref('')
const err = ref(''); const loading = ref(true); const ld = ref(false)

const DRAFT_KEY = 'edit_draft'

const selectedCategoryNames = computed(() => {
  return c.value ? c.value.split(',').map(s => s.trim()).filter(Boolean) : null
})

function saveDraft() {
  sessionStorage.setItem(DRAFT_KEY, JSON.stringify({
    title: t.value, author: a.value, category: c.value,
    publishDate: pd.value, keywords: kw.value, abstract: ab.value,
    docId: route.params.id,
  }))
}

function clearDraft() {
  sessionStorage.removeItem(DRAFT_KEY)
}

onMounted(async () => {
  const fromCategory = !!route.query.categories
  if (fromCategory) {
    // 从分类选择页返回，优先恢复草稿中的表单数据
    const raw = sessionStorage.getItem(DRAFT_KEY)
    if (raw) {
      try {
        const draft = JSON.parse(raw)
        if (draft.docId === route.params.id || draft.docId === String(route.params.id)) {
          t.value = draft.title || ''
          a.value = draft.author || ''
          pd.value = draft.publishDate || ''
          kw.value = draft.keywords || ''
          ab.value = draft.abstract || ''
        }
      } catch (e) { /* ignore */ }
    }
    c.value = route.query.categories
    loading.value = false
    return
  }

  // 首次进入：从后端加载
  try {
    const r = await api.get(`/api/document/${route.params.id}/edit-data`)
    if (r.data.code === 200) {
      const d = r.data.data.document
      t.value = d.title; a.value = d.author; c.value = d.category
      pd.value = d.publish_date; kw.value = d.keywords; ab.value = d.abstract
    } else {
      err.value = '加载文献信息失败'
    }
  } catch (e) { err.value = '加载文献信息失败' } finally { loading.value = false }
})

function goToCategorySelect() {
  saveDraft()
  router.push({ path: '/select_category', query: { returnTo: 'edit', docId: route.params.id, selected: c.value } })
}

function removeCategory(name) {
  const names = c.value.split(',').map(s => s.trim()).filter(s => s && s !== name)
  c.value = names.join(',')
}

async function go() {
  err.value = ''; ld.value = true
  try {
    const r = await api.put(`/api/document/${route.params.id}`, { title: t.value, author: a.value, category: c.value, publish_date: pd.value, keywords: kw.value, abstract: ab.value })
    if (r.data.code === 200) { clearDraft(); flash.show('修改保存成功', 'success'); router.push('/my_documents') }
    else err.value = r.data.message
  } catch (e) { err.value = e.response?.data?.message || '保存失败' } finally { ld.value = false }
}
</script>

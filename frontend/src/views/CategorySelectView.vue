<template>
<div class="min-h-screen bg-slate-50">
  <div class="bg-gradient-to-r from-slate-800 to-indigo-900 text-white">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 py-6">
      <button @click="goBack"
        class="text-slate-300 hover:text-white transition-colors mb-3 flex items-center gap-1.5 text-sm">
        <i class="fa fa-arrow-left"></i>返回上传页面
      </button>
      <h1 class="text-2xl font-bold">选择文献分类标签</h1>
      <p class="text-slate-300 text-sm mt-1">可多选，已选标签返回后将填入分类字段</p>
    </div>
  </div>

  <div class="max-w-3xl mx-auto px-4 sm:px-6 py-6">
    <!-- 搜索 -->
    <div class="relative mb-4">
      <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400">
        <i class="fa fa-search"></i>
      </span>
      <input v-model="search" type="text" placeholder="搜索分类标签..."
        class="w-full pl-11 pr-4 py-3 bg-white/80 backdrop-blur-xl border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all">
    </div>

    <!-- 已选标签预览 -->
    <div v-if="selected.size > 0" class="bg-indigo-50/80 backdrop-blur-sm border border-indigo-100 rounded-2xl p-4 mb-4">
      <div class="flex items-center gap-2 mb-2">
        <i class="fa fa-check-circle text-indigo-500"></i>
        <span class="text-sm font-semibold text-indigo-700">已选择 {{ selected.size }} 个分类</span>
      </div>
      <div class="flex flex-wrap gap-1.5">
        <span v-for="name in Array.from(selected)" :key="name"
          @click="toggle(name)"
          class="bg-indigo-600 text-white px-3 py-1 rounded-full text-xs font-medium cursor-pointer hover:bg-indigo-700 transition-colors flex items-center gap-1">
          {{ name }} <i class="fa fa-times text-indigo-300"></i>
        </span>
      </div>
    </div>

    <!-- 分类标签网格 -->
    <div v-if="loading" class="text-center py-16">
      <div class="w-10 h-10 border-3 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-3"></div>
      <p class="text-slate-500 text-sm">加载分类标签...</p>
    </div>

    <div v-else class="bg-white/80 backdrop-blur-xl rounded-2xl border border-slate-100 shadow-sm p-5">
      <div class="flex flex-wrap gap-2">
        <button v-for="cat in filteredCategories" :key="cat.id"
          @click="toggle(cat.name)"
          :class="selected.has(cat.name)
            ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
          class="px-4 py-2 rounded-xl text-sm font-medium transition-all cursor-pointer">
          {{ cat.name }}
        </button>
        <div v-if="filteredCategories.length === 0" class="text-center w-full py-10 text-slate-400">
          <i class="fa fa-search text-2xl block mb-2"></i>
          <p class="text-sm">未找到匹配的分类标签</p>
        </div>
      </div>
    </div>

    <!-- 底栏 -->
    <div class="mt-6 flex gap-3 justify-end">
      <button @click="goBack"
        class="px-6 py-3 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-2xl text-sm font-medium transition-all">
        取消
      </button>
      <button @click="confirmSelection"
        class="px-8 py-3 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-2xl text-sm font-medium hover:shadow-lg hover:-translate-y-0.5 transition-all">
        <i class="fa fa-check mr-1.5"></i>确认选择（{{ selected.size }} 个）
      </button>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../api'

const router = useRouter()
const route = useRoute()
const categories = ref([])
const loading = ref(true)
const search = ref('')
const selected = ref(new Set())

// 从 query 中恢复之前的选择
onMounted(async () => {
  try {
    const r = await api.get('/api/categories')
    if (r.data.code === 200) {
      categories.value = r.data.data.categories || []
    }
  } catch (e) {
    console.error('加载分类失败:', e)
  } finally {
    loading.value = false
  }

  // 恢复之前的选择
  const preselected = route.query.selected
  if (preselected) {
    const names = preselected.split(',').map(s => s.trim()).filter(Boolean)
    names.forEach(n => selected.value.add(n))
  }
})

const filteredCategories = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return categories.value
  return categories.value.filter(c => c.name.toLowerCase().includes(q))
})

function toggle(name) {
  if (selected.value.has(name)) {
    selected.value.delete(name)
  } else {
    selected.value.add(name)
  }
  // 触发响应式
  selected.value = new Set(selected.value)
}

function confirmSelection() {
  const names = Array.from(selected.value).join(',')
  // 带回上传页面
  const returnTo = route.query.returnTo || '/upload'
  if (returnTo === 'upload') {
    router.push({ path: '/upload', query: { categories: names } })
  } else if (returnTo === 'edit') {
    const docId = route.query.docId
    router.push({ path: `/edit_document/${docId}`, query: { categories: names } })
  } else {
    router.back()
  }
}

function goBack() {
  router.back()
}
</script>

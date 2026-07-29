<template>
<div class="max-w-4xl mx-auto px-4 py-8">
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 md:p-8">
    <div class="flex items-center gap-3 mb-6 pb-4 border-b border-slate-100">
      <div class="w-10 h-10 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center">
        <i class="fa fa-link text-white text-lg"></i>
      </div>
      <div>
        <h2 class="text-2xl font-bold text-slate-800">设置引用关系</h2>
        <p class="text-slate-500 text-sm">为当前文献添加引用关系</p>
      </div>
    </div>

    <div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-4 mb-6 border border-indigo-100">
      <div class="flex items-center gap-3">
        <i class="fa fa-file-text-o text-indigo-500"></i>
        <span class="text-sm text-slate-700">当前文献：<strong class="text-slate-800">{{ cd?.title || '加载中...' }}</strong></span>
      </div>
      <!-- 目前已引用的文献 -->
      <div v-if="existingDocs.length" class="mt-3 pt-3 border-t border-indigo-200/60">
        <p class="text-xs text-slate-500 mb-2 flex items-center gap-1">
          <i class="fa fa-link"></i>目前已引用的文献（{{ existingDocs.length }} 篇）
        </p>
        <div class="flex flex-wrap gap-1.5">
          <span v-for="d in existingDocs" :key="d.id"
            class="bg-indigo-600/10 text-indigo-700 px-2.5 py-1 rounded-full text-xs font-medium">
            {{ d.title }} <span class="text-indigo-400 ml-1">{{ d.author }}</span>
            <i class="fa fa-times ml-1 cursor-pointer hover:text-red-500" @click="removeExisting(d.id)"></i>
          </span>
        </div>
      </div>
      <p v-else class="mt-2 text-xs text-slate-400">暂未引用任何文献</p>
    </div>

    <div v-if="err" class="mb-4 px-4 py-3 bg-red-50 border border-red-100 text-red-600 rounded-xl text-sm flex items-center">
      <i class="fa fa-exclamation-circle mr-2"></i>{{ err }}
    </div>

    <div v-if="succ" class="mb-4 px-4 py-3 bg-emerald-50 border border-emerald-100 text-emerald-600 rounded-xl text-sm flex items-center">
      <i class="fa fa-check-circle mr-2"></i>{{ succ }}
    </div>

    <div class="mb-4">
      <div class="relative">
        <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400">
          <i class="fa fa-search"></i>
        </span>
        <input v-model="skw" type="text" @keyup.enter="searchCit" placeholder="输入标题搜索文献"
          class="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>
    </div>

    <button type="button" @click="searchCit" :disabled="searching"
      class="px-5 py-2.5 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed">
      <i v-if="searching" class="fa fa-spinner fa-spin mr-1"></i>
      {{ searching ? '搜索中...' : '搜索文献' }}
    </button>

    <!-- 搜索结果 -->
    <div v-if="sres.length" class="mt-6 space-y-2">
      <div v-for="d in sres" :key="d.id" class="flex justify-between items-center p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-indigo-200 transition-all">
        <div><span class="text-slate-800 font-medium">{{ d.title }}</span><span class="text-slate-400 text-sm ml-2">{{ d.author }}</span></div>
        <button type="button" @click.stop="addCit(d)"
          :class="isSelected(d.id) ? 'bg-emerald-100 text-emerald-600' : 'bg-indigo-50 text-indigo-600 hover:bg-indigo-100'"
          class="px-4 py-1.5 rounded-lg text-sm font-medium transition whitespace-nowrap">
          {{ isSelected(d.id) ? '已添加' : '添加引用' }}
        </button>
      </div>
    </div>
    <p v-if="searched && !sres.length && !searching" class="text-slate-400 py-6 text-center">未找到匹配的文献</p>

    <!-- 已选引用 -->
    <div v-if="sel.length" class="mt-6">
      <h3 class="text-base font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <i class="fa fa-check-circle text-emerald-500"></i>已选引用文献（{{ sel.length }} 篇）
      </h3>
      <div class="space-y-2">
        <div v-for="d in sel" :key="d.id" class="flex justify-between items-center p-4 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl border border-indigo-100">
          <router-link :to="`/document/${d.id}`" class="text-indigo-600 hover:text-indigo-800 font-medium text-sm transition-colors">{{ d.title }}</router-link>
          <button type="button" @click="rmCit(d.id)" class="w-8 h-8 bg-white/80 rounded-lg flex items-center justify-center text-red-400 hover:text-red-600 hover:bg-red-50 transition-all"><i class="fa fa-times"></i></button>
        </div>
      </div>
    </div>

    <button type="button" @click="saveCit" :disabled="saving"
      class="mt-6 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm disabled:opacity-50 disabled:cursor-not-allowed">
      <i v-if="saving" class="fa fa-spinner fa-spin mr-2"></i>
      <i v-else class="fa fa-floppy-o mr-2"></i>
      {{ saving ? '保存中...' : `保存引用关系（${sel.length} 篇）` }}
    </button>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashStore } from '../stores/flash'
import api from '../api'

const route = useRoute(); const router = useRouter(); const flash = useFlashStore()
const cd = ref(null); const existingDocs = ref([]); const sel = ref([]); const skw = ref(''); const sres = ref([])
const searched = ref(false); const searching = ref(false); const saving = ref(false)
const err = ref(''); const succ = ref('')

onMounted(async () => {
  try {
    const r = await api.get(`/api/citation/${route.params.id}`)
    if (r.data.code === 200) {
      cd.value = r.data.data.current_doc
      existingDocs.value = r.data.data.existing_docs || []
      sel.value = [...existingDocs.value]
    } else {
      err.value = r.data.message || '加载当前文献信息失败'
    }
  } catch (e) {
    err.value = e.response?.data?.detail || e.response?.data?.message || '加载失败，请检查网络连接'
  }
})

async function searchCit() {
  const keyword = skw.value.trim()
  if (!keyword) return
  err.value = ''; succ.value = ''; searched.value = true; searching.value = true
  try {
    const r = await api.get('/api/search_citation', { params: { keyword, doc_id: route.params.id } })
    if (r.data.code === 200) {
      sres.value = r.data.data.results
      if (r.data.data.results.length === 0) {
        succ.value = '未找到匹配的文献，请尝试其他关键词'
      }
    } else {
      err.value = r.data.message || '搜索失败'
      sres.value = []
    }
  } catch (e) {
    err.value = e.response?.data?.detail || e.response?.data?.message || '搜索失败，请稍后重试'
    sres.value = []
  } finally {
    searching.value = false
  }
}

function isSelected(id) {
  return sel.value.some(x => x.id === id)
}

function addCit(d) {
  err.value = ''; succ.value = ''
  if (!isSelected(d.id)) {
    sel.value = [...sel.value, d]
    succ.value = `已添加引用文献「${d.title}」`
    setTimeout(() => { succ.value = '' }, 3000)
  }
}

function rmCit(id) {
  sel.value = sel.value.filter(x => x.id !== id)
}

// 删除已存在于数据库中的引用
function removeExisting(id) {
  existingDocs.value = existingDocs.value.filter(x => x.id !== id)
  sel.value = sel.value.filter(x => x.id !== id)
}

async function saveCit() {
  err.value = ''; succ.value = ''
  if (sel.value.length === 0) {
    err.value = '请先添加至少一篇引用文献'
    return
  }
  saving.value = true
  try {
    const r = await api.post(`/api/save_citation/${route.params.id}`, { target_doc_ids: sel.value.map(d => d.id) })
    if (r.data.code === 200) {
      flash.show('引用关系已保存', 'success')
      router.push('/my_documents')
    } else {
      err.value = r.data.message || '保存失败'
    }
  } catch (e) {
    err.value = e.response?.data?.detail || e.response?.data?.message || '保存失败，请稍后重试'
  } finally {
    saving.value = false
  }
}
</script>

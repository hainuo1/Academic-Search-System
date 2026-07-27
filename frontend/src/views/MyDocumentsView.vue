<template>
<div class="max-w-6xl mx-auto px-4 py-8">
  <div class="mb-8">
    <div class="flex items-center mb-2">
      <div class="w-10 h-10 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center mr-3 shadow-md">
        <i class="fa fa-file-text text-white text-lg"></i>
      </div>
      <div>
        <h1 class="text-2xl font-bold text-slate-800">我的文献</h1>
        <p class="text-slate-500 text-sm">管理您上传的所有学术文献</p>
      </div>
    </div>
  </div>

  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 md:p-8">
    <div class="flex justify-between items-center mb-6 pb-4 border-b border-slate-100">
      <span class="text-sm text-slate-500">共 {{ docs.length }} 篇文献</span>
      <router-link to="/upload" class="px-5 py-2.5 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm flex items-center gap-2">
        <i class="fa fa-upload"></i> 上传新文献
      </router-link>
    </div>

    <div v-if="docs.length" class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="bg-slate-50">
            <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">ID</th>
            <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">标题</th>
            <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">作者</th>
            <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">发表日期</th>
            <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in docs" :key="d.id" class="hover:bg-slate-50 border-b border-slate-50 last:border-0">
            <td class="py-3 px-4 text-sm text-slate-500">{{ d.id }}</td>
            <td class="py-3 px-4 text-sm text-slate-800">{{ d.title }}</td>
            <td class="py-3 px-4 text-sm text-slate-500">{{ d.author }}</td>
            <td class="py-3 px-4 text-sm text-slate-500">{{ d.publish_date }}</td>
            <td class="py-3 px-4">
              <div class="flex flex-wrap gap-1.5">
                <router-link :to="`/document/${d.id}`" class="bg-indigo-50 text-indigo-600 hover:bg-indigo-100 px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap">查看</router-link>
                <router-link :to="`/citation/${d.id}`" class="bg-amber-50 text-amber-600 hover:bg-amber-100 px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap">设置引用</router-link>
                <a href="#" @click.prevent="downloadPdf(d.id)" class="bg-emerald-50 text-emerald-600 hover:bg-emerald-100 px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap">下载</a>
                <router-link :to="`/edit_document/${d.id}`" class="bg-purple-50 text-purple-600 hover:bg-purple-100 px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap">编辑</router-link>
                <button @click="confirmDel(d)" class="bg-red-50 text-red-600 hover:bg-red-100 px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap cursor-pointer">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center py-16">
      <div class="w-24 h-24 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
        <i class="fa fa-file-text-o text-indigo-400 text-4xl"></i>
      </div>
      <h3 class="text-xl font-bold text-slate-700 mb-2">暂无文献</h3>
      <p class="text-slate-500 mb-6">您暂时还没有上传任何文献</p>
      <router-link to="/upload" class="inline-block px-6 py-3 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all">立即上传</router-link>
    </div>
  </div>

  <!-- 删除确认弹窗 -->
  <div v-if="showModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
    <div class="bg-white rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl border border-slate-100">
      <div class="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-4">
        <i class="fa fa-exclamation-triangle text-red-500 text-lg"></i>
      </div>
      <h3 class="text-xl font-bold text-slate-800 mb-2">确认删除</h3>
      <p class="text-slate-600 mb-6">确定删除文献 "{{ delTarget?.title }}" 吗？此操作不可撤销。</p>
      <div class="flex gap-3 justify-end">
        <button @click="showModal = false" class="px-5 py-2.5 bg-slate-100 text-slate-600 rounded-xl hover:bg-slate-200 transition font-medium text-sm">取消</button>
        <button @click="doDel" class="px-5 py-2.5 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-xl hover:shadow-lg transition-all font-medium text-sm">确认删除</button>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useFlashStore } from '../stores/flash'
import api from '../api'

const flash = useFlashStore()
const docs = ref([]); const showModal = ref(false); const delTarget = ref(null)

onMounted(async () => {
  try { const r = await api.get('/api/my_documents'); if (r.data.code === 200) docs.value = r.data.data.documents } catch (e) { console.error('加载文献列表失败:', e) }
})

function confirmDel(d) { delTarget.value = d; showModal.value = true }

async function doDel() {
  try {
    const r = await api.delete(`/api/document/${delTarget.value.id}`)
    if (r.data.code === 200) { docs.value = docs.value.filter(x => x.id !== delTarget.value.id); flash.show('文献已成功删除', 'success') }
    else flash.show(r.data.message, 'error')
  } catch (e) { flash.show(e.response?.data?.message || '删除失败', 'error') } finally { showModal.value = false; delTarget.value = null }
}

async function downloadPdf(docId) {
  try {
    const token = localStorage.getItem('token') || ''
    // 用 axios 发起带 Authorization 头的 blob 下载
    const resp = await api.get(`/api/download/${docId}`, {
      responseType: 'blob',
      headers: { Authorization: `Bearer ${token}` }
    })
    // 成功：创建 Blob URL 并触发下载
    const url = window.URL.createObjectURL(new Blob([resp.data]))
    const link = document.createElement('a')
    link.href = url
    // 从 content-disposition 或默认命名
    const disposition = resp.headers['content-disposition']
    let filename = 'document.pdf'
    if (disposition) {
      const match = disposition.match(/filename="?(.+)"?/)
      if (match) filename = decodeURIComponent(match[1])
    }
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) {
    if (e.response && e.response.status === 404) {
      alert('PDF 文件不存在，可能已被删除')
    } else if (e.response && e.response.status === 401) {
      alert('暂未登录，请先登录后再下载')
    } else {
      alert('下载失败，请稍后重试')
    }
  }
}
</script>

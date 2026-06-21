// ============================================================
// static/js/citation.js —— 引用关系设置页交互逻辑
//
// 对应页面：citation.html
// 功能：在引用设置页面，输入关键词后异步搜索可引用的文献，
//       并把结果渲染成带复选框的列表
// ============================================================


// ============================================================
// 搜索可引用的文献
//
// 这个函数被 citation.html 里的"搜索文献"按钮调用。
// 注意：doc_id 和 selected_ids 由 HTML 模板通过
//       全局变量注入（在 citation.html 里定义），
//       这里直接使用。
// ============================================================
function searchDocument() {
    // 获取用户输入的关键词
    const keyword = document.getElementById('keyword').value.trim();

    if (!keyword) {
        return;  // 关键词为空就不搜索
    }

    // 向后端的 /search_citation 接口发请求
    // 带上关键词和当前文献 ID（用于排除自身）
    fetch(`/search_citation?keyword=${encodeURIComponent(keyword)}&doc_id=${CURRENT_DOC_ID}`)
        .then(res => res.json())
        .then(data => {
            // 拿到搜索结果后，动态生成 HTML 插入到页面里
            let html = '';

            if (data.length === 0) {
                html = '<p class="text-gray-500 py-4 text-center">没有找到相关文献</p>';
            } else {
                data.forEach(doc => {
                    // 判断这篇文献是否已经被选中（之前就已经引用了）
                    // SELECTED_IDS 是从 HTML 模板注入的已选 ID 列表
                    const isChecked = SELECTED_IDS.includes(doc.DocumentID) ? 'checked' : '';

                    html += `
                        <div class="border p-3 rounded mb-2 hover:bg-gray-50">
                            <label class="flex items-start gap-3 cursor-pointer">
                                <input
                                    type="checkbox"
                                    name="target_doc_ids"
                                    value="${doc.DocumentID}"
                                    ${isChecked}
                                    class="mt-1"
                                >
                                <div>
                                    <div class="font-medium text-gray-800">${doc.Title}</div>
                                    <div class="text-sm text-gray-500">${doc.Author}</div>
                                </div>
                            </label>
                        </div>
                    `;
                });
            }

            // 把生成的 HTML 插入到页面的结果区域
            document.getElementById('resultArea').innerHTML = html;
        })
        .catch(err => {
            console.error('搜索文献失败：', err);
        });
}
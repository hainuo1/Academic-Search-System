// ============================================================
// static/js/document.js —— 文献详情页交互逻辑
//
// 对应页面：document.html
// 功能：收藏 / 取消收藏按钮的异步切换
// ============================================================


// ============================================================
// 收藏 / 取消收藏
//
// 参数：docId → 当前文献的 ID（从 HTML 里传入）
//
// 流程：
// 1. 向后端发送 POST 请求（Ajax，不刷新页面）
// 2. 后端返回 { success: true, is_favorited: true/false }
// 3. 根据返回结果更新按钮的样式和文字
// ============================================================
function toggleFavorite(docId) {
    // fetch 是浏览器内置的发送 HTTP 请求的函数
    fetch('/toggle_favorite', {
        method: 'POST',
        headers: {
            // 告诉后端：我发送的数据格式是 JSON
            'Content-Type': 'application/json',
        },
        // JSON.stringify 把 JS 对象转成 JSON 字符串发送
        body: JSON.stringify({ document_id: docId })
    })
    .then(res => res.json())   // 把后端返回的 JSON 字符串解析成 JS 对象
    .then(data => {
        if (data.success) {
            // 找到页面上的按钮、图标、文字元素
            const btn  = document.getElementById('favoriteBtn');
            const icon = document.getElementById('favoriteIcon');
            const text = document.getElementById('favoriteText');

            if (data.is_favorited) {
                // 变成"已收藏"状态：黄色按钮 + 实心星星
                btn.className  = 'btn-hover flex items-center gap-2 px-4 py-2 rounded-lg border transition-all bg-yellow-50 border-yellow-300 text-yellow-600';
                icon.className = 'fa fa-star';
                text.innerText = '已收藏';
            } else {
                // 变成"未收藏"状态：灰色按钮 + 空心星星
                btn.className  = 'btn-hover flex items-center gap-2 px-4 py-2 rounded-lg border transition-all bg-gray-50 border-gray-300 text-gray-600';
                icon.className = 'fa fa-star-o';
                text.innerText = '收藏';
            }
        }
    })
    .catch(err => {
        // catch：如果请求失败（比如断网），在控制台打印错误
        // 用户看不到这个，但开发者可以按 F12 在控制台里看到
        console.error('收藏操作失败：', err);
    });
}
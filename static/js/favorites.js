// ============================================================
// static/js/favorites.js —— 我的收藏页交互逻辑
//
// 对应页面：favorites.html
// 功能：在收藏列表里点击"取消收藏"按钮，异步删除并刷新列表
// ============================================================


// ============================================================
// 取消收藏
//
// 参数：docId → 要取消收藏的文献 ID
//
// 流程：
// 1. 弹出确认对话框，用户点"取消"就中止操作
// 2. 向后端发送 POST 请求
// 3. 成功后刷新当前页面，更新收藏列表
// ============================================================
function cancelFavorite(docId) {
    // confirm 弹出一个浏览器原生的确认对话框
    // 用户点"确定"返回 true，点"取消"返回 false
    if (!confirm('确定要取消收藏这篇文献吗？')) {
        return;  // 用户点了"取消"，直接退出函数，什么都不做
    }

    fetch('/toggle_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ document_id: docId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // 取消收藏成功后，刷新整个页面来更新列表
            // location.reload() 相当于按了浏览器的"刷新"按钮
            location.reload();
        }
    })
    .catch(err => {
        console.error('取消收藏失败：', err);
    });
}
// ============================================================
// static/js/upload.js —— 上传文献页交互逻辑
//
// 对应页面：upload.html
// 功能：
//   1. 上传按钮状态：点击提交后按钮变成"上传中..."并禁用，
//      防止用户重复点击提交多次
// ============================================================

document.addEventListener('DOMContentLoaded', function () {

    // --------------------------------------------------------
    // 上传按钮防重复点击
    //
    // 上传大文件需要时间，如果用户反复点击"上传"按钮，
    // 会发出多个请求，导致重复上传。
    // 解决方案：点击一次后立即禁用按钮并修改文字提示。
    // --------------------------------------------------------
    const uploadForm = document.querySelector('form[enctype="multipart/form-data"]');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function () {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                // disabled = true：按钮变灰、无法再次点击
                submitBtn.disabled = true;
                // innerHTML：修改按钮里显示的内容（包含图标）
                // fa-spinner fa-spin 是一个旋转的加载图标
                submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin mr-2"></i>上传中，请稍候...';
            }
        });
    }
});
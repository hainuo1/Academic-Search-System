// ============================================================
// static/js/captcha.js —— 验证码刷新与交互逻辑
// 对应页面：forgot_password.html
// ============================================================

// 定义全局刷新函数（供 HTML 的 onclick 调用）
window.refreshCaptcha = function() {
    const img = document.getElementById('captcha_img');
    // 使用 data 属性获取 URL，或者直接写 '/captcha'
    // 这里从 HTML 的 data-captcha-url 属性读取，更灵活
    if (img) {
        const baseUrl = img.dataset.captchaUrl || '/captcha';
        img.src = baseUrl + '?' + new Date().getTime();
    }
};

// 页面加载完成后，绑定自动刷新逻辑
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('captcha_input');
    if (input) {
        // 当用户点击输入框时，如果为空则自动刷新验证码
        input.addEventListener('focus', function() {
            if (this.value === '') {
                window.refreshCaptcha();
            }
        });
    }
});
// ============================================================
// static/js/app.js —— 全局公共 JS
//
// 功能：
//   1. 折叠面板的展开/收起（通用，适用于所有页面）
// ============================================================

// ============================================================
// 折叠面板控制
// 使用方式：在任意页面中，给标题栏添加 class="panel-header"
// 并设置 data-target="内容区ID"，内容区添加 id="xxx"
// 点击标题栏即可切换内容区的显示/隐藏
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
    const headers = document.querySelectorAll('.panel-header');

    headers.forEach(function(header) {
        header.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const content = document.getElementById(targetId);
            const icon = this.querySelector('.panel-icon');

            if (!content) return;

            content.classList.toggle('hidden');

            if (icon) {
                if (content.classList.contains('hidden')) {
                    icon.style.transform = 'rotate(0deg)';
                } else {
                    icon.style.transform = 'rotate(180deg)';
                }
            }
        });
    });
});
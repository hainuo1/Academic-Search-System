// ============================================================
// static/js/index.js —— 首页打字机效果
// ============================================================

document.addEventListener('DOMContentLoaded', function () {
    const phrases = [
        { icon: '🔍', text: '智能检索，精准定位目标文献' },
        { icon: '📊', text: '数据洞察，掌握研究趋势' },
        { icon: '🔗', text: '引用分析，追踪学术脉络' },
        { icon: '⭐', text: '收藏管理，构建个人知识库' },
        { icon: '📚', text: '海量文献，一站式获取' }
    ];

    let phraseIndex = 0;
    let charIndex = 0;
    let isIconShown = false;
    const typedElement = document.getElementById('typed-text');

    if (!typedElement) return;

    const TYPING_SPEED = 150;
    const PAUSE_AFTER_COMPLETE = 2000;
    const PAUSE_BEFORE_NEXT = 300;

    function typeEffect() {
        const current = phrases[phraseIndex];

        if (!isIconShown) {
            typedElement.textContent = current.icon + ' ';
            isIconShown = true;
            setTimeout(typeEffect, 300);
            return;
        }

        if (charIndex < current.text.length) {
            typedElement.textContent = current.icon + ' ' + current.text.substring(0, charIndex + 1);
            charIndex++;
            setTimeout(typeEffect, TYPING_SPEED);
        } else {
            setTimeout(() => {
                typedElement.textContent = '';
                charIndex = 0;
                isIconShown = false;
                phraseIndex = (phraseIndex + 1) % phrases.length;
                setTimeout(typeEffect, PAUSE_BEFORE_NEXT);
            }, PAUSE_AFTER_COMPLETE);
        }
    }

    setTimeout(typeEffect, 500);
});
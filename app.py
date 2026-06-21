# ============================================================
# app.py —— 程序入口文件
# ============================================================

import os
import re
from flask import Flask, render_template
from markupsafe import Markup, escape
from config import Config
from db import close_connection   # 新增导入


def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)

    # --------------------------------------------------------
    # 加载配置
    # --------------------------------------------------------
    app.config.from_object(Config)

    # --------------------------------------------------------
    # 确保上传文件夹存在
    # --------------------------------------------------------
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --------------------------------------------------------
    # 注册蓝图
    # --------------------------------------------------------
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes.document import document_bp
    app.register_blueprint(document_bp)

    from routes.search import search_bp
    app.register_blueprint(search_bp)

    from routes.stats import stats_bp
    app.register_blueprint(stats_bp)

    from routes.favorites import favorites_bp
    app.register_blueprint(favorites_bp)

    from routes.citation import citation_bp
    app.register_blueprint(citation_bp)

    from routes.profile import profile_bp
    app.register_blueprint(profile_bp)

    # --------------------------------------------------------
    # 注册请求结束钩子：自动关闭数据库连接
    # --------------------------------------------------------
    app.teardown_appcontext(close_connection)

    # --------------------------------------------------------
    # 自定义 Jinja2 过滤器：关键词高亮
    # --------------------------------------------------------
    def highlight_filter(text, keyword):
        if not keyword or not text:
            return text
        escaped_text = escape(text)
        escaped_keyword = escape(keyword)
        pattern = re.compile(re.escape(escaped_keyword), re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f'<mark class="search-highlight">{m.group(0)}</mark>',
            escaped_text
        )
        return Markup(highlighted)

    app.jinja_env.filters['highlight'] = highlight_filter

    # --------------------------------------------------------
    # 全局错误处理器
    # --------------------------------------------------------
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', message='您访问的页面不存在，请检查链接是否正确。'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        if app.debug:
            raise e
        return render_template('error.html', message='服务器内部错误，请稍后重试。'), 500

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        if app.debug:
            raise e
        print(f"未捕获的异常: {e}")
        return render_template('error.html', message='系统出现异常，请稍后重试。'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from db import close_connection


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True, origins=['http://localhost:5173'])
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    from routes.search import search_bp
    app.register_blueprint(search_bp)
    from routes.document import doc_bp
    app.register_blueprint(doc_bp)
    from routes.favorites import fav_bp
    app.register_blueprint(fav_bp)
    from routes.citation import cit_bp
    app.register_blueprint(cit_bp)
    from routes.profile import prof_bp
    app.register_blueprint(prof_bp)
    from routes.stats import stats_bp
    app.register_blueprint(stats_bp)
    from routes.typhoon import typhoon_bp
    app.register_blueprint(typhoon_bp)
    from routes.earthquake import earthquake_bp
    app.register_blueprint(earthquake_bp)
    from routes.tornado import tornado_bp
    app.register_blueprint(tornado_bp)

    app.teardown_appcontext(close_connection)

    @app.errorhandler(404)
    def _404(e):
        return jsonify({'code': 404, 'message': '接口不存在', 'data': None}), 404

    @app.errorhandler(500)
    def _500(e):
        return jsonify({'code': 500, 'message': '服务器内部错误', 'data': None}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

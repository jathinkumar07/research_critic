import os
from flask import Flask
from config import Config
from src.extensions import init_extensions
from src.utils.errors import register_error_handlers

def create_app(config_class=Config):
    """Flask application factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from src.routes.auth import bp as auth_bp
    from src.routes.documents import bp as documents_bp
    from src.routes.analysis import bp as analysis_bp
    from src.routes.reports import bp as reports_bp
    from src.routes.factcheck import factcheck_bp
    from src.routes.citations import citations_bp
    from src.routes.simple_analyze import simple_analyze_bp
    from src.routes.protected_analyze import protected_analyze_bp
    from src.routes.results import results_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(factcheck_bp, url_prefix='/api/factcheck')
    app.register_blueprint(citations_bp, url_prefix='/api/citations')
    app.register_blueprint(simple_analyze_bp)
    app.register_blueprint(protected_analyze_bp)
    app.register_blueprint(results_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'success',
            'message': 'AI Research Critic API is running',
            'data': {
                'service': 'ai_research_critic',
                'health': 'healthy'
            }
        }, 200
    
    # Root endpoint
    @app.route('/')
    def root():
        return {
            'status': 'success',
            'message': 'AI Research Critic API',
            'data': {
                'version': '1.0.0',
                'service': 'ai_research_critic'
            }
        }, 200

    # ✅ PRELOAD MODEL WITH APP CONTEXT
    with app.app_context():
        try:
            print("🚀 Preloading HuggingFace summarizer model...")
            from src.services.summarizer_service import _get_summarizer
            _get_summarizer()
        except Exception as e:
            print(f"⚠️ Failed to preload summarizer: {e}")

    return app


if __name__ == '__main__':
    print("running")
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

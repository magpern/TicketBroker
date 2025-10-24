from app import create_app
import os

# Create app with environment-aware configuration
app = create_app()

# Override debug mode based on environment
is_production = os.environ.get('FLASK_ENV') == 'production'
if is_production:
    app.debug = False
elif os.environ.get('FLASK_DEBUG', '0') == '1':
    app.debug = True
else:
    app.debug = False

if __name__ == '__main__':
    # Check if running in production mode
    if os.environ.get('FLASK_ENV') == 'production':
        print("⚠️  Production mode detected!")
        print("💡 Use 'python start_production.py' for production deployment")
        print("🔧 Or run: gunicorn -c gunicorn.conf.py run:app")
        exit(1)
    
    # Development mode - suppress the warning
    import warnings
    warnings.filterwarnings("ignore", message=".*development server.*")
    
    print("🔧 Starting TicketBroker in development mode...")
    print("🌐 URL: http://localhost:5001")
    print("📝 For production: python start_production.py")
    print("-" * 50)
    
    # SECURITY FIX: Use the app's debug setting (already set above)
    app.run(host='0.0.0.0', port=5001, debug=app.debug)
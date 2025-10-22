from app import create_app
import os

app = create_app()

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
    
    app.run(host='0.0.0.0', port=5001, debug=True)

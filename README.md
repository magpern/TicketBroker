# Ticket Booking Application - Klasskonsert 24C

A Flask-based ticket booking system for class concerts with admin panel, mobile-first design, and Docker deployment.

## Features

- **Public Booking Interface**: Multi-step booking process with time slot selection
- **Admin Panel**: Manage bookings, confirm payments, export data
- **Mobile-First Design**: Optimized for iPhone and Android devices
- **Email Notifications**: Automatic emails to buyers and admin
- **Payment Workflow**: Manual Swish payment confirmation system
- **Excel Export**: Download booking data as Excel files
- **Responsive Design**: Red theme with music note decorations

## Enhanced Features (Phase 2)

### Individual Ticket Tracking
- **Booking References**: Each booking gets a unique 5-character reference (e.g., "65TGR")
- **Individual Tickets**: After payment confirmation, individual tickets are generated:
  - Normal tickets: `BOOKING_REF-N01`, `BOOKING_REF-N02`, etc.
  - Student tickets: `BOOKING_REF-D01`, `BOOKING_REF-D02`, etc.
- **Ticket Management**: Admin can view, search, and delete individual tickets
- **Ticket Checking**: Admin interface for checking tickets at the venue

### Swish Payment Integration
- **Deep Link Integration**: "Betala nu" button opens Swish app directly
- **Payment Tracking**: System tracks when payment is initiated and confirmed
- **Dynamic Recipient**: Swish recipient name configurable in admin settings
- **Session Recovery**: Users can resume payment flow if they leave the page

### Audit Logging System
- **Comprehensive Logging**: All actions are logged with timestamps and details
- **Audit Trail**: Track booking creation, payment initiation, ticket generation, etc.
- **Admin Audit View**: View and filter audit logs in admin panel
- **Compliance**: Full audit trail for financial compliance

### Enhanced Admin Features
- **Ticket Management**: View all tickets with filters and search
- **Booking References**: Display booking references in admin dashboard
- **Ticket Deletion**: Delete unused tickets with audit logging
- **Read-only Fields**: Prevent editing ticket quantities after booking
- **Dynamic Contact**: Footer contact email from settings

### Database Schema
- **New Tables**: `Ticket`, `Buyer`, `AuditLog`
- **Enhanced Booking**: Added `booking_reference`, `swish_payment_initiated`, etc.
- **Settings**: Added `swish_recipient_name`, `contact_email`

### Database Migrations

This project uses **Flask-Migrate** (Alembic) for database versioning, similar to Flyway for Java applications.

#### Migration Commands

```bash
# Initialize migration repository (first time only)
python migrate.py init

# Create a new migration after model changes
python migrate.py create "Add new feature"

# Apply all pending migrations
python migrate.py upgrade

# Rollback last migration
python migrate.py downgrade

# Show current migration status
python migrate.py current

# Show migration history
python migrate.py history

# Populate database with default data
python migrate.py populate

# Reset database (WARNING: Deletes all data!)
python migrate.py reset
```

#### Manual Flask Commands

```bash
# Set Flask app
set FLASK_APP=run.py

# Create migration
flask db migrate -m "Your migration message"

# Apply migrations
flask db upgrade

# Show current version
flask db current
```

## Quick Start

### Option 1: Automated Setup (Recommended)

**For Windows:**
```bash
# Run the setup script
setup.bat

# Start development server (no warnings)
start_dev.bat

# Start production server (Gunicorn)
start_production.bat
```

**For Linux/Mac:**
```bash
# Make scripts executable
chmod +x setup.sh dev.sh

# Run the setup script
./setup.sh

# Start development server
./dev.sh

# Start production server
python start_production.py
```

### Production Deployment

**Using Gunicorn (Recommended):**
```bash
# Start production server
python start_production.py

# Or directly with Gunicorn
gunicorn -c gunicorn.conf.py run:app
```

**Configuration:**
- **Workers**: 4 processes
- **Port**: 5001
- **Logs**: `/logs/access.log`, `/logs/error.log`
- **Timeout**: 30 seconds
- **Max Requests**: 1000 per worker

### Option 2: Manual Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your settings:
   # - SECRET_KEY: Generate a secure random key
   # - MAIL_USERNAME: Your Gmail address
   # - MAIL_PASSWORD: Gmail app password
   # - ADMIN_PASSWORD: Admin login password
   ```

4. **Add class photo**:
   ```bash
   # Place your class photo as:
   app/static/images/class-photo.jpg
   ```

5. **Run the application**:
   ```bash
   python run.py
   ```

### Option 3: Docker Deployment

1. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

2. **Add class photo**:
   ```bash
   # Place your class photo as:
   app/static/images/class-photo.jpg
   ```

3. **Run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

### Access the Application

- **Public site**: http://localhost:5001
- **Admin panel**: http://localhost:5001/admin/login
- **Password**: `klasskonsert26` (or your custom password)

### VS Code Debugging

1. **Select Python interpreter**: 
   - Press `Ctrl+Shift+P` → "Python: Select Interpreter"
   - Choose `./venv_new/Scripts/python.exe` (Windows) or `./venv/bin/python` (Linux/Mac)

2. **Start debugging**:
   - Press `F5` or go to Run → Start Debugging
   - Select "Flask App Debug" configuration

## Configuration

### Email Setup (Gmail)

1. Enable 2-factor authentication on your Gmail account
2. Generate an "App Password" for this application
3. Use the app password in `MAIL_PASSWORD` environment variable

### Admin Settings

Access the admin panel to configure:
- Ticket prices (adult/student)
- Swish phone number
- Concert date and venue
- Notification email addresses
- Show times and capacities

## Usage

### For Buyers

1. Visit the homepage
2. Click "Boka biljetter" (Book tickets)
3. Select time slot (17:45-18:45 or 19:00-20:00)
4. Choose ticket quantities (max 4 total)
5. Fill in contact information
6. Complete booking
7. Pay via Swish to 070 123 45 67
8. Confirm payment on the website

### For Administrators

1. Login at `/admin/login`
2. **Dashboard**: View all bookings, confirm payments
3. **Settings**: Configure prices, contact info, show details
4. **Shows**: Manage concert times and capacities
5. **Export**: Download booking data as Excel

## File Structure

```
TicketBroker/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes/
│   │   ├── __init__.py      # Blueprint imports
│   │   ├── public.py        # Public booking routes
│   │   └── admin.py         # Admin panel routes
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── booking.html
│   │   ├── booking_success.html
│   │   └── admin/
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       ├── settings.html
│   │       ├── shows.html
│   │       └── edit_booking.html
│   ├── static/
│   │   ├── css/style.css    # Mobile-first CSS
│   │   ├── js/booking.js     # JavaScript functionality
│   │   └── images/          # Class photo and assets
│   └── utils/
│       └── email.py         # Email notification functions
├── .vscode/                 # VS Code configuration
│   ├── launch.json         # Debug configurations
│   └── settings.json       # Python interpreter settings
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── setup.sh / setup.bat    # Setup scripts
├── dev.sh / dev.bat        # Development scripts
├── env.example             # Environment variables template
└── README.md               # This file
```

## Database Schema

- **Show**: Concert time slots with capacity tracking
- **Booking**: Individual reservations with payment status
- **Settings**: Configurable application parameters

## Deployment

### Raspberry Pi Deployment

1. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker pi
   ```

2. **Deploy application**:
   ```bash
   git clone https://github.com/magpern/TicketBroker.git
   cd TicketBroker
   cp env.example .env
   # Edit .env with production settings
   docker-compose up -d
   ```

3. **Configure reverse proxy** (optional):
   ```bash
   # Install nginx
   sudo apt install nginx
   # Configure nginx to proxy to localhost:5001
   ```

### Production Considerations

- Change default admin password
- Use strong SECRET_KEY
- Set up SSL/TLS certificates
- Configure firewall rules
- Regular database backups
- Monitor application logs

## Development

### Running in Development Mode

```bash
# Activate virtual environment
venv_new\Scripts\activate  # Windows
source venv/bin/activate   # Linux/Mac

# Set development environment
set FLASK_ENV=development  # Windows
export FLASK_ENV=development  # Linux/Mac

# Run application
python run.py
```

### Database Management

The application uses SQLite with automatic table creation. Database file is stored in `/data/ticketbroker.db` in Docker or current directory in development.

### Adding New Features

1. **Models**: Add to `app/models.py`
2. **Routes**: Add to appropriate blueprint in `app/routes/`
3. **Templates**: Add HTML templates in `app/templates/`
4. **Styling**: Update `app/static/css/style.css`

## Troubleshooting

### Common Issues

1. **Email not sending**:
   - Check Gmail app password
   - Verify MAIL_USERNAME and MAIL_PASSWORD
   - Check Gmail security settings

2. **Database errors**:
   - Ensure data directory is writable
   - Check DATABASE_URL configuration

3. **Admin login issues**:
   - Verify ADMIN_PASSWORD environment variable
   - Check session configuration

4. **Mobile display issues**:
   - Clear browser cache
   - Check viewport meta tag
   - Verify CSS media queries

5. **Port conflicts**:
   - Default port is 5001 (changed from 5000)
   - Modify `run.py` to use different port if needed

### Logs

View application logs:
```bash
# Docker
docker-compose logs -f ticketbroker

# Development
# Check console output when running python run.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is created for educational purposes. Please ensure compliance with local data protection regulations (GDPR) when handling personal information.

## Support

For technical support, contact: oliver.ahlstrand@icloud.com

## Acknowledgments

- Built with Flask and SQLAlchemy
- Mobile-first design with responsive CSS
- Docker deployment ready
- Swedish language support for Klasskonsert 24C
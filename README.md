# Archive Management System

A web-based Archive Management System developed using Django to help organizations manage, organize, track, and retrieve documents efficiently.

The system provides role-based access control, document version management, advanced search, activity tracking, reports, user administration, and a complete audit trail.

## Live Demo

https://archive-management-system.onrender.com/

## Features

### Authentication & User Management

- User registration and login
- Account approval workflow
- Role-based access control
- User activation and deactivation
- Role management by the System Administrator
- Separate permissions for System Administrator, Manager, and Employee

### Document Management

- Create and manage documents
- Edit document information
- Archive and track document status
- Delete documents with restricted permissions
- Upload and download document files
- Document details and metadata
- Department and document type classification

### Advanced Search

Documents can be filtered using multiple criteria, including:

- Document number
- Title
- Description
- Department
- Document type
- Status
- Created by
- Date range

### Document Version History

- Upload multiple versions of a document
- Automatic version numbering
- Version upload notes
- Download previous versions
- Latest version identification
- Upload activity recorded automatically

### Movement History

Each document includes a complete activity history showing events such as:

- Document creation
- Document edits
- Status changes
- File/version uploads
- Document deletion

Each activity records the responsible user and timestamp.

### Reports & Statistics

Managers and System Administrators can access reports including:

- Total documents
- Active documents
- Archived documents
- File versions
- Departments
- Document types
- Active users
- Documents by department
- Documents by type
- Documents by status
- Recent activity
- Documents created per user
- Date-based report filtering

### Global Audit Log

The System Administrator has access to a centralized audit trail with:

- Action filtering
- User filtering
- Document search
- Date filtering
- Pagination
- Activity details
- User and timestamp tracking

## User Roles

### System Administrator

Has access to:

- Dashboard
- Documents
- Add Document
- Edit Documents
- Delete Documents
- Upload Document Versions
- Reports & Statistics
- User Management
- Account Approval
- Global Audit Log

### Manager

Has access to:

- Dashboard
- Documents
- Add Document
- Edit Documents
- Upload Document Versions
- Reports & Statistics

Managers cannot delete documents or manage system users.

### Employee

Has read-only access to:

- Dashboard
- Document List
- Advanced Search
- Document Details
- Version History
- File Downloads
- Movement History

## Technologies Used

- Python
- Django
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- SQLite
- Django ORM
- Git
- GitHub
- PostgreSQL (Neon)
- Cloudinary
- Render

## Project Structure

```text
Archive-Management-System/
├── accounts/
├── archive_project/
├── core/
├── dashboard/
├── documents/
├── reports/
├── templates/
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Nour-Nasan/Archive-Management-System.git
cd Archive-Management-System
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example` and configure the required environment variables.

Run database migrations:

```bash
python manage.py migrate
```

Create a System Administrator account:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

Then open the application in your browser.

## Security

Sensitive and runtime-generated files are excluded from version control, including:

- `.env`
- `db.sqlite3`
- Uploaded media
- Virtual environments
- Cache files
- Replit-specific development files

Environment variable examples are provided through `.env.example`.

No passwords, database files, or secret environment values are included in the public repository.

## Responsive Design

The interface is designed using Bootstrap 5 and supports:

- Desktop
- Tablet
- Mobile

The system uses a professional responsive dashboard layout with role-based navigation.

## Project Status

The system is complete, deployed, and available as a live demo.

Implemented modules include:

- Authentication and registration
- Account approval
- Role-based permissions
- User management
- Document management
- Advanced document search
- Document version history
- Movement history
- Reports and statistics
- Global audit logging
- Responsive user interface

## Author

**Nour Nasan**

Software Engineer | Full-Stack Developer

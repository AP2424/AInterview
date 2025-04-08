# AInterview

An AI-powered admission platform for universities to conduct and assess student interviews automatically.

## Features

- **Automated Interviews**: AI-powered system for conducting student admission interviews
- **Proctoring**: Real-time face detection to ensure interview integrity
- **Role-Based Access**: Separate interfaces for students and committee members
- **Interview Management**: Create and customize interview questions
- **Study Programs**: Manage different programs and their admission requirements
- **Automated Assessment**: AI-assisted evaluation of student responses

## Prerequisites

- Python 3.8 or higher
- Windows OS (for PowerShell setup script)
- Web camera for interview proctoring
- Modern web browser (Chrome/Firefox recommended)
- PowerShell with execution policy allowing scripts

## Quick Start

1. **Clone the Repository**
```powershell
git clone https://github.com/your-username/AInterview.git
cd AInterview
```

2. **Run Setup Script**
```powershell
.\setupscript.ps1
```

The setup script automatically:
- Creates a virtual environment
- Installs required dependencies
- Sets up the database
- Applies all migrations

3. **Access the Application**
```
http://localhost:8000
```

## Project Structure

```
AInterview/
├── main/                   # Main application
│   ├── templates/         # HTML templates
│   ├── static/           # CSS, JS, and other static files
│   ├── models.py         # Database models
│   └── views.py          # View controllers
├── media/                 # User-uploaded files
├── requirements.txt       # Project dependencies
└── setupscript.ps1       # Automated setup script
```

## Usage

### For Students
1. Login using student credentials
2. Select your study program
3. Start the interview when ready
4. Answer questions within the time limit
5. Ensure your face is visible during the interview

### For Committee Members
1. Login using committee credentials
2. Create or modify interview templates
3. Review and assess completed interviews
4. Manage study programs and questions

## Development

If you need to make changes to the database schema:
```powershell
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

1. **Setup Script Fails**
   - Ensure PowerShell execution policy is set correctly:
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```

2. **Camera Not Working**
   - Check browser permissions
   - Ensure camera is properly connected
   - Verify no other application is using the camera

3. **Authentication Issues**
   - Use the Django shell to create test users:
   ```powershell
   python manage.py shell
   ```
   ```python
   from main.models import User
   User.objects.create_user(username='test', password='test', role='applicant')
   ```

## License

This project is licensed under the MIT License.
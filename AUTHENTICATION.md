# 🔐 ENPROM Finance Portal - Authentication System

## Overview
Secure authentication system with role-based access control for the ENPROM Finance Portal. All user credentials are stored in the `secrets.toml` file, keeping them out of your codebase.

## Features
- ✅ **Secure Login**: Username/password authentication
- ✅ **Role-Based Access**: 4 permission levels (Viewer, Editor, Finance, Admin)
- ✅ **Session Management**: Stay logged in during session
- ✅ **Password Hashing**: Support for SHA-256 hashed passwords
- ✅ **User Info Display**: Shows logged-in user name and role
- ✅ **Easy Logout**: One-click logout functionality

## User Roles

### 1. **Viewer** (Read-Only)
- View all reports and analytics
- Browse documents (read-only)
- No edit or upload permissions

### 2. **Editor** 
- All Viewer permissions
- Manage documents
- Upload files
- Use document tools

### 3. **Finance**
- All Editor permissions
- Access financial comparison section
- Full financial data access
- Advanced analytics

### 4. **Admin** (Full Access)
- All Finance permissions
- Access to all settings
- Complete system control
- User management view (future)

## Setup Instructions

### 1. Configure Users

Edit `.streamlit/secrets.toml` to add/modify users:

```toml
[users.username_key]
username = "user@enprom.com"  # Login username/email
password = "password123"       # Plain text or hash
role = "admin"                 # viewer, editor, finance, or admin
name = "Display Name"          # Shown in the app
```

### 2. Generate Secure Passwords (Recommended)

For production, use hashed passwords:

```bash
# Run the password hash generator
python generate_password_hash.py

# Or use Python directly
python -c "import hashlib; print(hashlib.sha256(b'your_password').hexdigest())"
```

Example:
```toml
[users.john]
username = "john@enprom.com"
password = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # Hash of 'password'
role = "finance"
name = "John Doe"
```

### 3. Add Users to Streamlit Cloud

When deploying to Streamlit Cloud:

1. Go to your app settings
2. Click on "Secrets"
3. Copy the entire contents of `.streamlit/secrets.toml`
4. Paste and save

## Usage

### Login
1. Navigate to the app URL
2. Enter username and password
3. Click "Sign In"
4. You'll be redirected to the main app

### Logout
1. Click the "🚪 Logout" button in the sidebar
2. You'll be returned to the login page

### Default Test Accounts

⚠️ **Change these passwords before production!**

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| admin@enprom.com | admin123 | Admin | Full access |
| naseer@enprom.com | naseer123 | Admin | Full access |
| finance@enprom.com | finance123 | Finance | Financial data + editing |
| editor@enprom.com | editor123 | Editor | Document editing |
| viewer@enprom.com | viewer123 | Viewer | Read-only |

## Adding New Users

1. Open `.streamlit/secrets.toml`
2. Add a new user block:
   ```toml
   [users.newuser]
   username = "newuser@enprom.com"
   password = "secure_password_or_hash"
   role = "editor"
   name = "New User Name"
   ```
3. Save the file
4. Restart the Streamlit app (if running locally)
5. For Streamlit Cloud: Update secrets in app settings

## Removing Users

1. Open `.streamlit/secrets.toml`
2. Delete the entire `[users.username]` block
3. Save and restart

## Security Best Practices

### ✅ DO:
- Use SHA-256 hashed passwords in production
- Change all default passwords immediately
- Use strong passwords (12+ characters)
- Keep secrets.toml private (never commit to git)
- Regularly review and update user access
- Use different passwords for each user

### ❌ DON'T:
- Commit secrets.toml to version control
- Share passwords via email/chat
- Use simple passwords like "password123"
- Reuse passwords across multiple users
- Leave default test accounts active in production

## Troubleshooting

### "Invalid username or password"
- Check username spelling (case-sensitive)
- Verify password is correct
- Ensure user exists in secrets.toml
- Check for extra spaces in secrets.toml

### "Authentication error"
- Check secrets.toml syntax (valid TOML format)
- Ensure secrets.toml is in `.streamlit/` folder
- Restart Streamlit app
- Check Streamlit Cloud secrets if deployed

### Can't logout
- Clear browser cache
- Close and reopen browser
- Check browser console for errors

## File Structure

```
project-flowwer/
├── .streamlit/
│   ├── secrets.toml              # Your actual secrets (DO NOT COMMIT)
│   ├── secrets.toml.template     # Template for reference
│   └── config.toml
├── generate_password_hash.py     # Password hash generator
├── enprom_financial_app.py       # Main app with authentication
└── AUTHENTICATION.md             # This file
```

## Migration Guide

### From No Auth to Auth
1. All existing features work the same
2. Users must now log in to access
3. No data migration needed
4. Session state preserved after login

### Updating Passwords
1. Generate new hash with `generate_password_hash.py`
2. Update password in secrets.toml
3. User must use new password on next login

## Support

For issues or questions:
1. Check this README
2. Review secrets.toml.template
3. Run generate_password_hash.py for password help
4. Contact system administrator

---

**Version**: 1.0  
**Last Updated**: November 25, 2025  
**Maintainer**: Naseer Ahmed

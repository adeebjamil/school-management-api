# 🐘 PostgreSQL Setup Guide

## ✅ **Backend Now Uses PostgreSQL**

Your Django backend has been configured to use **PostgreSQL** instead of SQLite.

---

## 📋 Prerequisites

You need PostgreSQL installed on your system.

---

## 🔧 Installation

### **Windows**

1. **Download PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Download PostgreSQL 16 installer
   - Run the installer

2. **During Installation:**
   - Set a password for the `postgres` user (remember this!)
   - Port: `5432` (default)
   - Install all components

3. **Add to PATH:**
   - The installer usually does this automatically
   - Verify: Open PowerShell and type `psql --version`

### **macOS**

```bash
# Using Homebrew
brew install postgresql@16
brew services start postgresql@16
```

### **Linux (Ubuntu/Debian)**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## 🗄️ Create Database

### **Method 1: Using pgAdmin (GUI)**

1. Open **pgAdmin** (installed with PostgreSQL)
2. Connect to PostgreSQL server
3. Right-click "Databases" → Create → Database
4. Name: `school_management`
5. Click "Save"

### **Method 2: Using psql (Command Line)**

**Windows PowerShell:**
```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE school_management;

# Verify
\l

# Exit
\q
```

**macOS/Linux:**
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE school_management;

# Verify
\l

# Exit
\q
```

---

## ⚙️ Configure Django

Your `.env` file should look like this:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

# PostgreSQL Database Configuration
DB_NAME=school_management
DB_USER=postgres
DB_PASSWORD=yourpassword        # ← Change this!
DB_HOST=localhost
DB_PORT=5432

# Super Admin Credentials
SUPER_ADMIN_EMAIL=superadmin@sms.com
SUPER_ADMIN_PASSWORD=SuperAdmin@2025

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**⚠️ IMPORTANT:** Update `DB_PASSWORD` with your actual PostgreSQL password!

---

## 🚀 Run Migrations

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run migrations
python manage.py migrate

# Create Super Admin
python manage.py init_superadmin

# Start server
python manage.py runserver
```

---

## ✅ Verify Connection

If migrations run successfully, PostgreSQL is working! ✨

You should see output like:
```
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, sessions, tenants, students, teachers, parents, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

---

## 🔍 Common Issues

### **Error: "psycopg2.OperationalError: FATAL: password authentication failed"**

**Solution:** Check your `.env` file:
- Verify `DB_PASSWORD` matches your PostgreSQL password
- Check `DB_USER` (default is `postgres`)

### **Error: "psycopg2.OperationalError: could not connect to server"**

**Solution:** PostgreSQL service not running

**Windows:**
```powershell
# Check status
Get-Service -Name postgresql*

# Start service
Start-Service -Name "postgresql-x64-16"
```

**macOS:**
```bash
brew services start postgresql@16
```

**Linux:**
```bash
sudo systemctl start postgresql
```

### **Error: "database 'school_management' does not exist"**

**Solution:** Create the database using steps above

---

## 🌐 For Deployment

### **Railway**
- PostgreSQL is automatically provisioned
- Connection string provided as `DATABASE_URL`

### **Render**
- Add PostgreSQL service (free tier)
- Connection details auto-configured

### **AWS RDS**
- Create PostgreSQL instance
- Update `.env` with RDS endpoint

---

## 📊 Database Admin Tools

### **pgAdmin** (Included with PostgreSQL)
- GUI tool for managing databases
- View tables, run queries, manage users

### **DBeaver** (Alternative)
- Download: https://dbeaver.io/
- Connect using your PostgreSQL credentials

### **TablePlus** (Mac/Windows)
- Modern GUI: https://tableplus.com/

---

## 🔐 Security Notes

**For Production:**

1. **Never commit `.env` file**
   - Already in `.gitignore` ✅

2. **Use strong passwords**
   - Not `yourpassword` 😅

3. **Create separate DB user**
   ```sql
   CREATE USER school_admin WITH PASSWORD 'strong_password';
   GRANT ALL PRIVILEGES ON DATABASE school_management TO school_admin;
   ```

4. **Restrict connections**
   - Use `127.0.0.1` instead of `*`
   - Configure `pg_hba.conf`

---

## 📚 Next Steps

1. ✅ Install PostgreSQL
2. ✅ Create database `school_management`
3. ✅ Update `.env` with your password
4. ✅ Run migrations
5. ✅ Start development!

**Need help?** Check the main [README.md](../README.md) or backend [SETUP_GUIDE.md](SETUP_GUIDE.md).

# Deploy Sample Data to Production

This guide explains how to populate your production database (Render) with the same test data created locally.

## Current Status

✅ **Local Database**: Sample data created (4 users + relationships)  
❌ **Production Database**: No sample data yet

## Option 1: Run Script on Production Database (Recommended)

### Step 1: Get Production Database URL

1. Go to your Render dashboard: https://dashboard.render.com
2. Navigate to your PostgreSQL database
3. Copy the **Internal Database URL** or **External Database URL**
   - Format: `postgresql://user:password@host:port/database`

### Step 2: Set Environment Variable & Run Script

**Windows PowerShell:**
```powershell
# Set DATABASE_URL temporarily
$env:DATABASE_URL = "your-production-database-url-here"

# Run the script
python create_sample_data.py

# Verify
python manage.py shell -c "from accounts.models import User; print('Users:', User.objects.filter(tenant__school_code='DEMO2025').count())"
```

**Alternative - One Command:**
```powershell
$env:DATABASE_URL = "your-production-database-url-here"; python create_sample_data.py
```

### Step 3: Verify on Production

Visit your production frontend: https://school-management-theta-five.vercel.app

Try logging in with:
- **Email**: student@demohigh.edu
- **Password**: Student@2025
- **School Code**: DEMO2025

---

## Option 2: Use Render Shell (If Available)

Some Render services provide shell access:

1. Go to Render dashboard
2. Select your backend service
3. Click "Shell" tab
4. Upload `create_sample_data.py`
5. Run: `python create_sample_data.py`

---

## Option 3: Django Admin (Manual)

If you prefer not to run scripts on production, you can manually create users through Django Admin:

1. Visit: https://school-management-api-jrhr.onrender.com/admin
2. Login with superadmin credentials
3. Create users, profiles, and relationships manually

---

## Security Considerations

### ⚠️ Important Notes:

1. **Test Credentials Only**: These are weak passwords for testing
2. **Change in Production**: For real clients, use strong unique passwords
3. **Delete Test Data**: Remove test accounts before going live with real users
4. **Never Commit**: Don't commit production DATABASE_URL to git

### For Real Production Use:

```python
# Use strong passwords like:
import secrets
password = secrets.token_urlsafe(16)  # Generates: 'xK7mP9nQ2wR4tY6u'
```

---

## Verification Checklist

After running the script on production, verify:

- [ ] Can login with admin@demohigh.edu
- [ ] Can login with teacher@demohigh.edu
- [ ] Can login with student@demohigh.edu
- [ ] Can login with parent@demohigh.edu
- [ ] All users have school code DEMO2025
- [ ] Student is enrolled in Grade 10-A
- [ ] Parent is linked to student
- [ ] Teacher is assigned as class teacher

---

## Troubleshooting

### Error: "relation does not exist"
**Solution**: Run migrations first
```bash
python manage.py migrate
```

### Error: "connection refused"
**Solution**: Check DATABASE_URL is correct and database is accessible

### Error: "duplicate key value"
**Solution**: Data already exists. Script is idempotent, so this is OK.

### Error: SSL required
**Solution**: Add `?sslmode=require` to end of DATABASE_URL
```
postgresql://user:pass@host:port/db?sslmode=require
```

---

## Quick Command Reference

```powershell
# Check current database
python manage.py shell -c "from django.db import connection; print(connection.settings_dict['NAME'])"

# Count users in DEMO2025
python manage.py shell -c "from accounts.models import User; print(User.objects.filter(tenant__school_code='DEMO2025').count())"

# List all users
python manage.py shell -c "from accounts.models import User; [print(f'{u.email} - {u.role}') for u in User.objects.filter(tenant__school_code='DEMO2025')]"

# Delete test data (if needed)
python manage.py shell -c "from tenants.models import Tenant; Tenant.objects.filter(school_code='DEMO2025').delete()"
```

---

## Alternative: Export/Import Data

If you want to keep local and production data in sync:

### Export from Local:
```bash
python manage.py dumpdata accounts students teachers parents school_classes tenants --natural-foreign --natural-primary --indent 2 > sample_data.json
```

### Import to Production:
```bash
$env:DATABASE_URL = "your-production-url"
python manage.py loaddata sample_data.json
```

---

## Best Practice for Multiple Environments

Create separate scripts for different environments:

```python
# create_sample_data_prod.py
import os
if not os.getenv('DATABASE_URL'):
    print("❌ DATABASE_URL not set! Set production DB URL first.")
    exit(1)

# ... rest of script
```

This prevents accidentally running on wrong database.

---

## Summary

**Recommended Workflow:**

1. ✅ Develop and test locally with sample data
2. ✅ Commit `create_sample_data.py` to git
3. ✅ Set production DATABASE_URL temporarily
4. ✅ Run script to populate production
5. ✅ Test on production URL
6. ✅ Change passwords before giving to real users

**For Client Demo:**
- Use the same test credentials in both environments
- Document all credentials in TEST_CREDENTIALS.md
- Show client how to change passwords after demo

---

**Need Help?** Check the main documentation:
- [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Deployment guide
- [TEST_CREDENTIALS.md](TEST_CREDENTIALS.md) - All test credentials
- [SAMPLE_DATA_COMPLETE.md](../SAMPLE_DATA_COMPLETE.md) - What was created

**Last Updated**: January 2, 2026

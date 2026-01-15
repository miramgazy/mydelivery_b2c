# Manual Testing Guide

Follow these steps to verify the full system integration.

## 1. Prerequisites

Ensure all services are running:

```bash
# In backend directory
docker-compose up -d
docker-compose exec backend python manage.py migrate

# In frontend directory
npm run dev
```

## 2. Authentication

1. Open http://localhost:5173/login
2. Login with your admin credentials
   - If you don't have an admin user, create one via Django admin or shell:
     ```bash
     docker-compose exec backend python manage.py shell
     ```
     ```python
     from apps.users.models import User, Role
     from apps.organizations.models import Organization
     
     # Create Org
     org = Organization.objects.create(name="Test Org", org_name="Test Org")
     
     # Create Role
     role = Role.objects.get(role_name='ORG_ADMIN')
     
     # Create User
     User.objects.create_user(
         username='admin', 
         password='password', 
         role=role, 
         organization=org,
         first_name='Admin'
     )
     ```

## 3. Organization Setup

1. Navigate to **"Organization"** -> **"Settings"**
2. Enter your iiko credentials:
   - **IIKO Organization ID**: (Your GUID)
   - **API Key**: (Your API Key)
3. Fill in Phone and Address.
4. Click **"Save Settings"**.

## 4. Sync Data

1. **Terminals**:
   - Go to "Terminals"
   - Click **"Загрузить из IIKO"**
   - Verify terminals appear in the table.

2. **Payment Types**:
   - Go to "Payment Types"
   - Click **"Загрузить из IIKO"**
   - Verify payment types appear.

3. **Menu**:
   - Go to "Menu Management"
   - Click **"Выгрузить меню из IIKO"**
   - Select a menu from the dropdown
   - Click **"Загрузить выбранное меню"**
   - Wait for success message.

## 5. Verify Catalog

1. Go to **"Products"**.
   - Ensure products are listed.
   - Check if images and prices are correct.
   - Use filter buttons (Category, Availability).

2. Go to **"Modifiers"**.
   - Ensure modifiers are listed.
   - Check "Associated Product" column.

## 6. Orders Flow

1. **Create an Order** (if empty):
   - You can use Postman/cURL to create a test order via `/api/orders/`.
   - Or use the Telegram Bot if configured.

2. **Manage Orders**:
   - Go to **"Orders"**.
   - Click the **"Eye"** icon to view details.
   - Verify all fields (Client, Address, Products, Price).
   - Click **"Refresh"** icon to check status update from iiko.

## 7. Users

1. Go to **"Clients"**.
2. Verify list of users.
3. Check search functionality (search by name/phone).

---

**Troubleshooting:**
- If "Organization not found" error -> Ensure your user is linked to an organization.
- If iiko sync fails -> Check server logs (`docker-compose logs -f backend`) for detailed error messages.

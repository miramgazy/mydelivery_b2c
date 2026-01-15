# Desktop Frontend - Testing Checklist

## 🔐 Authentication & Access

- [ ] **Login Page**
  - [ ] Navigate to `/login`
  - [ ] Login with `superadmin` credentials works
  - [ ] Login with `org_admin` credentials works
  - [ ] Login with `customer` credentials redirects to `/` (not `/admin`)
  - [ ] Invalid credentials show error message
  - [ ] After successful admin login, redirects to `/admin/organization/settings`

- [ ] **Route Protection**
  - [ ] Unauthenticated users redirected to `/login`
  - [ ] Non-admin users cannot access `/admin/*` routes
  - [ ] Admin users can access all `/admin/*` routes
  - [ ] Logout button works and redirects to `/login`

## 🎨 Layout & UI

- [ ] **Desktop Layout**
  - [ ] Sidebar displays correctly
  - [ ] Sidebar toggle button works
  - [ ] Sidebar collapse animation is smooth (300ms transition)
  - [ ] Sidebar shows all 4 sections: Organization, Orders, Clients, Products
  - [ ] Active route highlighted in sidebar
  - [ ] Header shows correct page title
  - [ ] Header shows user name/username
  - [ ] Dark mode works throughout the interface

- [ ] **Responsive Design**
  - [ ] Desktop layout displays on screens ≥ 1024px
  - [ ] Mobile TMA routes still work on small screens
  - [ ] No layout breaks on different screen sizes

## 📋 Organization Section

### Settings Page (`/admin/organization/settings`)
- [ ] **Page Load**
  - [ ] Page loads without errors
  - [ ] Existing organization data loads and displays
  - [ ] Loading spinner shows during fetch
  - [ ] Error message displays if load fails

- [ ] **Form**
  - [ ] All fields display: iiko_organization_id, api_key, name, phone, address
  - [ ] API key field is masked (password type)
  - [ ] Eye icon toggles API key visibility
  - [ ] Form validation works (required fields)
  - [ ] Save button shows loading state
  - [ ] Success message displays after save
  - [ ] Error message displays if save fails
  - [ ] Data persists after page reload

### Terminals Page (`/admin/organization/terminals`)
- [ ] **Page Load**
  - [ ] Page loads without errors
  - [ ] Existing terminals display in table
  - [ ] Empty state shows if no terminals

- [ ] **Load from iiko**
  - [ ] "Загрузить из IIKO" button visible
  - [ ] Button disabled during loading
  - [ ] Loading spinner shows during sync
  - [ ] Success message after sync
  - [ ] Table updates with new terminals
  - [ ] Error message if sync fails

- [ ] **Table Display**
  - [ ] Terminal name shows correctly
  - [ ] Terminal iiko_terminal_id displays
  - [ ] Active/Inactive status badge shows
  - [ ] Table formatting is correct

### Payment Types Page (`/admin/organization/payment-types`)
- [ ] **Page Load**
  - [ ] Page loads without errors
  - [ ] Existing payment types display in table
  - [ ] Empty state shows if no payment types

- [ ] **Load from iiko**
  - [ ] "Загрузить из IIKO" button visible
  - [ ] Button disabled during loading
  - [ ] Loading spinner shows during sync
  - [ ] Success message after sync
  - [ ] Table updates with new payment types
  - [ ] Error message if sync fails

- [ ] **Table Display**
  - [ ] Payment type name shows correctly
  - [ ] Payment type iiko_payment_id displays
  - [ ] Payment type (CASH, CARD, etc.) displays
  - [ ] Active/Inactive status badge shows
  - [ ] Table formatting is correct

### Menu Page (`/admin/organization/menu`)
- [ ] **Step 1: Fetch Menus**
  - [ ] "Выгрузить меню из IIKO" button visible
  - [ ] Button disabled during loading
  - [ ] Loading spinner shows during fetch
  - [ ] Menu list displays after fetch
  - [ ] Success message displays
  - [ ] Error message if fetch fails

- [ ] **Step 2: Select and Load**
  - [ ] Menu items display with radio buttons
  - [ ] Radio button selection works
  - [ ] Only one menu can be selected at a time
  - [ ] "Загрузить выбранное меню" button visible
  - [ ] Button disabled if no menu selected
  - [ ] Loading spinner shows during load
  - [ ] Success message after load
  - [ ] Error message if load fails
  - [ ] Selection clears after successful load

## 📦 Orders Section

### Orders Page (`/admin/orders`)
- [ ] **Page Load**
  - [ ] Page loads without errors
  - [ ] Orders display in table
  - [ ] Empty state shows if no orders
  - [ ] Loading spinner during fetch

- [ ] **Table Display**
  - [ ] Order ID (number) displays
  - [ ] Client name/username displays
  - [ ] Client phone displays
  - [ ] Date formatted correctly (dd.MM.yyyy)
  - [ ] Time formatted correctly (HH:mm)
  - [ ] Total price formatted with thousands separator
  - [ ] Status badge displays with correct color
  - [ ] Status labels in Russian

- [ ] **View Order Action (Eye Icon)**
  - [ ] Eye icon visible in Actions column
  - [ ] Icon has correct color (blue)
  - [ ] Hover effect works
  - [ ] Click opens modal
  - [ ] Modal displays correct order data
  - [ ] Modal backdrop darkens screen
  - [ ] Modal can be closed by clicking backdrop
  - [ ] Modal can be closed by X button

- [ ] **Order Detail Modal**
  - [ ] Client info displays correctly
  - [ ] Phone number displays
  - [ ] Order date and time display
  - [ ] Status badge displays
  - [ ] Delivery address formatted correctly
  - [ ] Order items table displays
  - [ ] Product names show
  - [ ] Quantities show
  - [ ] Individual prices show
  - [ ] Line totals calculated correctly
  - [ ] Grand total matches order total
  - [ ] Table formatting is correct

- [ ] **Refresh Status Action (Refresh Icon)**
  - [ ] Refresh icon visible in Actions column
  - [ ] Icon has correct color (green)
  - [ ] Hover effect works
  - [ ] Click triggers refresh
  - [ ] Icon spins during refresh
  - [ ] Button disabled during refresh
  - [ ] Status updates after refresh
  - [ ] Error message if refresh fails

## 👥 Clients Section

### Users Page (`/admin/users`)
- [ ] **Page Load**
  - [ ] Page loads without errors
  - [ ] Users display correctly
  - [ ] Addresses displayed for each user
  - [ ] Modal editing works (existing functionality)

## 📦 Products Section

### Products Page (`/admin/products`)
- [ ] **Page Load**
  - [ ] Page loads without errors
  - [ ] Products display in table
  - [ ] Empty state shows if no products
  - [ ] Loading spinner during fetch

- [ ] **Filters**
  - [ ] Search input works
  - [ ] Search filters by name
  - [ ] Search filters by description
  - [ ] Category dropdown populated
  - [ ] Category filter works
  - [ ] Availability filter works
  - [ ] Multiple filters work together
  - [ ] Empty results message shows if no matches

- [ ] **Table Display**
  - [ ] Product image displays (or placeholder icon)
  - [ ] Product name displays
  - [ ] Product description displays (truncated)
  - [ ] Category name displays
  - [ ] Price formatted correctly
  - [ ] Modifiers indicator shows if has_modifiers=true
  - [ ] Availability badge displays
  - [ ] Table formatting is correct

### Modifiers Page (`/admin/modifiers`)
- [ ] **Page Load**
  - [ ] Page loads without errors
  - [ ] Modifiers display in table
  - [ ] Empty state shows if no modifiers
  - [ ] Loading spinner during fetch

- [ ] **Search**
  - [ ] Search input works
  - [ ] Search filters by modifier name
  - [ ] Search filters by description
  - [ ] Search filters by product name
  - [ ] Empty results message shows if no matches

- [ ] **Table Display**
  - [ ] Modifier name displays
  - [ ] Modifier description displays (if exists)
  - [ ] Associated product name displays
  - [ ] Price displays (or "Бесплатно" if 0)
  - [ ] Price formatted with + sign if > 0
  - [ ] Availability badge displays
  - [ ] Table formatting is correct

## 🎨 Visual & UX Checks

- [ ] **Icons**
  - [ ] All Iconify icons load correctly
  - [ ] Icons have appropriate sizes (w-5 h-5 for most)
  - [ ] Icons have appropriate colors
  - [ ] Loading spinner icon animates
  - [ ] Icon hover states work

- [ ] **Buttons**
  - [ ] Primary buttons (blue) have correct styling
  - [ ] Success buttons (green) have correct styling
  - [ ] Disabled state shows correctly
  - [ ] Hover effects work
  - [ ] Loading states show spinner

- [ ] **Forms**
  - [ ] Input fields styled correctly
  - [ ] Focus states work (blue ring)
  - [ ] Placeholder text visible
  - [ ] Required field validation works
  - [ ] Error messages display

- [ ] **Tables**
  - [ ] Row hover effects work
  - [ ] Text alignment correct (left for text, right for numbers)
  - [ ] Column widths appropriate
  - [ ] Responsive scrolling works

- [ ] **Messages**
  - [ ] Success messages (green background)
  - [ ] Error messages (red background)
  - [ ] Info messages display correctly
  - [ ] Auto-dismiss after 3 seconds (where applicable)

- [ ] **Dark Mode**
  - [ ] All backgrounds adapt to dark mode
  - [ ] All text readable in dark mode
  - [ ] All borders visible in dark mode
  - [ ] Icons visible in dark mode
  - [ ] Status badges work in dark mode

## 🔧 Technical Checks

- [ ] **Console**
  - [ ] No JavaScript errors in console
  - [ ] No broken image warnings
  - [ ] No 404s for routes
  - [ ] API calls log correctly

- [ ] **Network**
  - [ ] API endpoints called correctly
  - [ ] Bearer token sent in headers
  - [ ] CORS working
  - [ ] Response data format correct

- [ ] **State Management**
  - [ ] Pinia stores update correctly
  - [ ] Store data persists across route changes
  - [ ] Loading states synchronized
  - [ ] Error states handled

- [ ] **Browser Compatibility**
  - [ ] Works in Chrome
  - [ ] Works in Firefox
  - [ ] Works in Safari
  - [ ] Works in Edge

## 📱 Mobile TMA Verification

- [ ] **TMA Routes Still Work**
  - [ ] `/` (HomeView) loads for mobile users
  - [ ] `/menu` (MenuView) works
  - [ ] `/orders` (OrdersView) works
  - [ ] `/profile` (ProfileView) works
  - [ ] `/checkout` (CheckoutView) works
  - [ ] Telegram authentication still works
  - [ ] Cart functionality works
  - [ ] No visual regressions

## ⚡ Performance

- [ ] **Load Times**
  - [ ] Initial page load < 2 seconds
  - [ ] Route navigation instant
  - [ ] API responses reasonable
  - [ ] Images load progressively

- [ ] **Animations**
  - [ ] Sidebar collapse smooth (300ms)
  - [ ] Modal transitions smooth
  - [ ] Loading spinners smooth
  - [ ] No jank or stuttering

## 🐛 Error Handling

- [ ] **Network Errors**
  - [ ] Offline state handled gracefully
  - [ ] Timeout errors show message
  - [ ] 500 errors show message
  - [ ] 401 errors trigger re-login

- [ ] **Validation Errors**
  - [ ] Form validation errors display
  - [ ] API validation errors display
  - [ ] User-friendly error messages

## 📝 Notes

**Tested by:** _________________

**Date:** _________________

**Browser:** _________________

**Screen Size:** _________________

**Additional Notes:**
________________________________
________________________________
________________________________

---

## Critical Issues Found

| Issue # | Component | Description | Priority | Status |
|---------|-----------|-------------|----------|--------|
| 1 | | | ⚠️ High / 🔸 Med / 🔹 Low | ❌ / ⏳ / ✅ |
| 2 | | | | |
| 3 | | | | |

---

**Testing Status:**
- [ ] ✅ All Critical Features Working
- [ ] ✅ All UI Elements Displaying Correctly
- [ ] ✅ No Console Errors
- [ ] ✅ Mobile TMA Unaffected
- [ ] ✅ Ready for Production

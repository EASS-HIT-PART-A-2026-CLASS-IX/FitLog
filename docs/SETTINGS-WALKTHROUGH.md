# settings-tab-walkthrough.md

# 🎨 Settings Tab - Visual Walkthrough

## Tab Overview

When you click the "⚙️ **Settings**" tab (8th tab), you'll see:

```
┌─────────────────────────────────────────────────────────────────┐
│  FitLog - Fitness Tracker                            ⚙️ Settings │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ⚙️ Account Settings                                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  👤 Account Information                                    │ │
│  │                                                             │ │
│  │  [User ID: 9b4b476...]  [Email: ...user@example.com]      │ │
│  │  [Name: Test User]       [Account Status: Active ✅]       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ──────────────────────────────────────────────────────────      │
│                                                                   │
│  📋 Your Fitness Profiles                   🔄 Refresh           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  🟢 User 1 Training                                         │ │
│  │  ⚖️ 80kg • 📏 175cm • 🎂 28y • 🎯 MUSCLE                  │ │
│  │  ⚙️ male     [👁️ Select] [✏️ Edit] [🗑️ Delete]            │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  ⚪ User 1 Cutting Phase                                    │ │
│  │  ⚖️ 78kg • 📏 175cm • 🎂 28y • 🎯 FIT                     │ │
│  │  ⚙️ male     [👁️ Select] [✏️ Edit] [🗑️ Delete]            │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ──────────────────────────────────────────────────────────      │
│                                                                   │
│  📊 Account Statistics                                           │
│                                                                   │
│  [Total Exercises: 15]  [Total Workouts: 42]  [Tracked Days: 30] │
│                                                                   │
│  Profile Stats                                                   │
│  [Workouts (Current): 18]  [Total Volume (kg): 2,840]           │
│                                                                   │
│  ──────────────────────────────────────────────────────────      │
│                                                                   │
│  🔒 Security & Privacy                                           │
│                                                                   │
│  ✅ Passwords hashed with PBKDF2         [🔑 Change Password]    │
│  ✅ JWT tokens expire in 24 hours        [📥 Export My Data]    │
│  ✅ HTTPS recommended for production                             │
│  ✅ User data isolated by account                                │
│                                                                   │
│  ──────────────────────────────────────────────────────────      │
│                                                                   │
│  ⚠️ Danger Zone                                                  │
│                                                                   │
│  [🚪 Logout]              [🗑️ Delete Account]                   │
│                                                                   │
│  ──────────────────────────────────────────────────────────      │
│                                                                   │
│  🏋️ FitLog v2.0 | Powered by FastAPI + Streamlit + Gemini AI   │
│  [API Docs] • [GitHub] • [Contact]                              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Section Descriptions

### 1️⃣ Account Information
Shows your unique account details in a quick overview:
- **User ID** - Your unique identifier (first 8 chars shown for privacy)
- **Email** - Your login email address
- **Name** - Your display name
- **Account Status** - Currently Active ✅

### 2️⃣ Fitness Profiles Management

**List all your training profiles with:**

**Visual Indicators:**
- 🟢 Green circle = Currently selected profile
- ⚪ White circle = Inactive profile

**Per-Profile Information:**
- Profile name
- Weight (kg), Height (cm)
- Age and Gender
- Training goal (MUSCLE / FIT)

**Quick Action Buttons:**

| Button | Action | Result |
|--------|--------|--------|
| 👁️ Select | Choose as active | Updates dashboard, filters data |
| ✏️ Edit | Modify profile | Opens inline form, saves on submit |
| 🗑️ Delete | Remove profile | Asks confirmation, deletes permanently |

**Edit Mode** (when you click ✏️):
```
Profile Name: [User 1 Training        ]
Weight (kg):  [80.0                   ]
Height (cm):  [175                    ]
Age:          [28                     ]
Goal:         [Muscle ▼]

[💾 Save Changes]
```

### 3️⃣ Account Statistics

**Three Quick Stats:**
```
┌──────────────────┬──────────────────┬──────────────────┐
│ 💪 Total         │ 📝 Total Workouts│ 📊 Nutrition     │
│    Exercises     │    Logged        │    Days Tracked  │
│                  │                  │                  │
│    15            │    42            │    30            │
└──────────────────┴──────────────────┴──────────────────┘
```

**Profile-Specific Stats** (if profile selected):
```
Workouts (Current Profile): 18
Total Volume (kg):          2,840
```

### 4️⃣ Security & Privacy

**What's Protected:**
- ✅ **Passwords**: Hashed with PBKDF2 (FIPS 140-2 standard)
- ✅ **Tokens**: JWT expires in 24 hours
- ✅ **Encryption**: HTTPS recommended for production
- ✅ **Isolation**: Data separated per user account

**Account Actions:**
- **🔑 Change Password** - [Coming soon - disabled button]
- **📥 Export My Data** - Download account data as JSON

**What Gets Exported:**
```json
{
  "user_id": "9b4b4764-b10f-4411-8e10-1d154c771491",
  "name": "Test User",
  "profiles": [
    {"id": "...", "name": "User 1 Training", ...}
  ],
  "exercises": [...],
  "workout_logs": [...],
  "macro_entries": [...]
}
```

### 5️⃣ Danger Zone ⚠️

**Two critical actions:**

**🚪 Logout Button**
- Clears your session
- Removes authentication token
- Returns to login page
- You can re-login anytime

**🗑️ Delete Account Button**
- **⚠️ PERMANENT** - Cannot be undone
- Deletes ALL account data:
  - All profiles
  - All exercises
  - All workouts
  - All nutrition entries
- Requires email confirmation to prevent accidents

Confirmation flow:
```
⚠️ This will permanently delete your account and all data.

Type your email to confirm:  [user@example.com         ]

[🔴 PERMANENTLY DELETE ACCOUNT]
```

---

## 🔄 Workflow Examples

### Example 1: Edit Your Current Profile

1. Go to **Settings** tab
2. Find your profile (🟢 green = selected)
3. Click **✏️ Edit**
4. Update weight from 80kg → 75kg
5. Click **💾 Save Changes**
6. ✅ Profile updated - dashboard refreshes with new data

### Example 2: Switch Between Profiles

1. You have "Bulk Phase" (80kg) and "Cut Phase" (75kg) profiles
2. Click **👁️ Select** on "Cut Phase"
3. ✅ Dashboard now shows data for "Cut Phase"
4. All tabs filter to show only "Cut Phase" workouts/macros

### Example 3: Export Your Data

1. Go to **Settings** tab
2. Click **📥 Export My Data**
3. Complete account data appears as JSON
4. ✅ Copy and save locally for backup/analysis

### Example 4: Delete a Profile

1. Find profile to delete
2. Click **🗑️ Delete**
3. Confirm deletion
4. ✅ Profile and associated data removed
5. Remaining profiles still visible

---

## 🎯 Key Features at a Glance

| Feature | Description | Impact |
|---------|-------------|--------|
| **Account Display** | See your ID, email, name | Know your account details |
| **Profile Management** | Edit/delete/select profiles | Manage training phases |
| **Statistics** | View workout/exercise totals | Track usage patterns |
| **Data Export** | Download account as JSON | Data portability & backup |
| **Security Info** | See what's protecting you | Trust & transparency |
| **Logout** | Clear session safely | Account security |
| **Account Deletion** | Remove all data permanently | Complete account removal |

---

## 💡 Pro Tips

1. **Multiple Profiles** - Create different profiles for different training phases (bulk/cut/maintenance)
2. **Export Regularly** - Backup your data periodically
3. **Profile Names** - Use clear names like "Summer Cut 2026" or "Winter Bulk"
4. **Check Stats** - Review your "Total Workouts" and "Total Volume" to see your progress

---

## ❓ FAQ

**Q: Can I recover a deleted profile?**  
A: No - deletion is permanent. Make sure you're certain before deleting.

**Q: What if I forget my password?**  
A: Password recovery is coming soon. For now, create a new account.

**Q: Can I change my email?**  
A: Not yet - feature coming soon.

**Q: Is my data actually deleted when I delete the account?**  
A: Yes - all profiles, workouts, exercises, and nutrition data are deleted from the database.

**Q: Can I export my data?**  
A: Yes! Click "Export My Data" in the Security section to download as JSON.

---

**Next Steps:** 
- Try the Settings tab by logging into http://localhost:8502
- Create multiple profiles for different training phases
- Export your data as a backup

**Version:** v2.0  
**Last Updated:** March 25, 2026

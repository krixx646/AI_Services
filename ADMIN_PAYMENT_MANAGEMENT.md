# Admin Payment Management System

## Overview
Comprehensive payment and agent management interface for administrators to:
- View all user payments
- Confirm/update payment status
- Create and manage AI agents for users
- Upload agent links when processing is complete

## Access Points

### For Admin Users (Staff Only):

1. **Main Navigation Dropdown**
   - Click profile avatar → "Payment Management"
   - Click profile avatar → "Agent Management"

2. **Blog Page**
   - Scroll to bottom
   - Two cards: "Payment Management" and "Agent Management"

3. **Direct URLs**
   - `/cms/payments/` - Payment Management Dashboard
   - `/cms/bots/` - Agent Management Dashboard

## Features

### Payment Management (`/cms/payments/`)

#### Dashboard Stats (Top Cards)
- **Total Success**: Count and sum of successful payments
- **Pending**: Count and sum of pending payments
- **Agents Ready**: Number of agents with "ready" status
- **Needs Processing**: Successful payments without assigned agents

#### Search & Filters
- **Search**: By email, username, or payment reference
- **Payment Status Filter**: All, Pending, Success, Failed
- **Agent Status Filter**: All, Agent Pending, Processing, Ready, Failed, No Agent Yet

#### Payment Table Columns
1. **Student Info**: Avatar, username, email
2. **Reference**: Payment reference code
3. **Amount**: Payment amount and currency
4. **Payment Status**: Dropdown to update (Pending/Success/Failed)
   - Auto-saves on change
   - Auto-creates agent when changed to "Success"
5. **Agent Status**: Badge showing current agent status
6. **Agent Link**: 
   - Input field to enter/update agent URL
   - Check button to save
   - "Create Agent" button if no agent exists
7. **Date**: Payment creation timestamp
8. **Actions**:
   - Receipt icon: View payment receipt
   - WhatsApp icon: Direct message to user's WhatsApp

#### Workflow

**When a user pays:**
1. Payment appears in the table with status "Pending" or "Success"
2. No agent exists initially (shows "No Agent" badge)

**Admin confirms payment:**
1. Change payment status dropdown to "Success"
2. System automatically creates a new agent with status "Pending"

**Admin processes notes and creates agent:**
1. Build the AI agent externally
2. Return to Payment Management page
3. Find the user's payment row
4. Paste the agent URL in the "Agent Link" field
5. Click the check button (✓)
6. System automatically updates agent status to "Ready"

**User sees the agent:**
- Agent appears on their dashboard
- User receives notification (if email system is configured)

### Agent Management (`/cms/bots/`)

Similar interface focused solely on agents:
- Search by email or username
- Update agent status and URL
- Direct agent-focused management

## Auto-Created Agents

When a payment status is changed to "Success" (or webhook confirms success):
- System automatically creates a `BotInstance` with status "Pending"
- Links the agent to the payment in `raw_payload.bot_reference`
- Agent appears in both Payment Management and Agent Management

## Quick Actions

### Confirm Payment & Upload Agent (Common Flow)
1. Go to `/cms/payments/`
2. Find the user's payment
3. If status is "Pending", change to "Success" (auto-creates agent)
4. Process user's notes externally
5. Paste agent URL in the "Agent Link" field
6. Click check button
7. Done! User can now access their agent

### Contact User via WhatsApp
- Click WhatsApp icon in payment row
- Opens WhatsApp chat with pre-filled message including payment reference

### View Payment Receipt
- Click receipt icon to open detailed payment receipt in new tab

## Technical Details

### Files Created/Modified
- `templates/cms/payments.html` - Payment management UI
- `blog/views.py` - Added 4 new views:
  - `CmsPaymentListView` - Main dashboard
  - `CmsPaymentUpdateStatusView` - Update payment status
  - `CmsPaymentUpdateBotView` - Update agent URL
  - `CmsPaymentCreateBotView` - Manually create agent
- `core/urls.py` - Added 4 new routes
- `templates/base.html` - Added "Payment Management" to navbar
- `templates/cms/bots.html` - Added link to Payment Management
- `templates/blog/list.html` - Added admin cards with links
- `static/css/theme.css` - Styled tables for brown background

### URL Routes
- `/cms/payments/` - Main dashboard (GET)
- `/cms/payments/update-status/` - Update payment status (POST)
- `/cms/payments/update-bot/` - Update agent URL (POST)
- `/cms/payments/create-bot/` - Create agent for payment (POST)

### Permissions
All routes are protected:
- `@login_required` decorator
- Staff-only check: `if not request.user.is_staff`
- Redirects non-staff to blog list page

## Notes

- First 50 payments shown (use filters to narrow down)
- All actions auto-redirect back to payment dashboard
- Payment-agent linking uses `raw_payload.bot_reference` field
- Agent status auto-updates to "Ready" when URL is saved
- Supports pagination-ready (limit currently 50)

## Future Enhancements
- Email notifications when agent is ready
- Bulk actions (select multiple payments)
- Export to CSV
- Advanced date range filters
- Agent performance metrics


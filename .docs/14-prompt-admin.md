# Admin Panel Features - RAG Agent Platform

> **Last Updated:** December 2024
> **Status:** Planning
> **Related:** Phase 7 in todos.md, LiteLLM Features (15-note-feature-litellm.md)

---

## Overview

Admin Panel for managing RAG Agent Platform using LiteLLM capabilities.

---

## 1. Dashboard

### 1.1 System Overview

| Widget | Data | Source |
|--------|------|--------|
| **Total Users** | Total users, active today | PostgreSQL |
| **Total Requests** | Requests today/month | LiteLLM `/spend/logs` |
| **Total Cost** | Cost today/month (USD) | LiteLLM `/spend/logs` |
| **Revenue** | Subscription revenue | Stripe/Payment DB |
| **Active Conversations** | Active conversations count | PostgreSQL |
| **Documents Indexed** | Documents, chunks total | PostgreSQL |
| **System Health** | LiteLLM, DB, Redis status | Health checks |

### 1.2 Quick Charts

| Chart | Description |
|-------|-------------|
| **Usage Over Time** | Line chart: requests/day (7 days) |
| **Cost Over Time** | Line chart: cost/day (7 days) |
| **Revenue Over Time** | Line chart: revenue/day (30 days) |
| **Top Models** | Pie chart: usage by model |
| **Top Users** | Bar chart: top 10 users by usage |
| **Subscribers by Plan** | Pie chart: Free vs Pro vs Premium |

---

## 2. Pricing & Subscription Management

### 2.1 Pricing Plans

| Plan | Monthly Price | Annual Price | Target Users |
|------|---------------|--------------|--------------|
| **Free** | $0 | $0 | Trial users, hobbyists |
| **Pro** | $19/mo | $190/yr (save 17%) | Individual professionals |
| **Premium** | $49/mo | $490/yr (save 17%) | Power users, small teams |
| **Enterprise** | Custom | Custom | Large organizations |

### 2.2 Plan Features Matrix

| Feature | Free | Pro | Premium | Enterprise |
|---------|------|-----|---------|------------|
| **Monthly Tokens** | 50,000 | 500,000 | 2,000,000 | Unlimited |
| **Daily Requests** | 20 | 200 | 1,000 | Unlimited |
| **Documents** | 5 | 50 | 200 | Unlimited |
| **Projects** | 1 | 5 | 20 | Unlimited |
| **Custom Agents** | 1 | 5 | 20 | Unlimited |
| **File Size Limit** | 5MB | 25MB | 100MB | 500MB |
| **Rate Limit** | 5 req/min | 30 req/min | 100 req/min | 500 req/min |
| **Models Access** | Basic only | All standard | All + priority | All + custom |
| **Support** | Community | Email | Priority email | Dedicated |
| **API Access** | No | Yes | Yes | Yes |
| **Team Members** | - | - | 5 | Unlimited |
| **SSO/SAML** | No | No | No | Yes |
| **Custom Branding** | No | No | No | Yes |
| **SLA** | No | No | 99.5% | 99.9% |

### 2.3 Model Access by Plan

| Model | Free | Pro | Premium | Enterprise |
|-------|------|-----|---------|------------|
| gemini-2.0-flash | Yes | Yes | Yes | Yes |
| llama-3.3-70b (Groq) | Yes | Yes | Yes | Yes |
| gemini-2.0-pro | No | Yes | Yes | Yes |
| claude-3.5-sonnet | No | No | Yes | Yes |
| gpt-4-turbo | No | No | Yes | Yes |
| claude-3-opus | No | No | No | Yes |
| gpt-4o | No | No | No | Yes |

### 2.4 Plan Management (Admin UI)

**Features:**
- [ ] View all plans with features
- [ ] Edit plan limits (tokens, requests, etc.)
- [ ] Edit plan pricing
- [ ] Create custom plans
- [ ] Set trial period (default: 14 days Pro trial)
- [ ] Configure model access per plan
- [ ] Set rate limits per plan

### 2.5 Subscription Management

| Column | Description |
|--------|-------------|
| **User** | User email + name |
| **Plan** | Current plan (badge) |
| **Status** | Active, Trial, Cancelled, Past Due |
| **Started** | Subscription start date |
| **Renews/Expires** | Next billing or expiry date |
| **Billing Cycle** | Monthly / Annual |
| **Revenue** | Total revenue from user |
| **Actions** | Upgrade, Downgrade, Cancel, Extend |

**Admin Actions:**
- [ ] Manually upgrade/downgrade user
- [ ] Extend trial period
- [ ] Apply discount/coupon
- [ ] Cancel subscription
- [ ] Refund (partial/full)
- [ ] Gift premium access

### 2.6 Revenue Analytics

| Metric | Description |
|--------|-------------|
| **MRR** | Monthly Recurring Revenue |
| **ARR** | Annual Recurring Revenue |
| **Churn Rate** | Cancellation rate (monthly) |
| **ARPU** | Average Revenue Per User |
| **LTV** | Lifetime Value |
| **Conversion Rate** | Free -> Paid conversion |
| **Trial Conversion** | Trial -> Paid conversion |

**Charts:**
- Revenue over time (MRR trend)
- Subscribers by plan (pie chart)
- New vs churned subscribers
- Revenue by plan breakdown
- Cohort retention analysis

### 2.7 Billing Integration

**Payment Providers:**
| Provider | Features |
|----------|----------|
| **Stripe** | Cards, subscriptions, invoices |
| **Paddle** | Tax handling, global payments |
| **LemonSqueezy** | Simple setup, tax compliant |

**Billing Features:**
- [ ] Automatic recurring billing
- [ ] Invoice generation
- [ ] Failed payment handling
- [ ] Dunning emails (payment retry)
- [ ] Usage-based billing (overage)
- [ ] Proration on plan changes
- [ ] Tax calculation (VAT, etc.)

---

## 3. User Management

### 3.1 User List

| Column | Description |
|--------|-------------|
| **Email** | Email + avatar |
| **Name** | First + Last name |
| **Plan** | Free / Pro / Premium / Enterprise (badge) |
| **Status** | Active / Trial / Suspended / Banned |
| **Usage** | Tokens used / Quota (progress bar) |
| **Revenue** | Total paid (USD) |
| **Created** | Registration date |
| **Last Active** | Last activity timestamp |
| **Actions** | Edit, Upgrade, Suspend, Ban |

**Features:**
- [ ] Search by email/name
- [ ] Filter by plan, status
- [ ] Sort by any column
- [ ] Bulk actions (change plan, suspend)
- [ ] Export to CSV

### 3.2 User Detail Page

| Section | Content |
|---------|---------|
| **Profile** | Email, name, avatar, created date |
| **Subscription** | Current plan, billing info, payment history |
| **Usage Stats** | Tokens, requests, cost (daily/monthly) |
| **Usage Chart** | Line chart: usage over time |
| **Conversations** | List of recent conversations |
| **Documents** | List of uploaded documents |
| **Projects** | List of projects owned |
| **Agents** | List of custom agents created |
| **Activity Log** | Recent actions (login, chat, upload) |
| **Billing History** | Invoices, payments, refunds |

### 3.3 User Actions

| Action | Description | Confirmation |
|--------|-------------|--------------|
| **Change Plan** | Upgrade/downgrade subscription | Yes |
| **Edit Limits** | Override plan limits for user | Yes |
| **Extend Trial** | Add days to trial period | Yes |
| **Gift Premium** | Give free premium access | Yes + duration |
| **Suspend** | Temporarily disable account | Yes |
| **Ban** | Permanently ban user | Yes + reason |
| **Delete** | Delete user and all data | Yes + type email |
| **Reset Password** | Send reset password email | Yes |
| **Impersonate** | Login as user (debug) | Yes |

---

## 4. Usage & Cost Analytics

### 4.1 Usage Dashboard

| Metric | Description | API Source |
|--------|-------------|------------|
| **Total Tokens** | Input + Output tokens | LiteLLM `/spend/logs` |
| **Total Requests** | API calls count | LiteLLM `/spend/logs` |
| **Total Cost** | LLM cost (USD) | LiteLLM `/spend/logs` |
| **Gross Margin** | Revenue - Cost | Calculated |
| **Avg Cost/User** | Average cost per user | Calculated |

### 4.2 Usage Breakdown

| View | Description |
|------|-------------|
| **By User** | Table: user, tokens, requests, cost, plan |
| **By Plan** | Table: plan, users, tokens, cost, revenue |
| **By Model** | Table: model, tokens, requests, cost |
| **By Date** | Table: date, tokens, requests, cost |
| **By Project** | Table: project, tokens, requests, cost |

### 4.3 Cost vs Revenue Analysis

| Metric | Description |
|--------|-------------|
| **LLM Cost** | Cost of API calls to LLM providers |
| **Revenue** | Subscription revenue |
| **Gross Profit** | Revenue - LLM Cost |
| **Margin %** | (Profit / Revenue) * 100 |
| **Cost per Plan** | Avg LLM cost per plan tier |

**Profitability Chart:**
- Revenue vs Cost over time
- Profit margin trend
- Cost breakdown by model
- Revenue breakdown by plan

---

## 5. Quota & Rate Limit Management

### 5.1 Plan Limits (via LiteLLM Virtual Keys)

Each user gets a LiteLLM Virtual Key with limits based on their plan:

```yaml
# Example: Pro user key generation
POST /key/generate
{
  "user_id": "user_123",
  "max_budget": 10,           # $10/month budget
  "budget_duration": "monthly",
  "tpm_limit": 100000,        # 100K tokens/min
  "rpm_limit": 30,            # 30 requests/min
  "models": ["gemini-2.0-flash", "gemini-2.0-pro", "llama-3.3-70b"]
}
```

### 5.2 Quota Monitoring

| Alert | Condition | Action |
|-------|-----------|--------|
| **Warning** | Usage >= 80% | Email + in-app notification |
| **Critical** | Usage >= 95% | Email + upgrade prompt |
| **Blocked** | Usage >= 100% | Block requests + upgrade modal |

### 5.3 Overage Handling

| Strategy | Description |
|----------|-------------|
| **Hard Block** | Block when limit reached |
| **Soft Block** | Allow overage, charge extra |
| **Upgrade Prompt** | Suggest plan upgrade |
| **Grace Period** | Allow 10% overage free |

---

## 6. Model Management

### 6.1 Available Models

| Model | Provider | Cost/1K tokens | Available Plans |
|-------|----------|----------------|-----------------|
| gemini-2.0-flash | Google | $0.0001 | All |
| llama-3.3-70b | Groq | $0.0001 | All |
| gemini-2.0-pro | Google | $0.001 | Pro+ |
| claude-3.5-sonnet | Anthropic | $0.003 | Premium+ |
| gpt-4-turbo | OpenAI | $0.01 | Premium+ |
| claude-3-opus | Anthropic | $0.015 | Enterprise |

### 6.2 Model Configuration

- [ ] Enable/Disable models
- [ ] Set model access by plan
- [ ] Configure fallback chains
- [ ] Set custom pricing markup
- [ ] Priority queue for paid plans

---

## 7. Content Moderation (Guardrails)

### 7.1 Guardrail Configuration

| Guardrail | Status | Mode | Description |
|-----------|--------|------|-------------|
| **Prompt Injection** | Active | pre_call | Detect jailbreak attempts |
| **PII Detection** | Active | pre_call | Detect personal info |
| **Content Safety** | Active | during_call | Filter inappropriate content |
| **Thai PII** | Active | pre_call | Detect Thai PII (Presidio) |

### 7.2 Moderation Queue

- [ ] Review flagged content
- [ ] Approve/Reject actions
- [ ] User warnings
- [ ] Escalate to ban

---

## 8. System Monitoring

### 8.1 Health Status

| Service | Metrics |
|---------|---------|
| **LiteLLM Proxy** | Status, Uptime, RPS, Latency |
| **PostgreSQL** | Connections, Query time, Disk |
| **Redis** | Memory, Hit rate, Connections |
| **Payment Gateway** | Status, Failed payments |

### 8.2 Alerts

| Alert | Condition | Channel |
|-------|-----------|---------|
| **High Latency** | P99 > 5s | Slack, Email |
| **High Error Rate** | Error > 5% | Slack, Email |
| **Service Down** | Health check fail | Slack, Email, SMS |
| **Payment Failed** | Payment failure | Email |
| **High Churn** | Churn > threshold | Email |

---

## 9. Audit Logs

### 9.1 Admin Actions Log

| Column | Description |
|--------|-------------|
| **Timestamp** | Time of action |
| **Admin** | Admin who performed action |
| **Action** | Action type |
| **Target** | User/Resource affected |
| **Details** | Change details |
| **IP Address** | Admin IP |

**Tracked Actions:**
- Plan changes
- Manual upgrades/downgrades
- Refunds
- User suspend/ban
- Limit overrides
- Model changes

---

## 10. Settings

### 10.1 General Settings

| Setting | Description |
|---------|-------------|
| **Site Name** | Application name |
| **Default Plan** | Default plan for new users |
| **Trial Period** | Trial duration (days) |
| **Registration** | Open / Invite-only / Closed |

### 10.2 Payment Settings

| Setting | Description |
|---------|-------------|
| **Payment Provider** | Stripe / Paddle / LemonSqueezy |
| **Currency** | USD, EUR, THB, etc. |
| **Tax Handling** | Automatic / Manual |
| **Invoice Settings** | Company info, template |

### 10.3 LiteLLM Settings

| Setting | Description |
|---------|-------------|
| **Proxy URL** | LiteLLM proxy endpoint |
| **Master Key** | Admin API key |
| **Routing Strategy** | Default routing |
| **Cache Settings** | Redis TTL, semantic cache |

---

## Implementation Phases

### Phase 1: Core Admin (MVP)
- [ ] Admin authentication
- [ ] Dashboard with basic stats
- [ ] User list with search/filter
- [ ] Basic plan management (Free/Pro/Premium)
- [ ] Manual plan assignment

### Phase 2: Subscription & Billing
- [ ] Stripe integration
- [ ] Subscription management
- [ ] Payment processing
- [ ] Invoice generation
- [ ] Revenue dashboard

### Phase 3: Usage & Limits
- [ ] LiteLLM Virtual Keys per user
- [ ] Usage tracking integration
- [ ] Quota monitoring
- [ ] Overage handling
- [ ] Cost vs Revenue analytics

### Phase 4: Advanced Features
- [ ] Model access control by plan
- [ ] Rate limiting per plan
- [ ] Guardrails configuration
- [ ] Audit logs

---

## API Endpoints

### Subscription APIs
```
GET    /api/admin/plans              # List all plans
POST   /api/admin/plans              # Create plan
PUT    /api/admin/plans/:id          # Update plan
DELETE /api/admin/plans/:id          # Delete plan

GET    /api/admin/subscriptions      # List subscriptions
PUT    /api/admin/subscriptions/:id  # Update subscription
POST   /api/admin/subscriptions/:id/cancel    # Cancel
POST   /api/admin/subscriptions/:id/upgrade   # Upgrade
POST   /api/admin/subscriptions/:id/downgrade # Downgrade

GET    /api/admin/revenue            # Revenue stats
GET    /api/admin/revenue/by-plan    # Revenue by plan
GET    /api/admin/revenue/mrr        # MRR data
```

### User APIs
```
GET    /api/admin/users              # User list
GET    /api/admin/users/:id          # User detail
PUT    /api/admin/users/:id          # Update user
POST   /api/admin/users/:id/suspend  # Suspend
POST   /api/admin/users/:id/ban      # Ban
DELETE /api/admin/users/:id          # Delete
```

### LiteLLM Integration
```
POST   /key/generate                 # Create virtual key for user
GET    /key/info                     # Key info (limits, usage)
POST   /key/update                   # Update key limits
GET    /spend/logs                   # Usage logs
GET    /spend/users                  # Usage by user
```

---

## Database Schema (New Tables)

### plans
```sql
CREATE TABLE plans (
  id UUID PRIMARY KEY,
  name VARCHAR(50) NOT NULL,         -- Free, Pro, Premium, Enterprise
  slug VARCHAR(50) UNIQUE NOT NULL,
  monthly_price DECIMAL(10,2),
  annual_price DECIMAL(10,2),
  monthly_tokens INTEGER,
  daily_requests INTEGER,
  max_documents INTEGER,
  max_projects INTEGER,
  max_agents INTEGER,
  max_file_size_mb INTEGER,
  rate_limit_rpm INTEGER,
  allowed_models TEXT[],             -- Array of model names
  features JSONB,                    -- Additional features
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### subscriptions
```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  plan_id UUID REFERENCES plans(id),
  status VARCHAR(20),                -- active, trial, cancelled, past_due
  billing_cycle VARCHAR(20),         -- monthly, annual
  current_period_start TIMESTAMP,
  current_period_end TIMESTAMP,
  trial_end TIMESTAMP,
  cancelled_at TIMESTAMP,
  stripe_subscription_id VARCHAR(100),
  stripe_customer_id VARCHAR(100),
  litellm_key_id VARCHAR(100),       -- LiteLLM virtual key
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### invoices
```sql
CREATE TABLE invoices (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  subscription_id UUID REFERENCES subscriptions(id),
  stripe_invoice_id VARCHAR(100),
  amount DECIMAL(10,2),
  currency VARCHAR(3) DEFAULT 'USD',
  status VARCHAR(20),                -- paid, pending, failed
  paid_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Pricing Strategy Recommendations

### 1. Value-Based Pricing
- Free: ให้ลองใช้พอให้เห็นคุณค่า
- Pro: เหมาะกับ individual ที่ใช้เป็นประจำ
- Premium: power users ที่ต้องการ model ดีๆ

### 2. Usage Limits ที่เหมาะสม
- Free: ให้ใช้ได้ ~20 conversations/day
- Pro: พอสำหรับการใช้งานประจำวัน
- Premium: ไม่ต้องกังวลเรื่อง limits

### 3. Model Access เป็น Differentiator
- Free: Basic models (fast, cheap)
- Pro: Standard models (balanced)
- Premium: Best models (Claude, GPT-4)

### 4. Trial Strategy
- 14-day Pro trial for new users
- No credit card required for trial
- Email reminder at day 7, 12, 14

---

## Revenue Projections Example

| Metric | Month 1 | Month 6 | Month 12 |
|--------|---------|---------|----------|
| **Total Users** | 100 | 1,000 | 5,000 |
| **Free** | 80 (80%) | 700 (70%) | 3,500 (70%) |
| **Pro ($19)** | 15 (15%) | 240 (24%) | 1,200 (24%) |
| **Premium ($49)** | 5 (5%) | 60 (6%) | 300 (6%) |
| **MRR** | $530 | $7,500 | $37,500 |
| **ARR** | $6,360 | $90,000 | $450,000 |

---

## References

- [Stripe Subscriptions](https://stripe.com/docs/billing/subscriptions)
- [LiteLLM Virtual Keys](https://docs.litellm.ai/docs/proxy/virtual_keys)
- [LiteLLM Cost Tracking](https://docs.litellm.ai/docs/proxy/cost_tracking)
- [SaaS Pricing Best Practices](https://www.priceintelligently.com/)

---

*Document created: December 2024*

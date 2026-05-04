# Morning Email & Calendar Digest — Top 10 Action Items

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate dates accordingly.

- **Email window**: the past **7 days** ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: from today through the next **14 days** (Mountain Time).

---

## Step 2 — Fetch emails from the past 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates -from:noreply@ -from:no-reply@ -from:donotreply@`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

For any thread where the snippet alone is not enough to determine action items,
call `get_thread` to retrieve the full message body.

**Automatically skip** (do not include in the top-10):
- Marketing emails, newsletters, promotional offers
- Automated system notifications with no required action (e.g., "your statement is ready", routine calendar reminders from yourself)
- Messages from `noreply@`, `no-reply@`, `donotreply@`, or `notifications@` senders
- Social media notifications

**Do include** everything else: human-sent messages, transactional emails with action required, financial alerts, messages from colleagues/family/organizations that need a response or decision.

---

## Step 3 — Fetch upcoming one-time calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601, e.g. `2026-05-04T00:00:00-06:00`)
- `endTime`: 14 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

**Keep only events where ALL of the following are true:**
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are "out of the ordinary" one-time events — not part of the regular weekly routine.
Drop anything that belongs to a recurring series.

---

## Step 4 — Build the Top 10 action items list

Rank ALL qualifying emails and events together by urgency and importance:

**Priority order (highest to lowest):**
1. Security alerts, fraud alerts, compromised accounts — act immediately
2. Health/safety alerts (air quality, equipment failures, etc.)
3. Financial actions required (approve transactions, discrepancies to investigate)
4. Messages requiring a reply or decision from a specific person
5. Work or volunteer tasks with a deadline
6. Coordination needed with others (scheduling, follow-ups)
7. Upcoming one-time events that require preparation or RSVP
8. Informational items worth reviewing (statements available, etc.)

Select the **top 10** most important items across emails and calendar. Each item should have:
- A **numbered label** (#1–#10)
- A relevant **emoji** (🚨 for urgent, ⚠️ for important, 📋 for task, 📅 for event, 💰 for financial, etc.)
- A **short bold title** (5–8 words)
- **1–2 sentences** describing the specific action needed (concrete, not vague)

Use this colour scheme per item type:
| Urgency | Background | Border |
|---------|-----------|--------|
| Urgent (security/health/fraud) | `#fde8e8` | `#e74c3c` |
| Important action required | `#fff3cd` | `#e67e22` |
| Action needed (standard) | `#f0f7ff` | `#4A90D9` |
| Event/planning | `#e8f8e8` | `#27AE60` |

---

## Step 5 — Detect the account owner's email address

From all emails collected, find the **most frequently occurring address** in the `To:` field.
That is the owner's email. Store it as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `Daily Action Summary — {Weekday}, {Month} {Day}, {Year}`
  (e.g. `Daily Action Summary — Monday, May 4, 2026`)

**`htmlBody`**: use the template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Daily Action Summary &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; top 10 items from the past 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 20px;">&#128203; Top 10 Items to Address</h3>

<!-- Repeat this block for each of the 10 items -->
<div style="margin-bottom: 14px; padding: 12px; background: {bg-color}; border-left: 4px solid {border-color};">
  <p style="margin: 0;"><strong>#{N} &mdash; {emoji} {Short Title}</strong></p>
  <p style="margin: 6px 0 0 0;">{1–2 sentence description with the specific action required}</p>
</div>
<!-- End item block -->

<!-- ====== OUT-OF-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Upcoming One-Time Calendar Events (Next 14 Days)
</h3>

<!-- Repeat for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Day, Date &mdash; Start&ndash;End MT}</strong> &mdash; {Event Title}</p>
  <!-- Only include the lines below if data is present -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description or note}</p>
</div>
<!-- End event block -->

<!-- If no one-time events: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 14 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated daily digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Move the draft to Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

This delivers the digest directly to the inbox.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it in the Inbox via label assignment.

---

## Important rules

- Keep each action item to **1–2 sentences maximum** — brevity is key.
- Action items must be **concrete** ("Reply to Alice by Friday confirming the venue")
  not vague ("Follow up with Alice").
- If there are fewer than 10 genuinely actionable items, only list as many as exist.
- If there are no qualifying emails at all, write one item noting that clearly.
- Never include raw HTML, JSON, or code in the email body.
- Strip tracking pixels and HTML boilerplate from email bodies before summarising.

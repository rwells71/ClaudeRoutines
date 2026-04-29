# Top 10 Daily Briefing

You are running an automated 5 AM morning briefing for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

- **Email window**: the last 7 days.
  Gmail query: `newer_than:7d`
- **Calendar window**: today plus the next 7 days, in `America/Denver` timezone.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

**Skip** clearly automated bulk mail (marketing, newsletters, noreply addresses).
**Keep** transactional, human-sent, and important system notifications (expiry alerts,
school communications, financial alerts, calendar invites, action-required messages).

---

## Step 3 — Fetch non-recurring calendar events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` America/Denver (ISO 8601 with offset)
- `endTime`: 7 days from now at `23:59:59` America/Denver
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, identify **out-of-the-ordinary** events — defined as events that meet
ANY of the following criteria:
1. No `recurringEventId` field (one-time events).
2. The event title or description suggests something unusual, special, or time-sensitive
   (graduations, conferences, special meetings, one-off tasks, medical appointments,
   events with external guests, trips, etc.).
3. Events with attendees from outside the immediate family (i.e., not just
   megan.wells@gmail.com or richardlwells@gmail.com).

---

## Step 4 — Build the Top 10 Action Items list

Review all emails and unusual calendar events. Rank action items by urgency:

**Tier 1 — URGENT (deadline within 48 hours, or explicit "action required")**
**Tier 2 — IMPORTANT (deadline this week, or needs a response)**
**Tier 3 — GOOD TO KNOW (no hard deadline but worth acting on)**

Select the top 10 items across all tiers. Each item must be:
- Concrete and specific (what to do, not just "review this")
- Sourced from a real email or calendar event in this run's data
- Ranked so the most urgent appears first

---

## Step 5 — Determine the account owner's email address

Look at the "To:" fields of all fetched emails. The address that appears most
frequently is the account owner — use that as `{owner_email}`.

---

## Step 6 — Create the briefing draft and deliver it

### 6a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `📋 Daily Briefing - Top 10 Action Items | {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use the template below with real content substituted in.

```html
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px; color: #333;">

<h2 style="color:#1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 8px;">
  📋 Daily Briefing — {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color:#666; font-size:13px;">Last 7 days · Generated 5:00 AM MDT</p>

<h3 style="color:#333;">🔔 Top 10 Action Items</h3>

<table style="width:100%; border-collapse:collapse;">
  <!-- Repeat one <tr> block per action item (up to 10) -->
  <!-- Use red border (#d93025) for URGENT, orange (#f9ab00) for IMPORTANT, green (#34a853) for GOOD TO KNOW -->
  <!-- Use bg: #fce8e6 / #fff3e0 / #e8f5e9 to match -->

  <tr>
    <td style="padding:12px; background:{bg_color}; border-left:5px solid {border_color}; border-radius:4px; vertical-align:top;">
      <strong>{emoji} {rank}. {Action Item Title}</strong><br>
      {1–2 sentence description with the specific task and why it matters.}
    </td>
  </tr>
  <tr><td style="height:6px;"></td></tr>
  <!-- ... repeat for each item ... -->
</table>

<br>
<h3 style="color:#333;">📅 Unusual / One-Off Calendar Events (Next 7 Days)</h3>

<table style="width:100%; border-collapse:collapse; font-size:14px;">
  <tr style="background:#f1f3f4;">
    <th style="text-align:left; padding:8px;">Event</th>
    <th style="text-align:left; padding:8px;">When</th>
    <th style="text-align:left; padding:8px;">Notes</th>
  </tr>
  <!-- Repeat one <tr> per unusual event -->
  <tr>
    <td style="padding:8px; border-bottom:1px solid #e0e0e0;"><strong>{Event Title}</strong></td>
    <td style="padding:8px; border-bottom:1px solid #e0e0e0;">{Day Date · Start–End time}</td>
    <td style="padding:8px; border-bottom:1px solid #e0e0e0;">{Why it's unusual / any action needed}</td>
  </tr>
  <!-- If no unusual events: -->
  <!-- <tr><td colspan="3" style="padding:8px; color:#666;"><em>No unusual events in the next 7 days.</em></td></tr> -->
</table>

<br>
<p style="font-size:12px; color:#999; border-top:1px solid #e0e0e0; padding-top:10px;">
  Generated automatically by Claude at 5:00 AM MDT each morning.<br>
  Covers Gmail and Google Calendar activity from the past 7 days.
</p>

</body>
</html>
```

### 6b — Move the draft to Inbox

After `create_draft` returns a draft ID, call `label_message` with:
- `messageId`: the message ID from the draft response
- `addLabelIds`: `["INBOX"]`

This delivers the draft directly to the Inbox like a normal received email.

> **Note**: The Gmail MCP integration does not expose a send API. Delivery is
> accomplished by assigning the INBOX label to the draft. If `send_draft` becomes
> available in a future version, prefer that.

---

## Important rules

- If there are **no qualifying emails**, say so; do not omit the section.
- If there are **no unusual calendar events**, say so; do not omit the section.
- Never invent or hallucinate action items — every item must come from real data fetched in this run.
- Strip tracking pixels and boilerplate HTML before summarizing.
- Keep each action item description to 1–2 sentences maximum.
- The URGENT tier (🚨, red) is for hard deadlines within 48 hours or explicit "action required" messages.
- The IMPORTANT tier (⚠️, orange) is for deadlines this week or items needing a response.
- The GOOD TO KNOW tier (✅, green) is for no-deadline items worth knowing.

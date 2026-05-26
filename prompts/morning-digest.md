# Morning Email & Calendar Digest

You are running an automated morning digest for the account owner (richardlwells@gmail.com).
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time windows

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the last 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today plus the next 6 days (7 days total) in Mountain
  Time, from `00:00:00` today to `23:59:59` six days from now, timezone
  `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -in:draft -in:sent`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (cap at 150 threads to stay within context).

For each thread, use the snippet and metadata. Call `get_thread` only if the
snippet is insufficient to understand whether action is required.

**Always skip** these — they are noise, never action items:
- Marketing / promotional / newsletter emails
- Automated notifications from `noreply@`, `no-reply@`, `donotreply@`,
  `notifications@`, calendar-notification@google.com, voice-noreply@google.com,
  or `*@info*.*.com` / `*@reply.*.com` marketing domains
- Messages the owner sent themselves (sender == owner)
- Routine calendar reminder notifications

**Always include** these even if they come from automated addresses:
- Security alerts (login, card-not-present, fraud, account changes)
- Home or device alerts (smoke alarm, air quality, security cameras)
- Financial transaction confirmations
- Package / shipping notifications
- Human-written messages or replies

---

## Step 3 — Fetch the next 7 days of calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601, e.g. `2026-05-26T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, flag an event as **"out of the ordinary"** if ANY of the
following apply:
1. It does NOT have a `recurringEventId` (a one-time event).
2. It is a recurring event that was recently modified (its `updated` timestamp
   is within the last 7 days) — e.g. a cancellation, rescheduling, or update.
3. Its summary contains keywords suggesting a special commitment:
   hike, trek, tour, move, speak, visit, trip, tour, ceremony, performance,
   graduation, wedding, funeral, first, one-time, special.
4. It lasts 3+ hours (from start to end) during waking hours (6am–10pm).
5. It has a physical location that is not "home" or a regular meeting room.
6. The attendee response for the owner is `needsAction` or `tentative`.

---

## Step 4 — Determine action items from email

Review all collected emails. For each one that requires an action by the
account owner, create an action item with:
- A **priority level**: 🔴 High (urgent / time-sensitive / safety), 🟠 Medium
  (personal / important but not urgent), 🟡 Low (informational but worth noting)
- A **one-line title** (max 12 words)
- A **2–3 sentence description** with enough context to act without re-reading
  the original email

**Rank** all action items by priority (🔴 first, then 🟠, then 🟡), then by
recency within each tier.

Select the **top 10** action items. If there are fewer than 10 genuine action
items, include all of them and do not pad the list.

---

## Step 5 — Create and deliver the digest

### 5a — Create the draft

Call `create_draft` with:
- **`to`**: `["richardlwells@gmail.com"]`
- **`subject`**: `🌅 Daily Briefing — {Weekday}, {Month} {Day}, {Year}: Top 10 Action Items`
  e.g. `🌅 Daily Briefing — Tuesday, May 26, 2026: Top 10 Action Items`
- **`htmlBody`**: use the HTML template below

```html
<html>
<body style="font-family: Arial, sans-serif; max-width: 680px; margin: 0 auto; color: #222;">
<div style="background: #1a3a5c; color: white; padding: 20px 24px; border-radius: 8px 8px 0 0;">
  <h2 style="margin:0; font-size: 20px;">☀️ Good Morning, Richard</h2>
  <p style="margin: 4px 0 0; font-size: 13px; opacity: 0.85;">Daily Briefing · {Weekday}, {Month} {Day}, {Year} · 5:00 AM MDT</p>
</div>
<div style="background: #f8f9fb; padding: 20px 24px; border: 1px solid #dde1e7; border-top: none; border-radius: 0 0 8px 8px;">

  <h3 style="color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: 6px;">📋 Top 10 Action Items</h3>

  <table style="width:100%; border-collapse: collapse;">
    <!-- Repeat the block below for each action item (1–10) -->
    <tr>
      <td style="width:28px; vertical-align:top; padding: 10px 8px 10px 0; font-size:18px;">{PRIORITY_EMOJI}</td>
      <td style="padding: 10px 0; border-bottom: 1px solid #e0e4ea;">
        <strong>{NUMBER}. {TITLE}</strong><br>
        <span style="color:#555; font-size:13px;">{DESCRIPTION}</span>
      </td>
    </tr>
    <!-- End action item block -->
  </table>

  <!-- If fewer than 10 action items, end the table and note how many were found -->

  <h3 style="color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: 6px; margin-top: 28px;">📅 Out-of-the-Ordinary Calendar Events (Next 7 Days)</h3>

  <table style="width:100%; border-collapse: collapse; font-size:14px;">
    <tr style="background:#eef2f7;">
      <th style="text-align:left; padding:8px 10px; color:#1a3a5c;">Date/Time</th>
      <th style="text-align:left; padding:8px 10px; color:#1a3a5c;">Event</th>
      <th style="text-align:left; padding:8px 10px; color:#1a3a5c;">Why It's Notable</th>
    </tr>
    <!-- Repeat for each flagged event -->
    <tr>
      <td style="padding:8px 10px; border-bottom:1px solid #e0e4ea;"><strong>{DAY}</strong><br>{TIME}</td>
      <td style="padding:8px 10px; border-bottom:1px solid #e0e4ea;">{EVENT_TITLE}</td>
      <td style="padding:8px 10px; border-bottom:1px solid #e0e4ea;">{REASON}</td>
    </tr>
    <!-- End event row -->
  </table>

  <!-- If no flagged events this week: -->
  <!-- <p style="color:#555; font-size:14px;"><em>No out-of-the-ordinary events in the next 7 days.</em></p> -->

  <p style="margin-top: 24px; font-size: 12px; color: #888; border-top: 1px solid #dde1e7; padding-top: 14px;">
    This briefing was automatically generated from your Gmail and Google Calendar.<br>
    Sent daily at 5:00 AM MDT · <em>ClaudeRoutines Daily Summary</em>
  </p>
</div>
</body>
</html>
```

### 5b — Deliver the draft to the Inbox

After `create_draft` succeeds and returns an `id`, call `label_message` with:
- `messageId`: the `id` returned by `create_draft`
- `labelIds`: `["INBOX"]`

This moves the digest to the Inbox so it arrives like a normal email rather
than sitting silently in the Drafts folder.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via `label_message`.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- Never include more than 10 action items.
- Action items must be concrete and specific ("Text Keith Wells back about the
  photo-scanning project — he wants 4 copies and offered to pay expenses") not
  vague ("Follow up with Keith").
- If there are no genuine action items, say so clearly instead of inventing low-value items.
- Keep each description to 2–3 sentences max.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- For the calendar section, briefly explain *why* each event is flagged (e.g.
  "One-time event", "3-hour outdoor commitment", "RSVP still pending").
- If no calendar events are flagged, say so clearly; do not omit the section.

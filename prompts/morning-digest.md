# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the past 7 days (last 168 hours).
  Gmail query: `newer_than:7d`
- **Calendar window**: today through the next 7 days, from
  today `00:00:00` through 7 days out `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the past week

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -in:sent -in:draft`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 150 threads total).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID (be selective — only fetch full threads
where the snippet is too vague to extract an action item).

**Skip** clearly automated non-actionable mail: marketing emails, newsletters,
messages from `noreply@`, `no-reply@`, `donotreply@`, `notifications@`, or
`calendar-notification@` addresses. **Do include** transactional alerts that
require action (financial alerts, security alerts, school notifications, etc.)
and all human-sent messages.

---

## Step 3 — Fetch upcoming calendar events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, identify **"out of the ordinary" events** — events that
stand out from daily routine. Keep an event if ANY of these are true:
1. It does NOT have a `recurringEventId` field (it is a one-time event).
2. It has external attendees (people outside the owner's household).
3. It contains a location or video conference link (suggesting it is a real
   meeting rather than a personal reminder).
4. Its title contains words like: meeting, appointment, graduation, trip,
   travel, flight, interview, surgery, ceremony, event, game, performance,
   concert, wedding, funeral, party, or other milestone/social words.
5. It starts before 6:00 AM or after 9:00 PM (unusual time).

Drop purely personal recurring reminders (e.g. "Log all food", "Take out
garbage", "Check for baptisms", "Don't wake up Lyndie") that recur and
have no attendees or location.

---

## Step 4 — Build the Top 10 Action Item List

Review all collected emails and notable calendar events together. Identify
the **ten most important items** the account owner needs to act on or be
aware of today. Rank them by urgency and importance:

- **Priority 1 (🔴 Urgent)**: deadlines today or tomorrow, time-sensitive
  replies, urgent alerts (security, financial fraud, health, home safety),
  meetings today requiring preparation.
- **Priority 2 (🟡 This Week)**: follow-ups due within 7 days, upcoming
  meetings to prepare for, pending orders/requests awaiting a response,
  tasks with a known deadline this week.
- **Priority 3 (🟢 On Your Radar)**: informational items worth noting,
  opportunities, reminders with no hard deadline.

For each item:
- Give it a clear, specific title (not vague like "Finance alert")
- State the source (email from X, calendar event, etc.)
- Give 1–3 bullets of concrete context
- State a specific action: what needs to be done, by when, and with whom

---

## Step 5 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient
   addresses. The address that appears most frequently is almost certainly the
   account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of
   the other addresses in the "To:" fields.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `📋 Daily Action Summary — {Weekday}, {Month} {Day}, {Year}`
  e.g. `📋 Daily Action Summary — Friday, April 25, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="color:#1a56a0; border-bottom:2px solid #1a56a0; padding-bottom:8px;">
  📋 Daily Action Summary &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color:#555; font-size:13px;">Top items requiring your attention · Generated at 5:00 AM Mountain Time</p>

<!-- ====== URGENT SECTION ====== -->
<!-- Only include this section if there are 🔴 urgent items -->
<h3 style="color:#c0392b; margin-top:24px;">🔴 Urgent / Time-Sensitive</h3>

<!-- Repeat the block below for each urgent item (rank #1, #2, ...) -->
<table style="width:100%; border-collapse:collapse; margin-bottom:8px;">
<tr style="background:#fdf2f2;">
  <td style="padding:12px; border-left:4px solid #c0392b; vertical-align:top; width:30px;"><strong>#{N}</strong></td>
  <td style="padding:12px;">
    <strong>{Item Title}</strong><br>
    <em style="color:#888; font-size:12px;">Source: {email from X / calendar event}</em><br>
    {Context bullet 1}<br>
    {Context bullet 2 if needed}<br>
    <strong>Action:</strong> {Specific action, deadline, who}
  </td>
</tr>
</table>

<!-- ====== THIS WEEK SECTION ====== -->
<!-- Only include this section if there are 🟡 this-week items -->
<h3 style="color:#e67e22; margin-top:20px;">🟡 Needs Attention This Week</h3>

<!-- Same block structure, background:#fef9f0, border-left:#e67e22 -->

<!-- ====== ON YOUR RADAR SECTION ====== -->
<!-- Only include this section if there are 🟢 radar items -->
<h3 style="color:#27ae60; margin-top:20px;">🟢 On Your Radar</h3>

<!-- Same block structure, background:#f0fdf4, border-left:#27ae60 -->

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="color:#1a56a0; margin-top:24px; border-top:1px solid #ddd; padding-top:16px;">
  📅 Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each notable calendar event -->
<div style="margin-bottom:10px; padding:10px; background:#f0f7ff; border-left:4px solid #1a56a0;">
  <p style="margin:0;"><strong>{Day, Month Date} · {Start Time} – {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Include these lines only if data is present -->
  <p style="margin:4px 0 0 18px; color:#555;">📍 {Location or video link}</p>
  <p style="margin:4px 0 0 18px; color:#555;">👥 {Attendees if external}</p>
  <p style="margin:4px 0 0 18px; color:#555;">{Why this is notable}</p>
</div>

<!-- If no out-of-the-ordinary events: -->
<!-- <p><em>No unusual calendar events in the next 7 days.</em></p> -->

<hr style="margin-top:32px; border:none; border-top:1px solid #ddd;">
<p style="color:#aaa; font-size:11px;">Automated digest &mdash; ClaudeRoutines · Sent daily at 5 AM Mountain Time</p>

</body>
</html>
```

### 6b — Move the draft to Inbox

After `create_draft` returns an `id`, call `label_message` with:
- `messageId`: the `id` returned by `create_draft`
- `labelIds`: `["INBOX"]`

This moves the draft to the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- The list must contain **exactly 10 items** (adjust priority buckets to fill
  it; if fewer than 10 actionable items exist, add "good to know" items).
- Keep each item concise: 2–4 lines of context maximum.
- Action items must be concrete ("Reply to Camron Erickson by Wednesday to
  confirm proof-of-residency documents") not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Do not include calendar-notification@ emails as email action items — those
  are surfaced through the calendar section instead.

# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (the last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window**: from today through 7 days from now in Mountain Time.

---

## Step 2 — Fetch emails from the past week

Call `search_threads` with:
- `query`: `newer_than:7d in:inbox -category:promotions -category:social -is:draft`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 3 pages maximum).

For each thread, examine the snippet and metadata. If the full body is needed
to understand action items, call `get_thread` for that thread.

**Skip clearly automated mail**: marketing/promotional, newsletters, messages
from `noreply@`, `no-reply@`, `donotreply@`, calendar-notification@google.com
notifications, Qustodio reports, rewards/loyalty emails, and any message that
clearly requires zero action from the owner.

**Include**: human-sent messages, transactional emails requiring action (bills
due, shipments needing signature, approvals needed), important institutional
or church communications, financial statements/alerts, school/education notices
that require a parent response.

---

## Step 3 — Fetch upcoming calendar events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

---

## Step 4 — Identify "out of the ordinary" calendar events

From the full event list, select only events that are genuinely unusual or
noteworthy — not routine recurring appointments. An event is "out of the
ordinary" if it meets **at least one** of the following criteria:

1. **Non-recurring**: does NOT have a `recurringEventId` or `recurrence` field.
2. **High-profile or one-time**: title suggests a special occasion (tour, hike,
   performance, speaking engagement, trip, training, ceremony, etc.).
3. **Recently added**: `created` timestamp is within the last 7 days.
4. **External attendees**: has attendees whose email is not `richardlwells@gmail.com`,
   `megan.wells@gmail.com`, or a Google system address.
5. **Unusual time**: starts before 6:00 AM or after 9:00 PM.
6. **Multi-hour block**: duration is 3+ hours and not a recurring event.

Drop standard recurring events (weekly dinners, regular karate, recurring
meetings, daily reminders, chores) unless they also meet one of the above
criteria.

---

## Step 5 — Build the Top 10 Action Items list

From all the emails (and any relevant calendar items), identify and rank the
**top 10 items that require the account owner's personal attention or action**.

Ranking criteria (higher priority first):
1. **Time-sensitive / deadlines** — something due within 7 days
2. **Decisions required** — someone is waiting on a response or approval
3. **Financial** — bills, payments, account alerts needing review
4. **Family / household** — child school enrollment, appointments, logistics
5. **Professional / church leadership** — callings, training, scheduling
6. **Follow-up needed** — missed calls, unanswered texts, pending requests
7. **Review / read** — statements, reports, important documents

Each action item must be:
- **Specific** (name the person, amount, deadline, or decision) — not vague
- **Actionable** (starts with a verb: "Reply to…", "Pay…", "Confirm…", "Call…")
- **Tagged with source**: `[Email]`, `[Calendar]`, or `[Email + Calendar]`

---

## Step 6 — Determine the account owner's email address

Look at the **"To:"** field of the fetched emails. The address appearing most
frequently is the owner's. Store it as `{owner_email}`. If ambiguous, use
`richardlwells@gmail.com`.

---

## Step 7 — Create and deliver the digest

### 7a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use the HTML template below with real content substituted.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  ☀️ Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &nbsp;|&nbsp; Covering the past 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 24px;">✅ Top 10 Items to Address</h3>

<ol style="padding-left: 20px;">

  <!-- Repeat <li> block for each of the 10 items -->
  <li style="margin-bottom: 14px;">
    <strong>{Action verb + specific task}</strong>
    <span style="font-size:0.85em; color:#888;"> [{Email | Calendar | Email + Calendar}]</span><br/>
    <span style="color:#555; font-size:0.93em;">{One sentence of context — who, what, why it matters, deadline if any}</span>
  </li>

</ol>

<!-- ====== OUT-OF-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  📅 Out-of-the-Ordinary Calendar Events &mdash; Next 7 Days
</h3>

<!-- Repeat for each unusual event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Day, Mon D} &nbsp; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Include only if present -->
  <p style="margin: 4px 0 0 18px; color: #555;">📍 {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">{Why flagged: e.g. "One-time event added Jun 1" or "External attendees"}</p>
</div>
<!-- End event block -->

<!-- If no unusual events: -->
<!-- <p><em>No out-of-the-ordinary events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &mdash; Sent daily at 5:00 AM MT</p>

</body>
</html>
```

### 7b — Deliver the draft to Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

This moves the draft to the Inbox so it arrives like a real email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- Action items must be **specific and concrete** — never vague ("Follow up").
- If fewer than 10 genuine action items exist, list what there are; do not
  pad with trivial tasks.
- If there are no unusual calendar events, say so clearly.
- Strip tracking pixels and HTML boilerplate before summarizing emails.
- Never include raw HTML or JSON in the digest body.
- Multiple emails from the same sender/thread count as one action item.

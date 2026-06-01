# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the past 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days from now (Mountain Time),
  from `00:00:00` today to `23:59:59` seven days from now, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social in:inbox`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (maximum 3 pages).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to determine action items, call `get_thread` with
that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message whose subject or snippet clearly contains only advertising content.

**Include**: human-sent messages, transactional notifications requiring action
(bills due, approvals needed, items expiring, confirmations needed), urgent
system alerts, and anything that requires a response or decision.

---

## Step 3 — Fetch upcoming calendar events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, identify **"out of the ordinary" events** — events that stand
out from a typical week. An event is out of the ordinary if ANY of the following
is true:

1. It does **not** have a `recurringEventId` field (one-time event).
2. It involves travel, a special location, or a notable outing (trips, tours,
   hikes, performances, appointments, ceremonies).
3. The title contains a monetary amount, a proper name of a non-family person
   being contacted about a specific matter, or a time-sensitive action.
4. It is a meeting or activity with external attendees (non-family email addresses).
5. The title or description suggests urgency, a deadline, or an unusual task
   (e.g., "pay", "renew", "check", "fix", "virus scan", "ticket", "appointment").

Do **not** flag: daily log food, family dinner, take out garbage, karate
(recurring routine), baths for kids, laundry, bread, log all food — unless they
have an unusual note or attendee.

---

## Step 4 — Build the Top 10 Action Items list

From the emails collected in Step 2, identify everything that requires the
account owner to take an action: reply, pay, approve, confirm, call, renew,
fix, or decide. Rank the 10 most important by urgency and consequence.

For each item:
- Who it's from (person or system)
- What needs to be done (specific action verb)
- Any deadline or time sensitivity
- One-line context

If fewer than 10 actionable items exist, list all of them; do not pad.

---

## Step 5 — Determine the account owner's email address

Examine the **"To:"** fields of the fetched emails. The address appearing most
frequently is the account owner's. Store it as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `☀️ Daily Briefing — {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="background:#1a3a6b;color:white;padding:14px 18px;border-radius:6px;">
  ☀️ Daily Briefing &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color:#666;font-size:0.85em;">Generated at 5:00 AM Mountain Time &middot; Emails from the past 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top:24px;color:#1a3a6b;">🔴 Top 10 Action Items</h3>

<table style="width:100%;border-collapse:collapse;">
<!-- Repeat this row for each action item, alternating background #fff3f3 / #fff8f0 -->
<tr style="background:#fff3f3;">
  <td style="padding:10px 8px;width:28px;vertical-align:top;font-size:16px;font-weight:bold;">{N}</td>
  <td style="padding:10px 8px;">
    <strong>{Who — What}</strong><br>
    <span style="font-size:13px;color:#555;">{Context / deadline / one-line detail}</span>
  </td>
</tr>
<!-- End action item row -->
</table>

<!-- If fewer than 10 items, note how many were found -->

<!-- ====== UNUSUAL CALENDAR EVENTS ====== -->
<h3 style="margin-top:28px;border-top:1px solid #ddd;padding-top:16px;color:#1a3a6b;">
  📅 Unusual &amp; Notable Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each out-of-the-ordinary event -->
<div style="margin-bottom:10px;padding:10px;background:#f0f4ff;border-left:4px solid #4a90d9;">
  <p style="margin:0;"><strong>{Day, Date} &mdash; {Start}&ndash;{End} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin:4px 0 0 16px;color:#555;font-size:13px;">📍 {Location or video link}</p>
  <p style="margin:4px 0 0 16px;color:#555;font-size:13px;">{Why it's notable / brief description}</p>
</div>
<!-- End event block -->

<!-- If no unusual events, write: <p><em>No unusual events in the next 7 days.</em></p> -->

<hr style="margin-top:28px;"/>
<p style="font-size:0.75em;color:#aaa;text-align:center;">
  Automated Daily Briefing &mdash; ClaudeRoutines &middot; richardlwells@gmail.com
</p>
</body>
</html>
```

**`body`** (plain-text fallback): Write a plain-text version with the same
Top 10 list and calendar events, separated by `---`.

### 6b — Deliver the draft to the Inbox

`create_draft` returns a draft ID like `r123456789`. To deliver it as an
inbox message, you must find its underlying **message ID** (a hex string like
`19e82df7e2cac18c`). Follow these steps:

1. Call `list_drafts` with `query` set to the exact subject line you used
   (e.g., `subject:"☀️ Daily Briefing — Monday, June 1, 2026"`).
2. From the result, find the draft whose subject matches. Use the `id` field
   from that draft record — this is the message ID (hex format).
3. Call `label_message` with:
   - `messageId`: the hex message ID from step 2
   - `labelIds`: `["INBOX"]`

This moves the digest to the Inbox so it appears as a regular email rather than
sitting silently in Drafts.

> **Note**: The Gmail MCP integration does not expose a send API. Delivery is
> achieved by placing the draft directly in the Inbox via label assignment.

---

## Important rules

- The Top 10 list is the primary deliverable — it must always be present.
- If there are fewer than 10 actionable items, list all of them.
- Action items must be concrete: "Reply to Janet confirming you'll visit Primary
  on June 7" — not "Follow up with Janet."
- Calendar events section must always be present even if empty.
- Keep individual action item descriptions to 1–2 lines.
- Strip all HTML, tracking pixels, and boilerplate before summarizing email content.
- Never include raw HTML, JSON, or email headers in the digest body.
- If multiple emails from the same sender relate to the same topic, treat them as
  one action item.

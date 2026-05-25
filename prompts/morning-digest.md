# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 24-hour period ending right now (i.e. the last 24 hours).
  Gmail query: `newer_than:1d`
- **Calendar window**: today (the current date in Mountain Time), from
  `00:00:00` to `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:1d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with an `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch today's non-recurring calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **keep only events where ALL of the following are true**:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are genuinely one-time events. Drop anything that belongs to a
recurring series.

---

## Step 4 — Summarize

### Top 10 Action Items
Review ALL emails and calendar events. Produce a single ranked list of the
**10 most important things** the account owner needs to act on today or this week.
Order by urgency (deadlines first, then important people, then reminders).

For each item:
- **Bold title** (5–8 words)
- One concise sentence explaining what action is needed and why

Skip marketing, newsletters, and purely informational messages unless they
contain a deadline or direct request.

### Out-of-Ordinary Calendar Events
From the calendar results, highlight events that are NOT routine. An event is
"out of the ordinary" if it:
- Has no `recurringEventId` (it's a one-time event), **OR**
- Is a recurring event that has been recently created, updated, or canceled, **OR**
- Spans more than 2 hours, **OR**
- Involves an unusual commitment (moves, hikes, special meetings, travel)

For each qualifying event:
- Date and time (Mountain Time)
- Event title
- One sentence on why it stands out or what preparation is needed

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

## Step 6 — Create and label the digest draft

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Friday, April 25, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 650px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #2c5f8a; padding-bottom: 8px; color: #2c5f8a;">
  Daily Briefing &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #888; font-size: 0.85em;">Generated at 5:00 AM Mountain Time</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="color: #c0392b; margin-top: 24px;">&#128203; Top 10 Action Items</h3>
<ol style="line-height: 1.9; padding-left: 20px;">
  <!-- Repeat one <li> per action item, ordered by urgency -->
  <li><strong>{Bold title}</strong> &mdash; {One sentence explaining what to do and why.}</li>
  <!-- ... up to 10 items ... -->
</ol>
<!-- If there are fewer than 10 genuine action items, list only as many as exist. -->

<!-- ====== OUT-OF-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="color: #8e44ad; margin-top: 28px; border-top: 1px solid #eee; padding-top: 16px;">
  &#128197; Out-of-Ordinary Calendar Events
</h3>
<!-- Repeat one row per qualifying event -->
<table style="width:100%; border-collapse:collapse; font-size:14px;">
  <tr style="background:#f5f0ff;">
    <td style="padding:10px; border:1px solid #ddd; width:35%;">
      <strong>{Date}</strong><br>{Start Time} &ndash; {End Time} MT
    </td>
    <td style="padding:10px; border:1px solid #ddd;">
      <strong>{Event Title}</strong><br>
      <span style="color:#555;">{One sentence: why it stands out or what to prepare.}</span>
    </td>
  </tr>
  <!-- ... -->
</table>
<!-- If no out-of-ordinary events, replace table with: -->
<!-- <p><em>No unusual events this week.</em></p> -->

<hr style="margin-top: 32px; border: none; border-top: 1px solid #eee;"/>
<p style="font-size: 0.75em; color: #aaa;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Confirm draft creation

After `create_draft` succeeds, print a single confirmation line:

```
Digest draft created: "<subject line>"
```

Do **not** call `label_message` or `list_labels`. The Gmail MCP only has
`gmail.compose` scope; any attempt to modify labels returns 403.
Delivery to the inbox is handled by the `deliver_digest.py` step that runs
after this Claude step in the GitHub Actions workflow.

---

## Important rules

- If there are **no emails**, say so clearly; do not omit the section.
- If there are **no non-recurring calendar events**, say so clearly; do not omit the section.
- Keep email summaries concise: maximum 4 bullets per email.
- Action items must be concrete ("Reply to Alice confirming the meeting time")
  not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If multiple emails from the same sender arrive in the window, group them all
  under one sender heading with separate subject/key-points/action-items blocks.

# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the past 7 days (last week).
  Gmail query: `newer_than:7d`
- **Calendar window**: the next 7 days starting from today (the current date in
  Mountain Time), from `00:00:00` today to `23:59:59` seven days from now,
  timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 200 threads maximum).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch upcoming calendar events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-05-28T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, **flag an event as "out of the ordinary"** if it meets ANY of
the following criteria:

1. It does NOT have a `recurringEventId` field AND does NOT have a `recurrence`
   field — i.e. it is a genuine one-time/non-recurring event.
2. It starts before 7:00 AM or ends after 8:00 PM Mountain Time.
3. It has 5 or more attendees.
4. Its `created` timestamp is within the last 48 hours (recently added).
5. Its `updated` timestamp is within the last 48 hours AND it is not the same
   as its `created` timestamp (recently modified).
6. Its title or description contains words suggesting urgency or unusual
   circumstances: "urgent", "emergency", "all-hands", "offsite", "travel",
   "flight", "conference", "interview", "performance review", "1:1 with"
   a skip-level, "board", or "executive".

Keep only flagged events. Drop routine recurring events that do not meet any
of the above criteria.

---

## Step 4 — Build the Top 10 Action List

Review ALL emails from Step 2 and identify every concrete action item, decision
needed, or time-sensitive matter requiring attention. Then rank them by
**priority** using these criteria (higher priority = earlier in list):

1. **Deadline / time sensitivity** — explicit due dates, meeting prep needed
   today, items expiring soon.
2. **Sender importance** — emails from a manager, executive, client, or key
   collaborator rank higher than peer or vendor emails.
3. **Recency** — more recent emails rank higher when priority is otherwise equal.
4. **Waiting on you** — threads where the account owner has not yet replied
   rank higher than threads where a reply has been sent.

Select the **top 10** items. If fewer than 10 actionable items exist, list all
of them. If more than 10 exist, include only the top 10.

For each item in the list:
- A one-line action title (what needs to be done)
- The sender's name and email
- The email subject line
- The date/time the email was received
- 1–3 bullet points explaining the context and why action is needed
- A specific, concrete next step (not vague — e.g. "Reply to Alice by EOD
  confirming the meeting time" not just "Follow up")

---

## Step 5 — Summarize out-of-the-ordinary calendar events

For each flagged calendar event from Step 3:
- Date, start and end time (Mountain Time, e.g. "Wed May 28 · 9:00 AM – 10:00 AM MT")
- Event title
- Why it is flagged as out of the ordinary (e.g. "New one-time event",
  "Added 4 hours ago", "Starts at 6:30 AM", "8 attendees", etc.)
- Location or video link (if present)
- Attendee count and names/emails if ≤ 6 attendees, or just count if more
- One-line description excerpt (if present)

---

## Step 6 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient
   addresses. The address that appears most frequently is almost certainly the
   account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of
   the other addresses in the "To:" fields.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 7 — Create and deliver the digest

### 7a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `☀️ Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `☀️ Morning Digest — Wednesday, May 28, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 720px; margin: auto; color: #222;">

<h2 style="border-bottom: 3px solid #4A90D9; padding-bottom: 8px;">
  ☀️ Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Emails from the past 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px; color: #C0392B;">🎯 Top 10 Items to Address</h3>

<!-- Repeat the block below for each action item (up to 10) -->
<div style="margin-bottom: 18px; padding: 14px; background: #fff8f8; border-left: 5px solid #C0392B; border-radius: 3px;">
  <p style="margin: 0 0 4px 0; font-size: 1.05em; font-weight: bold;">
    #{rank}. {Action Title}
  </p>
  <p style="margin: 0 0 6px 0; font-size: 0.85em; color: #777;">
    From: {Sender Name} &lt;{sender@example.com}&gt; &bull;
    Subject: <em>{Email Subject}</em> &bull;
    Received: {Date &amp; Time}
  </p>
  <ul style="margin: 4px 0; padding-left: 20px;">
    <li>{Context bullet 1}</li>
    <li>{Context bullet 2 (if needed)}</li>
    <li>{Context bullet 3 (if needed)}</li>
  </ul>
  <p style="margin: 8px 0 0 0; padding: 8px; background: #fdecea; border-radius: 3px;">
    <strong>➡️ Next Step:</strong> {Specific concrete action required}
  </p>
</div>
<!-- End action item block -->

<!-- If no actionable items were found: -->
<!-- <p><em>No actionable items found in emails from the past 7 days.</em></p> -->

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px; color: #1A6B3A;">
  📅 Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each flagged event -->
<div style="margin-bottom: 14px; padding: 12px; background: #f0faf4; border-left: 5px solid #27AE60; border-radius: 3px;">
  <p style="margin: 0 0 2px 0; font-weight: bold;">
    {Day, Month Date} &bull; {Start Time} &ndash; {End Time} MT &mdash; {Event Title}
  </p>
  <p style="margin: 4px 0 0 0; font-size: 0.85em; color: #888;">
    ⚠️ Flagged: {Reason this event is out of the ordinary}
  </p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">📍 {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">👥 {Attendee count and names if ≤ 6}</p>
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">{Brief description excerpt}</p>
</div>
<!-- End event block -->

<!-- If no out-of-the-ordinary events in the next 7 days: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 36px;"/>
<p style="font-size: 0.8em; color: #999; text-align: center;">
  Automated morning digest &mdash; ClaudeRoutines &bull; Delivered daily at 5:00 AM MT
</p>

</body>
</html>
```

### 7b — Deliver the digest to the Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — its ID is literally the string `"INBOX"`.
Do **not** call `list_labels` to look it up; use `"INBOX"` directly.

This moves the draft to the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- The Top 10 list is the primary deliverable — make it sharp and actionable.
- If there are **fewer than 10 actionable items**, list all of them; do not pad.
- If there are **no actionable items**, say so clearly; do not omit the section.
- If there are **no out-of-the-ordinary calendar events**, say so clearly.
- Action items must be concrete ("Reply to Alice by EOD confirming the 2 PM slot")
  not vague ("Follow up with Alice").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Calendar event flags must cite the specific criterion that triggered the flag
  (e.g. "Non-recurring one-time event", "Recently added 3 hours ago",
  "Early start: 6:30 AM", "9 attendees").

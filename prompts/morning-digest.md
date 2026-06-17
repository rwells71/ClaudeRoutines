# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through the next 7 days, starting at
  `00:00:00` Mountain Time, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 150 threads maximum).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, and important system notifications.

---

## Step 3 — Fetch out-of-the-ordinary calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-06-17T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **keep only events where at least one of the following is true**:
1. The event does NOT have a `recurringEventId` field (one-time events).
2. The event does NOT have a `recurrence` field (one-time events).
3. The event title contains words like: urgent, important, deadline, review, interview, demo, launch, due, decision, offsite, travel, flight, conference, workshop.
4. The event starts before 8:00 AM or ends after 7:00 PM Mountain Time (outside normal business hours).
5. The event has 5 or more attendees.

These are the "out of the ordinary" events worth highlighting.

---

## Step 4 — Build the Top 10 Action Items list

Analyze ALL emails collected in Step 2. Identify every concrete action item
the account owner needs to take: replies required, decisions pending, approvals
needed, deadlines approaching, requests from other people, and follow-ups due.

**Rank** all action items by urgency and importance using these criteria
(highest priority first):
1. Hard deadlines mentioned explicitly in the email
2. Requests from people senior to the owner, clients, or direct reports
3. Time-sensitive items (replies overdue or due within 48 hours)
4. Items blocking other people's work
5. Everything else, ordered by recency

Select the **top 10** highest-priority action items. For each:
- Assign a priority rank (1 = most urgent)
- Note the source email subject and sender
- Write one specific, concrete action sentence (e.g. "Reply to Alice confirming the 2pm Thursday slot" not "Follow up with Alice")
- Note any deadline if one is mentioned

If fewer than 10 actionable items exist, list all of them.

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

## Step 6 — Create and label the digest

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Tuesday, June 17, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; reviewing the last 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#9989; Top 10 Action Items</h3>

<!-- If no action items found -->
<!-- <p><em>No action items found in the last 7 days.</em></p> -->

<!-- Repeat the block below for each action item, #1 = most urgent -->
<div style="margin-bottom: 14px; padding: 12px; background: #f9f9f9; border-left: 4px solid #E74C3C;">
  <p style="margin: 0 0 4px 0;">
    <strong>#1</strong>
    <!-- Change border-left color for lower priority: #E74C3C for 1-3, #F39C12 for 4-7, #27AE60 for 8-10 -->
  </p>
  <p style="margin: 0 0 4px 0;"><strong>Action:</strong> {specific action sentence}</p>
  <p style="margin: 0; color: #555; font-size: 0.9em;">
    From: {Sender Name} &mdash; <em>{Email Subject}</em>
    <!-- Only include if a deadline exists: -->
    &mdash; <strong style="color: #E74C3C;">Due: {deadline}</strong>
  </p>
</div>
<!-- End action item block -->

<!-- Use red border (#E74C3C) for items 1-3, orange (#F39C12) for 4-7, green (#27AE60) for 8-10 -->

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events &mdash; Next 7 Days
</h3>

<!-- If no unusual events -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<!-- Repeat for each out-of-the-ordinary event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Day, Month Date}</strong> &mdash; <strong>{Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description or reason it's out of the ordinary}</p>
</div>
<!-- End event block -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &mdash; 7-day email window</p>

</body>
</html>
```

### 6b — Move the digest to the Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — its ID is literally the string `"INBOX"`.
Do **not** call `list_labels` to look it up; use `"INBOX"` directly.

This moves the draft to the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.

---

## Important rules

- The top 10 list is the primary deliverable — make it specific and actionable.
- Color-code action items by priority: red border for #1–3, orange for #4–7, green for #8–10.
- If fewer than 10 genuine action items exist, list only real ones — do not pad with low-value items.
- Action items must be concrete ("Reply to Alice confirming the meeting time")
  not vague ("Follow up with Alice").
- For calendar events, note WHY each event is out of the ordinary (one-time, early/late, large group, urgent title, etc.).
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If there are no qualifying emails or calendar events, say so clearly; do not omit the section.

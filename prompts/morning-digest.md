# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today (the current date in Mountain Time), from
  `00:00:00` to `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 150 threads total).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch calendar events

Call `list_events` twice:

**A) Today's events**
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601, e.g. `2026-06-21T00:00:00-06:00`)
- `endTime`: today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

**B) Next 7 days (look-ahead)**
- Same parameters but `endTime` = 7 days from today at `23:59:59` Mountain Time

From both result sets, **flag an event as "out of the ordinary"** if it meets
ANY of the following criteria:
1. It does NOT have a `recurringEventId` or `recurrence` field (genuine one-time event).
2. Its start time is before 7:00 AM or after 7:00 PM Mountain Time.
3. Its title or description contains words like: urgent, emergency, deadline,
   critical, important, cancel, reschedule, alert, RSVP, confirm, approval,
   review, decision, escalat, board, exec, crisis, or a dollar amount ($).
4. It has more than 8 attendees.
5. It was created or last modified within the past 48 hours (check `created`
   and `updated` fields — treat as unusual if the event is recent and in the
   near future).
6. Its location is a physical address outside the owner's normal area, or
   it requires travel.

Collect all flagged events from both windows, de-duplicate by event ID.

---

## Step 4 — Build the Top 10 Action Items list

Review all emails collected in Step 2. Extract every concrete action item
or decision the account owner needs to take. Consider:
- Explicit requests ("Can you send me…", "Please review…", "Let me know…")
- Pending replies that appear to be waiting on the owner
- Deadlines or time-sensitive items mentioned in email bodies
- Approvals, sign-offs, or decisions needed
- Documents or files requested or shared that need attention

Score each action item by urgency using these factors (highest weight first):
1. Explicit deadline mentioned (today or this week = highest priority)
2. Sender is a person (not a system), especially if the same person has
   followed up more than once
3. Financial, legal, or contractual implications
4. Multiple people are waiting on the owner's response
5. Recency — more-recent emails rank higher when all else is equal

Select the **top 10** action items. If fewer than 10 exist, include all of them.
Number them 1 (most urgent) through 10 (least urgent).

For each action item record:
- **Priority number** (1–10)
- **Action**: one concise sentence describing what needs to be done
- **From**: sender name + email address
- **Subject**: the email subject line
- **Why urgent**: one phrase explaining the urgency signal
- **Deadline**: explicit date/time if mentioned, otherwise "this week" or "no explicit deadline"

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

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Saturday, June 21, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; Email window: last 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#128204; Top 10 Action Items</h3>

<!-- If no action items were found: -->
<!-- <p><em>No action items requiring attention in the last 7 days.</em></p> -->

<!-- Repeat the block below for each action item, #1 first -->
<div style="margin-bottom: 16px; padding: 12px; background: #fff8e1; border-left: 4px solid #F5A623; border-radius: 3px;">
  <p style="margin: 0 0 4px 0; font-size: 1.05em;">
    <strong>#{priority_number} &mdash; {Action sentence}</strong>
  </p>
  <table style="font-size: 0.88em; color: #555; border-collapse: collapse;">
    <tr><td style="padding: 1px 8px 1px 0; white-space: nowrap;"><strong>From:</strong></td><td>{Sender Name} &lt;{sender@example.com}&gt;</td></tr>
    <tr><td style="padding: 1px 8px 1px 0; white-space: nowrap;"><strong>Subject:</strong></td><td>{email subject}</td></tr>
    <tr><td style="padding: 1px 8px 1px 0; white-space: nowrap;"><strong>Why urgent:</strong></td><td>{urgency phrase}</td></tr>
    <tr><td style="padding: 1px 8px 1px 0; white-space: nowrap;"><strong>Deadline:</strong></td><td>{deadline or "no explicit deadline"}</td></tr>
  </table>
</div>
<!-- End action item block -->

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events
</h3>
<p style="color: #666; font-size: 0.88em; margin-top: -8px;">
  Today + next 7 days &mdash; one-time, urgent, outside normal hours, or recently added events
</p>

<!-- If no flagged events were found: -->
<!-- <p><em>No out-of-the-ordinary events on the calendar this week.</em></p> -->

<!-- Repeat for each flagged event, ordered chronologically -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60; border-radius: 3px;">
  <p style="margin: 0;"><strong>{Date, Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 0; font-size: 0.85em; color: #555;">
    &#9888;&#65039; <em>{reason this event is flagged as out-of-the-ordinary}</em>
  </p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.88em;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.88em;">{Brief description or attendee count if notable}</p>
</div>
<!-- End event block -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Move the draft to the Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `addLabelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — its ID is literally the string `"INBOX"`.
Do **not** call `list_labels` to look it up; use `"INBOX"` directly.

This moves the draft to the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- The action items list is the primary deliverable — make it as actionable as possible.
- If fewer than 10 genuine action items exist, show all of them; do not pad the list.
- If no qualifying emails were found, say so clearly; do not omit the section.
- If no out-of-the-ordinary calendar events were found, say so clearly; do not omit the section.
- Keep each action item's "Action" sentence to one clear, specific instruction.
- Action items must be concrete ("Reply to Alice by Friday confirming budget approval")
  not vague ("Follow up with Alice").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If multiple emails from the same sender relate to the same action, merge them
  into one action item and note the thread.

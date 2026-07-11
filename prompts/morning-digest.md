# Morning Email & Calendar Digest — Top 10 Action Items

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (i.e. the last week).
  Gmail query base: `newer_than:7d`
- **Calendar window**: today (the current date in Mountain Time), from
  `00:00:00` to `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 200 threads total).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

**For each qualifying email, identify**:
- Any explicit requests, questions, or asks directed at the account owner
- Deadlines or time-sensitive information
- Decisions required
- Follow-up actions needed

---

## Step 3 — Fetch today's calendar events and flag out-of-the-ordinary ones

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **flag an event as "out of the ordinary"** if ANY of the
following are true:
1. The event does NOT have a `recurringEventId` or `recurrence` field (one-time event).
2. The event was created or last modified within the past 48 hours (check `created` or `updated` timestamp).
3. The event has an unusually large number of attendees (10 or more).
4. The event is scheduled outside normal business hours (before 8:00 AM or after 6:00 PM Mountain Time).
5. The event includes a physical location or video conferencing link that differs from the account owner's usual meeting pattern.

Collect all flagged events. Also note events that are new additions to the calendar since yesterday.

---

## Step 4 — Build the Top 10 action items list

Review all emails and flagged calendar events collected above. Score each
potential action item by urgency and importance:

**Urgency signals** (raise the score):
- Explicit deadline mentioned (especially today or within 48 hours)
- Reply requested, question asked directly to owner
- Words like "urgent", "ASAP", "time-sensitive", "by end of day", "by tomorrow"
- Sender is a manager, client, or key stakeholder
- Email thread has multiple back-and-forth messages awaiting owner's reply

**Importance signals** (raise the score):
- Financial or legal implications
- Involves multiple people blocked on owner's action
- A calendar event today that requires preparation or a response

Rank and select the **top 10** action items. If there are fewer than 10, list
all of them. Number them 1 (most urgent/important) to 10.

For each action item, capture:
- **Rank**: 1–10
- **Action**: A concise, specific task (e.g., "Reply to Alice confirming budget approval by EOD")
- **Source**: Email subject / sender name OR calendar event title
- **Why it matters**: One sentence on urgency or impact
- **Deadline**: Explicit or inferred deadline, or "No hard deadline"

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
  e.g. `Morning Digest — Friday, April 25, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Email window: last 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 24px;">&#9989; Top 10 Action Items</h3>
<p style="color: #555; font-size: 0.9em; margin-top: -8px;">Ranked by urgency &amp; importance</p>

<!-- Repeat the block below for each action item (1–10) -->
<div style="margin-bottom: 14px; padding: 12px 14px; background: #f9f9f9; border-left: 4px solid #4A90D9; border-radius: 3px;">
  <p style="margin: 0 0 4px 0;">
    <span style="font-size: 1.1em; font-weight: bold; color: #4A90D9;">#1</span>
    &nbsp;<strong>{Concise action, e.g. "Reply to Alice confirming budget approval"}</strong>
  </p>
  <p style="margin: 2px 0 2px 0; color: #555; font-size: 0.9em;">
    <strong>Source:</strong> {Email subject — Sender Name | Calendar: Event Title}
  </p>
  <p style="margin: 2px 0 2px 0; color: #555; font-size: 0.9em;">
    <strong>Why:</strong> {One sentence on urgency or impact}
  </p>
  <p style="margin: 2px 0 0 0; color: #c0392b; font-size: 0.9em;">
    <strong>Deadline:</strong> {Explicit or inferred deadline, or "No hard deadline"}
  </p>
</div>
<!-- End action item block — repeat up to 10 times -->

<!-- If no action items were found, replace with: -->
<!-- <p><em>No action items found in the last 7 days.</em></p> -->

<!-- ====== OUT-OF-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events Today
</h3>
<p style="color: #555; font-size: 0.9em; margin-top: -8px;">
  One-time events, recently added meetings, unusual timing, or large gatherings
</p>

<!-- Repeat for each flagged calendar event -->
<div style="margin-bottom: 12px; padding: 10px 14px; background: #f0f7ff; border-left: 4px solid #27AE60; border-radius: 3px;">
  <p style="margin: 0 0 2px 0;"><strong>{Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 2px 0 2px 0; color: #555; font-size: 0.9em;">
    <strong>Why flagged:</strong> {e.g. "One-time event added yesterday" | "10+ attendees" | "Outside business hours"}
  </p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 2px 0 0 18px; color: #555; font-size: 0.9em;">&#128205; {Location or video link}</p>
  <p style="margin: 2px 0 0 18px; color: #555; font-size: 0.9em;">{Brief description if present}</p>
</div>
<!-- End calendar event block -->

<!-- If no out-of-the-ordinary events today, replace with: -->
<!-- <p><em>No out-of-the-ordinary calendar events scheduled for today.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &bull; Covers emails from the last 7 days</p>

</body>
</html>
```

### 6b — Label the draft for inbox delivery

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `addLabelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — its ID is literally the string `"INBOX"`.
Do **not** call `list_labels` to look it up; use `"INBOX"` directly.

This moves the draft to the Inbox so it arrives like a normal email rather
than sitting silently in the Drafts folder.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- The top 10 list is the primary deliverable — every item must be **specific and actionable**, not vague.
- If there are fewer than 10 genuine action items, list only what exists; do not pad with low-value items.
- Calendar "out of the ordinary" events are secondary; include them to provide today's context.
- If there are **no emails**, say so clearly.
- If there are **no out-of-the-ordinary calendar events**, say so clearly.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Deadlines must be specific when stated in the email ("by Friday", "EOD today") — do not invent deadlines.

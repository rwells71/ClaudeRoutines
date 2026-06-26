# Morning Email & Calendar Digest — Weekly Top 10

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (i.e. the last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days from today, in timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 3 pages max).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID (prioritize unread or action-oriented threads).

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with an `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch upcoming calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, identify **out-of-the-ordinary events** — flag an event if it
meets ANY of the following criteria:
1. It does NOT have a `recurringEventId` or `recurrence` field (genuinely one-time).
2. It starts before 8:00 AM or after 7:00 PM Mountain Time (unusual hours).
3. It spans more than 3 hours (unusually long).
4. Its title or description contains words suggesting urgency or importance:
   interview, board, emergency, deadline, legal, urgent, decision, all-hands,
   offsite, travel, flight, doctor, medical, surgery, contract, negotiation.
5. It has an unusual or out-of-office location (not a typical meeting room or video link).
6. It has more than 10 attendees (large gathering).

---

## Step 4 — Build the Top 10 Action List

Review ALL emails and flagged calendar events together. Create a single
prioritized numbered list of the **10 most important items** the account owner
needs to act on or be aware of.

### Ranking criteria (apply in order):
1. **Hard deadlines or time-sensitive requests** (responses due, meetings today, contracts expiring)
2. **Direct questions or requests from real people** (not automated systems)
3. **Financial or legal matters** (invoices, contracts, legal notices)
4. **Upcoming unusual calendar events** within 48 hours
5. **Replies owed** — threads where the owner was asked something and hasn't responded
6. **Important upcoming calendar events** more than 48 hours out
7. **Significant informational emails** that may require follow-up

### For each item in the list, include:
- **Source**: Email (with sender + subject) or Calendar (with event title + date/time)
- **What it is**: One sentence describing the situation
- **Action needed**: One specific, concrete action (e.g., "Reply to Alice by EOD confirming attendance" — not "Follow up")
- **Priority label**: 🔴 Urgent (today) | 🟡 Soon (this week) | 🔵 Awareness (no immediate action)

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
  e.g. `Morning Digest — Friday, April 25, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; Top 10 items from the last 7 days</p>

<!-- ====== TOP 10 ACTION LIST ====== -->
<h3 style="margin-top: 24px;">&#128203; Your Top 10 — Action Required</h3>

<!-- Repeat the block below for each of the 10 items, in priority order -->
<div style="margin-bottom: 16px; padding: 14px; background: #f9f9f9; border-left: 5px solid {priority_color}; border-radius: 3px;">
  <p style="margin: 0 0 4px 0;">
    <strong>#{number}</strong> &nbsp; {priority_emoji} <strong>{priority_label}</strong>
    &nbsp;&mdash;&nbsp; <span style="color: #555; font-size: 0.9em;">{source_type}: {source_detail}</span>
  </p>
  <p style="margin: 6px 0 4px 0;"><strong>{what_it_is}</strong></p>
  <p style="margin: 4px 0 0 0; color: #1a6b3c;">&#9654; <em>Action: {specific_action}</em></p>
</div>
<!-- End item block -->

<!-- Priority colors: 🔴 Urgent → border #E74C3C | 🟡 Soon → border #F39C12 | 🔵 Awareness → border #3498DB -->

<!-- ====== UNUSUAL CALENDAR EVENTS ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Unusual Calendar Events — Next 7 Days
</h3>

<!-- Repeat for each flagged unusual event -->
<div style="margin-bottom: 12px; padding: 10px; background: #fff8e1; border-left: 4px solid #F39C12;">
  <p style="margin: 0;"><strong>{Date}, {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 8px; color: #555; font-size: 0.9em;">Why flagged: {reason_flagged}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 8px; color: #666; font-size: 0.85em;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 8px; color: #666; font-size: 0.85em;">{Brief description if present}</p>
</div>
<!-- End event block -->

<!-- If no unusual events found: -->
<!-- <p><em>No unusual calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &mdash; Last 7 days of email + 7 days of calendar</p>

</body>
</html>
```

### 6b — Move the draft to Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

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

- The Top 10 list must have **exactly 10 items** (or fewer only if there are genuinely fewer than 10 actionable things across all emails and calendar events).
- Actions must be **concrete and specific** — never vague. Good: "Reply to John by Friday confirming the contract terms." Bad: "Follow up."
- If there are **no unusual calendar events**, say so clearly; do not omit the section.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Use Mountain Time for all times displayed.
- Group related emails (same thread) into a single Top 10 item, not separate items.

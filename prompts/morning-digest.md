# Morning Email & Calendar Digest — Top 10 Action Items

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (i.e. the last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window**: today through the next 7 days, in Mountain Time (`America/Denver`).
  - Start: today at `00:00:00`
  - End: 7 days from today at `23:59:59`

---

## Step 2 — Fetch emails from the last week

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to identify action items or deadlines, call `get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

From the qualifying emails, extract every **action item**, **deadline**, **decision needed**,
**pending reply**, or **important piece of information** that requires the account owner's
attention. Tag each item with the source email's sender and subject.

---

## Step 3 — Fetch calendar events for the next 7 days

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-06-14T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

For each event, determine whether it is **"out of the ordinary"** by checking if ANY of the following are true:
1. The event does NOT have a `recurringEventId` or `recurrence` field (genuinely one-time event).
2. The event was created or modified within the last 48 hours (recently added/changed).
3. The event has 3 or more attendees (unusual gathering).
4. The event has a location or video link that is different from the account owner's usual venues.
5. The event title or description contains keywords suggesting it is special or unusual (e.g., "interview", "review", "deadline", "urgent", "offsite", "travel", "flight", "conference", "presentation", "demo", "launch").
6. The event is outside normal business hours (before 8 AM or after 6 PM local time, or on a weekend).

Collect all "out of the ordinary" events and note WHY each one is flagged (e.g., "one-time event", "recently added", "5 attendees", "outside business hours").

---

## Step 4 — Build the Top 10 Action Items list

Combine ALL items from Steps 2 and 3 (email action items + flagged calendar events) into a single prioritized list.

**Rank by the following criteria (highest priority first):**
1. Hard deadlines or time-sensitive replies due today or tomorrow
2. Requests from important contacts (manager, key clients, executives, colleagues)
3. Financial, legal, or contractual matters
4. Upcoming out-of-the-ordinary calendar events happening today or tomorrow
5. Pending decisions or approvals that are blocking others
6. Other flagged calendar events later in the week
7. Emails that have been unanswered for more than 3 days
8. Everything else, ordered by estimated importance

Select the **top 10 items** from this ranked list. If there are fewer than 10, include all of them.

For each item in the final list, record:
- **Rank number** (1–10)
- **Type**: `Email Action` or `Calendar Event`
- **Title**: A concise, specific description of what needs to be done or attended (one line)
- **Source**: Sender + email subject (for emails) or event title + date/time (for calendar events)
- **Why it matters**: One sentence explaining urgency, importance, or why it is flagged
- **Suggested action**: One concrete next step (e.g., "Reply to Jane confirming the budget by EOD", "Block 30 min to prepare slides before the 2 PM demo")

---

## Step 5 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient addresses.
   The address that appears most frequently is almost certainly the account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of the other addresses in the "To:" fields.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 6 — Create and label the digest draft

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Sunday, June 14, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content for all `{placeholders}`.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  &#9728; Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Covering emails from the last 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#128203; Top 10 Items to Address</h3>

<!-- Repeat the block below for each of the top 10 items (rank 1 = most urgent) -->
<div style="margin-bottom: 16px; padding: 14px; background: #f9f9f9; border-left: 4px solid #4A90D9; border-radius: 2px;">
  <div style="display: flex; align-items: baseline; gap: 10px;">
    <span style="font-size: 1.4em; font-weight: bold; color: #4A90D9; min-width: 32px;">#{rank}</span>
    <!-- For Email Action items use border color #4A90D9; for Calendar Events use #27AE60 -->
    <span style="font-size: 0.75em; font-weight: bold; text-transform: uppercase; letter-spacing: 0.05em;
                 color: #fff; background: #4A90D9; padding: 2px 7px; border-radius: 10px;">
      {TYPE}
      <!-- Use background:#27AE60 for Calendar Event -->
    </span>
  </div>
  <p style="margin: 8px 0 4px 0; font-size: 1.05em; font-weight: bold;">{Title of action item}</p>
  <p style="margin: 0 0 4px 0; font-size: 0.85em; color: #555;">
    <strong>Source:</strong> {Sender + email subject, OR event title + date/time}
  </p>
  <p style="margin: 0 0 4px 0; font-size: 0.9em;">
    <strong>Why it matters:</strong> {One sentence on urgency or importance}
  </p>
  <p style="margin: 0; font-size: 0.9em; color: #1a6e2e;">
    &#10003; <strong>Next step:</strong> {Concrete suggested action}
  </p>
</div>
<!-- End action item block — repeat above div for each rank 1–10 -->

<!-- If fewer than 10 items exist, include only those found. -->
<!-- If no items at all, replace list with: -->
<!-- <p><em>No actionable items found in the last 7 days. Enjoy your morning!</em></p> -->

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR SECTION ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>
<p style="font-size: 0.85em; color: #666; margin-top: -8px;">
  One-time, recently added, large-group, after-hours, or otherwise notable events.
</p>

<!-- Repeat for each flagged calendar event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60; border-radius: 2px;">
  <p style="margin: 0;"><strong>{Day, Month Date} &bull; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 0; font-size: 0.85em; color: #888;">
    &#128204; <em>Flagged because: {reason — e.g. "one-time event", "added 4 hours ago", "6 attendees", "Sunday 7 PM"}</em>
  </p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">{Brief description or notes excerpt}</p>
</div>
<!-- End event block -->

<!-- If no out-of-the-ordinary events found: -->
<!-- <p><em>No unusual calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &bull; Top 10 items ranked by urgency &amp; importance</p>

</body>
</html>
```

### 6b — Move the draft to the Inbox

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

- **Always produce exactly 10 items** (or all items if fewer than 10 exist). Do not pad with low-value filler.
- Items must be **actionable** — not just informational. Each item must have a concrete next step.
- **Calendar events in the top 10** should only appear if they require preparation, a decision, or a response.
- Keep the "Why it matters" and "Next step" fields to one sentence each — no more.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If an email has already been replied to by the account owner, lower its priority significantly (it likely needs no further action).
- Group related items if they are truly the same issue (e.g., multiple follow-up emails about the same project count as one item).

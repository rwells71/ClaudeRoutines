# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the past 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days ahead, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the past week

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with an `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch unusual calendar events for the next 7 days

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-06-07T00:00:00-06:00`)
- `endTime`: 7 days from now at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **keep only events where ALL of the following are true**:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are genuinely one-time (unusual / out-of-the-ordinary) events. Drop
anything that belongs to a recurring series.

---

## Step 4 — Build the Top 10 Action Items list

Review all emails and unusual calendar events collected. Identify the most
important things the account owner needs to address. Score and rank them using
these criteria:

**Urgency signals (highest weight)**:
- Explicit deadlines or time-sensitive language ("by EOD", "urgent", "ASAP", "today", "tomorrow")
- Emails awaiting a reply from the owner
- Meeting invitations needing a response
- Unusual calendar events happening today or tomorrow

**Importance signals (medium weight)**:
- Emails from known important contacts (managers, clients, direct reports)
- Financial matters, contracts, legal documents
- Travel, reservations, or logistics that need confirmation

**Informational (lowest weight)**:
- FYI emails with no action needed
- Recurring status reports

Select the top 10 items. If fewer than 10 clearly actionable items exist,
include the most important informational items to reach 10.

For each item in the top 10, provide:
- A **priority rank** (1 = most urgent/important)
- A **one-line action** (e.g. "Reply to Alice confirming the 2 PM Thursday meeting")
- The **source**: sender name + subject line, OR calendar event title + date/time
- A **deadline or date** if applicable (e.g. "Due today", "Event: Thu Jun 12 at 9 AM MT")

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
  e.g. `Morning Digest — Sunday, June 7, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Email window: past 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 24px;">&#9989; Your Top 10 &mdash; Things to Address</h3>

<table style="width:100%; border-collapse: collapse; font-size: 0.95em;">
  <thead>
    <tr style="background: #4A90D9; color: white;">
      <th style="padding: 8px; text-align: center; width: 36px;">#</th>
      <th style="padding: 8px; text-align: left;">Action</th>
      <th style="padding: 8px; text-align: left; width: 200px;">Source</th>
      <th style="padding: 8px; text-align: left; width: 130px;">Due / When</th>
    </tr>
  </thead>
  <tbody>
    <!-- Repeat for each of the top 10 items; alternate row background -->
    <!-- Odd rows: background #f9f9f9 | Even rows: background #ffffff -->
    <tr style="background: #f9f9f9;">
      <td style="padding: 8px; text-align: center; font-weight: bold; color: #4A90D9;">1</td>
      <td style="padding: 8px;">{one-line action}</td>
      <td style="padding: 8px; color: #555; font-size: 0.9em;">{sender name / event title}</td>
      <td style="padding: 8px; color: #c0392b; font-size: 0.9em; font-weight: bold;">{deadline or date}</td>
    </tr>
    <!-- ... repeat rows 2–10 ... -->
  </tbody>
</table>

<!-- ====== UNUSUAL CALENDAR EVENTS ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Unusual Calendar Events &mdash; Next 7 Days
</h3>

<!-- Repeat the block below for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Day of Week}, {Month} {Day} &bull; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include the lines below if the data is present -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{One-line description excerpt}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events found, replace blocks with: -->
<!-- <p><em>No unusual calendar events in the next 7 days.</em></p> -->

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

This moves the draft to the Inbox so it arrives like a normal email rather
than sitting silently in the Drafts folder.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- Always include all 10 items; use lower-priority informational items if needed to reach 10.
- Action descriptions must be concrete ("Reply to Alice confirming the meeting time"), not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If there are **no unusual calendar events**, say so clearly; do not omit the section.
- Calendar events already in the Top 10 list may also appear in the calendar section — that duplication is intentional and helpful.

# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (i.e. the last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window**: today (the current date in Mountain Time), from
  `00:00:00` to `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
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

## Step 3 — Fetch today's out-of-the-ordinary calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **keep only events where ALL of the following are true**:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are genuinely one-time, out-of-the-ordinary events. Drop anything that
belongs to a recurring series (daily standups, weekly team meetings, etc.).

---

## Step 4 — Compile the Top 10 Items to Address

Review all emails and calendar events collected above. Identify the **10 most
important items** requiring the account owner's attention today. Rank them by
urgency and importance — deadlines, direct requests, decisions needed, and
one-time events outrank general FYIs.

For each item in the list:
- Assign a rank (1 = most urgent)
- Write a single clear action sentence (e.g., "Reply to Jane confirming budget approval by EOD")
- Note the source: the sender name / email subject for emails, or event title for calendar items
- Note any deadline or time constraint if apparent

If there are fewer than 10 actionable items, list only what exists — do not pad
with trivial items.

---

## Step 5 — Summarize email details

Group by sender (use the sender's display name and email address as the heading).
For each sender, list every email they sent in the window. For each email:
- Subject line
- 2–4 bullets covering the key points
- A separate "Action Items" section with concrete, specific tasks required of the reader (omit this section if there are none)

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

## Step 7 — Create and label the digest draft

### 7a — Create the draft

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
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 24px; color: #c0392b;">&#9989; Top 10 Items to Address Today</h3>

<ol style="padding-left: 20px;">
  <!-- Repeat <li> block for each item, ranked 1–10 -->
  <li style="margin-bottom: 10px; padding: 8px; background: #fff8f8; border-left: 4px solid #c0392b;">
    <strong>{Action sentence}</strong><br>
    <span style="color: #666; font-size: 0.9em;">Source: {Sender / Subject or Event Title}</span>
    <!-- Only include deadline line if a deadline exists -->
    <span style="color: #c0392b; font-size: 0.9em;"> &mdash; &#9201; {Deadline or time constraint}</span>
  </li>
  <!-- End item -->
</ol>

<!-- If fewer than 10 items exist, list only what's there -->
<!-- If no actionable items at all: -->
<!-- <p><em>No actionable items found in the last 7 days.</em></p> -->

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events Today
</h3>

<!-- Repeat for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events today: -->
<!-- <p><em>No out-of-the-ordinary events scheduled for today.</em></p> -->

<!-- ====== EMAIL DETAIL SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128139; Email Detail &mdash; Last 7 Days
</h3>

<!-- Repeat the block below for each unique sender -->
<div style="margin-bottom: 20px; padding: 12px; background: #f9f9f9; border-left: 4px solid #4A90D9;">
  <h4 style="margin: 0 0 6px 0;">{Sender Name} &lt;{sender@example.com}&gt;</h4>
  <p style="margin: 0 0 4px 0;"><strong>Subject:</strong> {email subject}</p>
  <ul style="margin: 4px 0 0 0;">
    <li><strong>Key Points:</strong>
      <ul>
        <li>{point 1}</li>
        <li>{point 2}</li>
      </ul>
    </li>
    <!-- Only include if there are action items -->
    <li><strong>Action Items:</strong>
      <ul>
        <li>{action item}</li>
      </ul>
    </li>
  </ul>
</div>
<!-- End sender block -->

<!-- If no qualifying emails were found: -->
<!-- <p><em>No emails received in the last 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 7b — Label the draft for inbox delivery

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

- The **Top 10 list is the most important section** — make it specific and actionable.
- If there are **no emails**, say so clearly; do not omit the section.
- If there are **no out-of-the-ordinary calendar events**, say so clearly; do not omit the section.
- Keep email summaries concise: maximum 4 bullets per email.
- Action items must be concrete ("Reply to Alice confirming the meeting time")
  not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If multiple emails from the same sender arrive in the window, group them all
  under one sender heading with separate subject/key-points/action-items blocks.

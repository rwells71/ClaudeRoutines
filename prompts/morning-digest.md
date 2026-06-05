# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the past 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today (the current date in Mountain Time), from
  `00:00:00` to `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

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
message with a `List-Unsubscribe` header. Include everything else —
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

These are genuinely one-time or out-of-the-ordinary events. Drop anything that
belongs to a recurring series.

---

## Step 4 — Build the Top 10 Priority List

Analyze all emails collected in Step 2. Identify up to 10 items the account
owner most needs to act on or be aware of today. Rank them by urgency and
importance — consider:
- Explicit deadlines or time-sensitive language ("by Friday", "ASAP", "urgent")
- Direct questions or requests addressed to the owner
- Replies still needed or decisions pending
- Financial, legal, or contract-related matters
- Messages from important senders (colleagues, clients, direct reports, family)
- Any non-recurring calendar event today that requires preparation

Format each item as a single line:
`{Rank}. {Sender/Source} — {Concise action or awareness item} ({Date of email or event})`

Example:
`1. Alice Smith — Reply confirming budget approval before 3 PM today (Jun 5)`

---

## Step 5 — Summarize emails

Group by sender (use the sender's display name and email address as the heading).
For each sender, list every email they sent in the window. For each email:
- Subject line
- 2–4 bullets covering the key points
- A separate "Action Items" section with concrete, specific tasks required of
  the reader (omit this section if there are none)

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

<!-- ====== TOP 10 SECTION ====== -->
<h3 style="margin-top: 28px;">&#128204; Top 10 Items to Address Today</h3>

<ol style="padding-left: 20px; line-height: 1.8;">
  <!-- Repeat one <li> per ranked item, up to 10 -->
  <li><strong>{Sender/Source}</strong> &mdash; {Concise action or awareness item} <span style="color:#888;">({Date})</span></li>
</ol>

<!-- If no actionable items, replace list with: -->
<!-- <p><em>No action items identified for today.</em></p> -->

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

<!-- If no non-recurring events today, replace event blocks with: -->
<!-- <p><em>No out-of-the-ordinary calendar events today.</em></p> -->

<!-- ====== EMAIL DETAIL SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">&#128139; Email Detail &mdash; Last 7 Days</h3>

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

<!-- If no qualifying emails were found, replace sender blocks with: -->
<!-- <p><em>No emails received in the last 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 7b — Label the draft for easy retrieval

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

- The **Top 10 list** is the most important section — place it first and make
  it scannable at a glance.
- If there are **no emails**, say so clearly; do not omit the section.
- If there are **no non-recurring calendar events**, say so clearly; do not omit the section.
- Keep email summaries concise: maximum 4 bullets per email.
- Action items must be concrete ("Reply to Alice confirming the meeting time")
  not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If multiple emails from the same sender arrive in the window, group them all
  under one sender heading with separate subject/key-points/action-items blocks.

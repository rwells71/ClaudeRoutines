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
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch calendar events

### 3a — Fetch today's events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601, e.g. `2026-06-12T00:00:00-06:00`)
- `endTime`: today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

### 3b — Identify "out-of-the-ordinary" events

From the full list of today's events, flag an event as **out-of-the-ordinary** if it meets
**at least one** of the following criteria:

1. It does NOT have a `recurringEventId` or `recurrence` field (one-time event).
2. It is scheduled outside normal business hours (before 7:00 AM or after 7:00 PM MT).
3. It has an unusual duration — either very short (≤ 10 minutes) or very long (≥ 4 hours).
4. It has a location or video link that differs from the account owner's usual meeting platform.
5. It involves 5 or more attendees.
6. It was added or modified within the last 48 hours (check `created` or `updated` timestamp).
7. Its title contains words suggesting urgency: "urgent", "emergency", "critical", "ASAP", "crisis".

Keep the full list of today's events visible for the email. **Bold-flag** the
out-of-the-ordinary ones in the digest so they stand out.

---

## Step 4 — Build the Top 10 Priority List

From all the emails and calendar events collected, identify the **10 most important items
the account owner needs to act on today**. Rank them by urgency and impact:

**Ranking criteria (highest to lowest):**
1. Urgent requests with explicit deadlines today or tomorrow
2. Replies awaited from the account owner (someone is blocked waiting on them)
3. Time-sensitive financial, legal, or compliance matters
4. Out-of-the-ordinary calendar events requiring preparation or a decision
5. Action items from important senders (manager, client, executive, legal)
6. Follow-ups that are overdue (thread started >3 days ago with no reply from owner)
7. Meeting prep needed for events today
8. Anything marked important/starred or with urgent subject keywords
9. General replies that should happen within 24–48 hours
10. Low-priority but easy wins (< 2 min to handle)

For each item in the top 10, write:
- **Rank number** (1–10)
- **Type**: Email or Calendar
- **One-line summary**: what needs to happen and why it matters
- **Source**: sender name + subject (email), or event title + time (calendar)

---

## Step 5 — Summarize emails in detail

Group by sender (use the sender's display name and email address as the heading).
For each sender, list every email they sent in the window. For each email:
- Subject line
- 2–4 bullets covering the key points
- A separate "Action Items" section with concrete, specific tasks required of the reader
  (omit this section if there are none)

---

## Step 6 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Use `richardlwells@gmail.com` as the primary address.
2. If that address does not appear in any "To:" field, fall back to the address
   that appears most frequently across all "To:" fields.

Store this address as `{owner_email}`.

---

## Step 7 — Create and deliver the digest

### 7a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Friday, June 12, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 720px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; covering emails from the last 7 days</p>

<!-- ====== TOP 10 PRIORITY LIST ====== -->
<h3 style="margin-top: 28px; background: #4A90D9; color: white; padding: 10px 14px; border-radius: 4px;">
  &#128073; Top 10 Priority Items for Today
</h3>

<ol style="padding-left: 20px;">
  <!-- Repeat for each of the top 10 items -->
  <li style="margin-bottom: 14px;">
    <span style="background: #e8f0fe; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; font-weight: bold; color: #4A90D9;">{TYPE: Email | Calendar}</span>
    &nbsp;<strong>{One-line summary of what needs to happen}</strong><br/>
    <span style="color: #555; font-size: 0.9em;">&#128188; {Sender Name} &mdash; <em>{Subject or Event Title}</em></span>
  </li>
  <!-- End item -->
</ol>

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Today's Calendar Events
</h3>

<!-- Repeat for each event today -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;">
    <strong>{Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}
    <!-- Add the badge below ONLY for out-of-the-ordinary events -->
    &nbsp;<span style="background: #ff6b35; color: white; padding: 1px 6px; border-radius: 3px; font-size: 0.75em;">&#9888; OUT OF ORDINARY</span>
  </p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Why flagged as out-of-ordinary, if applicable}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no events today: -->
<!-- <p><em>No calendar events scheduled for today.</em></p> -->

<!-- ====== EMAIL DETAIL SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128139; Email Details &mdash; Last 7 Days
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

### 7b — Deliver to inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — use the string `"INBOX"` directly, do **not**
call `list_labels` to look it up.

This moves the draft to the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.

---

## Important rules

- Always produce **exactly 10 items** in the priority list; if fewer than 10 actionable
  items exist, fill remaining slots with the most relevant informational items from the week.
- Keep email summaries concise: maximum 4 bullets per email.
- Action items must be concrete ("Reply to Alice by EOD confirming the 3 PM meeting")
  not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If multiple emails from the same sender arrive in the window, group them all
  under one sender heading with separate subject/key-points/action-items blocks.
- If there are **no emails**, say so clearly; do not omit the section.
- If there are **no calendar events**, say so clearly; do not omit the section.

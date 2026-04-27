# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 24-hour period ending right now.
  Gmail query: `newer_than:1d`
- **Calendar window**: today (the current date in Mountain Time), from
  `00:00:00` to `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:1d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail with no action required: pure marketing
emails, newsletters, and messages from `noreply@`, `no-reply@`,
`donotreply@`, or `notifications@` senders that contain an
`List-Unsubscribe` header and carry zero action items.

**Keep** everything else — transactional mail, human-sent messages,
financial alerts, security notices, school/work communications, and any
system alert that signals a real-world issue (failed payment, air-quality
alert, security breach, etc.).

---

## Step 3 — Fetch today's non-recurring calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601 with offset,
  e.g. `2026-04-27T00:00:00-06:00`)
- `endTime`: today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

**Keep only events where ALL of the following are true:**
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are genuinely one-time events. Drop anything that belongs to a
recurring series.

If you need more detail about a specific event, call `get_event`.

---

## Step 4 — Summarize

### 4a — Emails: group by sender

For each **unique sender** (display name + email address), collect every
email they sent within the window. Render one block per sender:

- **Sender heading**: display name and email address
- For each email from that sender:
  - Subject line
  - 2–4 bullets covering the key points
  - **Action Items** sub-section listing concrete, specific tasks required
    of the reader (omit this sub-section entirely if there are none)

### 4b — Calendar: list non-recurring events

For each qualifying event:
- Date and time range in Mountain Time (e.g. "9:00 AM – 10:00 AM MT")
- Event title
- Location or video link (if present)
- One-line description excerpt (if present)

---

## Step 5 — Determine the account owner's email address

Use the following strategy, stopping at the first successful result:

1. Look at the **"To:"** field of every fetched email. Collect all
   recipient addresses. The most frequently appearing address is almost
   certainly the owner's — use that.
2. On a tie, prefer the address whose domain matches the majority of other
   "To:" addresses.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Monday, April 27, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time</p>

<!-- ====== EMAIL SECTION ====== -->
<h3 style="margin-top: 28px;">&#128139; Email Summary &mdash; Last 24 Hours</h3>

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

<!-- If no qualifying emails, replace all sender blocks with: -->
<!-- <p><em>No emails received in the last 24 hours.</em></p> -->

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Non-Recurring Calendar Events Today
</h3>

<!-- Repeat for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events, replace all event blocks with: -->
<!-- <p><em>No one-time calendar events scheduled for today.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Deliver the digest to the Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `addLabelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — its string value is literally `"INBOX"`.
Do **not** call `list_labels` to look it up.

This moves the draft into the Inbox so it arrives like a normal email
rather than sitting silently in Drafts.

> **Note**: The Gmail MCP integration does not expose a send API. Inbox
> delivery is achieved by applying the INBOX label to the draft. If a
> `send_message` or `send_draft` tool becomes available, prefer that.

---

## Important rules

- If there are **no qualifying emails**, say so; do not omit the section.
- If there are **no non-recurring calendar events**, say so; do not omit
  the section.
- Maximum 4 bullets per email.
- Action items must be concrete ("Reply to Alice confirming the 3 PM call")
  not vague ("Follow up").
- Multiple emails from the same sender go under one sender heading with
  separate subject/key-points/action-items blocks per email.
- Strip tracking pixels and HTML boilerplate before summarizing.
- Never include raw HTML or JSON in the digest body.

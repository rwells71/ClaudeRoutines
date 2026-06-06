# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time windows

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days from now, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (cap at 150 threads total).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to assess action items, call `get_thread` with that
thread's ID (limit to the 30 threads that look most action-requiring).

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch upcoming non-recurring calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601, e.g. `2026-06-06T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, **keep only events that are "out of the ordinary"** — meaning
ALL of the following are true:
1. The event does NOT have a `recurringEventId` field (not part of a recurring series).
2. The event does NOT have a `recurrence` field.
3. The event is NOT an all-day event that looks like a standard holiday or birthday.

These are genuinely one-time, notable events. Drop everything from recurring series.

---

## Step 4 — Build the Top 10 action items list

Review all emails collected. For each email thread, identify concrete tasks
or decisions required of the reader. Score each by urgency and importance.

**Select the top 10 most important items** the owner needs to address.
Rank them 1 (most urgent/important) through 10.

For each item include:
- A concise one-line description of the action ("Reply to John confirming Thursday meeting")
- The sender name and email
- The email subject
- Due date or urgency signal if mentioned

If fewer than 10 actionable items exist, include all of them and note the total.

---

## Step 5 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. The address that appears
   most frequently is almost certainly the account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of
   the other "To:" addresses.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 6 — Create and label the digest draft

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Friday, June 6, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Emails from the last 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#9989; Top 10 Items to Address</h3>

<!-- If no actionable emails, replace list with: -->
<!-- <p><em>No action items found in the last 7 days.</em></p> -->

<ol style="padding-left: 20px;">
  <!-- Repeat <li> block for each of the top 10 items, ranked 1–10 -->
  <li style="margin-bottom: 14px;">
    <strong>{One-line action description}</strong><br/>
    <span style="color: #555; font-size: 0.9em;">
      From: {Sender Name} &lt;{sender@example.com}&gt; &bull;
      Subject: <em>{email subject}</em>
      <!-- Only include if urgency/due date is present: -->
      &bull; <span style="color: #c0392b;">Due: {date or urgency}</span>
    </span>
  </li>
  <!-- End item -->
</ol>

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events — Next 7 Days
</h3>

<!-- Repeat for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Date}, {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events in the next 7 days, replace event blocks with: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

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

- Rank action items by urgency first, then importance. Time-sensitive items
  (deadlines mentioned, replies awaited, meetings upcoming) rank highest.
- Action items must be concrete ("Reply to Alice confirming Thursday at 2pm")
  not vague ("Follow up with Alice").
- If fewer than 10 actionable items exist, list all and note the count.
- Calendar section covers the next 7 days, not just today.
- Keep calendar event descriptions to one line.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.

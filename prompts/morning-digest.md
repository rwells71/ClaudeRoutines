# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (the last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days from now in Mountain Time,
  timezone `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates -from:calendar-notification@google.com -from:noreply-travel@google.com`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip automatically** (do not include in action item analysis):
- Marketing emails, newsletters, promotional offers
- Messages from `noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses
- Any message with a `List-Unsubscribe` header
- Google Voice text message notifications (from addresses ending in `@txt.voice.google.com` or sender `voice-noreply@google.com`)
- Google Calendar notifications (from `calendar-notification@google.com`)
- Automated weekly/daily reports (Qustodio, Canvas, FamilySearch, etc.)
- Loyalty/rewards program emails (hotel points, airline miles, etc.)

**Include**: human-sent emails, emails that need a reply, emails requiring a decision,
financial emails needing action, and any email where someone is waiting on the account owner.

---

## Step 3 — Fetch upcoming "out of the ordinary" calendar events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601, e.g. `2026-06-08T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, **keep only events that are "out of the ordinary"** — events where ALL of the following are true:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are one-time events. Drop anything that belongs to a recurring series.

---

## Step 4 — Generate the Top 10 Action Items list

### 4a — Identify actionable items from emails

From all non-skipped emails gathered in Step 2, identify every item requiring action from the account owner. Examples:
- A reply is needed
- A decision or approval is required
- Information needs to be sent
- A transaction needs approval or follow-up
- An RSVP is pending
- A follow-up was promised

### 4b — Score and rank

Score each actionable item on three dimensions (0–5 each):
- **Urgency**: Is there a clear deadline or time pressure?
- **Impact**: Does this affect finances, work, family, health, or important relationships?
- **Waiting on me**: Is someone explicitly waiting for the account owner's response?

Sort by total score (highest first). Take the top 10. If fewer than 10 email action items
exist, fill remaining slots with calendar event preparations that need action
(e.g., "Prepare for [event] happening on [date]").

---

## Step 5 — Determine the account owner's email address

Use the following strategy, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient addresses.
   The address that appears most frequently is almost certainly the account owner's — use that.
2. If there is a tie, prefer the address whose domain matches the majority of other "To:" addresses.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Monday, June 8, 2026`

**`htmlBody`**: Use the template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Email summary covers the past 7 days</p>

<!-- ====== OUT OF THE ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 24px; color: #E67E22;">&#128680; Out-of-the-Ordinary Events This Week</h3>

<!-- Repeat for each one-time event found in Step 3 -->
<div style="margin-bottom: 12px; padding: 10px; background: #FFF8EE; border-left: 4px solid #E67E22;">
  <p style="margin: 0;"><strong>{Day of week, Month Day} &mdash; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Include the lines below only if the data is present -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no one-time events exist in the next 7 days: -->
<!-- <p><em>No out-of-the-ordinary events in the next 7 days.</em></p> -->

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">&#9989; Top 10 Action Items</h3>
<p style="color: #666; font-size: 0.9em; margin-top: 0;">Ranked by urgency &bull; impact &bull; waiting on you &bull; Past 7 days of email</p>

<!-- Repeat for each of the top 10 items, numbered 1–10 -->
<div style="margin-bottom: 16px; padding: 12px; background: #f9f9f9; border-left: 4px solid #4A90D9;">
  <p style="margin: 0 0 4px 0;"><strong>#{rank}. {Specific action required}</strong></p>
  <p style="margin: 0 0 4px 0; font-size: 0.85em; color: #777;">
    From: {Sender Name} &lt;{sender@email}&gt; &bull; &ldquo;{Email Subject}&rdquo; &bull; {Date received}
  </p>
  <p style="margin: 0; color: #333;">{1–2 sentence description: what needs to be done and why it matters}</p>
</div>
<!-- End action item -->

<!-- If fewer than 10 items exist, show what is available and note the count -->

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

This moves the draft to the Inbox so it appears like a received email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If `send_message` or `send_draft` becomes available in a future version,
> prefer that over `label_message`.

---

## Important rules

- The Top 10 list must be **ranked by priority** — most urgent/impactful first.
- Each action item title must be **specific**: "Reply to Josh Clarke re: Trek permission forms" not "Follow up."
- Descriptions must say **exactly what needs to be done** in 1–2 sentences.
- If fewer than 10 action items come from email, supplement with calendar prep tasks.
- Skip all automated mail, Google Voice texts, calendar notifications, and promotions.
- Never include raw HTML or JSON in the digest body.
- Both sections (calendar events and top 10 list) must always appear, even if empty.

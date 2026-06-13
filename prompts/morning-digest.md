# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window**: today (the current date in Mountain Time), from
  `00:00:00` to `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 200 threads maximum).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID — prioritize threads with unclear snippets
or those that appear to require a response.

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

These are genuinely one-time ("out of the ordinary") events. Drop anything
that belongs to a recurring series.

---

## Step 4 — Build the Top 10 Action Items list

Review ALL emails collected in Step 2. For each email that requires the
account owner to take action, note:
- What action is needed
- Who it is from
- How urgent/important it appears (deadline mentioned, tone, sender seniority, etc.)
- How old the email is

Rank all identified action items from most to least important and select
the **top 10**. Factors that increase priority:
1. Explicit deadline or time-sensitive language ("by Friday", "ASAP", "urgent")
2. Direct question or request requiring a reply
3. Financial, legal, or health-related matters
4. Email is from a known colleague, client, or manager (as opposed to automated systems)
5. The thread is recent (last 24 h beats last 7 days)

If fewer than 10 actionable items are found, include all of them.
If there are no actionable items from email, state that clearly.

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

## Step 6 — Create and label the digest draft

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
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Email lookback: last 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#9989; Top 10 Action Items</h3>
<p style="color: #555; font-size: 0.9em; margin-top: -8px;">Ranked by urgency and importance from your last 7 days of email.</p>

<ol style="padding-left: 20px;">

  <!-- Repeat the <li> block below for each of the top 10 action items (highest priority first) -->
  <li style="margin-bottom: 16px; padding: 10px 12px; background: #f9f9f9; border-left: 4px solid #4A90D9; list-style-position: outside;">
    <strong>{Concrete action required}</strong><br/>
    <span style="font-size: 0.88em; color: #555;">
      From: {Sender Name} &lt;{sender@example.com}&gt; &bull;
      Subject: <em>{email subject}</em> &bull;
      Received: {relative time, e.g. "2 days ago" or "Today at 8:42 AM MT"}
    </span>
    <!-- Only include the deadline line if a deadline was mentioned -->
    <br/><span style="font-size: 0.85em; color: #c0392b;">&#9201; Deadline: {deadline}</span>
  </li>
  <!-- End action item -->

</ol>

<!-- If no actionable emails found, replace the <ol> with: -->
<!-- <p><em>No action items found in the last 7 days of email.</em></p> -->

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Events Today
</h3>
<p style="color: #555; font-size: 0.9em; margin-top: -8px;">
  One-time (non-recurring) events on your calendar for today.
</p>

<!-- Repeat for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events today, replace event blocks with: -->
<!-- <p><em>No one-time calendar events scheduled for today.</em></p> -->

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

- The top-10 list must contain **specific, concrete action items** — not
  vague summaries. Good: "Reply to Alice confirming attendance at the June 18
  board meeting." Bad: "Follow up with Alice."
- Rank items correctly: time-sensitive items with explicit deadlines go first.
- If fewer than 10 actionable items exist, list all of them and note the total.
- If there are **no non-recurring calendar events**, say so clearly; do not
  omit the section.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Do not include the deadline line in an action item if no deadline was mentioned.

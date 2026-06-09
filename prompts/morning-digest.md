# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the last 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window for unusual events**: today through 7 days from now, in
  Mountain Time, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 150 threads maximum).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch calendar events for the next 7 days

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset,
  e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, identify **out-of-the-ordinary** events — those matching
one or more of these criteria:

1. **Non-recurring**: the event does NOT have a `recurringEventId` field AND
   does NOT have a `recurrence` field (genuine one-time events).
2. **Unusual timing**: starts before 7:00 AM or after 7:00 PM Mountain Time,
   OR falls on a Saturday or Sunday.
3. **New/recently added**: the event's `created` or `updated` timestamp is
   within the last 48 hours.
4. **Long duration**: the event is 3 or more hours long (excluding all-day
   events, which are expected to be long).
5. **New attendees**: the event has attendees and at least one attendee email
   domain has not appeared in any other event this week (a genuinely new
   contact or external party).
6. **Out-of-office or travel**: the event summary contains keywords like
   "flight", "travel", "out of office", "OOO", "hotel", "conference",
   "offsite", "away", or similar.

If an event meets none of these criteria, omit it from the digest.

---

## Step 4 — Build the Top 10 Priority Action List

Review ALL emails collected in Step 2 AND all out-of-the-ordinary calendar
events from Step 3. Identify every item that requires the account owner to
**do something** — reply, decide, approve, prepare, follow up, attend, review, etc.

Rank these items by urgency and importance using the following tiebreakers
(in order):
1. Hard deadline or event today or tomorrow → highest priority
2. Request from a person (not a system) waiting on a reply
3. Financial, legal, or contractual matter
4. Upcoming deadline within the next 7 days
5. Everything else

Select the **top 10** items and number them 1–10.

For each item write:
- **Item number and one-line title** (e.g. "1. Reply to Jane re: contract review")
- **Why it matters / urgency**: one sentence
- **Suggested action**: one concrete sentence (e.g. "Reply by EOD confirming the
  Tuesday meeting time")

If fewer than 10 actionable items exist, list all of them and stop — do not
pad with filler.

---

## Step 5 — Summarize emails by sender

Group by sender (use the sender's display name and email address as the heading).
For each sender, list every email they sent in the window. For each email:
- Subject line
- 2–4 bullets covering the key points
- A separate "Action Items" section with concrete, specific tasks required of
  the reader (omit this section if there are none)

---

## Step 6 — Summarize out-of-the-ordinary calendar events

For each event flagged in Step 3:
- Start and end time (Mountain Time, e.g. "9:00 AM – 10:00 AM MT") or "All Day"
- Event title
- Why it is flagged as out-of-the-ordinary (one short phrase, e.g.
  "Non-recurring", "Unusual time — Saturday 8 PM", "New external attendee")
- Location or video link (if present)
- Attendees (display names or email addresses, omit if just the owner)
- One-line description excerpt (if present)

---

## Step 7 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient
   addresses. The address that appears most frequently is almost certainly the
   account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of
   the other addresses in the "To:" fields.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 8 — Create and deliver the digest

### 8a — Create the draft

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
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; covering the last 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px; color: #C0392B;">&#128205; Top 10 Priority Action Items</h3>
<p style="color: #666; font-size: 0.9em;">Ranked by urgency and importance across email and calendar.</p>

<ol style="padding-left: 20px;">
  <!-- Repeat <li> block for each of the top 10 items (or fewer if less than 10 exist) -->
  <li style="margin-bottom: 14px;">
    <strong>{One-line title}</strong><br/>
    <span style="color: #555;">{Why it matters / urgency}</span><br/>
    <span style="color: #27AE60;"><em>&#10003; {Suggested action}</em></span>
  </li>
  <!-- End item block -->
</ol>

<!-- ====== OUT-OF-ORDINARY CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each flagged calendar event -->
<div style="margin-bottom: 12px; padding: 10px; background: #fff8e1; border-left: 4px solid #F39C12;">
  <p style="margin: 0;"><strong>{Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 18px; color: #E67E22; font-size: 0.85em;">&#9888; {Why flagged}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">&#128101; {Attendees}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no flagged calendar events, replace event blocks with: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<!-- ====== EMAIL SUMMARY SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128139; Full Email Summary &mdash; Last 7 Days
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

<!-- If no qualifying emails were found, replace sender blocks with: -->
<!-- <p><em>No emails received in the last 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 8b — Deliver the digest to the Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — its ID is literally the string `"INBOX"`.
Do **not** call `list_labels` to look it up; use `"INBOX"` directly.

This moves the draft to the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- The **Top 10 list must appear first** in the email — it is the most
  important section.
- If there are **fewer than 10** actionable items, list all of them; do not
  invent filler.
- If there are **no emails**, say so clearly; do not omit the section.
- If there are **no out-of-the-ordinary calendar events**, say so clearly; do
  not omit the section.
- Keep email summaries concise: maximum 4 bullets per email.
- Action items must be concrete ("Reply to Alice confirming the meeting time")
  not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If multiple emails from the same sender arrive in the window, group them all
  under one sender heading with separate subject/key-points/action-items blocks.

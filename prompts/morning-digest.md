# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: the next 7 days starting today, from
  `00:00:00` today to `23:59:59` seven days from now, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (max 3 pages / 150 threads).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID (prioritize threads that look actionable
— requests, questions, approvals, deadlines).

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Extract top 10 action items from email

Review all collected emails and extract the **top 10 most important action
items** the account owner needs to address. Rank them by urgency and importance
using this priority order:

1. **Deadlines** — items with explicit or implied due dates
2. **Direct requests** — emails where someone is waiting on a reply or decision
3. **Approvals / sign-offs** — things pending the owner's approval
4. **Follow-ups** — items promised or expected from previous conversations
5. **FYIs requiring acknowledgement** — important info that needs a response

For each action item:
- A concise title (≤ 12 words)
- The sender name and email
- The email subject that prompted it
- One sentence describing what needs to be done and why it matters
- Urgency tag: 🔴 Urgent · 🟡 This week · 🟢 When possible

If there are fewer than 10 genuine action items, list only the real ones —
do not pad the list with low-priority items.

---

## Step 4 — Fetch calendar events for the next 7 days

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **keep only events that meet at least one of the following
"out of the ordinary" criteria**:

1. **Non-recurring** — the event does NOT have a `recurringEventId` or `recurrence` field.
2. **Unusual time** — starts before 8:00 AM or after 7:00 PM Mountain Time.
3. **New / unfamiliar attendees** — attendees whose email domain is not one the owner regularly sees (use your best judgment from the email data collected in Step 2).
4. **Off-site / travel** — has a location that is not a home address, virtual meeting link, or blank.
5. **Out-of-office / travel blocks** — eventType is `OUT_OF_OFFICE` or the title contains travel-related keywords (flight, hotel, conference, trip, travel).
6. **Long or all-day events** — duration ≥ 4 hours, or allDay events that appear unusual (not birthdays, not standard holidays).
7. **High attendee count** — more than 10 attendees.

Drop routine recurring meetings (daily standups, weekly 1:1s, etc.) that do not
match any of the above criteria.

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
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Email window: last 7 days &bull; Calendar window: next 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#9989; Top 10 Email Action Items</h3>
<p style="color: #555; font-size: 0.9em;">Ranked by urgency. Click a sender name to open Gmail.</p>

<ol style="padding-left: 20px;">

  <!-- Repeat the block below for each action item (up to 10) -->
  <li style="margin-bottom: 16px; padding: 10px; background: #f9f9f9; border-left: 4px solid #4A90D9; list-style-position: outside;">
    <strong>{Action Item Title}</strong> {urgency emoji}<br/>
    <span style="color: #555; font-size: 0.9em;">From: {Sender Name} &lt;{sender@example.com}&gt;</span><br/>
    <span style="color: #555; font-size: 0.9em;">Re: <em>{Email Subject}</em></span><br/>
    <span style="margin-top: 4px; display: block;">{One-sentence description of what to do and why it matters}</span>
  </li>
  <!-- End action item -->

</ol>

<!-- If no action items, replace list with: -->
<!-- <p><em>No action items found in the last 7 days of email.</em></p> -->

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events &mdash; Next 7 Days
</h3>
<p style="color: #555; font-size: 0.9em;">Only non-routine, unusual, or one-time events are shown.</p>

<!-- Repeat for each unusual event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Date} &bull; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 0; color: #555; font-size: 0.85em;">Why flagged: {brief reason, e.g. "Non-recurring" / "Starts at 6:30 AM" / "15 attendees" / "Off-site: Denver Convention Center"}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no unusual events in the next 7 days, replace event blocks with: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Label the draft for delivery

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

- If there are **no action items**, say so clearly; do not omit the section.
- If there are **no out-of-the-ordinary calendar events**, say so clearly; do not omit the section.
- Action items must be concrete ("Reply to Alice confirming the meeting time")
  not vague ("Follow up").
- Do not duplicate action items — if the same thread spawns multiple asks,
  combine them into one action item.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Urgency tags: 🔴 = needs action today or has a past-due date; 🟡 = due within the week; 🟢 = no hard deadline.

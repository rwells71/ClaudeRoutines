# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time windows

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (i.e. the last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days from now, in Mountain Time (`America/Denver`).
  - `startTime`: today at `00:00:00` Mountain Time
  - `endTime`: 7 days from today at `23:59:59` Mountain Time

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 200 threads maximum).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID — prioritize threads that look like they
require a response or decision.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch calendar events for the next 7 days

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

Collect **all** events returned. You will filter and categorize them in Step 4.

---

## Step 4 — Build the Top 10 Action Items list

### 4a — Score and rank email action items

Review all emails collected. For each email requiring the owner's attention,
extract a single, specific action item. Score each item 1–10 by urgency:

- **9–10**: Explicit deadline within 48 hours, or marked urgent by sender
- **7–8**: Awaiting a decision or reply that is blocking someone else
- **5–6**: Needs a response within the week but not immediately blocking
- **3–4**: Informational follow-up or low-priority reply
- **1–2**: Nice-to-have, no real deadline

Keep the **top 10 highest-scoring items** across all emails. If fewer than
10 actionable items exist, include all of them. Discard the rest.

### 4b — Identify out-of-the-ordinary calendar events

From the events fetched in Step 3, flag an event as **out of the ordinary** if
it meets ANY of the following criteria:

1. **Non-recurring**: It does NOT have a `recurringEventId` or `recurrence` field
   (i.e. it is a one-time event, not part of a regular series).
2. **Unusual timing**: Starts before 7:00 AM or after 7:00 PM Mountain Time.
3. **All-day event on a weekday**: The event is an `allDay` event on Monday–Friday.
4. **Large guest list**: The event has 10 or more attendees.
5. **New or recently modified**: The event was created or last updated within the
   last 48 hours.
6. **External attendees**: The event includes attendees from outside the owner's
   email domain.

Collect all out-of-the-ordinary events. If none qualify, note that explicitly.

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
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; covering the last 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#9989; Top 10 Items to Address</h3>
<p style="color: #555; font-size: 0.9em; margin-top: -8px;">Ranked by urgency. Address these first.</p>

<ol style="padding-left: 20px;">

  <!-- Repeat the <li> block below for each of the top 10 action items (highest score first) -->
  <li style="margin-bottom: 16px;">
    <div style="display: flex; align-items: baseline; gap: 8px;">
      <strong>{Action item — specific, concrete task}</strong>
      <!-- Urgency badge: use color based on score:
           9-10 → background #c0392b (red),  7-8 → #e67e22 (orange),
           5-6  → #f1c40f (yellow, text #222), 3-4 → #27ae60 (green), 1-2 → #95a5a6 (grey) -->
      <span style="font-size: 0.75em; background: {badge_color}; color: #fff; padding: 2px 7px; border-radius: 10px; white-space: nowrap;">
        Priority {score}/10
      </span>
    </div>
    <p style="margin: 4px 0 0 0; color: #555; font-size: 0.9em;">
      From: <strong>{Sender Name}</strong> &mdash; <em>{email subject}</em>
      &mdash; {date received, e.g. "Mon Jun 16"}
    </p>
    <p style="margin: 4px 0 0 0; color: #555; font-size: 0.9em;">{One sentence of context explaining why this needs attention}</p>
  </li>
  <!-- End action item block -->

</ol>

<!-- If no actionable emails were found, replace the <ol> with: -->
<!-- <p><em>No actionable emails found in the last 7 days.</em></p> -->

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events &mdash; Next 7 Days
</h3>
<p style="color: #555; font-size: 0.9em; margin-top: -8px;">
  One-time, unusual-hour, newly added, or large-group events.
</p>

<!-- Repeat for each out-of-the-ordinary event -->
<div style="margin-bottom: 14px; padding: 12px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;">
    <strong>{Day of week, Month Day}</strong> &mdash;
    <strong>{Start Time} &ndash; {End Time} MT</strong> &mdash;
    {Event Title}
  </p>
  <!-- Reason badge: state why it is out of the ordinary -->
  <p style="margin: 4px 0 0 0; font-size: 0.85em; color: #27AE60;">
    &#9888; {Reason: e.g. "One-time event", "Starts at 6:30 AM", "14 attendees", "Added yesterday"}
  </p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description or note}</p>
</div>
<!-- End event block -->

<!-- If no out-of-the-ordinary events exist in the next 7 days, replace event blocks with: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Label the draft for easy retrieval

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

- **Top 10 only**: Include at most 10 action items. Quality over quantity.
- **Concrete actions**: Each action item must be a specific task ("Reply to Alice
  confirming budget approval by Friday") not vague ("Follow up").
- **Calendar reasons**: For every out-of-the-ordinary event, state the specific
  reason it qualifies (e.g. "One-time event — not part of a recurring series").
- If there are **no actionable emails**, say so clearly; do not omit the section.
- If there are **no out-of-the-ordinary calendar events**, say so clearly; do not omit the section.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Badge colors for priority scores: 9–10 → `#c0392b`, 7–8 → `#e67e22`,
  5–6 → `#e6b800` (use text color `#222`), 3–4 → `#27ae60`, 1–2 → `#95a5a6`.

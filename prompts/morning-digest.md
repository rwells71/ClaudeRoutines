# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today + the next 7 days in Mountain Time (`America/Denver`).

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -in:sent -in:draft`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated marketing mail: newsletters, promotional messages,
marketing from `noreply@`, `no-reply@`, `donotreply@`, or bulk-sender domains.
**Keep** transactional emails (financial alerts, account statements, billing),
human-sent messages (personal emails, school communications, group messages),
and important notifications (fraud alerts, proxy votes, shareholder materials).

---

## Step 3 — Fetch upcoming calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-05-07T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **keep only events that appear to be one-time or unusual**:
1. The event does NOT have a `recurringEventId` field, OR
2. The event has a recurring ID but has a notably unusual title that suggests
   a special occasion (concerts, camps, ceremonies, graduations, parties,
   special meetings with many attendees, etc.)

Drop routine recurring events (daily reminders, weekly standing meetings,
routine chores) — focus on what's genuinely out of the ordinary.

---

## Step 4 — Build the Top 10 Action Items

Review all emails and calendar events collected. Identify the **10 most
important items that require the account owner's attention or action**.

Rank them by urgency and importance:
1. Time-sensitive financial alerts (potential fraud, account issues)
2. Human-sent emails requiring a reply or decision
3. Upcoming deadlines with a specific date
4. Calendar events needing preparation
5. Transactional items to review or act on

For each item, write:
- A concise title (under 10 words)
- The source (sender name or calendar)
- The deadline or date if applicable
- 1–2 sentences describing the required action

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

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Thursday, May 7, 2026`

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
<h3 style="margin-top: 28px;">&#9989; Top 10 Items to Address</h3>

<!-- Repeat for each of the 10 items, numbered 1–10 -->
<div style="margin-bottom: 16px; padding: 12px; background: #f9f9f9; border-left: 4px solid #4A90D9;">
  <p style="margin: 0 0 4px 0;">
    <strong>#{rank} — {Item Title}</strong>
    <span style="color: #888; font-size: 0.85em; margin-left: 8px;">{Source} {· Deadline if applicable}</span>
  </p>
  <p style="margin: 4px 0 0 0; color: #444;">{1–2 sentence action description}</p>
</div>
<!-- End action item block -->

<!-- ====== OUT-OF-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Upcoming One-Time &amp; Unusual Events (Next 7 Days)
</h3>

<!-- Repeat for each unusual event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Day, Month D} &nbsp;{Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description if present}</p>
</div>
<!-- End event block -->

<!-- If no unusual events, replace with: -->
<!-- <p><em>No one-time or unusual calendar events in the next 7 days.</em></p> -->

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

This moves the draft to the Inbox so it arrives like a normal email rather
than sitting silently in the Drafts folder.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- Always produce exactly 10 action items — no more, no fewer (combine closely
  related items if needed to hit exactly 10).
- If there are **no unusual calendar events**, say so clearly; do not omit the section.
- Action items must be concrete ("Reply to Mrs. Wootton with a mailing address")
  not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Skip purely promotional/marketing emails (tire sales, restaurant deals,
  cruise offers, etc.) unless there is a genuine deadline the owner set.

# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through the next 14 days (Mountain Time, `America/Denver`).

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -in:draft -in:sent -in:spam -category:promotions`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand action items, call `get_thread` with that thread's ID.

**Skip** clearly automated/marketing mail. **Include** transactional emails, financial alerts,
human-sent messages, school notices, medical billing, and important system notifications.

---

## Step 3 — Fetch upcoming non-recurring calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: 14 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, **keep only events where ALL of the following are true**:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are genuinely one-time events. Drop routine recurring events like daily reminders,
regular family dinners, weekly chores, etc.

---

## Step 4 — Generate the Top 10 Action Items

Review all emails collected in Step 2. Identify the **10 most important items** the account
owner needs to act on, ranked by urgency and importance.

Prioritize:
- Replies needed or decisions required
- Financial alerts (fraud flags, payments, billing disputes)
- Deadlines or time-sensitive tasks
- School/family obligations with a specific date
- Medical or health follow-ups
- Commitments made to others that need follow-through

Deprioritize:
- Newsletters and promotional content
- Purely informational updates with no action required

Format as a **numbered HTML list**, one concise sentence per item. Each item should state
the action needed, not just describe the email.

---

## Step 5 — Identify Unusual Calendar Events

From the one-time events collected in Step 3, select those that are genuinely noteworthy —
special occasions, appointments, milestone events, unusual locations, events with many
attendees, or anything that breaks from a regular weekly/daily pattern.

Examples of "out of the ordinary":
- Graduations, concerts, parties
- Medical or professional appointments
- Trek/camp outings, site visits
- Named social events (e.g. "Emily's graduation party")
- Canceled events (flag these — they may need rescheduling)

Format as a **bulleted HTML table** or styled list showing: date, time (MT), event name,
location (if any), and a one-line note.

---

## Step 6 — Determine the account owner's email address

Use the following strategy, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. The address that appears most
   frequently is almost certainly the account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of other "To:" addresses.
3. If still ambiguous, use the first address found in any "To:" field.

Store this as `{owner_email}`.

---

## Step 7 — Create and deliver the digest

### 7a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Briefing — Top 10 Items | {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Briefing — Top 10 Items | Wednesday, May 20, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 680px; margin: auto; color: #222;">

<h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 8px;">
  Morning Briefing &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; emails from the past 7 days</p>

<!-- ====== TOP 10 SECTION ====== -->
<h3 style="margin-top: 24px;">&#128203; Top 10 Action Items</h3>
<ol style="line-height: 2.0; padding-left: 20px;">
  <!-- One <li> per action item, one concise sentence each -->
  <li><strong>{Category/Emoji}</strong> {Action item description}</li>
</ol>

<!-- ====== UNUSUAL CALENDAR EVENTS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Unusual Calendar Events (Next 14 Days)
</h3>

<!-- Repeat block for each unusual one-time event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Day, Date} &mdash; {Start Time}&ndash;{End Time} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link, if present}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{One-line note, e.g. ticket info, attendees, or context}</p>
</div>
<!-- End event block -->

<!-- If no unusual events, use: <p><em>No unusual one-time events in the next 14 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &mdash; sent daily at 5 AM MT</p>

</body>
</html>
```

### 7b — Move the draft to Inbox

After `create_draft` returns an ID, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

This moves the draft into the Inbox so it arrives like a received email.

> **Note**: The Gmail MCP does not expose a send API. Delivery is via label assignment.
> If a `send_message` or `send_draft` tool becomes available, prefer that over `label_message`.

---

## Important rules

- If there are **no qualifying emails**, say so clearly; do not omit the section.
- If there are **no unusual calendar events**, say so clearly; do not omit the section.
- Keep action items concrete ("Reply to Alice confirming X") not vague ("Follow up").
- Never include raw HTML or JSON in the digest body.
- Strip tracking pixels and boilerplate from email bodies before summarizing.

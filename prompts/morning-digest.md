# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the past 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: the next 7 days starting from today (current date in
  Mountain Time), from `00:00:00` today through `23:59:59` seven days out,
  timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social in:inbox`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (stop after 3 pages maximum).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated, non-actionable mail: newsletters, general
marketing, routine notification digests (school progress reports with nothing
urgent, LinkedIn updates, price-drop alerts), messages from
`noreply@`, `no-reply@`, `donotreply@` unless they flag an alert or require
action, and standard legal/terms-update notices unless they require an
immediate response.

**Always include**: anything requiring a reply, approval, payment, vote, or
decision; urgent alerts (health, security, financial); messages from real
humans; and transactional emails with a specific deadline.

---

## Step 3 — Fetch upcoming calendar events (7-day window)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601 with offset)
- `endTime`: 7 days out at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, identify **out-of-the-ordinary** events using these signals:

1. **Non-recurring**: the event does NOT have a `recurringEventId` field —
   it is a genuinely one-time event.
2. **Newly added or recently modified**: `created` or `updated` timestamp is
   within the past 48 hours.
3. **Unusually long duration**: spans more than 4 hours.
4. **Logistical impact**: title keywords like "road", "repair", "flight",
   "travel", "move", "camp", "closed", "no parking", etc.
5. **Scheduling conflict or anomaly**: event falls on a known day-off (e.g.
   "9/80 Off Friday"), very early (<6 AM) or very late (>10 PM), or overlaps
   another event.

Flag any event matching one or more of the above signals as "out of the
ordinary." Include all non-recurring events and any recurring events that
meet signals 2–5.

---

## Step 4 — Build the Top 10 Action Items list

Analyze all emails and out-of-the-ordinary calendar events. Produce a
prioritized **Top 10 list** of the things the account owner most needs to
address. Use this priority order:

1. Urgent financial/security alerts (fraud, large bill alerts, expired cards)
2. Items with an explicit deadline or approval pending
3. Action items from real humans requiring a reply
4. Calendar events with logistical impact (need to move car, arrange rides, etc.)
5. Professional obligations (votes, subscriptions at risk, work tasks)
6. Family or household items with time sensitivity
7. Reminders created by the owner that are still outstanding
8. Lower-urgency but time-bound items

Each item in the list should include:
- A concise title (bold)
- Source (email subject/sender or calendar event title + date)
- 1–2 sentences on what needs to be done and why it matters
- Urgency tag: 🔴 Today · 🟡 This Week · 🟢 FYI

Limit to exactly 10 items. If there are fewer than 10 meaningful items,
fill remaining slots with the next most-useful context. If there are more
than 10, cut the lowest-priority items.

---

## Step 5 — Out-of-the-Ordinary Calendar Events summary

List all events flagged in Step 3 as out of the ordinary. For each:
- Date and time (Mountain Time)
- Event title
- Why it is flagged (non-recurring, newly added, logistical impact, etc.)
- One-line action or heads-up if applicable

---

## Step 6 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient
   addresses. The address that appears most frequently is almost certainly the
   account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of
   the other addresses in the "To:" fields.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 7 — Create and label the digest draft

### 7a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `☀️ Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `☀️ Morning Digest — Wednesday, July 8, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  ☀️ Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; emails from the past 7 days &middot; calendar next 7 days</p>

<!-- ====== TOP 10 SECTION ====== -->
<h3 style="margin-top: 28px;">🗒️ Top 10 Action Items</h3>

<!-- Repeat for each of the 10 items -->
<div style="margin-bottom: 14px; padding: 12px; background: #f9f9f9; border-left: 4px solid #4A90D9; border-radius: 4px;">
  <p style="margin: 0 0 4px 0;">
    <strong>{#}. {Item Title}</strong>
    &nbsp;<span style="font-size:0.85em;">{🔴 Today | 🟡 This Week | 🟢 FYI}</span>
  </p>
  <p style="margin: 0 0 2px 0; font-size: 0.85em; color: #555;">
    Source: {email subject / sender OR calendar event + date}
  </p>
  <p style="margin: 4px 0 0 0;">{1–2 sentence description of what to do and why}</p>
</div>
<!-- End item block -->

<!-- ====== OUT OF THE ORDINARY CALENDAR SECTION ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  📅 Out-of-the-Ordinary Calendar Events
</h3>
<p style="color: #666; font-size: 0.88em;">One-time events, newly added/modified events, or unusual scheduling in the next 7 days.</p>

<!-- Repeat for each flagged event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60; border-radius: 4px;">
  <p style="margin: 0;"><strong>{Date} &middot; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 12px; color: #555; font-size: 0.88em;">Why flagged: {reason}</p>
  <p style="margin: 4px 0 0 12px; color: #333; font-size: 0.88em;">{Action or heads-up}</p>
</div>
<!-- End event block -->

<!-- If no flagged events -->
<!-- <p><em>No out-of-the-ordinary events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &middot; emails from past 7 days &middot; calendar next 7 days</p>

</body>
</html>
```

### 7b — Label the draft for easy retrieval

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

- The Top 10 list is the primary deliverable — make it crisp and actionable.
- Keep each action item to 2–3 lines maximum.
- Urgency tags must reflect real deadlines: use 🔴 only if action is needed
  today, 🟡 if needed within 7 days, 🟢 for awareness items.
- Never include raw HTML, JSON, or email headers in the digest body.
- If there are fewer than 10 meaningful action items, do not pad with trivia.
- If you encounter a `send_email` or `send_draft` tool in a future run,
  use it instead of the draft + label approach.

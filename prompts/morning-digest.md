# Morning Email & Calendar Digest — Weekly Top 10

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the **7-day** period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today + the next **7 days** (current date through
  +7 days in Mountain Time), timezone `America/Denver`.

---

## Step 2 — Fetch emails from the past 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 150 threads max — stop after 3 pages).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand an action item, call `get_thread`
with that thread's ID. Limit full-body fetches to 10 threads.

**Skip** clearly automated mail: newsletters and pure marketing messages from
`noreply@`, `no-reply@`, `donotreply@`. **Include** transactional notifications
(bills, orders, bank alerts, school notices, important system alerts, and all
human-sent messages).

---

## Step 3 — Fetch calendar events for today + next 7 days

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601 with offset)
- `endTime`: 7 days from now at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

**Identify "out-of-the-ordinary" events** — keep an event if ANY of the
following are true:
1. It does NOT have a `recurringEventId` field (one-time event).
2. It has a `recurringEventId` but contains keywords in the title suggesting
   something unusual (e.g. "concert", "festival", "meet & greet", "trek",
   "trip", "surgery", "conference", "graduation", "recital", "wedding",
   "first time", "special", "only").
3. It starts before 6:00 AM or after 9:00 PM local time.
4. It has an external attendee (someone not on the primary account's domain).

Drop routine recurring events (daily chores, regular meetings, standard
standing appointments) unless they have an unusual characteristic above.

---

## Step 4 — Determine the account owner's email address

Look at the **"To:"** fields of all emails fetched. The address appearing most
frequently is the owner's address. Store this as `{owner_email}`.

---

## Step 5 — Build the Top 10 Action Item list

Analyze all emails and unusual calendar events together. Rank the top 10 items
the owner needs to act on, ordered by urgency (imminent deadlines first, then
financial, then social/family, then logistics, then low-priority).

For each item:
- Assign a priority number (#1–#10)
- Write a bold title (5–8 words)
- Write 1–2 sentences explaining what it is and what action is needed
- Note the source (email subject/sender or calendar event title + date)
- Tag with an urgency badge: 🔴 Urgent / 🟡 Soon / 🟢 This week

---

## Step 6 — Create the digest draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Friday, April 25, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 680px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #2c5f8a; padding-bottom: 8px; color: #2c5f8a;">
  📋 Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Past 7 days of email &bull; Next 7 days of calendar</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 24px; color: #c0392b;">🔴 Top 10 Action Items</h3>

<!-- Repeat this block for each of the 10 items -->
<div style="margin-bottom: 14px; padding: 10px 14px; background: #f9f9f9; border-left: 5px solid {urgency_color};">
  <p style="margin: 0 0 4px 0;">
    <strong>#{rank} — {Item Title}</strong>
    &nbsp; <span style="font-size:0.85em; color:#888;">{🔴 Urgent / 🟡 Soon / 🟢 This week}</span>
  </p>
  <p style="margin: 0 0 4px 0; font-size: 0.95em;">{1–2 sentence description and action needed}</p>
  <p style="margin: 0; font-size: 0.82em; color: #777;"><em>Source: {email subject/sender or calendar event + date}</em></p>
</div>
<!-- End item block -->

<!-- urgency_color values: #e74c3c for Urgent, #f39c12 for Soon, #27ae60 for This week -->

<!-- ====== UNUSUAL CALENDAR EVENTS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px; color: #e67e22;">
  🗓️ Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each unusual event -->
<div style="margin-bottom: 12px; padding: 10px 14px; background: #f0f7ff; border-left: 4px solid #27ae60;">
  <p style="margin: 0 0 2px 0;">
    <strong>{Day, Month Date} &bull; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}
  </p>
  <p style="margin: 2px 0 0 0; font-size: 0.88em; color: #555;">
    {📍 Location or 🔗 video link, if present} {Brief description or why it is unusual}
  </p>
</div>
<!-- End event block -->

<!-- If no unusual events in the next 7 days: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated morning digest &mdash; ClaudeRoutines &bull; Delivered daily at 5:00 AM MT</p>

</body>
</html>
```

---

## Step 7 — Move the draft to Inbox

After `create_draft` returns a draft ID, call `label_message` with:
- `messageId`: the message ID returned by `create_draft`
- `addLabelIds`: `["INBOX"]`

This delivers the digest directly to the Inbox so it arrives like a normal
email rather than sitting in Drafts.

---

## Important rules

- The Top 10 list is the heart of the digest — make it genuinely useful and
  prioritized, not just a list of emails in chronological order.
- Urgency: 🔴 = due within 2 days or time-sensitive, 🟡 = due within a week,
  🟢 = coming up but not immediate.
- If fewer than 10 actionable items exist, list only what exists (do not pad).
- Keep descriptions concise — one to two sentences max per item.
- Never include raw HTML or JSON in the digest body.
- Strip tracking pixels and boilerplate before summarizing email content.
- If full body fetch is needed, fetch only threads where the snippet is
  insufficient to determine the action item.

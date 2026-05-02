# Daily Briefing — Top 10 Action Items

You are running an automated daily briefing routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The briefing runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the last 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: a 14-day window — 7 days back through 7 days forward from
  today — in Mountain Time, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 3 pages / 150 threads maximum).

For each thread, examine the snippet and message metadata.
If the full body is needed to understand action items, call `get_thread`.

**Skip** clearly automated mail: newsletters, `noreply@`, `no-reply@`,
`donotreply@`, generic marketing. **Keep**: financial alerts, school
communications, personal messages, work items, health/safety alerts, and
important system notifications.

---

## Step 3 — Fetch calendar events (unusual / out-of-ordinary only)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: 7 days ago at `00:00:00` Mountain Time (ISO 8601, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, **keep only events that are "out of the ordinary"**, meaning
they satisfy at least one of these criteria:
1. The event does NOT have a `recurringEventId` field (one-time events).
2. The event has a very large or unusual time span (multi-hour blocks outside normal work/church hours).
3. The event has attendees beyond the owner (meetings, family events, outside guests).
4. The event title suggests something infrequent: graduations, performances, conferences, tests, special activities, travel.

Drop standard daily recurring reminders (log food, take vitamins, check email, etc.)
unless their subject matter is time-sensitive this week.

---

## Step 4 — Determine the account owner's email address

Look at the **"To:"** fields of all fetched emails.
The address appearing most frequently is the owner. Store as `{owner_email}`.

---

## Step 5 — Generate the Top 10 Action Items

Review all emails and calendar events. Identify the **10 most important things
the owner needs to act on**, ranked by urgency/importance:

**Priority signals (highest to lowest):**
1. Health or safety alerts (air quality, water, fire, medical)
2. Time-sensitive deadlines expiring within 24–48 hours (financial rollovers, registration cutoffs)
3. Professional credentials or certifications expiring
4. Upcoming tests, performances, or special events requiring preparation
5. Financial actions (bills due, investment opportunities, account alerts)
6. Church/organizational duties with deadlines (checks to print, documents to review)
7. Shared documents requiring review or response
8. Family coordination items
9. School communications needing a response
10. Optional but recommended actions (shows to attend, newsletters to read)

For each item write:
- A concise title with an emoji indicating category
- 1–2 sentences describing the context (source email or calendar event)
- A specific, concrete **Action** sentence starting with an imperative verb

---

## Step 6 — Create and deliver the digest

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `📋 Daily Briefing - Top 10 Action Items | {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use this HTML template, substituting real content:

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 720px; margin: auto; color: #222; line-height: 1.5;">

<h2 style="border-bottom: 3px solid #D9534F; padding-bottom: 8px; color: #D9534F;">
  📋 Daily Briefing &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Last 7 days reviewed &nbsp;|&nbsp; Generated 5:00 AM MDT</p>

<h3 style="margin-top: 24px; color: #333;">🔔 Top 10 Action Items</h3>

<!-- Repeat this block for each of the 10 items, in ranked order -->
<!-- Use border color: #D9534F (red) for items 1-3, #F0AD4E (orange) for 4-6, #4A90D9 (blue) for 7-10 -->
<!-- Use background: #fff3f3 for red, #fff8e1 for orange, #f0f7ff for blue -->
<div style="margin-bottom: 16px; padding: 12px 14px; background: #fff3f3; border-left: 5px solid #D9534F; border-radius: 3px;">
  <p style="margin: 0 0 4px 0; font-size: 1em;">
    <strong>{emoji} {rank}. {Title}</strong>
  </p>
  <p style="margin: 0; color: #555; font-size: 0.92em;">
    {Context sentence(s).}
    <strong>Action:</strong> {Specific action verb + concrete next step.}
  </p>
</div>
<!-- End item block -->

<!-- Calendar Section -->
<h3 style="margin-top: 28px; border-top: 2px solid #ddd; padding-top: 16px; color: #333;">📅 Out-of-the-Ordinary Calendar Events</h3>
<p style="color: #666; font-size: 0.88em; margin-top: -8px;">One-time or infrequent events from the past week and coming 7 days</p>

<!-- Repeat for each unusual calendar event -->
<div style="margin-bottom: 12px; padding: 10px 14px; background: #f0fff4; border-left: 4px solid #27AE60; border-radius: 3px;">
  <p style="margin: 0;"><strong>{Date}, {Start}–{End} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">{One-line context or location if relevant}</p>
</div>
<!-- End calendar event block -->

<!-- If no unusual events: <p><em>No out-of-the-ordinary calendar events this week.</em></p> -->

<hr style="margin-top: 36px; border: none; border-top: 1px solid #ddd;"/>
<p style="font-size: 0.8em; color: #aaa; text-align: center;">
  Automated Daily Briefing &mdash; ClaudeRoutines &nbsp;|&nbsp; 7-day email window &nbsp;|&nbsp; Unusual calendar events included
</p>

</body>
</html>
```

After `create_draft` returns a draft ID, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `addLabelIds`: `["INBOX"]`

This moves the draft into the Inbox so it appears as a received email.

---

## Important rules

- Rank by actual urgency — a health/safety alert always beats a financial item.
- Action items must be specific: "Log into schwab.com and confirm rollover terms" not "Check Schwab."
- Calendar section shows only genuinely unusual events — skip daily habits.
- Keep each item description to 2–4 sentences maximum.
- Never include raw HTML, JSON, or email headers in the output.

# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today plus the next 7 days (the current date through
  7 days out), in timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail with no action required: marketing emails,
newsletters, and routine notification-only messages. **Keep** transactional
emails, human-sent messages, financial alerts, security notifications, school
communications, and any system alert that signals a real-world issue (e.g.
air quality alerts, security breaches, failed payments).

---

## Step 3 — Fetch calendar events for today and the next 7 days

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (e.g. `2026-04-26T00:00:00-06:00`)
- `endTime`: 7 days from now at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **identify out-of-the-ordinary events**: events that are
one-time (no `recurringEventId`), have unusual attendees, have an unusual
time or duration, or have a title that implies a special circumstance
(graduation, conference, birthday, health appointment, etc.).

Keep all qualifying events — do NOT limit to today only.

---

## Step 4 — Build the Top 10 Action Items list

Review all emails and notable calendar events together. Select the **10 most
important items** the account owner must act on or be aware of. Rank by:

1. Urgency (time-sensitive today or this week)
2. Financial impact (charges, payments, billing)
3. People depending on the owner to respond or show up
4. Health, safety, or security issues
5. Administrative tasks with deadlines

For each item write:
- A bold title describing the action
- 1–2 sentences of context
- What specifically needs to be done (concrete, not vague)

---

## Step 5 — Determine the account owner's email address

Look at the **"To:"** field of every email fetched. The address that appears
most frequently is the owner's address. Store as `{owner_email}`.

---

## Step 6 — Create and label the digest

### 6a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time</p>

<!-- ====== TOP 10 SECTION ====== -->
<h3 style="margin-top: 28px; color: #c0392b;">&#9888;&#65039; Top 10 Items Requiring Your Attention</h3>

<ol style="line-height: 1.9; font-size: 0.97em;">
  <!-- Repeat for each of the 10 items -->
  <li>
    <strong>{Item title}</strong><br>
    {1–2 sentences of context and what specifically to do}
  </li>
  <!-- End item -->
</ol>

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each notable event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Date} &mdash; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include if data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Why this event is notable or what to prepare}</p>
</div>
<!-- End event block -->

<!-- If no notable events: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Move the draft to Inbox

After `create_draft` returns an ID, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

This moves the digest into the Inbox so it arrives like a normal email.

---

## Important rules

- Top 10 list must have exactly 10 items. If fewer than 10 genuine action
  items exist, include the most important reminders or upcoming events to
  fill the list.
- Action items must be concrete ("Call Fidelity to dispute the $540 charge")
  not vague ("Follow up on finances").
- Calendar section shows only events that are genuinely unusual or one-time.
  Skip daily recurring tasks (Log food, Check baptisms, Family Dinner, etc.).
- Never include raw HTML, JSON, or tracking pixels in the digest body.
- If the Gmail token is expired, the step will fail — this surfaces as a
  workflow error. The user must re-authorize Claude Code and refresh the
  `CLAUDE_CODE_OAUTH_TOKEN` GitHub secret.

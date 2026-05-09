# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the last 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through the next 7 days in Mountain Time,
  from today at `00:00:00` to 7 days from now at `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -in:sent -in:draft`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand action items, call `get_thread` with that thread's ID.

**Skip** purely marketing/newsletter mail. **Include**:
- Emails requiring a response or decision
- Financial alerts (fraud, large charges, bills, trade confirmations)
- School or family notifications with deadlines
- Human-to-human messages
- Important system notifications (air quality, security alerts, etc.)
- Calendar invitations, cancellations, and changes

---

## Step 3 — Fetch calendar events for the next 7 days

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601)
- `endTime`: 7 days from now at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, **flag as "out of the ordinary"** any event that meets one or more of these criteria:
1. The event does NOT have a `recurringEventId` field (one-time event).
2. A recurring event was **canceled** (status = "cancelled") or **rescheduled** (start time differs from `originalStartTime`).
3. A new invitation from another person arrived this week (has `attendees` and the organizer is not the account owner).
4. An event has an unusual or urgent-sounding title (e.g. contains words like "canceled", "urgent", "important", "deadline", "last chance", "only", "one time", "makeup").

---

## Step 4 — Build the Top 10 Action Items list

Score and rank all action items across **both** emails and flagged calendar events.
Prioritize in this order:
1. Security / fraud / health / safety alerts
2. Financial: bills due, unapproved expenses, large transactions
3. Time-sensitive items with a deadline today or tomorrow
4. Replies needed to human-sent messages
5. Family / school items with a deadline this week
6. Church / community responsibilities
7. Reminders and low-urgency follow-ups

Output **exactly 10 items** (or fewer if there truly aren't 10 actionable things). Number them 1–10 with the highest priority first.

For each item include:
- A short bold title (5–10 words)
- The source: `[Email]` or `[Calendar]`
- 1–2 sentences of context
- A concrete action the reader should take

---

## Step 5 — Determine the account owner's email address

Look at the **"To:"** field of every email fetched. The address that appears most
frequently is the account owner. Store this as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `📋 Morning Briefing — {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #1a73e8; padding-bottom: 8px; color: #1a73e8;">
  Good Morning &#128075; &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Your daily briefing generated at 5:00 AM Mountain Time</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 24px;">&#128203; Top 10 Action Items</h3>
<p style="color:#555; font-size:0.9em;">Ranked by urgency. Tackle the top items first.</p>

<ol style="line-height: 2;">
  <!-- Repeat for each item (1–10) -->
  <li>
    <strong>{Short bold title}</strong> <span style="color:#888; font-size:0.85em;">[{Email or Calendar}]</span><br>
    <span style="color:#444;">{1–2 sentences of context. Concrete action to take.}</span>
  </li>
</ol>

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px; color: #1a73e8;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- If none, replace with: <p><em>No unusual calendar events this week.</em></p> -->

<!-- Repeat for each flagged event -->
<div style="margin-bottom: 12px; padding: 10px; background: #fff8e1; border-left: 4px solid #f29900;">
  <p style="margin: 0;"><strong>{Day, Date} &mdash; {Start}–{End} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">Why flagged: {one sentence reason}</p>
  <!-- Only include if data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
</div>
<!-- End event block -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated morning digest &mdash; ClaudeRoutines &mdash; rwells71@gmail.com</p>

</body>
</html>
```

### 6b — Move the draft to Inbox

After `create_draft` returns a draft ID, call `label_message` with:
- `messageId`: the message ID from the draft response
- `addLabelIds`: `["INBOX"]`

This delivers the digest to the Inbox like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. Delivery is
> achieved by moving the draft to INBOX via `label_message`. If a `send_draft`
> tool becomes available, prefer that instead.

---

## Important rules

- Output **exactly 10 ranked action items** (fewer only if there are genuinely fewer actionable things).
- Keep each action item concise: context in 1–2 sentences, action in one imperative sentence.
- For calendar events, only flag events that are genuinely unusual compared to a normal recurring week.
- Never include raw HTML or JSON in the digest body.
- Strip marketing boilerplate before summarizing email content.

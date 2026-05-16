# Morning Email & Calendar Digest — Top 10 Priority List

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the past 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window — today**: current date in Mountain Time, `00:00:00` to `23:59:59`, timezone `America/Denver`.
- **Calendar window — upcoming**: today through 7 days from now.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -in:draft`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one (up to 3 pages).

For each thread, the snippet and metadata returned are usually sufficient.
Only call `get_thread` if the snippet is too vague to determine whether action is required.

**Skip automatically**: marketing emails, newsletters, promotional blasts, social network digests,
messages from addresses containing `noreply`, `no-reply`, `donotreply`, `notifications`, or `mailer-daemon`.

**Always include**: transactional alerts (bank charges, account changes, FICO changes), messages from
real people, school/church administrative emails, package/appointment notifications, and any
message that implies the reader needs to do something.

---

## Step 3 — Fetch calendar events

### 3a — Today's events (all)
Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601 with offset)
- `endTime`: today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

### 3b — Next 7 days of one-time events
Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: tomorrow at `00:00:00` Mountain Time
- `endTime`: 7 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From both result sets, flag events as **"one-time / unusual"** if ALL of the following are true:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.
3. The event is not a routine household task (trash, laundry, food logging, school runs, etc.).
4. The event has a title that suggests it is a specific appointment, social event, meeting with a named person, or community event.

---

## Step 4 — Build the Top 10 Action Item List

Review all emails and calendar items collected. Rank by urgency using this priority order:

1. **Deadlines / time-sensitive** (e.g., "excuse absence within 3 days", "payment due", "deadline today")
2. **Financial action required** (trade confirmations to review, tax forms to download, unusual charges)
3. **Family / school urgencies** (attendance, end-of-year events, pickup items)
4. **Upcoming appointments that need preparation** (one-time meetings within 48 hours)
5. **Pending RSVPs / invites not yet accepted**
6. **Home / maintenance alerts** (air quality, appliances, etc.)
7. **Church / community administrative tasks** (financial reports, checks to print, etc.)
8. **Texts or personal messages requiring a response**
9. **Financial account reviews** (monthly statements, portfolio summaries)
10. **Other noteworthy items** (upcoming events, opportunities, reminders)

Select exactly 10 items (or fewer if the inbox is light). Each item must be:
- Specific and actionable ("Log in to myDSD and excuse Lyndie's absence" not "Check school email")
- Attributed to its source (brief parenthetical: sender name or calendar event)
- Assigned a priority level: 🔴 Urgent, 🟡 Soon, or 🟢 FYI

---

## Step 5 — Identify unusual calendar events

From Step 3, list all flagged one-time/unusual events for today and the next 7 days.
Include: event title, date, time (Mountain Time), and any relevant location or attendees.

---

## Step 6 — Determine the account owner's email address

Use the following strategy, stopping at the first successful result:
1. Look at the **"To:"** field of every email fetched. The address that appears most frequently is the owner's.
2. Prefer addresses whose domain matches the majority of other "To:" fields.
3. Fall back to the first address found in any "To:" field.

Store this as `{owner_email}`.

---

## Step 7 — Create and deliver the digest

### 7a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `📋 Your Morning Digest — {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; color: #333;">

  <h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 8px;">
    Good Morning! ☀️ Your Daily Briefing — {Weekday}, {Month} {Day}, {Year}
  </h2>
  <p style="color: #888; font-size: 0.85em;">Generated at 5:00 AM Mountain Time · Email window: last 7 days</p>

  <!-- ====== TOP 10 ACTION ITEMS ====== -->
  <h3 style="color: #d93025;">🔔 Top 10 Items Requiring Your Attention</h3>

  <table style="width: 100%; border-collapse: collapse;">
    <!-- Repeat this row for each of the 10 items. Alternate row background: #f8f9fa for even rows. -->
    <tr style="background-color: #fce8e6;">
      <td style="padding: 10px; border: 1px solid #ddd; vertical-align: top; width: 30px;"><strong>1</strong></td>
      <td style="padding: 10px; border: 1px solid #ddd;">
        <strong>{PRIORITY_EMOJI} {Action Item Title}</strong><br>
        {One to two sentence description with specific details and what to do.}
        <em style="color: #888;">(Source: {sender name or calendar event})</em>
      </td>
    </tr>
    <!-- ... rows 2–10 ... -->
  </table>

  <!-- ====== UNUSUAL CALENDAR EVENTS ====== -->
  <h3 style="color: #188038; margin-top: 24px;">📅 Unusual / One-Off Calendar Events (Next 7 Days)</h3>

  <!-- If none found, replace with: <p><em>No unusual events found in the next 7 days.</em></p> -->
  <ul style="line-height: 1.9;">
    <!-- Repeat for each one-time event -->
    <li><strong>{Day, Month Date} · {Start Time – End Time MT}</strong> — {Event Title}
      <!-- Include location or attendees if present -->
      <span style="color: #888;"> · {Location or attendees if available}</span>
    </li>
  </ul>

  <hr style="border: none; border-top: 1px solid #ddd; margin: 24px 0;">
  <p style="color: #aaa; font-size: 0.8em;">
    Automated digest · ClaudeRoutines · Powered by Claude
  </p>

</body>
</html>
```

### 7b — Deliver to Inbox

After `create_draft` returns a draft ID, call `label_message` with:
- `messageId`: the message ID returned by `create_draft`
- `addLabelIds`: `["INBOX"]`

This places the digest directly in the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. Inbox delivery via
> `label_message` with `"INBOX"` is the correct approach. Do NOT call `list_labels` to
> look up the INBOX ID — use the string `"INBOX"` directly.

---

## Important rules

- The top 10 list must contain **specific, actionable items** — not vague categories.
- Attribute every item to its source (email sender or calendar event).
- Omit purely marketing, newsletter, and promotional emails from the list entirely.
- Do not include more than 10 items; if fewer than 10 genuinely actionable items exist, list only those.
- Strip tracking pixels and HTML boilerplate before summarizing email bodies.
- Never include raw HTML or JSON in the digest body.
- Calendar events that are part of a recurring series (identified by `recurringEventId`) are routine and should NOT appear in the unusual events section unless their title clearly describes a one-time occasion.

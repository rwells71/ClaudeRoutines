# Morning Email & Calendar Digest — Top 10 Action Items

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Use the following windows:

- **Email window**: the last 7 days.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days from now, in Mountain Time
  (`America/Denver`), from today at `00:00:00` to day+7 at `23:59:59`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected.

For each thread, examine the snippet and metadata already returned.
Call `get_thread` only when the snippet is insufficient to determine
whether the email requires action.

**Skip** clearly automated mail with no action required: pure newsletters,
marketing blasts, and purely informational system notifications. **Include**:
- Any email that requires a reply, decision, payment, or follow-up
- Financial alerts (bills, investment activity, payments due)
- School communications (events, deadlines, exam notices)
- Health/safety alerts (air quality, security, device alerts)
- Deadline-driven requests (forms, nominations, sign-ups)
- Broken automation / expired token / system failure notices
- Anything from family members or known contacts

---

## Step 3 — Fetch calendar events for the next 7 days

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601, e.g. `2026-05-01T00:00:00-06:00`)
- `endTime`: day+7 at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, identify events that are **out of the ordinary** — meaning
any of the following apply:
1. The event does NOT have a `recurringEventId` (one-time events).
2. The event title contains prep instructions, deadlines, or specific
   amounts (payments, purchases, tasks with a named subject).
3. The event involves a named third party (child's name, family member,
   person outside the household).
4. The event has an unusual start time (e.g. before 6 AM or after 9 PM).
5. The event has a video link or location that suggests travel/attendance.
6. The event title references a school function, church calling, medical
   appointment, or financial obligation.

---

## Step 4 — Build the Top 10 Action Items

Review all emails and notable calendar events collected above. Identify and
rank the **10 most important things** the account owner needs to act on today.

Ranking criteria (highest priority first):
1. **Urgent / time-sensitive today**: deadlines expiring today, payments due
   today, events happening today that need preparation.
2. **Financial**: bills, investment executions, credit/banking alerts.
3. **Health & safety**: air quality alerts, medical, security notices.
4. **School / family obligations**: exams, performances, school deadlines.
5. **Work / professional**: work tasks, performance reviews, meetings.
6. **Broken automation / system issues**: expired tokens, failed jobs.
7. **Upcoming deadlines (this week)**: items due within 7 days.
8. **Church / community**: callings, meetings, service obligations.
9. **General follow-up**: replies needed, decisions pending.
10. **Nice-to-do / informational**: useful but low-urgency items.

For each action item write:
- A short bold title (under 10 words)
- Source: `[Email]` or `[Calendar]`
- 1–2 sentence description of what needs to be done and why it matters
- If there is a concrete deadline, call it out explicitly.

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

**`subject`**: `📋 Daily Briefing - Top 10 Action Items | {Weekday}, {Month} {Day}, {Year}`
  e.g. `📋 Daily Briefing - Top 10 Action Items | Friday, May 1, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 660px; margin: auto; color: #333;">

<div style="background: #1a1a2e; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
  <h1 style="margin: 0; font-size: 22px;">📋 Daily Briefing</h1>
  <p style="margin: 5px 0 0; opacity: 0.8;">{Weekday}, {Month} {Day}, {Year} &nbsp;|&nbsp; Last 7 days &nbsp;|&nbsp; Generated 5:00 AM MDT</p>
</div>

<div style="background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; border: 1px solid #ddd; border-top: none;">

  <h2 style="color: #1a1a2e; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px;">🔔 Top 10 Action Items</h2>

  <!-- Repeat the block below for each of the 10 action items.
       Choose the background color based on priority:
         #f8d7da / #dc3545  = urgent/critical
         #fff3cd / #ffc107  = high priority / today deadline
         #d1ecf1 / #17a2b8  = medium / financial / school
         #d4edda / #28a745  = standard / this week
         #e2e3e5 / #6c757d  = informational / low urgency
  -->
  <div style="background: {bg_color}; border-left: 4px solid {border_color}; padding: 12px; margin-bottom: 12px; border-radius: 4px;">
    <strong>{priority_emoji} {N}. {Action Item Title} <span style="font-weight: normal; font-size: 12px; color: #666;">[{Email or Calendar}]</span></strong><br>
    <span style="font-size: 14px;">{1–2 sentence description. Include deadline if applicable.}</span>
  </div>
  <!-- End action item block -->

  <!-- ====== NOTABLE CALENDAR EVENTS ====== -->
  <h2 style="color: #1a1a2e; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; margin-top: 24px;">📅 Notable Calendar Events (Next 7 Days)</h2>

  <!-- Repeat for each notable calendar event identified in Step 3 -->
  <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
    <tr style="background: #f0f4ff;">
      <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; white-space: nowrap;">{Day, Date}</td>
      <td style="padding: 8px; border: 1px solid #ddd;">
        <strong>{Event Title}</strong> — {Start Time}–{End Time} MT<br>
        <!-- Only include lines below if data exists -->
        <em style="color: #555;">{Location or prep note if present}</em>
      </td>
    </tr>
    <!-- Alternate row style: background: #ffffff -->
  </table>

  <!-- If no notable events, replace table with: -->
  <!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

  <hr style="margin: 24px 0; border: none; border-top: 1px solid #ddd;">
  <p style="font-size: 12px; color: #999; text-align: center;">
    Automated digest &mdash; ClaudeRoutines &nbsp;|&nbsp; Daily at 5:00 AM MDT
  </p>
</div>
</body>
</html>
```

### 6b — Move the draft to the Inbox

After `create_draft` returns a message ID, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — use the literal string `"INBOX"`.
Do **not** call `list_labels` to look it up.

This moves the draft to the Inbox so it arrives like a normal email rather
than sitting silently in the Drafts folder.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- Rank ruthlessly — include only the 10 items that most need the owner's
  attention today. Drop pure FYIs.
- Action items must be concrete ("Pay $1,351 to Costco CC today") not
  vague ("Handle finances").
- Deadlines must be explicit when known.
- Keep each action item description to 1–2 sentences.
- Never include raw HTML or JSON in the digest body.
- If there are no qualifying emails, say so clearly; do not omit the section.
- If there are no notable calendar events, say so clearly; do not omit the section.

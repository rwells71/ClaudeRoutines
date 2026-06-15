# Morning Priority Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time windows

The digest runs at 5:00 AM Mountain Time.

- **Email window**: the past 7 days ending right now.
  Gmail query filter: `newer_than:7d`
- **Calendar window (past)**: the past 7 days — to detect patterns of recurring events.
- **Calendar window (upcoming)**: today through 7 days from now, in `America/Denver` timezone —
  to surface out-of-the-ordinary events coming up.

---

## Step 2 — Fetch emails from the past 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 100

Repeat with `pageToken` if the response includes one, until all threads are collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to assess urgency, action items, or key details, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch calendar events

### 3a — Fetch upcoming events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601 with offset)
- `endTime`: 7 days from now at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

### 3b — Identify "out of the ordinary" events

From the upcoming events, flag an event as **out of the ordinary** if it meets
ANY of the following criteria:

1. **Non-recurring**: the event does NOT have a `recurringEventId` or `recurrence` field
   (it is a one-time event not part of a repeating series).
2. **Unusual time**: starts before 7:00 AM or after 7:00 PM Mountain Time.
3. **All-day event**: the event has a `date` field instead of `dateTime`.
4. **Many attendees**: has 5 or more attendees (including organizer).
5. **External attendees**: attendees whose email domain differs from the account
   owner's email domain.
6. **New or recently modified**: `created` or `updated` timestamp is within the
   past 48 hours.
7. **Unusual duration**: shorter than 15 minutes or longer than 4 hours.
8. **Contains special keywords**: title or description contains words like
   "urgent", "emergency", "offsite", "conference", "interview", "deadline",
   "due", "launch", "demo", "review", "board", "all-hands", "all hands".

Collect all out-of-the-ordinary events along with the reason(s) they were flagged.

---

## Step 4 — Build the Top 10 Priority List

Analyze ALL emails from Step 2 and ALL out-of-the-ordinary calendar events from Step 3.
Your goal is to rank the 10 most important things the account owner needs to address.

**Scoring guidance** (higher score = higher priority):
- Explicit deadline or time-sensitive language ("today", "by EOD", "ASAP", "urgent") → very high
- Direct question or request requiring a reply → high
- Financial, legal, or compliance matters → high
- Email from a known VIP (boss, major client, board member) → high
- Calendar event requiring preparation or decision → medium-high
- Unanswered thread older than 3 days → medium
- Upcoming out-of-the-ordinary event in the next 48 hours → high
- Out-of-the-ordinary event more than 2 days away → medium

**For each item in the Top 10**:
- **Rank**: 1 (most urgent) through 10
- **Type**: EMAIL or CALENDAR
- **Title/Subject**: the email subject or event title
- **Why it matters**: 1–2 sentences explaining the urgency or significance
- **Action needed**: one specific, concrete action the owner should take
  (e.g. "Reply to Alice by 3 PM confirming budget approval",
   "Block 30 min before the 9 AM interview to review candidate's resume")
- **Deadline/Date**: the relevant date or time, if applicable

If fewer than 10 items qualify, list as many as exist — do not pad with low-priority items.

---

## Step 5 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. The address appearing most
   frequently is almost certainly the account owner's address — use that.
2. If tied, prefer the address whose domain matches the majority of other "To:" addresses.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Priorities — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Priorities — Friday, April 25, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 720px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  &#9989; Morning Priorities &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; Top items from the past 7 days</p>

<!-- ====== TOP 10 SECTION ====== -->
<h3 style="margin-top: 24px;">&#128204; Top 10 Items to Address</h3>

<!-- Repeat the block below for each ranked item, #1 first -->
<div style="margin-bottom: 18px; padding: 14px; background: #f9f9f9; border-left: 5px solid {BORDER_COLOR}; border-radius: 3px;">
  <p style="margin: 0 0 4px 0; font-size: 0.82em; color: #888; text-transform: uppercase; letter-spacing: 0.05em;">
    #{RANK} &bull; {TYPE} {TYPE_ICON}
  </p>
  <p style="margin: 0 0 6px 0; font-size: 1.05em; font-weight: bold;">{TITLE_OR_SUBJECT}</p>
  <p style="margin: 0 0 4px 0; color: #444;">{WHY_IT_MATTERS}</p>
  <p style="margin: 0 0 4px 0;">
    <strong>&#128073; Action:</strong> {ACTION_NEEDED}
  </p>
  <!-- Only include the line below if a deadline/date exists -->
  <p style="margin: 4px 0 0 0; font-size: 0.88em; color: #C0392B;">
    <strong>&#128197; By:</strong> {DEADLINE_OR_DATE}
  </p>
</div>
<!-- End ranked item block -->

<!-- BORDER_COLOR guidance:
     #E74C3C = red   → rank 1-3 (critical)
     #E67E22 = orange → rank 4-6 (important)
     #27AE60 = green  → rank 7-10 (noteworthy)
-->

<!-- If no priority items exist, replace all ranked blocks with: -->
<!-- <p><em>No significant action items found in the past 7 days. Nice!</em></p> -->

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR SECTION ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>
<p style="font-size: 0.88em; color: #666;">Events flagged as unusual — new, non-recurring, after-hours, large/external attendance, or keyword-triggered.</p>

<!-- Repeat for each flagged calendar event -->
<div style="margin-bottom: 12px; padding: 10px 14px; background: #fffbf0; border-left: 4px solid #F39C12; border-radius: 3px;">
  <p style="margin: 0; font-weight: bold;">{EVENT_TITLE}</p>
  <p style="margin: 3px 0 0 0; font-size: 0.9em; color: #555;">
    &#128336; {START_TIME} &ndash; {END_TIME} MT &bull; {DATE}
  </p>
  <!-- Only include lines below if data exists -->
  <p style="margin: 3px 0 0 0; font-size: 0.88em; color: #555;">&#128205; {LOCATION_OR_LINK}</p>
  <p style="margin: 3px 0 0 0; font-size: 0.88em; color: #888;">&#9888;&#65039; Flagged: {REASON_FLAGGED}</p>
</div>
<!-- End event block -->

<!-- If no out-of-the-ordinary events, replace with: -->
<!-- <p><em>No unusual calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &mdash; covers emails from the past 7 days</p>

</body>
</html>
```

### 6b — Move the draft to Inbox

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

- The Top 10 must be genuinely the 10 most important items — prioritize ruthlessly.
- Keep "Why it matters" to 1–2 sentences. No padding.
- Action items must be concrete and specific, not vague ("Reply to Alice confirming
  approval by EOD Friday", not "Follow up with Alice").
- If a calendar event appears in both the Top 10 and the out-of-the-ordinary
  section, include it in both — they serve different purposes.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Do not include emails that are clearly automated (noreply, newsletters, etc.)
  even if they look interesting.
- If there are no qualifying emails and no out-of-the-ordinary events, still
  send the digest saying so — the owner needs to know the check ran.

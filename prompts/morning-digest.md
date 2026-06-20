# Morning Priority Digest

You are running an automated morning priority digest for richardlwells@gmail.com.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the last 7 days (past week).
  Gmail query: `newer_than:7d`
- **Calendar window**: today (the current date in Mountain Time), from
  `00:00:00` to `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the past week

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 200 threads total).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch today's out-of-the-ordinary calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset,
  e.g. `2026-06-20T00:00:00-06:00`)
- `endTime`: today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **keep only events where ALL of the following are true**:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are "out of the ordinary" one-time events. Drop anything that belongs to
a recurring series — daily standups, weekly syncs, etc. are excluded.

---

## Step 4 — Build the Top 10 Priority Action List

Review all emails and calendar events collected above. Your goal is to surface
the **10 most important things the account owner needs to act on or be aware of
today**, ranked from most to least urgent.

**Ranking criteria (apply in this order):**
1. **Hard deadlines today or tomorrow** — anything explicitly time-sensitive
2. **Direct requests from real people** — replies expected, approvals or
   decisions needed, invitations requiring a response
3. **Financial matters** — invoices, payments, contracts, account issues
4. **Out-of-the-ordinary calendar events today** — one-time meetings,
   appointments, travel (include time in Mountain Time)
5. **Unresolved ongoing threads** — conversations awaiting the owner's reply
6. **Other notable items** — anything else genuinely worth acting on

For each item in the Top 10, include:
- **Action**: A single, specific, concrete action (e.g., "Reply to John Smith
  confirming the 2 PM meeting on Tuesday" — NOT "Follow up with John")
- **From**: Sender name + email, or calendar event title + time MT
- **Context**: 1–2 sentences explaining why it matters / what is at stake /
  any deadline

If there are fewer than 10 genuinely actionable items, include as many as exist.
Do not pad the list with noise or vague items.

---

## Step 5 — Compose and deliver the digest

**`to`**: `["richardlwells@gmail.com"]`

**`subject`**: `Morning Priority Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Priority Digest — Friday, June 20, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content for all
`{placeholders}`.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Priority Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">
  Generated at 5:00 AM Mountain Time &bull; Emails from the past 7 days
</p>

<!-- ====== TOP 10 PRIORITY LIST ====== -->
<h3 style="margin-top: 24px;">&#128203; Top 10 Things to Address Today</h3>

<!-- Repeat the block below for each ranked item (1 through 10) -->
<div style="margin-bottom: 14px; padding: 12px 14px; background: #f9f9f9;
     border-left: 4px solid #4A90D9; display: flex; gap: 14px;">
  <span style="font-size: 1.5em; font-weight: bold; color: #4A90D9;
       min-width: 28px; line-height: 1.2;">{#}</span>
  <div>
    <p style="margin: 0 0 5px 0; font-weight: bold; font-size: 1em;">
      {Specific action to take}
    </p>
    <p style="margin: 0 0 4px 0; color: #555; font-size: 0.88em;">
      <strong>From:</strong> {Sender Name &lt;email@example.com&gt; or Event Title}
      <!-- For calendar events, append the time: -->
      &nbsp;&bull;&nbsp;&#128336; {Start Time – End Time MT}
    </p>
    <p style="margin: 4px 0 0 0; color: #444; font-size: 0.9em;">
      {1–2 sentence context explaining why this matters or what is at stake}
    </p>
  </div>
</div>
<!-- End item block — repeat for each ranked item -->

<!-- If fewer than 10 actionable items exist, end the list early and note it: -->
<!-- <p style="color: #888; font-size: 0.9em; font-style: italic;">
       Only {N} actionable items found this week.
     </p> -->

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR SECTION ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Events Today
</h3>
<p style="color: #666; font-size: 0.85em; margin-top: -8px;">
  One-time events only &mdash; recurring meetings are excluded
</p>

<!-- Repeat for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px 14px; background: #f0f7ff;
     border-left: 4px solid #27AE60;">
  <p style="margin: 0; font-weight: bold;">
    {Start Time} &ndash; {End Time} MT &mdash; {Event Title}
  </p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 16px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 16px; color: #555;">{Brief description if present}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events today: -->
<!-- <p><em>No out-of-the-ordinary calendar events scheduled for today.</em></p> -->

<hr style="margin-top: 36px;"/>
<p style="font-size: 0.8em; color: #999;">
  Automated priority digest &mdash; ClaudeRoutines
</p>

</body>
</html>
```

### Step 5b — Deliver to Inbox

Call `create_draft` with the `to`, `subject`, and `htmlBody` fields above.

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — use the literal string `"INBOX"`. Do **not**
call `list_labels` to look it up.

This places the digest directly in the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest is
> delivered by placing it in the Inbox via label assignment. If a `send_message`
> or `send_draft` tool becomes available in a future version, prefer that.

---

## Important rules

- **Action items must be specific and concrete.** "Reply to Alice Wells
  confirming the 3 PM Thursday call" is good. "Follow up with Alice" is not.
- Skip all automated/marketing/newsletter emails entirely.
- Calendar events that appear in the Top 10 should also appear in the
  "Out-of-the-Ordinary Events" section below.
- Never include raw HTML or JSON in the digest body.
- Strip tracking pixels and HTML boilerplate from email bodies before
  summarizing.
- Multiple emails from the same sender count as separate action items only if
  each requires a distinct action; otherwise consolidate them into one item.

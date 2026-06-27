# Morning Top-10 Briefing

You are running an automated morning briefing routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the past 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today plus the next 6 days (a full 7-day look-ahead),
  starting at `00:00:00` today in Mountain Time through `23:59:59` seven days
  from now, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -in:spam -in:trash`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 150 threads max).

For each thread, examine the snippet and metadata returned. Call `get_thread`
for any thread where the snippet alone is insufficient to judge urgency or
extract action items.

**Skip** clearly automated mail: newsletters, messages from `noreply@`,
`no-reply@`, `donotreply@`, `notifications@`, `support@` (if generic/automated),
or any message with an `List-Unsubscribe` header. Include everything else —
human-sent messages, transactional mail requiring action, and important alerts.

---

## Step 3 — Fetch upcoming calendar events (7-day look-ahead)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601 with offset)
- `endTime`: 7 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

---

## Step 4 — Identify "out of the ordinary" calendar events

From the events fetched, flag any event where ONE OR MORE of the following
is true:

1. Starts before 8:00 AM or ends after 7:00 PM Mountain Time
2. Occurs on a Saturday or Sunday
3. Duration is greater than 4 hours or less than 15 minutes
4. Has 10 or more attendees
5. Title or description contains keywords like: urgent, emergency, deadline,
   offsite, travel, flight, hotel, cancelled, rescheduled, reschedule,
   important, critical, ASAP, all-hands, all hands, board, investor, legal,
   interview
6. Event is NOT part of a recurring series (no `recurringEventId` field)
   AND involves external attendees (attendees from a different email domain
   than the account owner)
7. The event was created or modified within the last 24 hours (check
   `created` or `updated` timestamps)

Build a list of flagged events with the reason(s) each was flagged.

---

## Step 5 — Build the Top 10 Action Items list

Analyze ALL emails and calendar events together. Produce a ranked list of
the **10 most important things** the account owner needs to address.

**Ranking criteria (most important first):**
1. Explicit questions or requests directed at the account owner awaiting a reply
2. Deadlines mentioned in emails that fall within the next 7 days
3. Out-of-the-ordinary calendar events (from Step 4) requiring preparation
4. Unresolved multi-message threads where the owner is expected to respond
5. Decisions or approvals requested
6. Time-sensitive opportunities (interviews, bids, confirmations)
7. Important FYI items (policy changes, significant announcements)
8. Upcoming recurring events where prep work is implied by the email thread
9. Administrative items (invoices, confirmations, bookings needing action)
10. Everything else, sorted by recency

If there are fewer than 10 genuinely actionable items, include only real ones —
do not pad with trivial items.

**For each action item include:**
- **Priority number** (1 = most urgent)
- **Title** — one clear line (e.g. "Reply to Sarah Chen re: contract extension deadline")
- **Source** — email thread subject + sender, or calendar event name + date/time
- **Context** — 1–3 sentences explaining what it is and why it matters
- **Suggested action** — specific and concrete (e.g. "Reply with approval before
  Friday EOD", "Prepare slide deck for Tuesday 10 AM", "Call back by today")

---

## Step 6 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient
   addresses. The address appearing most frequently is almost certainly the
   owner's — use that.
2. If there is a tie, prefer the address whose domain matches the majority of
   "To:" addresses.
3. If still ambiguous, use the first address found in any "To:" field.

Store this as `{owner_email}`.

---

## Step 7 — Create and deliver the digest draft

### 7a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Briefing — Top 10 Items for {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use the template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  &#9728; Morning Briefing &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Covering the last 7 days of email + next 7 days of calendar</p>

<!-- ====== TOP 10 SECTION ====== -->
<h3 style="margin-top: 28px;">&#128203; Top 10 Action Items</h3>

<!-- Repeat this block for each action item, 1 through 10 (or fewer if warranted) -->
<div style="margin-bottom: 16px; padding: 14px; background: #f9f9f9; border-left: 4px solid #4A90D9; border-radius: 2px;">
  <p style="margin: 0 0 4px 0; font-size: 1.05em;">
    <strong>#{priority} &mdash; {Title}</strong>
  </p>
  <p style="margin: 0 0 4px 0; color: #555; font-size: 0.88em;">
    &#128196; {Source}
  </p>
  <p style="margin: 4px 0;">{Context}</p>
  <p style="margin: 4px 0; background: #e8f4fd; padding: 6px 10px; border-radius: 2px;">
    <strong>&#9654; Action:</strong> {Suggested action}
  </p>
</div>
<!-- End action item block -->

<!-- If no actionable items found: -->
<!-- <p><em>No actionable items found in the last 7 days. Enjoy the quiet!</em></p> -->

<!-- ====== OUT-OF-ORDINARY CALENDAR SECTION ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each flagged event -->
<div style="margin-bottom: 12px; padding: 10px; background: #fff8e1; border-left: 4px solid #F5A623; border-radius: 2px;">
  <p style="margin: 0;"><strong>{Date} &bull; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">&#9888;&#65039; <em>Flagged because: {reason(s)}</em></p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description if available}</p>
</div>
<!-- End flagged event block -->

<!-- If no flagged events: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated briefing &mdash; ClaudeRoutines &bull; Unsubscribe by removing the morning-digest.yml workflow.</p>

</body>
</html>
```

### 7b — Move the draft to the Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

This delivers the draft to the Inbox so it arrives like a normal email rather
than sitting silently in Drafts.

> **Note**: The Gmail MCP does not expose a send API. Delivery is achieved by
> labeling the draft with `INBOX`. If a `send_draft` tool is added in the
> future, prefer it.

---

## Important rules

- **Be specific**: name the sender, subject, date, and exact action needed.
  Never use vague actions like "follow up" — say exactly what to do.
- **No padding**: only include items that genuinely require the owner's
  attention. A top-8 list is better than a padded top-10.
- **Calendar events in the Top 10**: if an out-of-the-ordinary calendar event
  also implies email prep or a required action, include it in the Top 10 *and*
  in the calendar section.
- **Dedup**: if an email thread and a calendar event are about the same topic,
  merge them into one action item.
- **Strip noise**: remove tracking pixels and HTML boilerplate from email
  bodies before summarizing.
- **Never include raw HTML or JSON** in the digest body.

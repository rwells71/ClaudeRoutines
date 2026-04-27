# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (i.e. the last week).
  Gmail query: `newer_than:7d`
- **Calendar window**: today (the current date in Mountain Time), from
  `00:00:00` to `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to a maximum of 200 threads).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch today's non-recurring calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **keep only events where ALL of the following are true**:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are genuinely one-time, out-of-the-ordinary events. Drop anything that
belongs to a recurring series (e.g. weekly standups, daily meetings).

---

## Step 4 — Build the Top 10 action items list

### Prioritization criteria

Review all qualifying emails from the last 7 days. For each email, identify
any concrete action required of the account owner. Then rank every action item
by **priority**, using these factors (highest weight first):

1. **Explicit deadline or urgency signal** — words like "urgent", "ASAP",
   "by [date]", "deadline", "today", "this week"
2. **Direct question or request** from a known human sender
3. **Financial or legal content** — invoices, contracts, approvals required
4. **Meeting or event coordination** — scheduling, RSVPs, agenda items
5. **Recency** — more recent emails rank higher when other factors are equal

Select the **top 10** highest-priority action items across all emails. If
fewer than 10 qualifying action items exist, include all of them.

For each action item in the top 10, record:
- **Priority rank** (1 = most urgent)
- **Action**: one concrete sentence describing what must be done
  (e.g. "Reply to Alice by Friday confirming attendance at the board meeting")
- **Source**: sender name + subject line + email date
  (e.g. "Alice Smith — 'Board Meeting' — Apr 23")
- **Context**: 1–2 sentences of background if needed to act without opening
  the email

### Calendar action items

If any non-recurring calendar events were found in Step 3, also note any
preparation or logistics required for each event
(e.g. "Prepare slides for 2 PM client presentation"). These do not count
against the top-10 email action items limit.

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

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Friday, April 25, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#128221; Top 10 Action Items &mdash; Last 7 Days</h3>

<!-- Repeat the block below for each action item (rank 1 through 10) -->
<div style="margin-bottom: 16px; padding: 12px; background: #f9f9f9; border-left: 4px solid #4A90D9; border-radius: 2px;">
  <p style="margin: 0 0 4px 0;">
    <span style="font-size: 1.1em; font-weight: bold; color: #4A90D9;">#{Rank}</span>
    &nbsp;<strong>{Action — one concrete sentence}</strong>
  </p>
  <p style="margin: 4px 0 0 0; font-size: 0.85em; color: #555;">
    <strong>Source:</strong> {Sender Name} &mdash; &ldquo;{Subject}&rdquo; &mdash; {Date}
  </p>
  <!-- Only include if context helps the reader act without opening the email -->
  <p style="margin: 4px 0 0 0; font-size: 0.85em; color: #666;">{1–2 sentence context}</p>
</div>
<!-- End action item block -->

<!-- If no qualifying action items were found, replace all blocks with: -->
<!-- <p><em>No action items found in emails from the last 7 days.</em></p> -->

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events Today
</h3>

<!-- Repeat for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60; border-radius: 2px;">
  <p style="margin: 0;"><strong>{Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
  <!-- Only include if preparation is needed -->
  <p style="margin: 4px 0 0 18px; color: #E67E22;"><strong>Prep needed:</strong> {preparation action}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events today, replace event blocks with: -->
<!-- <p><em>No out-of-the-ordinary calendar events scheduled for today.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Label the draft for delivery

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

- If there are **no action items**, say so clearly; do not omit the section.
- If there are **no non-recurring calendar events**, say so clearly; do not omit the section.
- Action items must be concrete ("Reply to Alice confirming the meeting time by Friday"),
  not vague ("Follow up" or "Handle email").
- Prioritize ruthlessly: only the genuinely most time-sensitive and impactful items
  make the top 10.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Do not include automated notifications, marketing, or newsletters as action items.

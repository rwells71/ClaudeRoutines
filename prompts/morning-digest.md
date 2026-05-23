# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the past 7 days (last week).
  Gmail query: `newer_than:7d`
- **Calendar window**: the next 7 days starting from today in Mountain Time,
  timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

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
message with an `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch upcoming non-recurring calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-05-23T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, **keep only events where ALL of the following are true**:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are genuinely one-time / out-of-the-ordinary events. Drop anything that
belongs to a recurring series.

---

## Step 4 — Build the Top 10 Action List

Analyze all collected emails and non-recurring calendar events together.
Extract every concrete action item, decision needed, deadline, or important
event. Then **rank them by urgency and importance** and select the top 10.

Ranking criteria (apply in order):
1. Hard deadlines (explicit dates/times mentioned)
2. Time-sensitive requests from humans (waiting on your reply)
3. Upcoming one-time calendar events (soonest first)
4. Financial, legal, or health-related items
5. Items from known important contacts (boss, family, clients)
6. Everything else, by recency

For each of the top 10 items, record:
- **Source**: email subject + sender, or calendar event title
- **Why it matters**: one sentence
- **What to do**: one concrete action ("Reply to X confirming Y", "Attend Z at 2 PM", "Sign document by Friday")
- **Deadline or date** (if known)

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

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Friday, May 23, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; covering the past 7 days</p>

<!-- ====== TOP 10 ACTION LIST ====== -->
<h3 style="margin-top: 28px;">&#9989; Top 10 Items to Address</h3>
<p style="color: #555; font-size: 0.9em;">Ranked by urgency and importance.</p>

<!-- Repeat the block below for each of the 10 items, numbered 1–10 -->
<div style="margin-bottom: 16px; padding: 12px; background: #f9f9f9; border-left: 4px solid #4A90D9; display: flex; gap: 12px;">
  <div style="font-size: 1.4em; font-weight: bold; color: #4A90D9; min-width: 28px;">{N}</div>
  <div>
    <p style="margin: 0 0 4px 0; font-weight: bold;">{Source — email subject + sender, or calendar event title}</p>
    <p style="margin: 0 0 4px 0; color: #555;">{Why it matters — one sentence}</p>
    <p style="margin: 0 0 4px 0;"><strong>Action:</strong> {Concrete action to take}</p>
    <!-- Only include the line below if a deadline or date is known -->
    <p style="margin: 0; color: #c0392b;"><strong>By:</strong> {Deadline or event date/time}</p>
  </div>
</div>
<!-- End item block -->

<!-- If fewer than 10 actionable items exist, include as many as found and note it -->
<!-- <p><em>Only {N} actionable items found in the last 7 days.</em></p> -->

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>
<p style="color: #555; font-size: 0.9em;">One-time events only — recurring meetings are excluded.</p>

<!-- Repeat for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Day, Month Date} &mdash; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events in the next 7 days: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Move the draft to the Inbox

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

- The Top 10 list is the primary deliverable — make it genuinely useful and prioritized.
- If there are **fewer than 10 actionable items**, include all of them and note the count.
- If there are **no qualifying emails**, say so clearly; do not omit the email section.
- If there are **no non-recurring calendar events**, say so clearly.
- Action items must be concrete ("Reply to Alice confirming the meeting time") not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Do not include items already clearly resolved or acknowledged in a later email in the same thread.

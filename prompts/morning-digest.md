# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (i.e. the last week).
  Gmail query: `newer_than:7d`
- **Calendar window**: today through the next 7 days (the current date through
  +7 days in Mountain Time), from `00:00:00` today to `23:59:59` seven days
  out, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social in:inbox`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 3 pages maximum).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses,
calendar notification emails, and any message with a `List-Unsubscribe`
header. Include everything else — transactional, human-sent, or important
system notifications that require action (e.g., fraud alerts, pending
approvals, shared documents).

---

## Step 3 — Fetch non-recurring calendar events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset,
  e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: 7 days from now at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, **keep only events where ALL of the following are true**:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are genuinely one-time events. Drop anything that belongs to a
recurring series.

---

## Step 4 — Produce the Top 10 Action Items and Calendar Highlights

### 4a — Top 10 Email Action Items

Review all emails collected in Step 2. Identify every concrete action the
account owner needs to take. Then rank them by urgency and importance:

**Ranking criteria (highest priority first):**
1. Deadlines or time-sensitive requests (today or very soon)
2. Financial matters (fraud alerts, pending approvals, transactions)
3. Requests from family members or close contacts
4. Work/professional obligations
5. Community/organizational duties
6. Everything else

Select the **top 10** highest-priority action items. For each, produce a
single numbered entry in this format:

```
N. [ACTION VERB] — Brief description of what to do
   From: Sender Name | Subject: Email subject line
   Why urgent: One sentence explaining the priority
```

Example:
```
1. REVIEW — Possible fraudulent card charge at STEAMGAMES.COM for $16.12
   From: Fidelity Alerts | Subject: Your Fidelity card was not present during a recent purchase
   Why urgent: Potential unauthorized transaction — verify or dispute immediately
```

If fewer than 10 actionable items exist, list all of them and note that no
further actions were found.

### 4b — Notable Calendar Events (Next 7 Days)

For each non-recurring event identified in Step 3, list:
- Date and start–end time (Mountain Time, e.g. "Thu Jun 5 · 9:00 AM – 10:00 AM MT")
- Event title
- Location or video link (if present)
- One-line description excerpt (if present)

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

## Step 6 — Create and deliver the digest draft

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
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &mdash; Email window: last 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#9989; Top 10 Action Items</h3>

<!-- Repeat the block below for each action item, #1 through #10 -->
<div style="margin-bottom: 14px; padding: 12px; background: #f9f9f9; border-left: 4px solid #E74C3C;">
  <p style="margin: 0 0 4px 0;">
    <strong style="font-size: 1.05em;">{N}. {ACTION VERB} &mdash; {Brief description}</strong>
  </p>
  <p style="margin: 0 0 2px 0; color: #555; font-size: 0.9em;">
    <strong>From:</strong> {Sender Name} &nbsp;|&nbsp; <strong>Subject:</strong> {Email subject}
  </p>
  <p style="margin: 0; color: #888; font-size: 0.85em; font-style: italic;">
    {Why urgent — one sentence}
  </p>
</div>
<!-- End action item block -->

<!-- If no actionable emails found: -->
<!-- <p><em>No action items found in the last 7 days.</em></p> -->

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each non-recurring event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Day, Date} &middot; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events in the next 7 days: -->
<!-- <p><em>No one-time calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 6b — Deliver the draft to the Inbox

After `create_draft` returns a `messageId`, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

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

- If there are **no actionable emails**, say so clearly; do not omit the section.
- If there are **no non-recurring calendar events**, say so clearly; do not omit the section.
- Action items must be concrete ("Reply to Alice confirming the meeting time")
  not vague ("Follow up").
- Keep the why-urgent sentence to one line — factual, not padded.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Calendar notifications from `calendar-notification@google.com` are **not**
  action items; skip them entirely in Step 2.

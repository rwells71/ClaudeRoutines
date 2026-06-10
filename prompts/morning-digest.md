# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days from now (Mountain Time), from
  today at `00:00:00` to 7 days from now at `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates`
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

## Step 3 — Fetch upcoming non-recurring calendar events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-04-25T00:00:00-06:00`)
- `endTime`: 7 days from now at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **keep only events where ALL of the following are true**:
1. The event does NOT have a `recurringEventId` field.
2. The event does NOT have a `recurrence` field.

These are genuinely one-time ("out of the ordinary") events. Drop anything
that belongs to a recurring series.

---

## Step 4 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient
   addresses. The address that appears most frequently is almost certainly the
   account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of
   the other addresses in the "To:" fields.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 5 — Build the Top 10 Priority Action Items

From all emails and non-recurring calendar events collected, extract every
explicit or implied action required of the account owner. Then select the
**top 10** most important ones, ranked by this priority order (highest first):

1. Hard deadlines due today or tomorrow
2. Replies explicitly requested by the sender
3. Time-sensitive decisions, approvals, or sign-offs needed
4. Non-recurring calendar events in the next 48 hours that require preparation
5. Requests from key stakeholders (clients, managers, partners)
6. Financial, legal, or compliance matters
7. Items mentioned in multiple threads or by multiple people
8. Everything else by recency (newest first)

Format each item as a single, complete, actionable sentence that specifies:
**what to do**, **who it involves**, and **when it's due** (if known).

Example: *"Reply to Jane Smith confirming the contract terms by end of day today."*

If fewer than 10 action items exist across all emails and calendar events,
list all of them; do not pad with filler.

---

## Step 6 — Summarize emails by sender

Group by sender (use the sender's display name and email address as the heading).
For each sender, list every email they sent in the 7-day window. For each email:
- Subject line
- 2–4 bullets covering the key points
- A separate "Action Items" section with concrete, specific tasks required of
  the reader (omit this section if there are none)

---

## Step 7 — Create and deliver the digest

### 7a — Create the draft

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

<!-- ====== TOP 10 SECTION ====== -->
<h3 style="margin-top: 28px; color: #C0392B;">&#128204; Top 10 Items to Address</h3>
<ol style="line-height: 1.9; padding-left: 20px;">
  <li style="margin-bottom: 6px;">{Action item 1 — highest priority}</li>
  <li style="margin-bottom: 6px;">{Action item 2}</li>
  <li style="margin-bottom: 6px;">{Action item 3}</li>
  <li style="margin-bottom: 6px;">{Action item 4}</li>
  <li style="margin-bottom: 6px;">{Action item 5}</li>
  <li style="margin-bottom: 6px;">{Action item 6}</li>
  <li style="margin-bottom: 6px;">{Action item 7}</li>
  <li style="margin-bottom: 6px;">{Action item 8}</li>
  <li style="margin-bottom: 6px;">{Action item 9}</li>
  <li style="margin-bottom: 6px;">{Action item 10 — lowest priority}</li>
</ol>
<!-- If fewer than 10 action items exist, list all of them. Do not pad. -->

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each non-recurring event, ordered by date/time -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;"><strong>{Day, Month Date} &mdash; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include the lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">{Brief description excerpt}</p>
</div>
<!-- End event block -->

<!-- If no non-recurring events, replace event blocks with: -->
<!-- <p><em>No out-of-the-ordinary events in the next 7 days.</em></p> -->

<!-- ====== EMAIL SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128139; Full Email Summary &mdash; Last 7 Days
</h3>

<!-- Repeat the block below for each unique sender -->
<div style="margin-bottom: 20px; padding: 12px; background: #f9f9f9; border-left: 4px solid #4A90D9;">
  <h4 style="margin: 0 0 6px 0;">{Sender Name} &lt;{sender@example.com}&gt;</h4>
  <p style="margin: 0 0 4px 0;"><strong>Subject:</strong> {email subject}</p>
  <ul style="margin: 4px 0 0 0;">
    <li><strong>Key Points:</strong>
      <ul>
        <li>{point 1}</li>
        <li>{point 2}</li>
      </ul>
    </li>
    <!-- Only include if there are action items -->
    <li><strong>Action Items:</strong>
      <ul>
        <li>{action item}</li>
      </ul>
    </li>
  </ul>
</div>
<!-- End sender block -->

<!-- If no qualifying emails were found, replace sender blocks with: -->
<!-- <p><em>No emails received in the last 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines</p>

</body>
</html>
```

### 7b — Move the draft to Inbox

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

- The Top 10 list must appear first in the email, before the calendar and email sections.
- If there are **no emails**, say so clearly; do not omit the section.
- If there are **no non-recurring calendar events**, say so clearly; do not omit the section.
- Keep email summaries concise: maximum 4 bullets per email.
- Action items must be concrete ("Reply to Alice confirming the meeting time")
  not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If multiple emails from the same sender arrive in the window, group them all
  under one sender heading with separate subject/key-points/action-items blocks.

# Morning Priority Digest

You are running an automated morning priority digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days from now (Mountain Time),
  timezone `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -in:sent`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, collecting up to 3 pages total.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with a `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch "out of the ordinary" calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-06-19T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, flag an event as **"out of the ordinary"** if ANY of the following are true:
1. It does NOT have a `recurringEventId` or `recurrence` field (genuine one-time event).
2. It starts before 8:00 AM or ends after 7:00 PM local time (outside normal hours).
3. It is an all-day event (could signal travel, a holiday, or a special occasion).
4. It has more than 8 attendees.
5. It involves an unusual or unfamiliar location (not a commonly recurring meeting room or video link).

Keep only events that meet at least one criterion. Drop everything else.

---

## Step 4 — Build the Top 10 Action Items List

Review all emails collected. For each email that requires a response, decision,
or action from the account owner, extract the specific action needed.

**Score each action item** for urgency and importance:
- +3 points if the sender is explicitly waiting on a reply (direct question or request addressed to the owner)
- +3 points if a deadline is mentioned within the next 3 days
- +2 points if a deadline is mentioned within the next 7 days
- +2 points if the email is from an executive, client, or external party
- +2 points if the email involves money, contracts, or legal matters
- +1 point if the email is unread
- +1 point if there are multiple follow-up messages on the same thread

Select the **top 10 highest-scoring action items**. If fewer than 10 qualify, list all of them.

For each item note:
- **Rank** (#1 = most urgent)
- **Action**: The specific thing the owner needs to do — be concrete ("Reply to Alice confirming the 3 PM Thursday meeting time", not "Follow up")
- **From**: Sender name and email address
- **Subject**: Email subject line
- **Why urgent**: One short phrase (e.g. "Client deadline Friday", "Reply requested", "Unread 5 days")

---

## Step 5 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient
   addresses. The address that appears most frequently is almost certainly the
   account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of
   the other "To:" addresses.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with the following fields:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Friday, June 19, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  Morning Priority Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Top actions from the past 7 days</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px;">&#128204; Top 10 Email Action Items</h3>

<!-- Repeat the block below for each action item, #1 (most urgent) first -->
<div style="margin-bottom: 16px; padding: 12px; background: #f9f9f9; border-left: 4px solid #E74C3C;">
  <p style="margin: 0 0 4px 0;">
    <strong style="font-size: 1.1em;">#1</strong>
    &nbsp;&mdash;&nbsp;
    <strong>{Specific action the owner must take}</strong>
  </p>
  <p style="margin: 4px 0 0 0; font-size: 0.9em; color: #555;">
    <strong>From:</strong> {Sender Name} &lt;{sender@example.com}&gt;
    &nbsp;&bull;&nbsp;
    <strong>Subject:</strong> {email subject}
    &nbsp;&bull;&nbsp;
    <strong>Why urgent:</strong> {one short phrase}
  </p>
</div>
<!-- End action item block — repeat up to 10 times -->

<!-- If no action items were found, replace blocks with: -->
<!-- <p><em>No action items found in the last 7 days.</em></p> -->

<!-- ====== CALENDAR SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each flagged event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f0f7ff; border-left: 4px solid #27AE60;">
  <p style="margin: 0;">
    <strong>{Day of week, Month Day} &bull; {Start Time} &ndash; {End Time} MT</strong>
    &mdash; {Event Title}
  </p>
  <p style="margin: 4px 0 0 18px; font-size: 0.85em; color: #555;">
    &#128204; Why notable: {one-line reason, e.g. "One-time event", "Starts at 6:30 AM", "All-day event — possible travel", "18 attendees"}
  </p>
  <!-- Only include the lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
</div>
<!-- End event block -->

<!-- If no flagged events in the next 7 days, replace event blocks with: -->
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

This moves the draft into the Inbox so it arrives like a normal email rather
than sitting silently in Drafts.

> **Note**: The Gmail MCP integration does not expose a send API. The digest is
> delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- Action items must be **concrete and specific** — name the person, the decision, or the exact reply required.
- Never write vague items like "Review email" or "Follow up". If an email requires no action, skip it.
- The #1 item must be the single most time-sensitive or highest-stakes action.
- If one email thread has multiple action items, list only the most critical one and mention the others in the "Why urgent" field.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If there are **no action items**, say so clearly in that section; do not omit the section.
- If there are **no out-of-ordinary calendar events**, say so clearly in that section; do not omit the section.

# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (the last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window**: the next 7 days from today (current date in Mountain Time),
  from `00:00:00` today to `23:59:59` seven days from now, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (max 3 pages).

For each thread, examine the snippet and message metadata. If the full body is
needed to determine action items, call `get_thread` with that thread's ID.

**Skip** clearly automated, non-actionable mail: bulk newsletters, marketing
emails from brands, and purely informational notifications with no action
required. **Include** anything that requires a response, a decision, money,
a task, or a deadline.

---

## Step 3 — Fetch upcoming calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601, e.g. `2026-05-31T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, identify **out-of-the-ordinary** events by flagging any event
that meets at least one of these criteria:
1. No `recurringEventId` — it is a one-time event.
2. Has a dollar amount, financial obligation, or payment in the title/description.
3. Involves an unusual time (before 6 AM or after 10 PM).
4. Has external attendees beyond the account owner and their household.
5. Has a location that is not home, church, or a regular recurring venue.
6. Involves a deadline, confirmation needed, or has "confirm," "follow up," or
   "action" in the title.
7. Is a farewell, award, ceremony, celebration, or special appointment.

---

## Step 4 — Build the Top 10 Action Items list

Review all emails and flagged calendar events together. Identify the 10 most
time-sensitive or important items the account owner must personally act on.

Rank them by urgency (deadlines first, then financial, then relationship/social,
then everything else). For each item write:
- A short, bold headline (e.g. **Renew Atlassian API Token by June 30**)
- The source (email from X / calendar event on DATE)
- One concrete action sentence

If fewer than 10 genuinely actionable items exist, list only the real ones.

---

## Step 5 — Determine the account owner's email address

Use the following strategy, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient
   addresses. The most frequently appearing address is the account owner's.
2. If there is a tie, prefer the address whose domain matches the majority.
3. If still ambiguous, use the first address found in any "To:" field.

Store this as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222; padding: 20px;">

<h2 style="color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 8px;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Covers last 7 days of email + next 7 days of calendar</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 28px; color: #c0392b;">&#9989; Top 10 Action Items</h3>
<ol style="line-height: 2.2;">
  <!-- Repeat for each action item, ranked by urgency -->
  <li>
    <strong>{Action Item Headline}</strong><br>
    <span style="color: #555; font-size: 0.9em;">Source: {email from X / calendar on DATE}</span><br>
    <span>{One concrete action sentence.}</span>
  </li>
  <!-- End action item -->
</ol>

<!-- ====== UNUSUAL CALENDAR EVENTS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px; color: #8e44ad;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each flagged calendar event -->
<div style="margin-bottom: 12px; padding: 10px; background: #f9f0ff; border-left: 4px solid #8e44ad;">
  <p style="margin: 0;"><strong>{Start Time} &ndash; {End Time} MT, {Date}</strong> &mdash; {Event Title}</p>
  <p style="margin: 4px 0 0 18px; color: #555;">Why flagged: {one-line reason}</p>
  <!-- Only include if data exists -->
  <p style="margin: 4px 0 0 18px; color: #555;">&#128205; {Location or video link}</p>
</div>
<!-- End calendar event -->

<!-- If no flagged events, replace blocks with: -->
<!-- <p><em>No out-of-the-ordinary events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &bull; Sent daily at 5 AM MT</p>

</body>
</html>
```

### 6b — Deliver to inbox

After `create_draft` returns an ID, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

This delivers the draft directly to the Inbox. Use the literal string `"INBOX"` —
do not call `list_labels` to look it up.

---

## Important rules

- Rank action items by deadline/urgency, not by email arrival order.
- Each action item must be **concrete and personal** to the account owner.
  Bad: "Follow up." Good: "Reply to Sherrie Anthony confirming newsletter submission."
- Flag calendar events conservatively — only genuinely unusual ones. Skip
  recurrences that are normal weekly activities (bishopric meeting, family dinner,
  YM, karate, etc.) unless they have something extra attached this week.
- Strip tracking pixels and HTML boilerplate before summarizing.
- Never include raw HTML or JSON in the digest body.
- If fewer than 3 action items exist, say so; never pad with trivial items.

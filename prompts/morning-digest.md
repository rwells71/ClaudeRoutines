# Morning Email & Calendar Digest — Top 10 Daily Summary

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the last 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days ahead (Mountain Time), from
  today at `00:00:00` to 7 days later at `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (max 150 threads total).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID — but only do so for threads that appear
to require human action (questions, approvals, confirmations, deadlines).

**Skip** clearly automated mail: pure marketing emails, newsletters, and any
message where the sender address starts with `noreply@`, `no-reply@`, or
`donotreply@`. **Keep** transactional emails (orders, deliveries, statements,
approvals), any human-sent messages, and important system notifications.

---

## Step 3 — Fetch upcoming calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601 with offset)
- `endTime`: 7 days later at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, identify **unusual or noteworthy** events. An event is
unusual if ANY of the following apply:
1. It does NOT have a `recurringEventId` field (a genuine one-time event).
2. Its title suggests an unusual action (e.g. giving things away, a
   cancellation, a one-off task, a meeting outside normal hours).
3. It was created or updated within the last 72 hours (check `updated` field).
4. It starts before 6 AM or after 9 PM (unusually early or late).
5. It spans more than 4 hours on a normally busy day.
6. An attendee has responded "declined" (potential scheduling conflict).

---

## Step 4 — Rank and select the Top 10 action items

From all emails and calendar events collected, identify items that require
the account owner to **do something**. Score and rank them by priority:

- **Urgent / time-sensitive** (deadlines today or tomorrow, approvals, financial
  alerts, deliveries) — rank highest
- **People-dependent** (someone waiting on a reply, a group message unanswered,
  a follow-up needed on someone's wellbeing) — rank second
- **Task reminders** (recurring to-dos with a clear next action, school
  deadlines, maintenance items) — rank third
- **Informational but actionable** (statements ready, order shipped, report
  available) — rank fourth

Select the top 10. If fewer than 10 exist, list all. Number them 1–10 with #1
being the highest priority.

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

<h2 style="border-bottom: 2px solid #2c5f8a; padding-bottom: 8px; color: #2c5f8a;">
  &#128203; Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &bull; Reviewing last 7 days of email + upcoming calendar</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="margin-top: 24px; color: #c0392b;">&#128680; Top 10 Items to Address</h3>

<ol style="line-height: 2.2; padding-left: 20px;">
  <!-- Repeat <li> block for each of the 10 items -->
  <li>
    <strong>{Short title of item}</strong> &mdash; {1–2 sentence explanation of
    what needs to be done, by when, and why it matters. Be specific: name
    amounts, people, deadlines.}
  </li>
  <!-- ... items 2–10 ... -->
</ol>

<!-- If fewer than 10 actionable items exist, note it at the end of the list:
     <p><em>Only {N} actionable items found this period.</em></p> -->

<!-- ====== UNUSUAL CALENDAR EVENTS ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px; color: #e67e22;">
  &#128197; Unusual or Noteworthy Calendar Events
</h3>

<!-- Repeat the block below for each unusual event -->
<div style="margin-bottom: 12px; padding: 10px; background: #fff8f0; border-left: 4px solid #e67e22;">
  <p style="margin: 0;">
    <strong>{Day, Date} &bull; {Start Time} &ndash; {End Time} MT</strong>
    &mdash; {Event Title}
  </p>
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">
    {Why this event is unusual or what makes it noteworthy — one sentence.}
  </p>
  <!-- Only include if present: -->
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">
    &#128205; {Location or video link}
  </p>
</div>
<!-- End event block -->

<!-- If no unusual events: -->
<!-- <p><em>No unusual calendar events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">
  Automated digest &mdash; ClaudeRoutines &bull; Items ranked by priority.
</p>

</body>
</html>
```

### 6b — Move the draft to Inbox

After `create_draft` returns a draft `id`, call `search_threads` with:
- `query`: `subject:"Morning Digest" in:draft newer_than:1h`
- `pageSize`: 1

Take the `id` from the first message in the first thread returned. Then call
`label_message` with:
- `messageId`: that message `id`
- `labelIds`: `["INBOX", "UNREAD"]`

This moves the digest to the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- Top 10 list items must be **concrete and specific** — name the person, amount,
  deadline, or platform involved. Not "follow up" but "Reply to Brian Coutts
  about the 3 remaining trek youth by Wednesday."
- Rank ruthlessly: #1 should be the single most urgent thing.
- Unusual calendar events section is **separate** from the top 10 — include
  calendar items in the top 10 only if they require direct action.
- Keep each top-10 entry to 1–2 sentences max.
- Never include raw HTML, JSON, or tracking pixels in the digest body.
- If multiple related emails form a single action item, group them as one entry.

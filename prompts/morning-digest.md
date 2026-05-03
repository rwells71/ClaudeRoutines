# Morning Email & Calendar Digest — Weekly Top 10

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time windows

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (i.e. the last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window**: today plus the next 7 days in Mountain Time, from
  today at `00:00:00` to 7 days from now at `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch emails from the last 7 days

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -in:spam -in:trash`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (max 3 pages).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID — but only for threads where the snippet
suggests an action is needed.

**Skip** clearly automated bulk mail: marketing, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses (unless
the notification contains a time-sensitive alert like a fraud warning, bill due,
or security alert). Include everything else — transactional, human-sent, and
important system notifications.

---

## Step 3 — Fetch upcoming and unusual calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-05-03T00:00:00-06:00`)
- `endTime`: 7 days from now at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`

From the results, **flag as "out of the ordinary"** any event where ANY of the following is true:
1. The event does NOT have a `recurringEventId` field (one-time event).
2. The event has a `recurringEventId` but the summary contains words like
   "special", "graduation", "rehearsal", "showcase", "conference", "retreat",
   "trip", "camp", or refers to a specific named occasion.
3. The event has external attendees (attendees not from `gmail.com` or matching
   the owner's known domains).
4. The event has a physical location (not a video link).

---

## Step 4 — Build the Top 10 Action Items list

Review ALL emails and flagged calendar events and produce a ranked list of the
**10 most important things the account owner needs to do or be aware of**.

Ranking criteria (highest to lowest priority):
1. Financial alerts, fraud warnings, card-not-present alerts, payment due dates
2. Security alerts (unrecognized device sign-ins, password issues, OAuth failures)
3. Time-sensitive requests from real people (texts via Google Voice, direct emails)
4. Pending approvals or decisions with a deadline
5. Upcoming one-time calendar events requiring preparation or RSVP
6. Follow-up actions from recent conversations
7. Bills or statements ready for payment
8. Administrative tasks (ward/organization duties, registrations, etc.)
9. General informational items worth noting
10. Price drops, travel deals, or discretionary opportunities

For each item in the top 10:
- Write a **bold, descriptive title** (e.g. "Citi Card Payment Due May 6")
- One or two sentences explaining what it is and why it matters
- A specific, concrete action the owner should take (not vague like "follow up")

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
  e.g. `Morning Digest — Sunday, May 3, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222; padding: 20px;">

<h2 style="border-bottom: 2px solid #e74c3c; padding-bottom: 8px; color: #1a1a2e;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #888; font-size: 0.85em;">Generated at 5:00 AM Mountain Time &mdash; weekly email review</p>

<!-- ====== TOP 10 SECTION ====== -->
<h3 style="margin-top: 24px;">&#128203; Top 10 Items to Address</h3>

<!-- Repeat this block for each of the 10 items, numbered 1–10 -->
<div style="margin-bottom: 14px; padding: 12px 14px; background: #f9f9f9; border-left: 4px solid #e74c3c;">
  <p style="margin: 0 0 4px 0;"><strong>{N}. {Item Title}</strong></p>
  <p style="margin: 0 0 4px 0; font-size: 0.9em;">{1-2 sentence explanation}</p>
  <p style="margin: 0; font-size: 0.9em; color: #27ae60;"><strong>Action:</strong> {Specific action to take}</p>
</div>
<!-- End item block -->

<!-- ====== UNUSUAL CALENDAR EVENTS SECTION ====== -->
<h3 style="margin-top: 28px; border-top: 1px solid #ddd; padding-top: 16px;">
  &#128197; Out-of-the-Ordinary Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each flagged event -->
<div style="margin-bottom: 12px; padding: 10px 12px; background: #f0f7ff; border-left: 4px solid #27ae60;">
  <p style="margin: 0;"><strong>{Day, Month Date} &bull; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 16px; color: #555; font-size: 0.9em;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 16px; color: #555; font-size: 0.9em;">{Brief description or attendees if notable}</p>
</div>
<!-- End event block -->

<!-- If no unusual events: -->
<!-- <p><em>No out-of-the-ordinary events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px; border: none; border-top: 1px solid #eee;"/>
<p style="font-size: 0.8em; color: #aaa;">Automated digest &mdash; ClaudeRoutines &mdash; 5:00 AM daily</p>

</body>
</html>
```

### 6b — Deliver the draft to the Inbox

After `create_draft` returns an `id`, call `label_message` with:
- `messageId`: the `id` returned by `create_draft`
- `labelIds`: `["INBOX"]`

This moves the message from Drafts into the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- The Top 10 list must always have exactly 10 items. If there are fewer than
  10 meaningful items, fill remaining slots with the next most useful
  informational notes.
- Keep each item's explanation to 1–2 sentences maximum.
- Actions must be concrete and specific, not vague.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- If a calendar event has an RSVP of "needsAction" or "tentative", flag that
  in the action for that item.

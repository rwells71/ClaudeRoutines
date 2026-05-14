# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the last 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through the next 7 days in Mountain Time (`America/Denver`).

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -in:sent -in:draft`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (stop after 3 pages maximum).

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand action items, call `get_thread` with
that thread's ID (limit to threads where the snippet alone is insufficient).

**Skip entirely**: marketing/newsletter emails, purely automated alerts with no
action required (e.g. "your package was delivered" with nothing to do),
calendar notification emails from `calendar-notification@google.com`, and
Qustodio/school flyer digests.

**Keep and prioritize**: human-sent emails, financial alerts requiring a
decision, school absence/grade notices, church/organization coordination,
texts forwarded via Google Voice, and any email with a clear ask or deadline.

---

## Step 3 — Fetch upcoming calendar events (next 7 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601 with -06:00 or -07:00 offset)
- `endTime`: 7 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, identify **out-of-the-ordinary events** — events that stand
out from the normal daily routine. An event is "out of the ordinary" if it
meets ANY of these criteria:
1. It does NOT have a `recurringEventId` field (it is a one-time event).
2. It is a recurring event that was **recently modified** (its `updated`
   timestamp is within the last 7 days).
3. Its summary contains keywords suggesting something special: concert, trip,
   travel, graduation, wedding, birthday, campout, festival, visit, meeting,
   conference, surgery, appointment, deadline, test, exam, performance,
   ceremony, trek, retreat, training.
4. It involves attendance by others (has an `attendees` list with more than
   one person).

Drop routine daily reminders (food logging, laundry checks, "don't wake up X",
quick chores) unless they have a concrete deadline or consequence.

---

## Step 4 — Build the Top 10 Action Items list

Synthesize the emails and calendar events into a **ranked list of the 10 most
important things the account owner needs to address**. Rank by urgency and
impact: items due today or tomorrow come first, then items with explicit
deadlines, then items that are blocking others, then everything else.

For each item:
- Assign a number (1–10).
- Write a **bold title** (5–10 words).
- Write 1–3 sentences of context: what is needed, why it matters, any
  deadline or consequence if ignored.
- If an action is time-sensitive, add `⚠️ Due: [date/time]` on its own line.

If there are fewer than 10 genuine action items, stop the list early rather
than padding with trivial tasks.

---

## Step 5 — Determine the account owner's email address

Look at the **"To:"** field of every email fetched. The address that appears
most frequently is the owner's address. Store it as `{owner_email}`.

---

## Step 6 — Create and label the digest

### 6a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `Morning Digest — Friday, April 25, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 680px; margin: auto; color: #222; line-height: 1.5;">

<h2 style="border-bottom: 2px solid #2c5f8a; padding-bottom: 8px; color: #2c5f8a;">
  Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #888; font-size: 0.85em; margin-top: 0;">Generated at 5:00 AM Mountain Time &bull; Last 7 days of email</p>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<h3 style="color: #2c5f8a; margin-top: 24px;">&#128203; Top 10 Action Items</h3>
<ol style="padding-left: 20px;">

  <!-- Repeat for each action item (up to 10) -->
  <li style="margin-bottom: 14px;">
    <strong>{Bold item title}</strong><br>
    {1-3 sentences of context, deadline, consequence.}
    <!-- Only include if time-sensitive -->
    <br><span style="color: #c0392b;">&#9888;&#65039; Due: {date/time}</span>
  </li>
  <!-- End action item -->

</ol>
<!-- If fewer than 10 genuine items exist, end the list early. -->

<!-- ====== OUT-OF-THE-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="color: #2c5f8a; border-top: 1px solid #ddd; padding-top: 16px; margin-top: 28px;">
  &#128197; Upcoming Unusual Calendar Events (Next 7 Days)
</h3>

<!-- Repeat for each out-of-the-ordinary event -->
<div style="margin-bottom: 12px; padding: 10px 14px; background: #f0f7ff; border-left: 4px solid #27AE60; border-radius: 3px;">
  <p style="margin: 0;"><strong>{Day, Date} &bull; {Start Time} &ndash; {End Time} MT</strong> &mdash; {Event Title}</p>
  <!-- Only include if data exists -->
  <p style="margin: 4px 0 0 0; color: #555; font-size: 0.9em;">&#128205; {Location or video link}</p>
  <p style="margin: 4px 0 0 0; color: #555; font-size: 0.9em;">{Why it is out of the ordinary / brief description}</p>
</div>
<!-- End event block -->

<!-- If no out-of-the-ordinary events, replace blocks with: -->
<!-- <p><em>No unusual events in the next 7 days.</em></p> -->

<hr style="margin-top: 32px; border: none; border-top: 1px solid #eee;"/>
<p style="font-size: 0.75em; color: #aaa;">Automated digest &mdash; ClaudeRoutines &bull; richardlwells@gmail.com</p>

</body>
</html>
```

### 6b — Move draft to Inbox

After `create_draft` returns a draft ID, call `label_message` with:
- `messageId`: the message ID returned by `create_draft`
- `addLabelIds`: `["INBOX"]`

This delivers the digest to the Inbox rather than leaving it in Drafts.

> **Note**: The Gmail MCP does not expose a send API. Delivering via
> `label_message` with `"INBOX"` is the correct workaround. Do NOT call
> `list_labels` — use the literal string `"INBOX"`.

---

## Important rules

- **Top 10 only**: synthesize across all emails and calendar events into the
  10 highest-priority action items. Do not list every email; identify what
  actually needs doing.
- Action items must be concrete and specific, not vague ("Reply to Brad Hales
  about the campout ride for him and Anson" not "Follow up on texts").
- Keep the calendar section to genuinely unusual events. Do not list routine
  recurring events like daily reminders, family dinner, or laundry checks.
- Never include raw HTML, JSON, or email headers in the digest body.
- If an email thread spans multiple messages, read enough to understand the
  current status and what is still outstanding.

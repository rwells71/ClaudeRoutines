# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the last 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through 7 days from now (in Mountain Time),
  from `00:00:00` today to `23:59:59` seven days from now, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social -category:updates -in:sent`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail: marketing emails, newsletters, messages from
`noreply@`, `no-reply@`, `donotreply@`, or `notifications@` addresses, and any
message with an `List-Unsubscribe` header. Include everything else —
transactional, human-sent, or important system notifications.

---

## Step 3 — Fetch upcoming calendar events

Call `list_events` with:
- `calendarId`: `richardlwells@gmail.com`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601, e.g. `2026-05-20T00:00:00-06:00`)
- `endTime`: 7 days from now at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, identify events that are **"out of the ordinary"** — meaning any of:
1. Does NOT have a `recurringEventId` field (one-time events).
2. Has a `recurringEventId` but was created or last updated within the past 14 days
   (check the `updated` or `created` field — a recently added occurrence of a recurring
   series counts as unusual).
3. Has a title or description suggesting a special occasion (graduation, party, conference,
   ceremony, appointment, trip, meeting with a specific person's name, etc.).
4. Is a multi-day all-day event.

Drop purely mechanical recurring reminders (e.g. "Log all food", "Take out garbage",
"Check for baptisms for the dead") unless they fall on an unusual day or time.

---

## Step 4 — Build the Top 10 Action Item List

Analyze all emails and unusual calendar events together. Produce a ranked list of
the **top 10 most important things the account owner needs to address today or this week**.

Ranking criteria (apply in order):
1. **Hard deadlines today or tomorrow** — assignments due, events happening, pickups required.
2. **Time-sensitive requests from real people** (family, friends, colleagues) that need a reply or action.
3. **Upcoming one-time calendar events** this week that require preparation.
4. **Alerts or warnings** (home sensors, account alerts, health notices).
5. **Coordination items** — plans that need to be confirmed with other people.
6. **Administrative tasks** — bills, forms, school communications.
7. Everything else, in rough deadline order.

For each item:
- Use a short, bolded title (max 10 words)
- Include a ⭐ marker if the item is from a non-recurring/unusual calendar event
- 1–3 bullet points of specific context (who asked, what's needed, when, where)
- Mark with 🚨 if the deadline is today

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

**`subject`**: `☀️ Morning Digest — {Weekday}, {Month} {Day}, {Year}`
  e.g. `☀️ Morning Digest — Friday, May 22, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222; padding: 20px;">

<h1 style="border-bottom: 3px solid #3498db; padding-bottom: 10px; color: #2c3e50;">
  ☀️ Morning Digest &mdash; {Weekday}, {Month} {Day}, {Year}
</h1>
<p style="color: #666; font-size: 0.9em;">Generated at 5:00 AM Mountain Time &nbsp;|&nbsp; Emails: last 7 days &nbsp;|&nbsp; Calendar: next 7 days</p>

<!-- ====== TOP 10 SECTION ====== -->
<h2 style="color: #e74c3c; margin-top: 24px;">🔴 Top 10 Items to Address</h2>

<ol style="line-height: 1.9; font-size: 15px; padding-left: 20px;">

  <!-- Repeat for each of the 10 items -->
  <li style="margin-bottom: 16px;">
    <strong>{Short bold title — include 🚨 if deadline is today, ⭐ if unusual calendar event}</strong><br>
    <ul style="margin: 4px 0 0 0; color: #444;">
      <li>{Specific context bullet 1}</li>
      <li>{Specific context bullet 2 — optional}</li>
      <li>{Specific context bullet 3 — optional}</li>
    </ul>
  </li>
  <!-- End item -->

</ol>

<!-- ====== UNUSUAL CALENDAR SECTION ====== -->
<h2 style="color: #8e44ad; margin-top: 28px; border-top: 2px solid #eee; padding-top: 16px;">
  ⭐ Upcoming Out-of-the-Ordinary Calendar Events
</h2>

<!-- If no unusual events: <p><em>No unusual calendar events in the next 7 days.</em></p> -->

<table style="width:100%; border-collapse: collapse; font-size: 14px;">
  <tr style="background:#f2f2f2;">
    <th style="text-align:left; padding:8px; border-bottom:2px solid #ddd;">Date &amp; Time (MT)</th>
    <th style="text-align:left; padding:8px; border-bottom:2px solid #ddd;">Event</th>
    <th style="text-align:left; padding:8px; border-bottom:2px solid #ddd;">Notes</th>
  </tr>
  <!-- Repeat for each unusual event -->
  <tr>
    <td style="padding:8px; border-bottom:1px solid #eee;">{Date, Time}</td>
    <td style="padding:8px; border-bottom:1px solid #eee;">{Event Title}</td>
    <td style="padding:8px; border-bottom:1px solid #eee;">{Location or short note}</td>
  </tr>
  <!-- End event row -->
</table>

<hr style="margin-top: 32px; border: none; border-top: 2px solid #eee;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &mdash; rwells71/clauderoutines</p>

</body>
</html>
```

### 6b — Label the draft so it arrives in the Inbox

After `create_draft` returns an `id`, call `label_message` with:
- `messageId`: the `id` returned by `create_draft`
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

- If there are **no qualifying emails**, say so clearly; do not omit the section.
- If there are **no unusual calendar events**, say so clearly; do not omit the section.
- The Top 10 list must contain exactly 10 items if there are enough qualifying signals;
  fewer only if there genuinely are fewer than 10 actionable items.
- Action items must be concrete ("Reply to Keith confirming flower pickup location")
  not vague ("Follow up with Keith").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Calendar reminders phrased as personal to-do notes (e.g. "Don't forget to X")
  should be surfaced as action items, not as calendar events.

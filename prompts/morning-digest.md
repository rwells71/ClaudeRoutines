# Morning Email & Calendar Digest

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the 7-day period ending right now (i.e. the last 7 days).
  Gmail query: `newer_than:7d`
- **Calendar window – past**: last 7 days (to catch recently-added one-time events that
  already occurred and may need follow-up).
- **Calendar window – future**: today through 14 days from now (to surface upcoming
  unusual events early).

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated / low-value mail:
- Marketing emails and newsletters.
- Messages from `noreply@`, `no-reply@`, `donotreply@`.
- Calendar notification emails (sender `calendar-notification@google.com`).
- Routine bank/statement-available notices (no action needed beyond awareness).
- YouTube, Substack, Raspberry Pi Magazine, or similar content newsletters.

**Keep** everything else — human-sent messages, financial alerts requiring action,
school/family communications, church/organization requests, package tracking,
and any system alert that implies a decision or response is needed.

---

## Step 3 — Fetch calendar events (past 7 days + next 14 days)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: 7 days ago at `00:00:00` Mountain Time (ISO 8601 with offset)
- `endTime`: 14 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, **identify "out-of-the-ordinary" events** using these criteria
(an event qualifies if it meets ANY of the following):

1. **No `recurringEventId`** — it is a one-time event (not part of a recurring series).
2. **Multiple attendees** from outside the immediate family (i.e. attendees who are
   not `richardlwells@gmail.com` or `megan.wells@gmail.com`).
3. **A location** field that is not blank (suggests travel or an offsite meeting).
4. **Title keywords** that suggest something unusual: "tour", "trek", "mission",
   "conference", "training", "speak", "visit", "surgery", "appointment",
   "interview", "birthday", "anniversary", "graduation", or similar one-time milestone words.
5. The event was **created or updated within the last 7 days** (newly scheduled).

---

## Step 4 — Build the Top 10 Action Items

Synthesize emails AND calendar events into a single ranked list of the
**10 most important things the account owner needs to do**.

Ranking criteria (higher = more urgent):
1. Hard deadlines or time-sensitive dates mentioned explicitly.
2. Requests from real people (not automated systems) waiting on a reply.
3. Financial actions (bills due, payments to make, statements to review with decisions).
4. Upcoming events within 7 days that require preparation.
5. Standing tasks that were triggered by an email this week.

Format each item as:
```
N. [CATEGORY EMOJI] Short title
   Why it matters / deadline / key detail (one sentence max).
```

Category emoji guide:
- ⛪ Church / religious
- 🏫 School / education
- 💰 Finance / billing
- 📦 Shipping / physical
- 👥 People / relationship
- 📅 Calendar / scheduling
- 🔧 Technical / admin
- 🏥 Health
- 🏕️ Activity / event

---

## Step 5 — Summarize email details

Group by sender (display name + email address as heading).
For each sender, list every relevant email they sent in the window. For each email:
- Subject line
- 2–4 bullets covering the key points
- "Action Items" section with concrete, specific tasks (omit if none)

---

## Step 6 — Determine the account owner's email address

Use the following strategy, in order, stopping at the first successful result:

1. Look at the **"To:"** field of every email fetched. Collect all recipient
   addresses. The address that appears most frequently is almost certainly the
   account owner's address — use that.
2. If there is a tie, prefer the address whose domain matches the majority of
   the other addresses in the "To:" fields.
3. If still ambiguous, use the first address found in any "To:" field.

Store this address as `{owner_email}`.

---

## Step 7 — Create and deliver the digest draft

### 7a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `🌅 Daily Briefing — {Weekday}, {Month} {Day}, {Year}`
  e.g. `🌅 Daily Briefing — Wednesday, June 3, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:700px;margin:auto;color:#222;">

<div style="background:#1a3a5c;color:white;padding:16px 20px;border-radius:6px 6px 0 0;">
  <h2 style="margin:0;font-size:20px;">☀️ Good Morning — Daily Briefing</h2>
  <p style="margin:4px 0 0;font-size:13px;opacity:0.8;">{Weekday}, {Month} {Day}, {Year} · 5:00 AM Mountain Time</p>
</div>

<!-- ====== TOP 10 ACTION ITEMS ====== -->
<div style="padding:20px;">
<h3 style="color:#1a3a5c;border-bottom:2px solid #e5e7eb;padding-bottom:6px;">📋 Top 10 Items to Address</h3>

<table style="width:100%;border-collapse:collapse;">
  <!-- Repeat this row for each of the 10 items; alternate background #f0f4ff / white -->
  <tr style="background:#f0f4ff;">
    <td style="padding:10px 12px;vertical-align:top;width:28px;font-weight:bold;color:#1a3a5c;">{N}.</td>
    <td style="padding:10px 12px;">
      <strong>{EMOJI} {Title}</strong><br>
      <span style="color:#555;font-size:14px;">{One-sentence detail / deadline}</span>
    </td>
  </tr>
</table>

<!-- ====== NOTABLE CALENDAR EVENTS ====== -->
<h3 style="color:#1a3a5c;border-bottom:2px solid #e5e7eb;padding-bottom:6px;margin-top:28px;">📅 Notable / Out-of-Ordinary Calendar Events</h3>

<!-- Repeat for each notable event; alternate background -->
<div style="margin-bottom:10px;padding:10px 14px;background:#f0fdf4;border-left:4px solid #16a34a;border-radius:0 4px 4px 0;">
  <strong>{Date} · {Start}–{End} MT</strong> — {Event Title}<br>
  <span style="color:#555;font-size:13px;">{Why it's notable / location / attendees}</span>
</div>

<!-- If no notable calendar events: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the ±14-day window.</em></p> -->

<!-- ====== EMAIL DETAILS ====== -->
<h3 style="color:#1a3a5c;border-bottom:2px solid #e5e7eb;padding-bottom:6px;margin-top:28px;">📧 Email Detail — Last 7 Days</h3>

<!-- Repeat for each sender -->
<div style="margin-bottom:18px;padding:12px;background:#f9f9f9;border-left:4px solid #4A90D9;border-radius:0 4px 4px 0;">
  <h4 style="margin:0 0 6px 0;color:#1a3a5c;">{Sender Name} &lt;{sender@example.com}&gt;</h4>
  <p style="margin:0 0 4px 0;"><strong>Subject:</strong> {subject}</p>
  <ul style="margin:4px 0 0 0;">
    <li>{key point 1}</li>
    <li>{key point 2}</li>
    <!-- Only if action items exist: -->
    <li><strong>Action:</strong> {specific action required}</li>
  </ul>
</div>

<!-- If no qualifying emails: -->
<!-- <p><em>No action-requiring emails received in the last 7 days.</em></p> -->

<hr style="margin-top:32px;border:none;border-top:1px solid #e5e7eb;"/>
<p style="font-size:12px;color:#9ca3af;">Automated digest · ClaudeRoutines · richardlwells@gmail.com</p>
</div>

</body>
</html>
```

### 7b — Move the draft to the Inbox

After `create_draft` returns an `id`, call `label_message` with:
- `messageId`: the `id` returned by `create_draft`
- `labelIds`: `["INBOX"]`

This moves the digest into the Inbox so it is delivered like a normal email
rather than sitting in Drafts.

> **Note**: The Gmail MCP does not expose a send API. Inbox delivery is
> achieved by assigning the `INBOX` label to the draft after creation.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- The Top 10 list is the most important part — spend the most effort getting it right.
- Only include items in the Top 10 that genuinely need the owner's attention;
  do not pad with routine automated notifications.
- Keep email detail summaries concise: max 4 bullets per email.
- Action items must be concrete ("Reply to Lori confirming the June 21st talk topic")
  not vague ("Follow up").
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Birthday or special occasion notes on the calendar should appear as a warm
  callout at the top of the email (e.g. "🎂 Today is your birthday!").
- If multiple emails from the same sender arrive in the window, group them all
  under one sender heading with separate subject/key-points/action-items blocks.

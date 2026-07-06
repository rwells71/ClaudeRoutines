# Morning Email & Calendar Digest — Top 10 Daily Briefing

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time window

The digest runs at 5:00 AM Mountain Time. Use the following windows:

- **Email window**: the last **7 days**.
  Gmail query: `newer_than:7d`
- **Calendar window**: from **today** through **7 days from today**, in Mountain Time
  (`America/Denver`), from `00:00:00` to `23:59:59` on the last day.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -in:draft -in:sent`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are
collected (up to 150 threads total).

For each thread, use the snippet and metadata already returned to assess
importance. If the full body is needed to determine the action required, call
`get_thread` with that thread's ID.

**Skip** these automatically:
- Marketing/promotional emails
- Social media notifications
- Newsletters (List-Unsubscribe header present)
- Routine calendar notification emails from `calendar-notification@google.com`
- Google Voice text-message forwarding (unless the text contains an urgent request)
- Travel deal emails (airlines, hotels, cruise lines)
- Automated "statement ready" emails that require no action beyond reading

**Always include**:
- Financial approvals or transactions requiring sign-off
- Safety or security alerts (air quality, intrusion, credential alerts)
- Billing or invoice emails (even if on autopay — note the amount and due date)
- Emails from real people requiring a reply or action
- Calendar invitations not yet responded to
- Parental monitoring reports (screen time, activity summaries)

---

## Step 3 — Fetch upcoming calendar events

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` Mountain Time (ISO 8601, e.g. `2026-07-06T00:00:00-06:00`)
- `endTime`: 7 days from today at `23:59:59` Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 50

From the results, identify **unusual / out-of-the-ordinary events** — keep an
event if ANY of the following are true:
1. It does **not** have a `recurringEventId` field (one-time event).
2. It involves attendees other than the account owner.
3. It represents a schedule disruption (road closures, construction, travel).
4. It is a medical, legal, financial, or care appointment.
5. It is a farewell, wedding, graduation, or similar social milestone.
6. Its title explicitly mentions something that needs preparation or coordination.

Drop purely routine recurring reminders (take trash out, check furnace filter,
text someone a weekly update, etc.) unless they require unusual coordination
this week.

---

## Step 4 — Identify the Top 10 Action Items

Review all emails and unusual calendar events together. Rank the **10 most
important things the account owner must act on**, using this priority order:

1. **Urgent / time-sensitive** (deadlines within 48 hours, safety alerts, pending approvals)
2. **Financial** (approvals, large payments, account alerts, statements needing review)
3. **Upcoming schedule disruptions** (road closures, travel, unusual appointments)
4. **People waiting on a response** (unanswered texts, calendar invites, meeting requests)
5. **Recurring monitoring** (parental reports, credit alerts, health/safety sensors)
6. **Upcoming events needing prep** (farewells, meetings with agenda, appointments)
7. **Low-urgency admin** (autopay invoices, routine statements, optional RSVPs)

Assign each item a **priority badge**:
- 🔴 **URGENT** — act today
- 🟡 **THIS WEEK** — act within 7 days
- 🔵 **FYI** — no action required, but worth knowing

---

## Step 5 — Determine the account owner's email address

Examine the **"To:"** field of every email fetched. The address that appears
most frequently is the account owner's — use that as `{owner_email}`.

---

## Step 6 — Create and deliver the digest

### 6a — Create the draft

Call `create_draft` with:

**`to`**: `["{owner_email}"]`

**`subject`**: `☀️ Daily Briefing — {Weekday}, {Month} {Day}, {Year}`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<html>
<body style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; color: #222; background: #fff;">

  <div style="background: #1a3a5c; color: white; padding: 20px 24px 14px; border-radius: 8px 8px 0 0;">
    <h1 style="margin: 0 0 4px; font-size: 22px;">☀️ Good Morning, Richard</h1>
    <p style="margin: 0; opacity: 0.8; font-size: 14px;">Daily Briefing · {Weekday}, {Month} {Day}, {Year}</p>
  </div>

  <div style="padding: 20px 24px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 8px 8px;">

    <h2 style="font-size: 16px; color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: 6px; margin-top: 4px;">
      🔔 Top 10 Action Items
    </h2>

    <!-- Repeat this block for each of the 10 items. Choose border/background color by priority:
         URGENT:    border #dc3545, background #f8d7da
         THIS WEEK: border #e6a817, background #fff3cd
         FYI:       border #0c7a8c, background #d1ecf1
    -->
    <div style="border-left: 4px solid {COLOR}; background: {BG}; padding: 12px 14px; margin: 10px 0; border-radius: 4px;">
      <strong>{N}. {BADGE} {TITLE}</strong>
      <p style="margin: 6px 0 0; font-size: 14px;">{2-3 sentence description with specific details: amounts, dates, names, required action.}</p>
    </div>
    <!-- End action item block -->

    <h2 style="font-size: 16px; color: #1a3a5c; border-bottom: 2px solid #1a3a5c; padding-bottom: 6px; margin-top: 24px;">
      📆 Unusual Calendar Events — Next 7 Days
    </h2>

    <!-- If no unusual events, write: <p><em>No out-of-the-ordinary events in the next 7 days.</em></p> -->
    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
      <tr style="background: #f0f4f8;">
        <th style="text-align: left; padding: 8px 10px; border: 1px solid #ddd; width: 28%;">When</th>
        <th style="text-align: left; padding: 8px 10px; border: 1px solid #ddd;">Event &amp; Notes</th>
      </tr>
      <!-- Repeat for each unusual event -->
      <tr>
        <td style="padding: 8px 10px; border: 1px solid #ddd; font-weight: bold;">{Day, Date · Time}</td>
        <td style="padding: 8px 10px; border: 1px solid #ddd;"><strong>{Event Title}</strong> — {one-line note on why it's unusual or what prep is needed}</td>
      </tr>
      <!-- End event row -->
    </table>

    <p style="font-size: 12px; color: #888; margin-top: 24px; border-top: 1px solid #eee; padding-top: 12px;">
      Generated daily at 5:00 AM MT · ClaudeRoutines · richardlwells@gmail.com
    </p>

  </div>
</body>
</html>
```

### 6b — Deliver the digest to the Inbox

After `create_draft` returns an `id`, call `label_message` with:
- `messageId`: the `id` returned by `create_draft`
- `labelIds`: `["INBOX"]`

This moves the draft to the Inbox so it appears like a normal email rather
than sitting silently in Drafts.

> **Note**: The Gmail MCP integration does not expose a send API. Delivery is
> accomplished by applying the `INBOX` label to the draft. If a `send_message`
> or `send_draft` tool becomes available, prefer that instead.

---

## Important rules

- Top 10 must be **genuinely actionable** — no filler. If there are fewer than
  10 real items, stop at the real count; never pad with noise.
- Descriptions must be **specific**: include dollar amounts, due dates, names,
  and the exact action required. Never write "follow up" without saying what to
  do and by when.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.
- Calendar items in the Top 10 must also appear in the Unusual Events table.
- If a safety alert fired multiple times for the same issue, count it as one item
  and note the frequency.

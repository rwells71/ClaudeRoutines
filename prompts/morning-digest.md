# Morning Email & Calendar Digest — Top 10 Action Items

You are running an automated morning digest routine for the account owner.
Complete every step below in order. Do not skip any step.

---

## Step 1 — Establish the time windows

The digest runs at 5:00 AM Mountain Time. Calculate:

- **Email window**: the last 7 days ending right now.
  Gmail query: `newer_than:7d`
- **Calendar window**: today through the next 14 days (Mountain Time).
  Use `startTime` = today at `00:00:00` and `endTime` = 14 days from today at `23:59:59`, timezone `America/Denver`.

---

## Step 2 — Fetch recent emails

Call `search_threads` with:
- `query`: `newer_than:7d -category:promotions -category:social`
- `pageSize`: 50

Repeat with `pageToken` if the response includes one, until all threads are collected.

For each thread, examine the snippet and message metadata already returned.
If the full body is needed to understand key points or action items, call
`get_thread` with that thread's ID.

**Skip** clearly automated mail with no action: marketing newsletters,
promotional flyers, messages from `school@peachjar.com`, `updates-noreply@linkedin.com`,
or any message with an `List-Unsubscribe` header indicating a marketing newsletter.

**Always include**: billing notices, financial alerts, school/teacher emails,
expiring credentials, OAuth errors, service outages, calendar invitations,
and any human-written messages.

---

## Step 3 — Fetch upcoming calendar events (14-day window)

Call `list_events` with:
- `calendarId`: `primary`
- `startTime`: today at `00:00:00` in Mountain Time (ISO 8601 with offset, e.g. `2026-04-30T00:00:00-06:00`)
- `endTime`: 14 days from today at `23:59:59` in Mountain Time
- `timeZone`: `America/Denver`
- `orderBy`: `startTime`
- `pageSize`: 100

From the results, identify **out-of-the-ordinary events** — those that meet ANY of the following:
1. The event does NOT have a `recurringEventId` field (genuinely one-time events).
2. It is a recurring event that involves a specific dollar amount, a speaking assignment, a medical or legal appointment, a school performance/event, or a named third-party participant.
3. It has an unusual start time (e.g., midnight to 6 AM) for a task that would normally happen during business hours.
4. It was created or last modified in the past 7 days (recently added/changed).

Drop routine daily reminders (e.g., "Log all food", "Family Dinner", "Check for baptisms for the dead") unless they involve an unusual circumstance.

---

## Step 4 — Build the Top 10 Action Items list

Combine insights from both emails and notable calendar events into a **single ranked list of 10 items** the account owner needs to address.

Ranking criteria (highest priority first):
1. **Expiring credentials / broken tokens** — act today or lose access
2. **Financial payments due within 48 hours** — late fees, interest charges
3. **Today's one-time events** — school programs, special meetings, speaking assignments
4. **School / academic warnings** — grade risks, teacher requests, term deadlines
5. **Upcoming financial deadlines** (within 7 days)
6. **Upcoming one-time events / invitations needing a response** (within 14 days)
7. **Investment / account alerts** requiring a decision
8. **Home / utility / subscription maintenance** items
9. **Family / church leadership tasks** with specific people or deadlines
10. **Informational items** worth awareness (home value reports, shareholder reports)

For each item in the list:
- Lead with an emoji and rank number (e.g., `🚨 1.`)
- Bold the title
- Include 1–3 sentences with: what happened, why it matters, and the specific next action

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

**`subject`**: `📋 Daily Briefing - Top 10 Action Items | {Weekday}, {Month} {Day}, {Year}`
  e.g. `📋 Daily Briefing - Top 10 Action Items | Thursday, April 30, 2026`

**`htmlBody`**: Use the HTML template below, substituting real content.

```html
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; max-width: 700px; margin: auto; color: #222;">

<h2 style="border-bottom: 2px solid #4A90D9; padding-bottom: 8px;">
  📋 Daily Briefing &mdash; {Weekday}, {Month} {Day}, {Year}
</h2>
<p style="color: #666; font-size: 0.9em;">Last 7 days &bull; Generated 5:00 AM MDT</p>

<h3 style="margin-top: 24px;">🔔 Top 10 Action Items</h3>

<!-- Repeat the block below for each of the 10 items. Use background/border color to indicate urgency:
     URGENT (red):   background: #fff0f0; border-left: 4px solid #e74c3c;
     WARNING (amber): background: #fff8e1; border-left: 4px solid #f39c12;
     INFO (green):   background: #eafaf1; border-left: 4px solid #27ae60;
     CALENDAR (blue): background: #e8f4fd; border-left: 4px solid #2980b9; -->
<div style="margin-bottom: 14px; padding: 12px; background: #fff0f0; border-left: 4px solid #e74c3c;">
  <p style="margin: 0;"><strong>🚨 1. {Title}</strong></p>
  <p style="margin: 6px 0 0 0; font-size: 0.95em;">{1-3 sentences: what happened, why it matters, specific next action}</p>
</div>

<!-- ... items 2 through 10 ... -->

<!-- ====== OUT-OF-ORDINARY CALENDAR EVENTS ====== -->
<h3 style="margin-top: 32px; border-top: 1px solid #ddd; padding-top: 16px;">
  📅 Upcoming Out-of-the-Ordinary Calendar Events
</h3>
<p style="font-size: 0.9em; color: #555;">Non-recurring and notable events in the next 14 days:</p>

<!-- Repeat for each notable event -->
<div style="margin-bottom: 10px; padding: 10px; background: #f0f7ff; border-left: 4px solid #2980b9;">
  <p style="margin: 0;"><strong>{Date, Start Time – End Time MT}</strong> &mdash; {Event Title}</p>
  <!-- Only include lines below if the data exists -->
  <p style="margin: 4px 0 0 18px; color: #555; font-size: 0.9em;">{Brief note about why it's notable or what action is needed}</p>
</div>

<!-- If no out-of-ordinary events, replace with: -->
<!-- <p><em>No out-of-the-ordinary calendar events in the next 14 days.</em></p> -->

<hr style="margin-top: 32px;"/>
<p style="font-size: 0.8em; color: #999;">Automated digest &mdash; ClaudeRoutines &bull; Emails: last 7 days &bull; Calendar: upcoming 14 days</p>

</body>
</html>
```

### 6b — Move the draft to the Inbox

After `create_draft` returns a message ID, call `label_message` with:
- `messageId`: the ID returned by `create_draft`
- `labelIds`: `["INBOX"]`

`INBOX` is a Gmail system label — its ID is literally the string `"INBOX"`.
Do **not** call `list_labels` to look it up; use `"INBOX"` directly.

This moves the draft to the Inbox so it arrives like a normal email.

> **Note**: The Gmail MCP integration does not expose a send API. The digest
> is delivered by placing it directly in the Inbox via label assignment.
> If a `send_message` or `send_draft` tool becomes available in a future
> version, prefer that over `label_message`.

---

## Important rules

- Rank by **urgency and actionability** — broken credentials and same-day events always outrank informational items.
- Each item must state a **specific next action** (e.g., "Renew at id.atlassian.com → Security → API tokens"), not a vague one ("Follow up").
- If fewer than 10 genuinely actionable items exist, fill remaining slots with informational calendar events or notable email content — never invent items.
- Skip routine recurring reminders (food logging, daily checklists) unless something unusual is noted.
- Strip tracking pixels and HTML boilerplate from email bodies before summarizing.
- Never include raw HTML or JSON in the digest body.

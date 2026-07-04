# Marketing Command Centre — Guide

A social media + SEO pipeline dashboard for Priceline Pharmacy Pacific Fair.
Runs locally, just like the POS dashboard.

## Run it

```
python marketing_app.py
```

Then open **http://localhost:8060** (the POS dashboard stays on 8050 — both can run at once).
Windows shortcut: double-click `run_marketing.bat`.

First run only: `pip install dash` if you don't already have it (you do if the POS dashboard runs).

## What's inside

| Tab | What it does |
|---|---|
| ✅ **Today** | Your queue. Overdue tasks stack in **Catch-up** (oldest first); the single next action is flagged **UP NEXT**. Tick **Done** or **Skip** to move on. |
| 📅 **Calendar** | Month grid, colour-coded by channel. Click a day to open its tasks. Green ✓ on a day = everything done. |
| 🗂️ **Pipeline** | The full 8-week plan, week by week with themes and per-week progress. |
| 📖 **Playbook** | Strategy, posting times, hashtag sets, review-reply templates, GBP + SEO checklists, AI prompt style guide, and pharmacy compliance guardrails. |

Every content task carries: a **paste-ready caption**, an **AI image prompt**, an **AI video
prompt** (reels), a **photo brief** (what to shoot in-store instead), best posting time,
and a time estimate. Click *"Show content ▾"* on any card; the 📋 icon copies a block.

## The plan at a glance

8 weeks, **6 Jul – 30 Aug 2026** (86 tasks): weekly themes running winter wellness →
skincare → beauty → services → vitamins → skincare science → community → spring prep.

Weekly rhythm: Mon feed post + Google Business post + one SEO task · Tue story + review
replies · Wed reel · Thu feed post (+ fortnightly catalogue uploads) · Fri story + GBP
photo upload · Sat feed post · **Sun off**.

## Your progress

Ticks save to `marketing_state.json` next to the app — local only (gitignored), survives
restarts. Untick anything by clicking the button again.

## Editing the plan

Everything lives in `marketing_plan.py`:

- **Change/add a task** — edit the `CONTENT_TASKS` list (each task is one `T(...)` call).
- **Change weekly recurring content** — edit the `WEEKS` list (stories, SEO tasks, GBP posts).
- **Catalogue dates** — sale-upload tasks sit on alternating Thursdays; shift the dates
  if the real cycle differs.
- **Next month** — run the Week 8 "Month-in-review ritual", then ask Claude to generate
  the next 4–8 week block in the same format (give it your theme notes, real staff names
  and current bestsellers to write in).

# TracePilot — Portfolio Case Study

## Title

**TracePilot** — a full-stack release intelligence & observability MVP.

## One-liner

TracePilot helps a small engineering team answer one question well: _"Is this release safe, and if something broke, which release broke it?"_

## Problem

Small teams (2–15 engineers) ship frequently but operate with fragmented tooling. After a deploy the questions are always the same — is the system healthy, did latency/errors move, which release is the likely culprit, and were we prepared to roll back? Answering usually means stitching together a logs tool, a release spreadsheet, and Slack memory. Full suites (Datadog + PagerDuty + LaunchDarkly) answer these but are heavy and expensive for a team of five.

## Product idea

**TracePilot's wedge is correlation, not collection.** Instead of out-instrumenting a logging platform, it connects the signals a team already has — services, releases, health checks, endpoint latency/error metrics, rollback-readiness checklists, and incident timelines — into one operational loop:

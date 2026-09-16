# Confluence ALB/Azure auth — first run checklist

Branch `app_specific_action_alb_auth`. The Azure/ALB Selenium login in
`app/extension/confluence/extension_ui.py` was ported from the Jira version on
2026-09-16 and **has not yet been run against Confluence**. The Jira equivalent
is validated: 139/139 iterations, every login identity-checked, 1 recovered retry.

This file is a checklist for that first Confluence run. Delete it once the run
is green.

---

## 1. Before starting

```bash
docker ps                      # nothing already running - never two runs at once
git log -1 --oneline           # the box must have the Confluence port
grep -c LOGIN_ATTEMPTS app/extension/confluence/extension_ui.py   # expect >= 1
```

**Do not `git pull` or edit files on the box while a run is in progress.** The
container is started with `-v "$PWD:/dc-app-performance-toolkit"`, and
`pytest_runner` starts a fresh pytest session — re-importing the extension
modules — on every iteration, so a mid-run change takes effect partway through
and corrupts the dataset.

## 2. The one genuine unknown: `ajs-remote-user`

`_verify_logged_in_user()` reads `<meta name="ajs-remote-user">` to prove the
session belongs to the user this iteration was handed. That tag is confirmed
present on Jira 11.3.1; it is **not yet confirmed on this Confluence version**.

In `pytest.out`, per iteration, expect:

```
login_with_alb_auth, user: performance_xxxxxxxxx
logged in, got node_id: >confluence-0<
verified logged in user: performance_xxxxxxxxx     <-- identity guarantee active
```

If instead you see:

```
WARNING: no ajs-remote-user meta tag, could not verify login of performance_xxx
```

the run still works, but the identity check is inert and needs a
Confluence-specific replacement. Not a reason to abort the run.

## 3. Second unknown: does `/logout.action` redirect to Azure?

`app_specific_logout` clicks the Azure "Which account do you want to sign out
of?" row, which is what `/logoutconfirm.jsp` redirects to on Jira. If Confluence
behaves the same, the click happens silently. If you see this on **every**
iteration:

```
Azure sign-out account row not shown, session may already be gone
```

then `/logout.action` lands somewhere else and the selector needs adjusting.
Harmless either way — `_reset_sessions()` clears the session at the start of the
next login regardless, which is why the logout is not load-bearing.

## 4. Health check while it runs

`bzt.log`'s per-second lines report **JMeter only** and keep flowing even if the
Selenium half is dead. `pytest.out` is block-buffered and can lag badly. The
files that flush per write are `selenium.jtl` and `PyTestExecutor.ldjson`.

```bash
R=app/results/confluence/<run-dir>

awk -F, 'NR>1{c[$3]++} END{printf "logins=%d completed=%d\n", \
  c["selenium_app_specific_login"], c["selenium_view_page"]}' $R/selenium.jtl

grep -c "verified logged in user" $R/pytest.out   # should equal logins
grep -c "Azure login attempt"      $R/pytest.out   # occasional is fine, see below
```

`logins` and `completed` should track each other. **Logins climbing while
completed stalls is the failure signature** — that is what hung the Jira run on
2026-09-15 for 94 minutes.

## 5. What a failure looks like now (and why it no longer hangs)

The old code recursed into `app_specific_action` forever when Azure did not show
the e-mail form. `bzt`'s `pytest_runner` checks its `-d/--duration` deadline only
*after* `pytest.main()` returns, so a login that never returned hung the entire
run and produced no `results.csv`.

Now a failing login retries `LOGIN_ATTEMPTS` (3) times and then raises:

```
Azure login attempt 1/3 failed for performance_xxx: TimeoutException: ...
Azure login failed for performance_xxx after 3 attempts
```

`print_timing` records the action as failed, sets `globals.login_failed`, and the
rest of that iteration is skipped. One bad login costs one iteration, not the
run. A few scattered retries are normal — the Jira run had exactly 1 in 139 and
lost no iteration.

## 6. Expectations, so nothing looks alarming

- **The login is much slower than before** and is meant to be. Every iteration
  now does a full Azure round-trip plus two cookie-clearing page loads. On Jira
  this took `selenium_app_specific_login` from ~2.4 s to ~7.6 s.
- **Fewer Selenium iterations than an unfixed run** — also fine. Compliance is
  driven by run duration and JMeter success rates, not Selenium iteration count.
  A compliant 2025-09-24 Jira run managed only 11 iterations; the fixed run did
  139.
- **`selenium_app_specific_log_out` is a new/changed label** relative to older
  archived runs. Keep that in mind when diffing against a previous profile.

## 7. If it does hang anyway

```bash
docker stop <container>     # SIGTERM: Taurus tears down and still post-processes
```

You get `results.csv` and `results_summary.log`. **Never `docker kill`** — SIGKILL
loses them. A run stopped early is marked FAIL purely on duration
(`Actual test duration N < 2700 sec`); the JMeter data is still valid.

## 8. Let it run the full duration

The only thing that failed the 2026-09-15 Jira attempt outright was stopping it
early. `Compliant` requires the full `test_duration` from `confluence.yml`.

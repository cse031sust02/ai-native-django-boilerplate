# How I Build Software With AI

I don't ask AI to "build the feature." I use it to think through the design with me, write the decisions down, and turn them into a clear spec. Only then does it write code, and I review that code the way I'd review a teammate's pull request.

## The 30-second version

> AI is fast and knows a lot, so I let it explore options and do most of the typing. I own the design decisions and the final review. Before any code is written, the design is agreed, written down, and turned into a spec with clear acceptance criteria. Then I check the code against that spec.

## The process at a glance

Step 1 happens once per project. Steps 2–6 repeat for every feature (step 4 only when needed).

| # | Step | When | Output |
|---|------|------|--------|
| 1 | **Set the rules** | Once, at project start | `AGENTS.md` |
| 2 | **Discuss the design** | Every feature | An agreed design (no code yet) |
| 3 | **Write a feature doc** | Every feature | `docs/features/*.md` |
| 4 | **Record decisions** | Only when a choice isn't obvious | `docs/decisions/*.md` |
| 5 | **Write the spec** | Every feature | `specs/active/*.md` |
| 6 | **Build & verify** | Every feature | Tested code; spec moves to `specs/completed/` |

---

## The six steps

### 1. Set the rules for the project (once)

Before any feature work, I write a short rules file that the AI reads at the start of every session. It lists the tech stack, where each kind of code belongs, the commands for tests and linting, and what "done" means. This keeps the AI consistent across hundreds of sessions.

| Me | AI | Output |
|---|---|---|
| Write the rules and the definition of done | Follows them every time | `AGENTS.md` |

### 2. Discuss the design before any code

I explain the problem and my constraints, and I ask the AI for options. It lays out the tradeoffs. I ask questions, push back on what doesn't fit, and make the final call. I explicitly tell it not to write code yet.

| Me | AI | Output |
|---|---|---|
| Describe the problem, challenge ideas, decide | Proposes options and explains tradeoffs | An agreed design |

### 3. Write a short feature doc

The agreed design becomes a one-page document in plain language: what the feature does, the user flow, and the endpoints. Anyone on the team can read it without opening the code.

| Me | AI | Output |
|---|---|---|
| Review and correct it | Drafts it from our discussion | `docs/features/*.md` |

### 4. Record important decisions

If a choice isn't obvious, I write an Architecture Decision Record (ADR): what we chose, why, and what we gave up. Months later, the answer to "why is it built like this?" is already written down.

| Me | AI | Output |
|---|---|---|
| Decide which choices need one | Drafts the reasoning | `docs/decisions/*.md` |

### 5. Write the spec

The spec is the contract for the code. It defines each endpoint's request and response, and lists acceptance criteria that can each be tested. If a criterion can't be tested, I rewrite it until it can.

| Me | AI | Output |
|---|---|---|
| Make sure every rule is testable | Drafts endpoints and criteria | `specs/active/*.md` |

### 6. Build, then verify against the spec

The AI writes the code and a test for each acceptance criterion. I read the diff, run the tests, linter and system checks, and confirm every criterion passes. When it's done, the spec moves to `specs/completed/`.

| Me | AI | Output |
|---|---|---|
| Review the diff, run checks, approve | Writes code and tests | Tested, reviewed code |

---

## Where everything lives

Every step leaves a file behind, so the project explains itself:

```
project/
├── AGENTS.md              # rules the AI reads every session
├── docs/
│   ├── features/          # what each feature does
│   └── decisions/         # why we chose X over Y
├── specs/
│   ├── active/            # being built now
│   └── completed/         # done and verified
└── src/                   # the code
```

---

## Worked example: adding "Forgot password" to a web app

A feature every app needs and everyone understands. Here is how it goes through steps 2 to 6.

### Step 2: The design discussion

> **Me:** I need forgot-password and reset-password endpoints. Don't write code yet. Propose a design and the main tradeoffs.
>
> **AI:** Two common options for the reset token: a signed token with nothing stored, or a random token saved in the database. Signed tokens are simpler but hard to cancel. Stored tokens can be single-use and revoked. I'd store them, with a 1-hour expiry.
>
> **Me:** Agreed. But if the database leaks, aren't the stored tokens usable by an attacker?
>
> **AI:** Yes. Store only a hash of the token and email the raw value, the same way passwords are stored. A leaked table is then useless.
>
> **Me:** Also, the forgot-password endpoint shouldn't reveal whether an email is registered. And a reset should log the user out everywhere else.
>
> **AI:** Then forgot-password always returns 200 with the same message, and a successful reset ends all existing sessions. I'll add both to the design.

All three security rules (hashed tokens, no hint about which emails exist, logging out other sessions) came from my questions, not from the AI's first answer. That's the point of discussing first.

### Step 3: The feature doc

`docs/features/password-reset.md`

```markdown
## Flow
1. User submits email to /auth/forgot-password
2. If the account exists, we email a reset link (valid 1 hour)
3. User submits the token and new password to /auth/reset-password
4. Password is updated, token is used up, other sessions end

## Rules
- Same response whether or not the email exists
- Tokens are stored hashed and work only once
```

### Step 4: The decision record

`docs/decisions/007-stored-reset-tokens.md`

```markdown
Decision:  Store reset tokens in the database, hashed.
           Not signed, stateless tokens.

Why:       Tokens must be single-use and cancellable.
           Hashing means a database leak exposes nothing usable.

Cost:      One extra table and a cleanup job for expired rows.
```

### Step 5: The spec

`specs/active/012-password-reset.md`

```markdown
POST /api/v1/auth/forgot-password
  body:  { email }
  200:   { message: "If that email exists, a link has been sent." }

POST /api/v1/auth/reset-password
  body:  { token, password, confirm_password }
  200:   { message: "Password updated." }

Acceptance criteria
  - [ ] Unknown email still returns 200 with the same message
  - [ ] Token stops working after 1 hour
  - [ ] Token works only once
  - [ ] Mismatched passwords return 400
  - [ ] All other sessions are logged out after a reset
```

### Step 6: Build and verify

The AI writes the code, following the project rules (business logic goes in a service, not the view):

`src/apps/accounts/services.py`

```python
def request_password_reset(email: str) -> None:
    user = get_active_user_by_email(email)
    if user is None:
        return  # same response either way

    raw_token = secrets.token_urlsafe(32)
    PasswordResetToken.objects.create(
        user=user,
        token_hash=hash_token(raw_token),
        expires_at=now() + timedelta(hours=1),
    )
    send_reset_email.delay(user.id, raw_token)
```

Then the tests, one per acceptance criterion. The first run caught a gap:

```
✓ unknown email still returns 200
✓ token expires after 1 hour
✓ token works only once
✓ mismatched passwords return 400
✗ other sessions are logged out after reset
```

The code reset the password but left other devices logged in. Because that rule was written in the spec, there was a test for it, and it failed before anything shipped. One fix later, all five pass, I review the diff, and the spec moves to `specs/completed/`.

---

## Why work this way

Asking AI to "build a password reset" gives you working code in seconds. But the security rules above wouldn't be there, nothing would test for them, and nobody could explain later why the code looks the way it does.

| Just prompting for code | Design, document, spec, build |
|---|---|
| The AI's defaults become your design | I make the design decisions |
| Nobody remembers why it was built this way | Every decision has a written reason |
| Nothing says what "correct" means | Acceptance criteria define "done" |
| Gaps are found after shipping | Tests catch gaps before shipping |
| Fast start, slow to fix later | Slower start, fewer surprises later |

---

**The AI makes me faster. The process makes sure faster still means correct.**

This works for any backend, API, or full-stack project, and with any AI coding tool. The tools change; thinking first and verifying last doesn't.

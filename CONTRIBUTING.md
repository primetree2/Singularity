# Contributing to Singularity

Thank you for your interest in contributing to **Singularity**!  
We welcome all contributions—bug fixes, features, documentation, and performance improvements.  
Please follow the guidelines below to ensure a smooth and consistent workflow.

---

## 🐞 How to Report Bugs

If you encounter a bug:

1. **Check existing issues** to avoid duplicates.
2. Open a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Logs, screenshots, or stack traces (if applicable)
3. Provide environment details:
   - OS, Node version, pnpm version
   - Branch or commit hash

Use the **"Bug Report"** issue template if available.

---

## 💡 How to Suggest Features

To propose new features:

1. Open a **Feature Request** issue.
2. Include:
   - Why the feature is needed  
   - Expected functionality  
   - Alternatives considered  
   - Mockups or examples if possible  
3. Discuss with maintainers before starting implementation.

---

## 🔀 Pull Request Process

Before submitting a PR:

1. Ensure your changes are consistent with project architecture.
2. Run:
   ```bash
   pnpm lint
   pnpm test
   pnpm -w -r exec tsc --noEmit
   ```
3. Update documentation if needed (README, API docs, comments).
4. Keep PRs focused and small—avoid mixing unrelated changes.

### When submitting:

- Use a clear and descriptive PR title.
- Add a detailed description of the change.
- Link related issues (e.g., `Closes #123`).
- Include screenshots or logs for UI/backend changes.

### All PRs must pass CI checks:

- Lint
- Typecheck
- Tests
- OpenAPI validation
- Build

---

## 👀 Code Review Expectations

Reviewers will check:

- Code readability and consistency
- Correct use of shared types and utilities
- Adequate test coverage
- No breaking changes without discussion
- Performance and security impact
- Architecture compliance (controllers thin, services thick)

Be open to feedback—reviews help maintain quality.

---

## 🌿 Branch Naming Conventions

Use descriptive branch names following this format:

```
feature/<short-description>
bugfix/<short-description>
chore/<short-description>
docs/<short-description>
refactor/<short-description>
```

### Examples:

```bash
feature/visibility-score
bugfix/login-rate-limit
docs/api-contract-updates
```

---

## 📝 Commit Message Format

Use the following structure:

```
<type>: <short summary>
```

Where `<type>` is one of:

- `feat` – new feature
- `fix` – bug fix
- `docs` – documentation
- `style` – formatting only
- `refactor` – code refactor
- `test` – tests added/updated
- `chore` – maintenance tasks

### Examples:

```
feat: add nearest dark-site endpoint
fix: correct visibility score calculation
docs: update onboarding guide
```

---

## 🧪 Testing Requirements

All contributions must include tests when applicable:

- Unit tests for services/utils
- Integration tests for API endpoints (optional)
- Tests for new types or DTO helpers in shared package
- Frontend component tests for visible UI elements

### Run tests:

```bash
pnpm test
```

PRs without sufficient test coverage may be requested to add more tests.

---

## 🙏 Thank You

Your contributions help make Singularity a powerful tool for space enthusiasts worldwide.  
We appreciate your time, creativity, and effort.

**Clear skies and happy coding!** 🌌🚀
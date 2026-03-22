# GitHub Actions Workflows

This document describes the automated workflows configured for RainingKeysPython.

---

## Workflows Overview

### 1. 🚀 Create Release (`.github/workflows/release.yml`)

**Trigger:** Tag push starting with `v*` or manual workflow dispatch

**Purpose:** Automatically creates GitHub releases using git-cliff for changelog generation

**Features:**
- ✅ Extracts version from git tag
- ✅ Uses git-cliff to generate changelog automatically
- ✅ Supports existing `CHANGELOG_{VERSION}.md` files (can override)
- ✅ Creates GitHub release with formatted notes
- ✅ Uploads build artifacts:
  - `RainingKeysPython.zip` (Release build)
  - `RainingKeysPython-debug.zip` (Debug build)
  - `CHANGELOG_{VERSION}.md` (Changelog file)
- ✅ Commits generated changelog to repository

**Changelog Generation:**
- Uses [git-cliff](https://github.com/orhun/git-cliff) for automated changelog
- Configured via `cliff.toml` in repository root
- Generates changelog from conventional commits
- Supports commit types: `feat`, `fix`, `perf`, `refactor`, `chore`, `test`, `docs`, `style`
- Follows [Conventional Commits](https://www.conventionalcommits.org/) format

**Manual Trigger:**
```bash
gh workflow run release.yml -f version=1.5.0

# With existing changelog
gh workflow run release.yml -f version=1.5.0 -f use_existing_changelog=true
```

**Automatic Trigger:**
```bash
# Tag version
git tag v1.5.0
git push origin v1.5.0

# Release workflow runs automatically
```

**Permissions Required:**
- `contents: write` - To create releases, upload artifacts, and commit changelogs

---

### 2. ✅ Code Quality (`.github/workflows/ci.yml`)

**Trigger:** Push to main/master/develop branches or Pull Requests

**Purpose:** Comprehensive code quality validation

**Jobs:**

#### Syntax Check
- Compiles all Python files to validate syntax
- Checks `main.py`, `core/*.py`, `core/ui/*.py`
- Fails build if syntax errors found

#### Linting Check
- Runs `pyflakes` on all Python files
- Detects unused imports and undefined variables
- Checks basic code quality issues

#### Import Validation
- Tests all module imports
- Validates import order and dependencies
- Checks for circular imports

#### Type Checking
- Validates AST (Abstract Syntax Tree) for all files
- Ensures type hints are valid
- Checks for syntax-level type errors

#### Configuration Validation
- Tests default configuration creation
- Validates schema checking
- Tests config save/load operations
- Tests temporary config file handling

#### Windows Build Test
- Tests PyInstaller build on Windows runner
- Validates build process
- Ensures executable is created

**Failure Behavior:**
Any job failure will fail the entire workflow, preventing merge of problematic code.

---

## Configuration Files

### 3. cliff.toml - Git-Cliff Configuration

**Purpose:** Configuration for git-cliff changelog generator

**Key Settings:**

#### Changelog Templates
```toml
[changelog]
header = "# Changelog - {{ version }} [{{ date | date(format='%Y-%m-%d') }}]"
body = """
{{ range .patches }}
## {{ .Commit.Title }}

{{ range .commits }}
### {{ .Commit.Header }}
{{ .Commit.Body }}
{{ end }}
{{ end }}
"""
footer = "Full Changelog: [CHANGELOG_{{ version }}.md](link)"
```

#### Commit Types
```toml
[git.conventional_commits]
types = ["feat", "fix", "perf", "refactor", "chore", "test", "docs", "style"]
scope_enhancement = ["feat"]
scope_bug = ["fix"]
scope_performance = ["perf"]
scope_refactor = ["refactor"]
scope_breaking = ["BREAKING CHANGE"]
```

#### Output Settings
```toml
[git]
conventional_commits = true
sort = "date"
git_tag_pattern = "v*"
```

#### Features
- ✅ Conventional commits support
- ✅ Customizable templates
- ✅ Multiple commit type categories
- ✅ Sort by date (chronological)
- ✅ Footer with release notes
- ✅ Automatic version detection

**For detailed git-cliff configuration:**
- [Official Docs](https://git-cliff.org/docs/configuration)

---

## Workflow Status

### Current Status

![GitHub Workflow Status](https://img.shields.io/github/actions/ianaw/RainingKeysPython/CI.yml?branch=main&style=for-the-badge)

### Build Status

![Release](https://img.shields.io/github/actions/ianaw/RainingKeysPython/release.yml?branch=main&style=for-the-badge)

---

## Usage Guide

### Creating a Release

**Option 1: Automatic with Git-Cliff (Recommended)**

1. Make conventional commits:
   ```bash
   git commit -m "feat: Add new feature"
   git commit -m "fix: Resolve bug in input handler"
   ```
2. Push to main branch
3. Create and push git tag:
   ```bash
   git tag v1.5.0
   git push origin v1.5.0
   ```
4. Release workflow runs automatically
5. Git-cliff generates changelog from commits
6. Release appears on GitHub with generated notes
7. Generated changelog is committed to repository

**Option 2: With Existing Changelog**

1. Create `CHANGELOG_{VERSION}.md` manually
2. Create and push git tag
3. Run workflow with `use_existing_changelog=true`:
   ```bash
   gh workflow run release.yml -f version=1.5.0 -f use_existing_changelog=true
   ```

**Option 3: Manual Release**

1. Update `CHANGELOG_{VERSION}.md` manually
2. Create and push git tag:
   ```bash
   git tag v1.5.0
   git push origin v1.5.0
   ```
3. Go to Actions tab
4. Select "Create Release" workflow
5. Click "Run workflow"
6. Enter version: `1.5.0`

### Checking Code Quality

Workflows run automatically on every push and PR:

1. Go to Actions tab in GitHub
2. Select "Code Quality" workflow
3. View results for each job:
   - ✅ Syntax Check
   - ✅ Linting
   - ✅ Import Validation
   - ✅ Type Checking
   - ✅ Config Validation
   - ✅ Windows Build Test
4. Fix any issues found
5. Push fixes and workflow will re-run

### Monitoring Changelog Generation

No separate changelog workflow! Git-cliff is integrated into release workflow.

1. Go to Actions tab
2. Select "Create Release" workflow
3. View changelog generation results

---

## Conventional Commits Guide

Git-cliff works best with [Conventional Commits](https://www.conventionalcommits.org/).

### Commit Format
```
<type>[optional scope]: <description>

[optional body]
[optional footer(s)]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `perf`: A code change that improves performance
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `chore`: Changes to the build process or auxiliary tools/libraries
- `test`: Adding missing tests or correcting existing tests
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, semi-colons, etc)

### Examples

```bash
# Feature addition
git commit -m "feat(input): Add keyboard shortcut configuration"

# Bug fix
git commit -m "fix(overlay): Resolve font caching issue"

# Performance improvement
git commit -m "perf(rendering): Optimize paint event"

# Refactoring
git commit -m "refactor(config): Simplify configuration loading"

# Documentation
git commit -m "docs(readme): Update installation instructions"

# Breaking change
git commit -m "feat!: Change configuration file format"

# With body
git commit -m "fix(input): Handle multiple key presses

Previously, only the last key was registered.
Now, all concurrent key presses are captured."
```

---

## Troubleshooting

### Release Workflow Not Running

**Check:**
1. Token is configured as `GITHUB_TOKEN` secret
2. Workflow YAML syntax is valid
3. Push was to correct branch (`main`, not `main`)
4. Tag format is correct (`vX.Y.Z`)

### Changelog Generation Issues

**Issue:** Changelog doesn't generate properly

**Causes:**
- Not using conventional commit format
- Missing `cliff.toml` configuration file
- No commits since last tag

**Solutions:**
1. Use conventional commit format (see above guide)
2. Ensure `cliff.toml` is in repository root
3. Check commit messages for valid types
4. Verify git history is available

### Code Quality Workflow Fails

**Issue:** CI workflow failing

**Common Causes:**
- Python syntax errors
- Linting errors (pyflakes)
- Import failures
- Type annotation issues

**Solutions:**
1. Check Actions tab for detailed error logs
2. Run checks locally:
   ```bash
   python -m py_compile *.py core/*.py
   python -m pyflakes *.py core/*.py
   ```
3. Fix issues and push
4. Workflow will pass on next run

---

## Secrets Required

### GitHub Token

For automated workflows to work, you need to configure:

**GITHUB_TOKEN**
- Used for: Creating releases, uploading artifacts, committing changes
- Source: Repository Settings → Secrets and variables → Actions
- Permission: `contents: write` (for releases, commits, and artifact uploads)

**Setup:**
1. Go to your repository on GitHub
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `GITHUB_TOKEN`
5. Value: Your personal access token with `repo`, `workflow` scopes
6. Click "Add secret"

---

## Badge Integration

### Add to README.md

```markdown
![CI](https://github.com/ianaw/RainingKeysPython/actions/workflows/ci.yml/badge.svg)
[![Release](https://github.com/ianaw/RainingKeysPython/actions/workflows/release.yml/badge.svg)]
```

Replace `ianaw/RainingKeysPython` with your actual repository path.

---

## Benefits of Git-Cliff

### Automated Changelog Generation
- ✅ No manual changelog maintenance
- ✅ Always reflects actual commits
- ✅ Prevents missing entries
- ✅ Reduces human error

### Consistency
- ✅ Uniform format across all releases
- ✅ Conventional commits structure
- ✅ Professional presentation

### Flexibility
- ✅ Customizable templates
- ✅ Support for multiple commit types
- ✅ Can be overridden with manual changelog
- ✅ Configurable sorting and filtering

---

## Migration from Old Workflow

### What Changed
- **Old:** Separate `changelog.yml` workflow for version bumping
- **New:** Git-cliff integration in `release.yml` workflow

### Why This Is Better
1. **Automated:** No need to manually write changelog entries
2. **Accurate:** Based on actual commit history
3. **Flexible:** Uses conventional commits for structured data
4. **Professional:** Standardized changelog format

### For Users
- No action required! Just make conventional commits.
- Chelogs generate automatically on release.

### For Developers
- Use conventional commit format
- Configure `cliff.toml` for custom templates
- Override with manual `CHANGELOG_{VERSION}.md` if needed

---

## Best Practices

### For Making Releases

1. **Use Conventional Commits**
   - Follow the commit format guide above
   - Use appropriate commit types
   - Include descriptive messages
   - Add scope for better organization

2. **Tag Correctly**
   - Always use format: `v{MAJOR}.{MINOR}.{PATCH}`
   - Example: `v1.4.0`
   - Tags trigger automated release workflow

3. **Test Build Locally**
   - Run `python build.py` before pushing tag
   - Verify both release and debug builds work
   - Check artifacts are generated correctly

4. **Review Generated Changelogs**
   - Git-cliff generates changelog automatically
   - Can be overridden with manual `CHANGELOG_{VERSION}.md`
   - Add detailed release notes if needed

### For Code Quality

1. **Conventional Commits**
   - Follow the commit format guide
   - Use appropriate types for changes
   - Be descriptive in commit messages

2. **Run Tests Locally**
   - Ensure all tests pass before pushing
   - Check for syntax errors with `py_compile`
   - Run linting tools locally

3. **Monitor CI Results**
   - Check Actions tab after pushing
   - Fix any code quality issues immediately
   - Don't merge PRs with failing workflows

---

## Workflow Artifacts

### CI Workflow
**Artifacts:** None (validation only)

### Release Workflow
**Artifacts:**
- `RainingKeysPython.zip` - Release build
- `RainingKeysPython-debug.zip` - Debug build
- `CHANGELOG_{VERSION}.md` - Changelog file (generated or manual)
- `CHANGELOG.md` - Git-cliff generated changelog
- `release_notes.md` - Formatted release notes for GitHub

**Retention:** 30 days

---

## Maintenance

### Updating Workflows

To modify workflows:

1. Edit `.github/workflows/*.yml` files
2. Commit changes
3. Push to repository
4. Workflows update automatically

### Updating Git-Cliff Configuration

To modify changelog generation:

1. Edit `cliff.toml` in repository root
2. Modify templates or settings
3. Commit and push
4. Changes apply on next release

### Adding New Workflows

1. Create new `.github/workflows/{name}.yml` file
2. Follow existing workflow patterns
3. Test workflow manually via Actions tab
4. Commit and push

---

## Security

### Token Security

- ✅ Use repository secrets (never commit tokens)
- ✅ Limit token scopes to minimum required
- ✅ Set token expiration dates
- ✅ Rotate tokens periodically

### Workflow Security

- ✅ Use official GitHub Actions from verified publishers
- ✅ Pin action versions (`@v4`)
- ✅ Review action permissions
- ✅ Enable branch protection rules

---

## Support

### GitHub Actions Documentation

- [Official Docs](https://docs.github.com/actions)
- [Workflow Syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [Contexts](https://docs.github.com/actions/learn-github-actions/contexts)

### Git-Cliff Documentation

- [Official Site](https://git-cliff.org/)
- [Configuration Guide](https://git-cliff.org/docs/configuration)
- [Examples](https://git-cliff.org/docs/examples)

### Troubleshooting

- [Actions Troubleshooting](https://support.github.com/label/actions)
- [Status Page](https://www.githubstatus.com/)

For issues specific to RainingKeysPython workflows:

1. **Check Workflow Logs**: Actions tab → Select workflow → View logs
2. **Review Workflow Files**: `.github/workflows/*.yml`, `cliff.toml`
3. **Report Issues**: Create issue with label `github-actions`

---

## Quick Reference

### Commands

```bash
# Trigger release manually
gh workflow run release.yml -f version=1.5.0

# Trigger release with existing changelog
gh workflow run release.yml -f version=1.5.0 -f use_existing_changelog=true

# View workflow runs
gh run list --workflow=release

# Check workflow status
gh workflow view release

# Cancel running workflow
gh run cancel <run-id>
```

### File Structure

```
.github/
└── workflows/
    ├── release.yml          # 🚀 Automated GitHub releases (with git-cliff)
    ├── ci.yml               # ✅ Code quality checks
    └── cliff.toml           # 📝 Git-cliff configuration
```

---

## Documentation

For detailed documentation on workflows and setup:

- [.github/README.md](.github/README.md) - Workflow directory reference
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Setup guide with troubleshooting
- [cliff.toml](cliff.toml) - Git-cliff configuration

---

## Summary

✅ **2 automated workflows** configured (release, CI)
✅ **Git-cliff** integrated for automatic changelog generation
✅ **Code quality** validation on every push
✅ **Automated releases** with conventional commit parsing
✅ **Comprehensive documentation** created

**Your repository now has a professional CI/CD pipeline with automated changelogs!** 🎉

---

## Next Steps

After setting up workflows:

1. **Configure Token**: Set up `GITHUB_TOKEN` secret following instructions above
2. **Review cliff.toml**: Customize changelog templates if needed
3. **Start Using Conventional Commits**: Format commit messages properly
4. **Test Release Process**:
   - Make small change with conventional commit
   - Push to main branch
   - Create and push tag
   - Verify release appears correctly
5. **Monitor CI**: Check code quality results regularly
6. **Add Badges**: Update README.md with workflow status badges

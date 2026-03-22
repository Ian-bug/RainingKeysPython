# GitHub Actions

This directory contains automated workflows for RainingKeysPython CI/CD pipeline.

---

## Workflows

### 📋 File Listing

```
.github/
├── workflows/
│   ├── release.yml        # 🚀 Automated GitHub release creation (uses git-cliff)
│   ├── ci.yml             # ✅ Code quality validation
│   └── cliff.toml         # 📝 Git-cliff configuration for changelog generation
├── README.md              # This file
```

---

## Workflow Descriptions

### 1. release.yml - Create Release

**Purpose:** Automate GitHub release creation using git-cliff for changelog generation

**Triggers:**
- Tag push (format: `v*`)
- Manual workflow dispatch

**Features:**
- Extracts version from git tag
- Generates changelog using git-cliff (if no existing CHANGELOG_{VERSION}.md)
- Uses existing CHANGELOG_{VERSION}.md if available (can override with `use_existing_changelog` input)
- Creates GitHub release with formatted notes
- Uploads build artifacts:
  - `RainingKeysPython.zip` (Release build)
  - `RainingKeysPython-debug.zip` (Debug build)
  - `CHANGELOG_{VERSION}.md` (Changelog file)

**Changelog Generation:**
- Uses [git-cliff](https://github.com/orhun/git-cliff) for automated changelog
- Configured via `cliff.toml` in repository root
- Generates changelog for commits since last tag
- Follows [Conventional Commits](https://www.conventionalcommits.org/) format
- Supports commit types: `feat`, `fix`, `perf`, `refactor`, `chore`, `test`, `docs`, `style`

**Requirements:**
- `GITHUB_TOKEN` secret configured
- `cliff.toml` configuration file in repository root
- Build artifacts in repository root (or workflow will warn)

**Usage:**
```bash
# Manual trigger with auto-generated changelog
gh workflow run release.yml -f version=1.4.0

# Manual trigger with existing changelog
gh workflow run release.yml -f version=1.4.0 -f use_existing_changelog=true

# Automatic trigger (uses git-cliff)
git tag v1.4.0
git push origin v1.4.0
```

---

### 2. ci.yml - Code Quality

**Purpose:** Comprehensive code validation on every push and PR

**Triggers:**
- Push to `main`, `master`, or `develop`
- Pull requests to these branches

**Jobs:**

#### Syntax Check
- Compiles all Python files with `py_compile`
- Validates syntax for `main.py`, `core/*.py`, `core/ui/*.py`
- Fails workflow if syntax errors found

#### Linting Check
- Runs `pyflakes` on all Python files
- Detects unused imports and undefined variables
- Checks basic code quality issues

#### Import Validation
- Tests all module imports
- Validates import order and dependencies
- Checks for circular import issues

#### Type Checking
- Validates AST (Abstract Syntax Tree)
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

**Requirements:**
- Python 3.10+
- Dependencies installed (from `requirements.txt`)
- PyInstaller installed (for Windows build test)

**Failure Behavior:**
- Any job failure fails entire workflow
- Prevents merging problematic code
- Runs all jobs in parallel for faster feedback

---

### 3. changelog.yml - Changelog Automation

**Purpose:** Automated changelog generation and version bumping

**Triggers:**
- Push to `main`, `master`, or `develop`
- Pull requests to these branches
- Manual workflow dispatch

**Features:**
- Detects changed files in latest commit
- Auto-increments version number (patch version)
- Creates `CHANGELOG_{VERSION}.md` with template
- Extracts git commit info (author, message, date)
- Commits new changelog to repository
- Creates git tag for new version
- Opens Pull Request for review
- Uploads changelog as artifact

**Version Bump Logic:**
- Any changes detected → Increment patch version
- Example: `1.4.0` → `1.4.1`

**Requirements:**
- `GITHUB_TOKEN` secret configured
- `VERSION` in `core/configuration.py` follows `X.Y.Z` format
- Git history available

**Manual Trigger:**
```bash
gh workflow run changelog.yml
```

**Pull Request Process:**
1. Changelog generated with template
2. Version number updated in `core/configuration.py`
3. Git tag created
4. PR opened with label `automated-release`
5. Review and merge PR
6. Release workflow runs on tag merge

---

## Setup Requirements

### Required Secrets

You must configure these repository secrets:

#### GITHUB_TOKEN

**Purpose:** Allows workflows to create releases, commits, and tags

**Setup:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Configure:
   - **Note**: `RainingKeysPython GitHub Actions`
   - **Expiration**: Select expiration period (recommended: 90 days)
   - **Scopes**:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)
4. Click "Generate token"
5. **Copy token immediately** (you won't see it again!)
6. Go to repository Settings → Secrets and variables → Actions
7. Click "New repository secret"
8. Name: `GITHUB_TOKEN`
9. Paste token in "Secret" field
10. Click "Add secret"

**Security Note:** Never commit tokens to your repository. Always use GitHub Secrets.

---

## Workflow Status Badges

Add these badges to your `README.md` to show workflow status:

```markdown
![CI](https://github.com/ianaw/RainingKeysPython/actions/workflows/ci.yml/badge.svg)
[![Release](https://github.com/ianaw/RainingKeysPython/actions/workflows/release.yml/badge.svg)]
[![Changelog](https://github.com/ianaw/RainingKeysPython/actions/workflows/changelog.yml/badge.svg)]
```

---

## Common Issues

### Workflows Not Running

**Symptoms:**
- Push doesn't trigger workflows
- Actions tab shows no recent runs

**Solutions:**
1. Check `GITHUB_TOKEN` secret is configured
2. Verify workflow files are in `.github/workflows/`
3. Check YAML syntax is valid
4. Verify push was to correct branch (`main`, not `main`)

### Release Workflow Fails

**Symptoms:**
- Release creation fails
- Artifacts not found
- Changelog parsing errors

**Solutions:**
1. Ensure `CHANGELOG_{VERSION}.md` exists in root
2. Check tag format (must be `vX.Y.Z`)
3. Run `build.py` locally first to generate artifacts
4. Commit and push artifacts to repository

### Code Quality Workflow Fails

**Symptoms:**
- Syntax check fails
- Linting errors
- Import failures

**Solutions:**
1. Check Actions tab for detailed error logs
2. Run checks locally:
   ```bash
   python -m py_compile *.py core/*.py
   python -m pyflakes *.py core/*.py
   ```
3. Fix issues and push
4. Workflow will pass on next run

### Changelog Workflow Fails

**Symptoms:**
- Version parsing error
- Git diff fails
- File creation permissions

**Solutions:**
1. Check `VERSION` in `core/configuration.py` follows `X.Y.Z` format
2. Ensure workflow has `contents: write` permission
3. Verify git history is available

---

## Usage Guide

### Creating a Release (Automatic - Recommended)

1. Make changes to code
2. Run `build.py` locally:
   ```bash
   python build.py
   ```
3. Commit and push artifacts:
   ```bash
   git add RainingKeysPython.zip RainingKeysPython-debug.zip
   git commit -m "chore: Add release artifacts"
   git push
   ```
4. Create changelog:
   ```bash
   # Create CHANGELOG_1.4.0.md with release notes
   ```
5. Create and push git tag:
   ```bash
   git tag v1.4.0
   git push origin v1.4.0
   ```
6. Release workflow triggers automatically
7. Release appears on GitHub

### Creating a Release (Manual)

1. Go to Actions tab
2. Select "Create Release" workflow
3. Click "Run workflow"
4. Enter version (e.g., `1.4.0`)
5. Click "Run workflow"
6. Release creates with latest code

### Checking Code Quality

Workflows run automatically on every push and PR:

1. Push changes to `main` branch
2. Go to Actions tab
3. Select "Code Quality" workflow
4. View results for each job:
   - ✅ Syntax Check
   - ✅ Linting
   - ✅ Import Validation
   - ✅ Type Checking
   - ✅ Config Validation
   - ✅ Windows Build Test
5. Fix any issues found
6. Push fixes and workflow will re-run

### Generating Changelog

1. Make code changes
2. Push to `main` branch
3. Changelog workflow automatically:
   - Detects changes
   - Increments version
   - Creates changelog file
   - Commits changelog
   - Creates tag
   - Opens PR for review
4. Review PR (labeled `automated-release`)
5. Merge PR
6. Release workflow runs on tag merge

---

## Best Practices

### For Developers

1. **Maintain Semantic Versioning**
   - Major version (`X.0.0`): Breaking changes
   - Minor version (`0.Y.0`): New features
   - Patch version (`0.0.Z`): Bug fixes

2. **Update Changelog Manually for Major/Minor Releases**
   - The automated workflow only bumps patch versions
   - For major/minor releases, create changelog manually
   - Update version number in `core/configuration.py` manually

3. **Review Automated Changelogs**
   - Changelog PR is created with draft status
   - Review and modify before merging
   - Add detailed release notes if needed

4. **Monitor Workflow Results**
   - Check Actions tab after pushing
   - Fix any code quality issues immediately
   - Don't merge PRs with failing workflows

### For Releases

1. **Tag Correctly**
   - Always use format: `v{MAJOR}.{MINOR}.{PATCH}`
   - Example: `v1.4.0`

2. **Create Changelog First**
   - Always create `CHANGELOG_{VERSION}.md` before pushing tag
   - Follow established changelog format
   - Include all changes since last release

3. **Test Build Locally**
   - Run `python build.py` before pushing tag
   - Verify both release and debug builds work
   - Check artifacts are generated correctly

4. **Push Tag Last**
   - Create changelog
   - Update version in code
   - Commit changelog
   - Push commit
   - Create and push tag

---

## Workflow Artifacts

### CI Workflow
**Artifacts:** None (validation only)

### Release Workflow
**Artifacts:**
- `RainingKeysPython.zip` - Release build
- `RainingKeysPython-debug.zip` - Debug build
- `CHANGELOG_{VERSION}.md` - Changelog file
- `release_notes.md` - Formatted release notes

**Retention:** 30 days

### Changelog Workflow
**Artifacts:**
- `CHANGELOG_{VERSION}.md` - Generated changelog

**Retention:** 30 days

---

## Maintenance

### Updating Workflows

To modify workflows:

1. Edit `.github/workflows/*.yml` files
2. Commit changes
3. Push to repository
4. Workflows update automatically

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

### Troubleshooting

- [Actions Troubleshooting](https://support.github.com/label/actions)
- [Status Page](https://www.githubstatus.com/)

For issues specific to RainingKeysPython workflows:

1. **Check Workflow Logs**: Actions tab → Select workflow → View logs
2. **Review Workflow Files**: `.github/workflows/*.yml`
3. **Report Issues**: Create issue with label `github-actions`

---

## Quick Reference

### Commands

```bash
# Trigger release manually
gh workflow run release.yml -f version=1.5.0

# View workflow runs
gh run list --workflow=release

# Check workflow status
gh workflow view release

# Cancel running workflow
gh run cancel <run-id>

# View workflow logs
gh run view <run-id>

# Trigger changelog workflow
gh workflow run changelog.yml

# List all workflows
gh workflow list
```

### File Structure

```
.github/
└── workflows/
    ├── release.yml          # 🚀 Automated GitHub releases
    ├── ci.yml               # ✅ Code quality checks
    └── changelog.yml         # 📝 Automated changelog generation
```

---

## Documentation

For detailed documentation on workflows and setup:

- [GITHUB_WORKFLOWS.md](../GITHUB_WORKFLOWS.md) - Comprehensive workflow documentation
- [GITHUB_SETUP.md](../GITHUB_SETUP.md) - Setup guide with troubleshooting

---

## Summary

✅ **3 automated workflows** configured
✅ **Code quality** validation on every push
✅ **Automated releases** with changelog parsing
✅ **Version bumping** and changelog generation
✅ **Artifact uploads** for distribution

**Ready for production use!** 🎉

# Git-Cliff Integration - Migration Guide

This document describes the migration to git-cliff for automated changelog generation.

---

## What Changed

### Removed
- ❌ `.github/workflows/changelog.yml` - Previous changelog automation workflow
  - Removed manual version bumping
  - Removed PR creation logic
  - Removed tag creation

### Added
- ✅ `cliff.toml` - Git-cliff configuration file
  - Configured changelog templates (header, body, footer)
  - Set up conventional commit parsing
  - Configured git settings (tag pattern, sorting)
- ✅ Updated `.github/workflows/release.yml` - Integrated git-cliff
  - Added git-cliff action step
  - Added changelog formatting
  - Added existing changelog support (can override)
- ✅ Updated documentation files
  - `.github/README.md` - Workflow directory reference
  - `GITHUB_WORKFLOWS.md` - Complete workflow documentation

---

## Why Git-Cliff?

### Benefits

1. **Automated Changelog Generation**
   - No need to manually write changelog entries
   - Based on actual commit history
   - Follows conventional commit format

2. **Consistent Format**
   - All releases use same structure
   - Professional presentation
   - Easy to maintain

3. **Flexibility**
   - Customizable templates
   - Multiple commit type support
   - Can be overridden with manual changelogs

4. **Time Saving**
   - No manual changelog maintenance
   - No version bumping manually
   - Automatic commit parsing

---

## How It Works

### Release Workflow

1. **Tag Push Triggered**
   ```bash
   git tag v1.5.0
   git push origin v1.5.0
   ```

2. **Release Workflow Runs**
   - Extracts version from tag
   - Checks for existing `CHANGELOG_{VERSION}.md`
   - Generates changelog with git-cliff (if no existing file)
   - Creates GitHub release
   - Uploads artifacts

3. **Changelog Generation**
   - Git-cliff parses commits since last tag
   - Follows `cliff.toml` configuration
   - Generates formatted markdown
   - Creates `CHANGELOG_{VERSION}.md`

4. **Commit Changelog**
   - Generated changelog is committed to repository
   - Available for next release

---

## Configuration Files

### cliff.toml

Located at repository root. Key sections:

```toml
[changelog]
header = "# Changelog - {{ version }} [{{ date }}]"
body = "{{ range .patches }}..."
footer = "Full Changelog:..."

[git]
conventional_commits = true
sort = "date"
git_tag_pattern = "v*"

[git.conventional_commits]
types = ["feat", "fix", "perf", "refactor", "chore", "test", "docs", "style"]
```

### Supported Commit Types

- `feat` - New features
- `fix` - Bug fixes
- `perf` - Performance improvements
- `refactor` - Code refactoring
- `chore` - Maintenance tasks
- `test` - Testing changes
- `docs` - Documentation updates
- `style` - Code style changes

---

## Usage Guide

### Automatic Release (Recommended)

1. **Make Conventional Commits**
   ```bash
   git commit -m "feat(input): Add keyboard shortcuts"
   git commit -m "fix(overlay): Resolve font caching issue"
   git commit -m "perf(rendering): Optimize paint event"
   ```

2. **Push Changes**
   ```bash
   git push origin main
   ```

3. **Create Tag**
   ```bash
   git tag v1.5.0
   git push origin v1.5.0
   ```

4. **Release Workflow Runs Automatically**
   - Git-cliff generates changelog
   - GitHub release created
   - Chelog committed to repository

### Manual Release with Existing Changelog

1. **Create Changelog Manually**
   ```bash
   # Create CHANGELOG_1.5.0.md with custom notes
   ```

2. **Create Tag**
   ```bash
   git tag v1.5.0
   git push origin v1.5.0
   ```

3. **Trigger Workflow**
   ```bash
   gh workflow run release.yml -f version=1.5.0 -f use_existing_changelog=true
   ```

### Manual Release with Auto-Generated Changelog

1. **Create Tag**
   ```bash
   git tag v1.5.0
   git push origin v1.5.0
   ```

2. **Trigger Workflow**
   ```bash
   gh workflow run release.yml -f version=1.5.0
   ```

3. **Git-Cliff Generates Changelog**
   - Parses commits since last tag
   - Uses `cliff.toml` configuration
   - Creates `CHANGELOG_1.5.0.md`

---

## Conventional Commits Format

### Structure
```
<type>[optional scope]: <subject>

[optional body]

[optional footer(s)]
```

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

### Commit Types Reference

| Type | Description | Example |
|-------|-------------|----------|
| `feat` | New feature | `feat(auth): Add OAuth login` |
| `fix` | Bug fix | `fix(api): Resolve null pointer exception` |
| `perf` | Performance | `perf(db): Add query caching` |
| `refactor` | Code refactoring | `refactor(ui): Extract components` |
| `chore` | Maintenance | `chore(deps): Update to React 18` |
| `test` | Testing | `test(auth): Add unit tests` |
| `docs` | Documentation | `docs(api): Update endpoints` |
| `style` | Code style | `style(lint): Fix formatting` |

---

## Migration Checklist

### For Developers

- [ ] Review `cliff.toml` configuration
- [ ] Customize changelog templates if needed
- [ ] Update commit messages to follow conventional format
- [ ] Test release process with test tag

### For Release Managers

- [ ] Verify `GITHUB_TOKEN` secret is configured
- [ ] Verify `cliff.toml` is in repository root
- [ ] Review workflow permissions
- [ ] Test manual release with existing changelog
- [ ] Test automatic release with git-cliff

---

## Troubleshooting

### Changelog Not Generated

**Issue:** No changelog file created

**Causes:**
- No conventional commits since last tag
- `cliff.toml` configuration issues
- Git history not available

**Solutions:**
1. Check commit messages follow conventional format
2. Verify `cliff.toml` is in repository root
3. Check git history is available: `git log --oneline`

### Wrong Chelog Format

**Issue:** Changelog looks incorrect

**Causes:**
- `cliff.toml` template issues
- Wrong commit types used
- Git-cliff version mismatch

**Solutions:**
1. Review `cliff.toml` templates
2. Verify commit types are in `types` array
3. Check git-cliff action version in workflow

### Override Not Working

**Issue:** Existing changelog not being used

**Causes:**
- Wrong filename format (must be `CHANGELOG_{VERSION}.md`)
- Not passing `use_existing_changelog=true`

**Solutions:**
1. Verify changelog filename matches version exactly
2. Use `use_existing_changelog=true` input when triggering workflow
3. Check workflow logs for changelog detection messages

---

## Benefits Summary

### Before (Manual Changelog)
- ❌ Manual changelog writing
- ❌ Version bumping required
- ❌ Inconsistent format
- ❌ Easy to miss entries
- ❌ Time-consuming

### After (Git-Cliff)
- ✅ Automatic changelog generation
- ✅ Based on actual commits
- ✅ Consistent format
- ✅ No manual maintenance
- ✅ Time saving

---

## Documentation

### Available Guides

- **[.github/README.md](.github/README.md)** - Workflow directory reference
- **[GITHUB_WORKFLOWS.md](GITHUB_WORKFLOWS.md)** - Complete workflow documentation
- **[GITHUB_SETUP.md](GITHUB_SETUP.md)** - Setup guide with troubleshooting
- **[cliff.toml](cliff.toml)** - Git-cliff configuration

### External Resources

- [Git-Cliff Official Site](https://git-cliff.org/)
- [Git-Cliff Documentation](https://git-cliff.org/docs/configuration)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions Documentation](https://docs.github.com/actions)

---

## Comparison

| Feature | Old Workflow | New (Git-Cliff) |
|----------|---------------|---------------------|
| Chelog Source | Manual files | Git commits |
| Version Bumping | Manual script | Automatic |
| Commit Format | Any | Conventional |
| PR Creation | Required | Optional |
| Changelog Format | Custom | Template-based |
| Maintenance | High | Low |

---

## Next Steps

### Immediate Actions

1. **Review cliff.toml** - Ensure templates match your needs
2. **Test Release Process** - Create a test tag to verify workflow
3. **Update Team** - Train developers on conventional commits
4. **Monitor Releases** - Check generated changelogs for accuracy

### Future Enhancements

- [ ] Custom commit type categories
- [ ] Changelog filtering by type
- [ ] Release notes templates
- [ ] Slack/Discord notifications
- [ ] Release verification workflow

---

## Support

### Git-Cliff Support

- [GitHub Repository](https://github.com/orhun/git-cliff)
- [Documentation](https://git-cliff.org/docs/)
- [Issues](https://github.com/orhun/git-cliff/issues)

### Workflow Support

For issues specific to RainingKeysPython workflows:

1. **Check Workflow Logs**: Actions tab → Select workflow → View logs
2. **Review Workflow Files**: `.github/workflows/*.yml`, `cliff.toml`
3. **Report Issues**: Create issue with label `github-actions`

---

## Summary

✅ **Migrated to git-cliff** for automated changelog generation
✅ **Conventional commits** support for structured changelogs
✅ **Flexible templates** in `cliff.toml`
✅ **Existing changelog** support (can override auto-generation)
✅ **Updated documentation** for all workflows

**Your repository now has automated changelogs based on actual commit history!** 🎉

---

## Migration Complete

All changes have been applied. Your repository is now using git-cliff for changelog generation.

**What to do next:**
1. Start using conventional commit format
2. Review `cliff.toml` configuration
3. Test the release process
4. Enjoy automated changelog generation! 🚀

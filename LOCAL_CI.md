# Local CI Runner

Run GitHub Actions CI checks locally for **10-100x faster** development iteration!

## Why Run Locally?

### ✅ Speed
- **No queue time** - GitHub Actions can take 1-5 minutes to start
- **No download time** - Dependencies already installed
- **No setup time** - Environment already configured
- **Local speed** - Your computer is usually faster than GitHub runners

### ✅ Debugging
- **Instant feedback** - See errors immediately
- **Interactive debugging** - Set breakpoints, inspect variables
- **Quick iteration** - Fix and retest in seconds
- **Detailed logs** - Add any debug output you want

### ✅ Resource Savings
- **Free** - Doesn't consume GitHub Actions minutes
- **Unlimited runs** - Run as many times as you need
- **Private repo friendly** - No quota limitations

### ✅ Flexibility
- **Selective runs** - Run only the checks you need
- **Custom tests** - Add temporary test scripts
- **Local environment** - Matches your development environment exactly

## Usage

### Run All Checks
```bash
python run_local_ci.py
```

This runs all 6 CI checks sequentially:
1. ✅ Syntax Check
2. ✅ Linting Check
3. ✅ Import Check
4. ✅ Type Check
5. ✅ Config Check
6. ✅ Build Test

### Run Individual Checks
```bash
python run_local_ci.py --syntax    # Run only syntax check
python run_local_ci.py --lint      # Run only linting
python run_local_ci.py --import    # Run only import check
python run_local_ci.py --type      # Run only type check
python run_local_ci.py --config    # Run only config check
python run_local_ci.py --build     # Run only build test
```

## Local vs GitHub Actions

| Metric | GitHub Actions | Local CI | Speedup |
|---------|---------------|-----------|---------|
| Queue time | 1-5 minutes | 0 seconds | 60-300x |
| Setup time | 30-60 seconds | 0 seconds | 30-60x |
| Download time | 10-30 seconds | 0 seconds | ∞ |
| Check time | 10-30 seconds | 5-15 seconds | 2x |
| **Total** | **2-6 minutes** | **5-15 seconds** | **8-72x** |

## Example Workflow

### Before (GitHub Actions only)
```bash
# 1. Make changes
git add .
git commit -m "fix: Something"

# 2. Push and wait 2-6 minutes
git push
# ... wait for CI ...

# 3. See CI failed (e.g., syntax error)
# 4. Fix error
git add .
git commit -m "fix: Correct syntax"

# 5. Push and wait 2-6 minutes again
git push
# ... wait for CI again ...

# 6. CI passes!
```

**Total time: 5-15 minutes**

### After (Local CI first)
```bash
# 1. Make changes
git add .
git commit -m "fix: Something"

# 2. Run local CI (5-15 seconds)
python run_local_ci.py
# ... checks pass!

# 3. Push once
git push
# ... GitHub Actions CI passes in 2-6 minutes ...

# 4. Done!
```

**Total time: 2-7 minutes** (3x faster iteration!)

## Benefits Summary

### For Individual Developers
- ⚡ **Faster iteration** - Fix bugs in seconds, not minutes
- 🐛 **Better debugging** - See errors with full stack traces
- 🚀 **Quick validation** - Test before pushing
- 💰 **Save quota** - Don't waste GitHub Actions minutes

### For Teams
- 🔄 **Faster PR reviews** - CI already passed when PR created
- 📊 **Consistent checks** - Everyone uses same local scripts
- 🎯 **Quality focused** - More time on code, less waiting

### For Continuous Deployment
- 🚀 **Quicker releases** - Don't wait for CI to deploy
- 🛡️ **Lower latency** - Deploy immediately after push
- 📈 **More frequent updates** - No CI bottleneck

## Tips

### 1. Run Before Each Push
```bash
# Make changes
# ... edit code ...

# Run local CI
python run_local_ci.py

# Only push if all checks pass
git add .
git commit -m "feat: New feature"
git push
```

### 2. Use Selective Checks
```bash
# Quick syntax check before committing
python run_local_ci.py --syntax

# Full check before pushing
python run_local_ci.py
```

### 3. Add Custom Checks
Add your own checks to `run_local_ci.py`:
```python
def run_custom_check():
    return run_command(
        "Custom Check",
        "python my_test.py",
        "Run my custom test"
    )
```

## Troubleshooting

### Missing Dependencies
If you see import errors:
```bash
# Install missing dependencies
pip install -r requirements.txt
```

### Path Issues
If you see `ModuleNotFoundError: No module named 'core'`:
```bash
# Run from repository root
cd path/to/RainingKeysPython
python run_local_ci.py
```

### Script Errors
If a script fails with unexpected errors:
```bash
# Run the script directly to see full error
python .github/scripts/syntax_check.py
python .github/scripts/type_check.py
python .github/scripts/config_validation.py
```

## Integration with Git Hooks (Optional)

### Pre-commit Hook
Run local CI automatically before each commit:
```bash
# Create .git/hooks/pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
python run_local_ci.py --syntax
EOF

# Make executable
chmod +x .git/hooks/pre-commit
```

### Pre-push Hook
Run all checks before each push:
```bash
# Create .git/hooks/pre-push
cat > .git/hooks/pre-push << 'EOF'
#!/bin/sh
python run_local_ci.py
EOF

# Make executable
chmod +x .git/hooks/pre-push
```

## Monitoring GitHub Actions CI

While using local CI, you can still monitor GitHub Actions:
```bash
# Watch latest CI run
python .github/scripts/monitor_ci.py

# Check CI status
gh run list --workflow="Code Quality" --limit 1
```

## Conclusion

Running CI locally is **highly recommended** for:

- ✅ Faster development iteration
- ✅ Better debugging experience
- ✅ Resource and cost savings
- ✅ Unlimited testing
- ✅ Improved code quality

**Best practice:** Run `python run_local_ci.py` before every push!

---

## Quick Start

```bash
# 1. Run local CI
python run_local_ci.py

# 2. If all checks pass, push
git push

# 3. GitHub Actions will pass too!
```

Happy fast coding! 🚀

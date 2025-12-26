# GitHub Publication - Quick Start Guide

**Status**: READY TO SANITIZE
**Estimated Time**: 2-3 hours minimum
**Risk Level**: HIGH (personal data present)

---

## 🚨 Before You Start

**DO NOT publish as-is!** The repository contains:
- Personal name in 51+ files
- Command history with timestamps
- Database files with personal data
- Local IP addresses
- Absolute file paths

---

## ⚡ Quick Sanitization (30 minutes)

### Step 1: Run Sanitization Script

```bash
cd ~/Home-Alexa
./sanitize_for_github.sh
```

This will:
- Delete logs/, data/, cache/ directories
- Remove Python cache files
- Create example configuration
- Archive session documentation (optional)

### Step 2: Manual Code Fixes

**Fix hardcoded path in camera_vision.py:**

```bash
# Edit terry/features/vision/camera_vision.py
# Change line 31 from:
self.face_recog_path = face_recog_path or "/Users/bruno/face-recognition"

# To:
import os
from pathlib import Path
self.face_recog_path = face_recog_path or os.getenv(
    "FACE_RECOG_PATH",
    str(Path.home() / "face-recognition")
)
```

### Step 3: Sanitize CLAUDE.md

```bash
# Replace all /Users/bruno/ with generic paths
sed -i '' 's|/Users/bruno/Home-Alexa|~/Home-Alexa|g' CLAUDE.md
sed -i '' 's|/Users/bruno/face-recognition|~/face-recognition|g' CLAUDE.md
```

Or manually search and replace in your editor.

### Step 4: Verify

```bash
./scripts/verify_sanitization.sh
```

If it passes, you're ready to publish!

---

## 📋 Complete Checklist (2-3 hours)

### Critical (Must Do)

- [ ] Run `./sanitize_for_github.sh`
- [ ] Fix `terry/features/vision/camera_vision.py` hardcoded path
- [ ] Sanitize CLAUDE.md (replace /Users/bruno/)
- [ ] Run `./scripts/verify_sanitization.sh`
- [ ] Review files still containing "Bruno"
- [ ] Add LICENSE file (see below)

### Recommended (Should Do)

- [ ] Update README.md for public audience
- [ ] Create CONTRIBUTING.md
- [ ] Review and clean session documentation
- [ ] Replace IP addresses with placeholders
- [ ] Add GitHub issue templates

### Optional (Nice to Have)

- [ ] Add screenshots/demo
- [ ] Create CODE_OF_CONDUCT.md
- [ ] Add GitHub badges
- [ ] Set up GitHub Actions

---

## 📄 Add LICENSE (5 minutes)

Choose a license and create `LICENSE` file:

### MIT License (Recommended - most permissive)

```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2025 Terry Voice Assistant Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

### GPL-3.0 (Copyleft - requires derivatives to be open source)

Visit: https://choosealicense.com/licenses/gpl-3.0/

### Apache-2.0 (Patent protection)

Visit: https://choosealicense.com/licenses/apache-2.0/

---

## 🚀 Publishing to GitHub

### Option 1: GitHub Web Interface (Easiest)

1. Go to https://github.com/new
2. Create repository "Terry-Voice-Assistant"
3. DON'T initialize with README (you have one)
4. Follow instructions shown

### Option 2: Command Line

```bash
# Initialize git (if not already)
git init

# Add files
git add .

# Create initial commit
git commit -m "Initial commit: Terry Voice Assistant v6.1.9"

# Create GitHub repo (using gh CLI)
gh repo create Terry-Voice-Assistant --public --source=. --remote=origin

# Or manually add remote
git remote add origin https://github.com/YOUR_USERNAME/Terry-Voice-Assistant.git

# Push
git branch -M main
git push -u origin main
```

---

## ✅ Post-Publication

After publishing:

1. **Add repository description** on GitHub
2. **Add topics/tags**: `voice-assistant`, `python`, `macos`, `ollama`, `speech-recognition`
3. **Enable GitHub Discussions** (optional)
4. **Set up branch protection** (if accepting PRs)
5. **Watch for security alerts** (Dependabot)

---

## 🔍 Verification Commands

Before publishing, verify with these commands:

```bash
# Check for personal name
grep -r "bruno\|Bruno" --include="*.py" --include="*.md" --exclude-dir=".venv" . | wc -l

# Check for absolute paths
grep -r "/Users/bruno" --exclude-dir=".venv" . | wc -l

# Check for IP addresses
grep -r "192\.168\.[0-9]\+\.[0-9]\+" --include="*.py" --include="*.yaml" --exclude-dir=".venv" . | wc -l

# Check for database files
find . -name "*.db" -o -name "*.sqlite" | grep -v ".venv"

# Check for log files
ls -la logs/ 2>/dev/null

# Check git status
git status
```

All should return 0 or minimal results.

---

## 📚 Documentation to Review

Before publishing, review these files:

1. **GITHUB_PUBLICATION_AUDIT.md** - Complete security audit
2. **README.md** - Make sure it's appropriate for public
3. **CLAUDE.md** - Excellent docs, just needs path sanitization
4. **Session notes** - Decide keep/archive/delete

---

## 🆘 Troubleshooting

### "Still finding personal data"

Run individual checks:
```bash
grep -n "bruno" terry/features/vision/camera_vision.py
grep -n "/Users/bruno" CLAUDE.md
```

### "Verification script fails"

Review what it's finding:
```bash
./scripts/verify_sanitization.sh 2>&1 | tee verification.log
```

### "Not sure what to keep"

When in doubt:
- Keep: Code, core documentation, configuration examples
- Delete: Logs, databases, cache, session notes
- Sanitize: Absolute paths, IP addresses, personal names

---

## ⏱️ Time Estimates

- **Quick sanitization**: 30 minutes
- **Thorough sanitization**: 2-3 hours
- **Professional polish**: 4-6 hours
- **Complete documentation**: 8-10 hours

Start with quick sanitization, publish, then improve iteratively.

---

## 🎯 Success Criteria

You're ready to publish when:

✅ `./scripts/verify_sanitization.sh` passes
✅ No personal data in committed files
✅ LICENSE file added
✅ README.md reviewed
✅ Example configs created
✅ All database/log/cache files excluded

---

## 📞 Need Help?

1. Review `GITHUB_PUBLICATION_AUDIT.md` for detailed analysis
2. Check individual sections for specific issues
3. Use verification script to identify problems
4. When in doubt, err on the side of caution (exclude rather than include)

---

**Remember**: Once published, it's public forever. Take the time to do it right!

Good luck with your publication! 🚀

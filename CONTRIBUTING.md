# Contributing to RockPod

We love your input! We want to make contributing to RockPod as easy and transparent as possible.

## 🚀 Quick Start

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch: `git checkout -b my-new-feature`
4. **Make** your changes and test them
5. **Commit** your changes: `git commit -am 'Add some feature'`
6. **Push** to the branch: `git push origin my-new-feature`
7. **Submit** a pull request

## 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/rockpod.git
cd rockpod

# Set up development environment
./setup.sh

# Run tests (if available)
python -m pytest tests/
```

## 📋 Areas We Need Help

### 🌍 Cross-Platform Support
- **Linux support**: Adapt iPod detection and mounting
- **Windows support**: Handle drive letters and Windows paths
- **Alternative mount points**: Support custom mount locations

### 🎨 User Interface
- **Themes**: Dark mode, custom colors
- **System tray**: Windows/Linux system tray integration
- **Desktop app**: Full GUI with settings panel
- **Web interface**: Browser-based control panel

### 📱 Device Support
- **Other firmware**: Support for iPod Linux, iDoom, etc.
- **Modern devices**: USB-C iPods, iPod Touch
- **Alternative players**: Sansa, other Rockbox devices
- **Streaming devices**: Cast to Sonos, AirPlay, etc.

### 🔧 Features
- **Streaming**: Play podcasts without downloading
- **Smart playlists**: Auto-generated based on preferences
- **Podcast discovery**: Search and browse new shows
- **Episode management**: Mark as played, favorites, etc.
- **Sync profiles**: Different settings for different devices

### 🐛 Bug Fixes
- **Error handling**: Better error messages and recovery
- **Performance**: Optimize large library handling
- **Memory usage**: Reduce memory footprint
- **Network resilience**: Better handling of connection issues

## 📖 Code Style

We follow these conventions:

### Python Style
- **PEP 8** compliance with 88 character line limit
- **Type hints** for function parameters and returns
- **Docstrings** for all public functions and classes
- **f-strings** for string formatting

### Git Commits
- **Descriptive titles**: Brief summary of changes
- **Body text**: Explain the "why" not just the "what"
- **Reference issues**: Use "Fixes #123" or "Closes #123"

Example:
```
Add parallel downloading support

Implements concurrent episode downloads using ThreadPoolExecutor
to improve sync performance by 3x. Episodes from different shows
can now download simultaneously while respecting rate limits.

Fixes #42
```

## 🧪 Testing

Before submitting a pull request:

1. **Test manually** with your iPod
2. **Run existing tests**: `python -m pytest tests/`
3. **Test edge cases**: Empty feeds, network errors, etc.
4. **Check different platforms**: If possible, test on macOS/Linux/Windows

## 📝 Pull Request Process

1. **Update documentation** if you change functionality
2. **Add tests** for new features
3. **Update CHANGELOG.md** with your changes
4. **Ensure CI passes** (GitHub Actions)
5. **Request review** from maintainers

### PR Template
When submitting a PR, please include:

```markdown
## Changes
- Brief description of what this PR does

## Testing
- How you tested these changes
- Any edge cases you considered

## Breaking Changes
- List any breaking changes (if any)

## Related Issues
- Fixes #123
- Related to #456
```

## 🎯 Feature Requests

For new features:

1. **Check existing issues** first
2. **Create a detailed issue** explaining:
   - The problem you're solving
   - Proposed solution
   - Alternative approaches considered
   - Example use cases

## 🐛 Bug Reports

For bugs, please include:

- **RockPod version** and platform (macOS version, etc.)
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Error messages** or logs
- **Screenshots** if applicable

## 💬 Community Guidelines

- **Be respectful** and inclusive
- **Help others** learn and contribute
- **Ask questions** if you're unsure
- **Celebrate contributions** from all skill levels

## 🏷️ Issue Labels

We use these labels to organize work:

- `good first issue` - Perfect for new contributors
- `help wanted` - We'd love community help
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Improvements to docs
- `question` - Further information is requested

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general chat
- **Wiki**: For detailed documentation

## 🏆 Recognition

Contributors are automatically added to:
- **README acknowledgments**
- **Release notes**
- **Contributors page**

Thank you for contributing to RockPod! 🎙️
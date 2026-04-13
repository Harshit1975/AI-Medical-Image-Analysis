# Contributing to AI Medical Image Analysis

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct
Be respectful and constructive in all interactions. This is a medical AI project—code quality and safety are paramount.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/AI-Medical-Image-Analysis.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8  # Optional: for linting

# Run tests (when available)
pytest
```

## Code Style

- Follow PEP 8 guidelines for Python
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep CSS organized and commented
- Write clean, readable JavaScript

## Testing

- Test your changes locally before submitting
- Include test cases for new features
- Ensure no regressions on existing functionality

## Pull Request Process

1. Update README.md if you're adding new features
2. Ensure your code passes linting checks
3. Provide a clear description of your changes
4. Reference any related issues

## Reporting Issues

Please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)

## Areas for Contribution

- [ ] Multi-class disease detection
- [ ] Grad-CAM implementation for real heatmaps
- [ ] Docker containerization
- [ ] Cloud deployment guides
- [ ] DICOM format support
- [ ] Documentation improvements
- [ ] Unit tests
- [ ] Bug fixes

---

**Thank you for making medical AI better! 🏥**

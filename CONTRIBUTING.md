# Contributing to Watchtower

Thank you for considering contributing to Watchtower! 🎉  
We welcome contributions of all kinds — from bug reports and feature requests to code, tests, and documentation.

---

## 🚀 Getting Started

1. **Fork the repo** and clone your fork locally.
2. Create a new branch:  
   ```bash
   git checkout -b my-feature-branch
   ```
3. Install dependencies using `pip-tools`:
   ```bash
   pip install pip-tools
   pip-sync requirements.txt
   ```
4. Set up your `.env` file with the required API keys (e.g., `basicAuth`, `n2yo_key`, `nom_key`).
5. Run the script locally and ensure it passes:
   ```bash
   python core/import_udl_to_nominal.py
   ```

---

## 🛠️ How to Contribute

### Bug Reports & Feature Requests
- Use [GitHub Issues](https://github.com/tarunprakash2468/watchtower/issues) to report bugs or request features.
- Please include steps to reproduce or a clear use case.

### Code Contributions
- Follow Python best practices (PEP8, type hints, docstrings).
- Make sure your changes are covered by tests if applicable.
- Keep commits atomic and descriptive.

---

## ✅ Pull Request Process

1. Push your branch to GitHub:
   ```bash
   git push origin my-feature-branch
   ```
2. Open a Pull Request against the `main` branch.
3. Fill out the PR template and explain what you’ve changed and why.
4. Wait for a review and make any requested changes.
5. Once approved, your changes will be merged into `main`.

---

## 🧪 Testing

If applicable, include sample data or test mocks.  
We will add a proper testing framework in future versions.

---

## 📦 Releases

Releases are created from the `main` branch using GitHub Actions.  
Version tags like `v0.1.0` automatically trigger a CI run and draft a GitHub Release.

---

## 🧑‍💻 Code Style

- Use type hints when possible.
- Prefer list/dict comprehensions.
- Avoid large functions; keep logic modular.

---

## 🙏 Code of Conduct

Please be respectful and inclusive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) (if available).

---

## 📬 Questions?

Reach out via GitHub Discussions or open an issue.

Thanks again!

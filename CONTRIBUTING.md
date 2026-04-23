# Making Contributions

Pull requests are always welcome, and the dev team appreciates any help the community can give to help make `finance-dag` better.

There are, however, a few considerations to keep in mind when making source code contributions:
1. Contributions must meet the finance-dag coding standards to be accepted.  This includes indenting standards, use of appropriate existing finance-dag functions.  Developers will help you with this.
2. To be accepted, contributions must follow the project's philosophy — forward compatibility, clean code, use of ruff formatter, use of git repository, etc. The best guide to it is to look at existing code and to ask the lead developers.
3. By submitting a contribution, you grant the project maintainers a non-exclusive, world-wide, royalty-free, irrevocable, and perpetual license to use, modify, and re-license your contribution. If your contribution contains third-party code (e.g., from another open-source project), you must preserve the original license headers and notify the maintainers in the pull request.
4. To ensure that all contributions to finance-dag are legally cleared for inclusion, this project uses the Developer Certificate of Origin (DCO)—the same process used by the Linux Kernel to maintain a clear record of code ownership. It is a per-commit sign-off made by the contributor certifying they have the legal right to submit the code under the terms at <https://developercertificate.org/>. By providing this sign-off in this repository, you also agree to the additional grant described in point 3. Please note that the DCO requires the use of your real name (pseudonyms or anonymous contributions are not accepted). The sign-off is stored as part of the commit message itself, as a line of the format: `Signed-off-by: Full Name <email>`. You can add this by configuring your git with your real name and using the `-s` flag when committing.

## Initial Steps

Before writing any code, please review the existing issues. This helps prevent duplicated efforts and ensures your proposed feature aligns with the project's roadmap. If you are unsure where to start, open an issue to discuss your ideas—the maintainers are happy to help guide you.

## Development

1. Fork the repository.
2. Clone your fork locally: `git clone git@github.com:{your_username}/finance-dag.git`
3. Navigate to the project directory: `cd finance-dag`
4. Create a feature branch: `git checkout -b your-feature-name`
5. Install dependencies: `uv sync --all-extras`
6. Open the codebase in your IDE and begin making your changes.

> Below are the most common commands you will use during development. You should also check the [Notes](#notes) and the [Deprecation Policy](#deprecation-policy) sections.

### Commands

- Install the library, Cython, and all necessary testing/linting tools into your local virtual environment:

`uv sync --all-extras`

- Check for linting errors and auto-fix if possible. It also orders imports:

`uv run ruff check --fix fdag`

- Format the project according to the guidelines:

`uv run ruff format fdag`

- Run tests quickly in your active workspace:

`uv run pytest tests/`

- Run tests and generate a coverage report (via `pytest-cov`):

`uv run pytest tests/ --cov=fdag --cov-report=term-missing`

- Run the full test suite, linting, and type checking across all supported Python environments (which is how they run in CI):

`uvx --with tox-uv tox`

- Enforce strict typing across the library:

`uv run mypy fdag` or `uvx --with tox-uv tox -e type`

- Generate stub files for documenting the Cython code:

`uvx stubgen-pyx fdag`

- Build the package from source (generates the `.whl` and `.tar.gz` files in a `dist/` directory):

`uv build`

## Deprecation Policy

- **Python Support:** The project supports at minimum the two latest minor versions of Python.
- **Deprecation:** Removal of deprecated functionality follows the [NumPy's approach](https://numpy.org/neps/nep-0023-backwards-compatibility.html):
  - Shall be done after at least 2 releases.
  - Shall be listed in the release notes of the release where the removal happened.
  - Can be done in any minor, but not bugfix, release.

## Notes

To install Cython on Windows you first need to install Visual Studio Build Tools:

```powershell
winget install --id Microsoft.VisualStudio.2022.BuildTools --override "--wait --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
```

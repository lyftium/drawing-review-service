# CI workflow

`github-actions-ci.yml` is the GitHub Actions pipeline for this repo: lint, tests,
evaluation gates, manifest validation, and an image build with a smoke test.

It lives here rather than in `.github/workflows/` only because the token used to
publish the repo could not write workflow files. To turn it on:

```bash
mkdir -p .github/workflows
git mv ci/github-actions-ci.yml .github/workflows/ci.yml
git commit -m "Enable CI" && git push
```

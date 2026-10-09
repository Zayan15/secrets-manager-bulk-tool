# AWS Secrets Manager Bulk Management Tool

## Overview

A spreadsheet-driven utility for creating secrets, identifying existing secrets, processing removal requests, and recording completion status and resulting resource references.

**Technologies:** Python · Boto3 · pandas · AWS Secrets Manager · Excel/CSV

**Engineering focus:** AWS SDK integration, batch processing, input validation, and operational automation.

## Features

- Validates required spreadsheet columns and processes per-row actions.
- Creates new secrets or retrieves the reference for an existing secret without updating its value.
- Skips rows already marked completed and writes processing status back to the workbook.
- Exports collected secret resource references to CSV.

## Limitations

- Local source reviewed only; the tool was not executed.
- The removal function uses immediate deletion without recovery. It is not an archive or recoverable deletion workflow.
- Inputs contain plaintext secret values, so real workbooks and generated inventories must never be included in a public demo.
- Before showcasing executable code, add a dry-run mode, recoverable deletion, explicit confirmation, and tests with synthetic values.

This is a prototype. Live AWS behavior and production readiness have not been verified.

## Local setup

Requires Python 3 and AWS credentials configured for an account you are authorized to use. Use a sandbox account with synthetic resources for demonstrations.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**Destructive operation:** a spreadsheet row with the Remove action triggers immediate deletion without recovery. Review every row before running; this prototype has no dry-run mode.

Create a local `secrets.xlsx` workbook with columns `Secret Name`, `Description`, and `Secret Value (Plain Text)`. Optional columns are `Action` (Add or Remove) and `Status` (Completed rows are skipped). Use synthetic values for testing. No workbook is distributed with this repository.

```sh
python manage_secrets.py
```

## Data handling

Local configuration, credentials, generated reports, spreadsheets, and asset bundles are excluded from this repository. Do not commit real account configuration, customer data, or secrets. AWS access uses configured local profiles or the SDK credential chain; no credentials are supplied.

## Validation

Python syntax was checked without executing application code. No AWS requests or deployment tests were run. The dependency list is not version-locked.

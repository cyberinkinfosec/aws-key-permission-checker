# AWS-IAM Permission checker

Got a set of AWS keys and want to know what they can actually do? Normally that means running a bunch of separate commands one by one to check the account, the permissions, and what S3 buckets are reachable. This single-file dashboard does it all for you — just drop your keys in and it shows you everything: who the key belongs to, what access it has, and which S3 buckets it can get into.

## Features

- Scan multiple AWS credential sets (accounts/keys) in one dashboard
- Resolves caller identity via STS (`get-caller-identity`)
- Detects whether the credential is an IAM user or role
- Lists attached IAM policies for IAM users
- Enumerates accessible S3 buckets and checks per-bucket access
- Surfaces errors per-account instead of crashing the whole scan

## Requirements

- Python 3.8+
- `flask`
- `boto3`

```bash
pip install flask boto3
```

## Setup

1. Clone the repo
2. Add your credential sets to the config list:
   ```python
   AWS_CREDENTIALS = [
       {
           "name": "AWS-ACCOUNT-1",
           "access_key": "",
           "secret_key": "",
           "region": "us-east-1"
       }
   ]
   ```
3. **Don't hardcode real keys in the file.** Pull them from environment variables, a secrets manager, or a local `.env` file that's excluded via `.gitignore` — then populate `AWS_CREDENTIALS` from that at runtime instead of committing values directly.

## Usage

```bash
python3 app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Notes

- Intended for local/authorized use only during sanctioned assessments — there's no auth layer on the dashboard itself, so don't expose it on a public interface.
- IAM role policy analysis is currently a stub (`get_user_policies` only handles IAM users) — extend it if you need role policy enumeration too.
- Useful for quickly confirming the real-world blast radius of a given key: identity, policy attachments, and S3 reach, all in one view.

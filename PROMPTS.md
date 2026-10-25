# TrustVault — AI Usage Log

## 1. Purpose
AI assistance was used during the development of TrustVault to understand Flask, debug errors, improve security, write tests, and prepare documentation.

## 2. AI Prompts and Usage

### Task 1: Flask Application Setup
- Prompt: Explain how to set up and run a Flask application in VS Code.
- Usage: Followed setup instructions and ran the application locally.

### Task 2: Debugging Python Errors
- Prompt: Help troubleshoot Python environment and Flask dependency errors.
- Usage: Checked the virtual environment and ran the application using the correct Python interpreter.

### Task 3: CSRF Protection
- Prompt: Explain how to add CSRF protection to Flask forms.
- Usage: Added CSRF tokens to relevant forms and tested rejection of a POST request without a token.

### Task 4: PDF Upload Security
- Prompt: Help test PDF upload validation and file-size restrictions.
- Usage: Tested rejection of a non-PDF file. The file-size limit still requires verification with a valid PDF larger than 10 MB.

### Task 5: Threat Model and Tests
- Prompt: Help create a threat model and security test checklist for a Flask PDF application.
- Usage: Prepared THREATS.md and recorded verified and pending security tests.

## 3. AI Mistakes and Corrections
- Issue: Python packages were initially unavailable in the interpreter used for testing.
- Correction: Used the project's virtual-environment Python interpreter.
- Issue: A form submission failed because its CSRF token was missing.
- Correction: Added CSRF tokens to relevant forms and verified the CSRF test.
- Issue: The first file-size test used a file that was not a valid PDF.
- Correction: Identified the need to use a valid PDF larger than 10 MB to verify the size restriction.

## 4. Verification Status
- Flask application runs locally.
- Login and basic PDF upload/download functionality were checked.
- The automated CSRF test passed.
- Invalid non-PDF upload was rejected.
- Remaining security tests must be verified before submission.

## 5. Responsible AI Use
AI-generated suggestions were reviewed and tested where possible. Unverified code and security claims were not treated as automatically correct. The final implementation and test results must reflect actual verification.

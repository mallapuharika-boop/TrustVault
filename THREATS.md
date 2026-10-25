# TrustVault — Threat Model and Security Tests

## 1. Assets to Protect
- User accounts and passwords
- Uploaded PDF documents
- Document storage and database records
- User sessions and authentication data

## 2. Potential Threats
- **Cross-Site Request Forgery (CSRF):** An attacker may try to submit unauthorized requests.
- **Unauthorized Document Access:** A user may try to access another user's documents.
- **Malicious File Upload:** An attacker may upload invalid or unexpected files.
- **File Size Abuse:** An attacker may upload excessively large files.
- **Credential Attacks:** An attacker may try incorrect passwords repeatedly.
- **Path Traversal:** An attacker may try to access files outside the intended upload directory.

## 3. Security Controls
- CSRF protection is enabled for form submissions.
- PDF uploads are checked for the PDF file signature.
- Upload size is limited to 10 MB.
- Uploaded files are stored using randomly generated filenames.
- Authentication is required for protected application features.

*Verify each control against the actual implementation before final submission.*

## 4. Security Test Results

### Test 1: CSRF Protection
- Test: Submit a POST request without a CSRF token.
- Expected: HTTP 400 response.
- Result: Automated test passed; request was rejected with HTTP 400.
- Status: Passed

### Test 2: PDF Upload Validation
- Test: Attempt to upload a non-PDF file.
- Expected: The application rejects the invalid file.
- Actual result: The .txt file was rejected with "Only PDF are allowed".
- Status: Passed

### Test 3: Upload Size Limit
- **Test:** Upload an 11 MB PDF file.
- **Expected:** The application rejects files larger than 10 MB.
- **Actual result:** The application displayed "File too large.      Maximum upload size is 10 MB."
- **Status:** Passed

### Test 4: Authentication
- **Test:** Attempt to access the dashboard without logging in.
- **Expected:** The application redirects the unauthenticated user to the login page.
- **Actual result:** The dashboard redirected the user to the login page.
- **Status:** Passed

### Test 5: Document Access Control
- **Test:** Logged in as `testuser2` and attempted to access another user's document at `/download/3`.
- **Expected Result:** Access denied with HTTP 403 Forbidden.
- **Actual Result:** HTTP 403 Forbidden returned.
- **Status:** PASS

## 5. Known Limitations
- Tests marked Pending verification have not yet been confirmed.
- Additional review is required before production deployment.
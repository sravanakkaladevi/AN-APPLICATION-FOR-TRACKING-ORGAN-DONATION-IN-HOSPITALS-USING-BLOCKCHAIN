# 🧪 OrganChain - Comprehensive Test Cases

This document outlines the testing strategy for the **Organ Donation Tracking System using Blockchain**. It covers various testing phases ensuring the system is reliable, secure, and ready for deployment.

As per project requirements, **only positive test cases (Happy Path)** have been documented to verify the expected functionality of the system.

---

## 1. Unit Testing
Focuses on verifying the smallest parts of the application (e.g., individual functions, forms, and database models) in isolation.

| Test ID | Test Description | Testing Type | Steps to Execute | Expected Result | Actual Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UT-01** | Validate Donor Registration Form | Unit | 1. Enter valid donor details in form.<br>2. Submit form. | Form validates successfully without throwing errors. | As Expected - Pass |
| **UT-02** | Validate Smart Contract Deployment | Unit | 1. Start Ganache.<br>2. Deploy `OrganDonation` contract. | Contract address is generated and stored successfully. | As Expected - Pass |
| **UT-03** | Validate Password Hashing | Unit | 1. Create new user programmatically.<br>2. Save to database. | Password is encrypted using the PBKDF2 hash algorithm. | As Expected - Pass |
| **UT-04** | Verify Blockchain Connection | Unit | 1. Initialize Web3 provider.<br>2. Call `w3.is_connected()`. | Returns `True` indicating an active blockchain connection. | As Expected - Pass |
| **UT-05** | Validate NLP Sentiment Logic | Unit | 1. Pass positive feedback text to the NLP function. | Function accurately returns a 'Positive' category. | As Expected - Pass |

---

## 2. Integration Testing
Focuses on verifying that different modules or services (e.g., Django, SQLite, and Ganache) work together correctly.

| Test ID | Test Description | Testing Type | Steps to Execute | Expected Result | Actual Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **IT-01** | Django to Ganache Integration | Integration | 1. Trigger blockchain write from a Django view. | A valid transaction hash is returned by Ganache. | As Expected - Pass |
| **IT-02** | Django to SQLite Database Link | Integration | 1. Save a new hospital profile via the ORM. | Record is successfully saved and perfectly retrievable. | As Expected - Pass |
| **IT-03** | Template and View Rendering | Integration | 1. Request dashboard URL.<br>2. Pass context data. | HTML renders correctly with context variables injected. | As Expected - Pass |
| **IT-04** | Authentication Middleware | Integration | 1. Login with valid credentials.<br>2. Access protected route. | Middleware grants access and resolves the user object. | As Expected - Pass |
| **IT-05** | Contract ABI Binding | Integration | 1. Load compiled contract JSON.<br>2. Invoke smart contract method. | Method executes seamlessly without ABI decoding errors. | As Expected - Pass |

---

## 3. Functional Testing
Focuses on verifying that the software functions according to the business requirements and user stories.

| Test ID | Test Description | Testing Type | Steps to Execute | Expected Result | Actual Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FT-01** | Hospital Login Functionality | Functional | 1. Navigate to login.<br>2. Enter hospital credentials.<br>3. Click login. | User is redirected directly to the Hospital Dashboard. | As Expected - Pass |
| **FT-02** | Organ Registration Process | Functional | 1. Login as hospital.<br>2. Click Add Organ.<br>3. Fill details and submit. | Organ immediately appears in the available organs list. | As Expected - Pass |
| **FT-03** | Issue Death Certificate | Functional | 1. Login as admin.<br>2. Select donor.<br>3. Issue certificate. | Donor status updates to deceased in the database. | As Expected - Pass |
| **FT-04** | Feedback Submission | Functional | 1. Login as donor.<br>2. Submit feedback with rating. | Feedback is saved and visible on the admin panel. | As Expected - Pass |
| **FT-05** | Organ Matching Mechanism | Functional | 1. Find available organ.<br>2. Click match button. | Organ status securely changes to 'Matched' on blockchain. | As Expected - Pass |

---

## 4. System Testing
Focuses on testing the complete, integrated system as a whole to evaluate compliance with specified requirements.

| Test ID | Test Description | Testing Type | Steps to Execute | Expected Result | Actual Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ST-01** | End-to-End Donation Flow | System | 1. Register donor.<br>2. Issue death cert.<br>3. Register organ.<br>4. Match organ. | Entire lifecycle completes successfully across all dashboards. | As Expected - Pass |
| **ST-02** | Multi-User Role Access | System | 1. Login as Admin, Hospital, and Donor simultaneously. | Each session maintains strict role boundaries and routing. | As Expected - Pass |
| **ST-03** | Blockchain Ledger Immutability | System | 1. Complete an organ match.<br>2. Fetch ledger history. | Ledger history accurately and permanently reflects transaction. | As Expected - Pass |
| **ST-04** | System UI Responsiveness | System | 1. Open application on mobile or tablet resolution. | Layout scales correctly without breaking native scrolling. | As Expected - Pass |
| **ST-05** | Dashboard Data Aggregation | System | 1. Add new users and transactions.<br>2. View admin charts. | Charts, graphs, and counters update accurately in real-time. | As Expected - Pass |

---

## 5. User Acceptance Testing (UAT)
Focuses on validating the end-to-end business flow with real-world scenarios to ensure the software is acceptable to the end user.

| Test ID | Test Description | Testing Type | Steps to Execute | Expected Result | Actual Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **UAT-01** | Hospital Admin Acceptance | UAT | 1. Hospital admin logs in.<br>2. Manages local donors. | Admin easily understands and navigates the custom UI. | As Expected - Pass |
| **UAT-02** | Visual Theme Consistency | UAT | 1. Switch between dark/light themes on dashboards. | UI remains beautiful, readable, and premium everywhere. | As Expected - Pass |
| **UAT-03** | System Feedback Notifications | UAT | 1. Perform an action like registering a new patient. | Success toast/alert appears clearly confirming the action. | As Expected - Pass |
| **UAT-04** | User Registration Flow | UAT | 1. New user registers on the public portal. | Process is highly intuitive and requires no manual training. | As Expected - Pass |
| **UAT-05** | Presentation Demo Viability | UAT | 1. Run full demo flow for viva project presentation. | System performs flawlessly and reliably without any crashes. | As Expected - Pass |

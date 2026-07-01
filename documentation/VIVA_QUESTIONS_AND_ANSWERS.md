# 🫀 OrganChain — Viva-Voce Questions and Answers

This guide is designed to help you prepare for your MCA Final Year Viva-Voce project presentation. It covers the technical stack, blockchain integration, system architecture, database, security, and project-specific workflows.

---

## 📋 Table of Contents
1. [General & Architecture Questions](#1-general--architecture-questions)
2. [Blockchain & Solidity Questions](#2-blockchain--solidity-questions)
3. [Django Backend & Database Questions](#3-django-backend--database-questions)
4. [Security & Workflows Questions](#4-security--workflows-questions)
5. [Troubleshooting & Demo Questions](#5-troubleshooting--demo-questions)

---

## 1. General & Architecture Questions

### Q1: What is the main objective of this project?
**Answer:** The objective of **OrganChain** is to create a secure, transparent, and decentralized organ donation tracking system. It manages the entire lifecycle of organ donation: donor pledging, hospital verification, recipient registration, matching, and transplant execution, while logging critical events to an immutable blockchain ledger to prevent data tampering, queue manipulation, or black-marketing.

### Q2: Why did you choose Blockchain for this project instead of a centralized database?
**Answer:** Centralized databases are managed by a single administrator, which makes them vulnerable to unauthorized alterations, insider attacks, and data deletion. In organ donation:
- **Trust and Immutability:** Patients and hospitals need absolute trust that the waiting lists, organ registrations, and transplant outcomes cannot be retroactively altered.
- **Audit Trails:** Blockchain creates a chronologically ordered, tamper-proof, cryptographic log of all events.
- **Decentralization:** No single hospital can control the network; decisions are governed by a shared smart contract.

### Q3: Explain the high-level architecture of your system.
**Answer:** The system follows a **3-tier architecture**:
1. **Presentation Layer (Frontend):** Responsive dashboards built with Bootstrap 5, Custom CSS, and Vanilla JS, tailored for Admins, Hospitals, and Donors.
2. **Business Logic Layer (Backend):** A Django web server handling authentication, database operations, forms validation, and business workflows. It uses `Web3.py` as the middleware connecting Python code to the blockchain.
3. **Ledger Layer (Blockchain):** A Solidity smart contract (`OrganDonation.sol`) compiled and deployed on a local Ethereum node (**Ganache**), executing transactions on-chain.

---

## 2. Blockchain & Solidity Questions

### Q4: What are the main functions in your smart contract, and what do they do?
**Answer:** The Solidity contract (`OrganDonation.sol`) manages organ state transitions. The key components are:
- **State Variable `organCount`:** Tracks the total number of registered organs.
- **Struct `Organ`:** Stores record details (ID, donor info, organ type, hospital name, doctor name, timestamp, status, recorder's address, and matched recipient hospital).
- **Enum `OrganStatus`:** Represents states: `Available` (0), `Matched` (1), and `Transplanted` (2).
- **Functions:**
  - `registerDonation()`: Registers a verified organ on the ledger.
  - `matchOrgan()`: Matches an available organ to a recipient hospital, changing status to `Matched`.
  - `completeTransplant()`: Confirms the successful transplant, changing status to `Transplanted`.
  - `getOrgan()`: Returns details of a specific organ.
- **Events:** `DonationRegistered`, `OrganMatched`, and `OrganTransplanted` are emitted to allow external observers (like Django) to process transaction receipts.

### Q5: What is Ganache, and why is it used here?
**Answer:** Ganache is a personal Ethereum blockchain simulator provided by the Truffle Suite. It runs locally on port `7545` and provides 10 pre-funded test accounts with 100 fake Ether (ETH) each. It is ideal for development and viva demos because it executes transactions instantly, requires no real-money gas costs, and does not depend on a live internet connection.

### Q6: What is Web3.py, and how does Django use it?
**Answer:** `Web3.py` is a Python library used to interact with Ethereum node JSON-RPC interfaces (like Ganache). 
In our application, Django uses Web3.py in the service layer (`service.py`):
1. Connects to Ganache via `Web3.HTTPProvider(settings.GANACHE_RPC_URL)`.
2. Loads the smart contract's **ABI** and deployed **address**.
3. Invokes contract transactions (e.g., `contract.functions.registerDonation().transact({'from': sender})`).
4. Waits for the blockchain receipt using `w3.eth.wait_for_transaction_receipt(tx_hash)`.

### Q7: What is the Contract ABI and Bytecode?
**Answer:**
- **Bytecode:** The compiled machine code of the Solidity smart contract that runs on the Ethereum Virtual Machine (EVM).
- **ABI (Application Binary Interface):** A JSON description of the contract’s functions, arguments, return types, and events. It acts as a map so that Web3.py knows how to encode Python inputs into binary data for the blockchain, and how to decode responses.

### Q8: What does a blockchain transaction receipt contain?
**Answer:** It contains metadata about an executed transaction, including:
- `transactionHash`: Unique cryptographic hash of the transaction.
- `blockNumber`: The index of the block in which the transaction was recorded.
- `gasUsed`: The amount of gas consumed by the execution.
- `status`: `1` for successful execution, `0` for reversion/failure.
- `logs`: Encoded event logs emitted by the smart contract during execution.

---

## 3. Django Backend & Database Questions

### Q9: What data is stored in the relational database (SQLite) vs. the Blockchain?
**Answer:** 
- **Relational Database (SQLite):** User credentials (username, hashed passwords), user profiles (names, emails, contact details, profile pictures, theme configurations), medical death certificates, system audit logs, and feedback text.
- **Blockchain (Ganache):** Only critical matching metadata (donor id/name, organ type, hospital name, doctor name, timestamp, organ status, and the transaction hash).
- **Why?**
  - **Cost (Gas):** Storing large texts or files on a blockchain is prohibitively expensive.
  - **Performance:** Relational databases are faster for search, filtering, and authentication queries.
  - **Privacy (GDPR/Compliance):** Personal Identifiable Information (PII) like home addresses or phone numbers should not be stored permanently on a public ledger where they cannot be deleted.

### Q10: How does the application maintain consistency between SQLite and the Blockchain?
**Answer:** We use a **hybrid database-blockchain pattern**:
1. When a hospital registers an organ, Django first attempts to write it to the blockchain via Web3.py.
2. Once the blockchain transaction succeeds and returns a `transactionHash` and block number, Django saves the record to the SQLite database, including the transaction hash.
3. This creates a link: the SQLite record contains the `blockchain_tx_hash` which can be verified at any time by querying the Ethereum node.

### Q11: How are Django forms and authentication structured in the project?
**Answer:**
- **Authentication:** Django's built-in authentication system is extended using a custom `User` model that tracks roles (is_superuser, is_hospital, is_donor).
- **Role-Based Routing:** Upon login, a custom redirection view (`CustomLoginView`) inspects the user profile type and sends Admins to `admin_dashboard`, Hospitals to `hospital_dashboard`, and Donors to `donor_dashboard`.
- **Forms:** Django `ModelForms` are used for security and validation. `DonorRegistrationForm` and `HospitalRegistrationForm` extend `UserCreationForm` to automatically handle security, email verification checks, password rules, and custom database bindings.

---

## 4. Security & Workflows Questions

### Q12: How is access security enforced in your views?
**Answer:** 
- **View-Level Protection:** Django decorators `@login_required` prevent unauthenticated access to dashboards.
- **Role Validation:** We check role flags (e.g., `hasattr(request.user, 'hospitalprofile')`) at the beginning of views. If a donor tries to access a hospital URL or a hospital tries to access an admin dashboard, they are redirected immediately with an error message.
- **Data Validation:** Form submissions validate inputs (e.g., ensuring a hospital can only match available organs, and cannot match an organ registered by itself).

### Q13: How does the organ donation matching workflow work?
**Answer:**
1. **Pledging (Donor):** A registered donor logs into the Donor Portal and submits a pledge for specific organs.
2. **Registration (Hospital):** When the donor arrives at a hospital or is certified deceased, the hospital registers the organ in the Hospital Portal, sending the registration transaction to the blockchain.
3. **Matching:** The matching hospital searches the location/organ catalog. They identify an available organ and click **Match**. Django executes the `matchOrgan` blockchain transaction, locking the organ to that recipient hospital.
4. **Transplantation:** Once the transplant surgery completes, the receiving hospital marks it as **Transplanted**, updating the status on the blockchain ledger permanently.

### Q14: What is the Death Certificate module, and what is its role?
**Answer:** In real-world organ donation, an organ can only be harvested from a deceased donor after medical verification. 
In our application:
- An Admin issues a digital **Death Certificate** containing a certificate number and cause of death, linked to a specific donor profile.
- Issuing this certificate automatically updates the donor profile state (`is_deceased = True`) in the database, allowing hospitals to proceed with organ registration and harvesting.

---

## 5. Troubleshooting & Demo Questions

### Q15: What happens if Ganache is offline when a user tries to register an organ?
**Answer:** If the Ganache blockchain server is offline, the Web3 provider raises a `ConnectionError` or `HTTPConnectionPool` exception. 
Our view handles this exception in `_format_blockchain_error(e)`:
- It intercepts the connection error.
- It prevents the record from being saved to SQLite (avoiding database-blockchain inconsistency).
- It displays a user-friendly error message on the frontend: *"Blockchain service is not running. Start Ganache at http://127.0.0.1:7545, then try again."*

### Q16: Why are there two service files in your codebase (`backend/blockchain_service.py` and `backend/core/blockchain/service.py`)?
**Answer:** 
- `backend/blockchain_service.py` is the **direct API service** that connects to `blockchain/compiled/` ABI and is mapped to REST endpoints under `/api/blockchain/...` (useful for external clients, integration testing, and mobile app APIs). It interacts with the contract using `registerDonor` and `getDonor`.
- `backend/core/blockchain/service.py` is the **core Django web service** that integrates with the main Django templates. It uses Truffle-style JSON artifacts (`backend/build/contracts/OrganDonation.json`) to invoke actions like `registerDonation`, `matchOrgan`, and `completeTransplant`.
- *This dual structure shows the ability to support both standard Django templated pages and separate JSON-RPC REST API integrations.*

### Q17: What commands did you write to test your system?
**Answer:** We wrote a comprehensive Python unit test suite at `blockchain/tests/test_blockchain.py` verifying 50 test cases. It can be run using:
```bash
python blockchain/tests/test_blockchain.py
```
This verifies blockchain connection status, smart contract functions, error boundaries (like matching an already transplanted organ), and database validation logic.

---

## 6. Advanced & Scenario-Based Questions

### Q18: What is Gas in Ethereum, and who pays for it in your system?
**Answer:** In Ethereum, "Gas" is a unit that measures the computational effort required to execute specific operations on the network. Every transaction (like registering an organ) costs gas to prevent infinite loops and spam. 
In our application, we use Ganache (a local test network), so transactions are executed using test Ether from predefined local accounts. If deployed to a real network, the Hospital invoking the smart contract would need to pay the gas fees using real cryptocurrency (e.g., ETH on Ethereum, or MATIC on Polygon).

### Q19: How did you design the user interface, and why is it important for this project?
**Answer:** The user interface was built using Bootstrap 5, custom Vanilla CSS, and modern design principles (like Glassmorphism, smooth animations, and responsive native scrolling). 
In healthcare, user experience is critical because medical professionals and patients need clear, uncluttered information. We implemented distinct dashboards (Admin, Hospital, Donor) with role-specific views so that a hospital administrator can instantly see pending approvals or match organs without being overwhelmed by unrelated data.

### Q20: What happens if two hospitals try to match the same organ at the exact same time?
**Answer:** This is a classic concurrency problem, which is elegantly solved by the blockchain. The Ethereum Virtual Machine (EVM) executes transactions sequentially. If two hospitals submit a match request simultaneously:
1. One transaction will be mined into a block slightly before the other.
2. The smart contract state will change (the organ's status updates from `Available` to `Matched`).
3. When the second transaction attempts to execute, the contract logic (using `require(organ.status == OrganStatus.Available)`) will fail, and the second transaction will safely revert.

### Q21: Can a hospital delete a registered organ from the blockchain if they made a mistake?
**Answer:** No. Blockchain is inherently **immutable**, meaning data cannot be erased or altered retroactively. 
If a mistake is made, the standard procedure is to issue a new corrective transaction (like marking the organ as unavailable or rejected). This ensures that a complete, auditable history of all actions—even mistakes—is preserved forever.

### Q22: Did you use Django Signals or specific ORM features?
**Answer:** We heavily utilized the Django ORM (Object-Relational Mapping) to interact with SQLite securely without writing raw SQL queries, which protects against SQL Injection attacks. 
For example, we use `select_related()` and `filter()` queries to efficiently retrieve complex related datasets (like joining a Donor profile with a Death Certificate) before presenting it on the dashboards.

### Q23: What are the future enhancements you would add to this project?
**Answer:** 
1. **IPFS Integration:** Storing heavy medical records (like X-Rays or tissue typing reports) on the InterPlanetary File System (IPFS) and only storing the resulting hash on the blockchain.
2. **AI/Machine Learning:** Integrating a predictive model that suggests the best recipient match based on tissue compatibility, distance, and urgency rather than a manual search.
3. **Smart Contract Audits:** Adding multi-signature (Multi-Sig) approvals so that both a hospital admin and a government official must sign off on a transplant before the state changes.

### Q24: How many blockchain transactions occur during a complete organ match lifecycle?
**Answer:** There are exactly **4** distinct blockchain transactions that happen during a full lifecycle:
1. **Donor Organ Registration:** Writing the donor's organ details to the blockchain (creating the Organ ID).
2. **Recipient Registration:** Writing the recipient's medical needs and details to the blockchain (creating the Recipient ID).
3. **Organ Matching:** When the admin approves the match, a smart contract function (`matchOrgan`) is called to formally link the Organ ID and Recipient ID together on-chain.
4. **Transplant Completion:** After surgery, a final smart contract function (`completeTransplantWithRecipient`) is called to permanently lock the organ state as "Transplanted" so it can never be used again.

### Q25: Can an organ from Hospital A (e.g. CARE) be given to a high-priority patient at Hospital B (e.g. Apollo)? Does the system support inter-hospital transfers?
**Answer:** **Yes, absolutely.** This is one of the strongest use cases of our blockchain system!
- **How it works:** The matching logic strictly checks for medical compatibility (Organ Type and Blood Group). It intentionally *does not* restrict the match to the same hospital.
- **The Benefit:** Because all hospitals are connected to the same decentralized ledger (Ganache), the Central Admin has a global view of all available organs and all waiting patients. The admin can instantly match Hospital A's organ to Hospital B's high-priority recipient.
- **UI Tracking:** The Transplant Tracking dashboard visually highlights these cross-hospital transfers with an "Inter-Hospital" badge, demonstrating how the system breaks down data silos between hospitals to save high-priority patients.

---

> [!TIP]
> **Viva Tip:** Keep your answers concise, highlight "Blockchain Immutability" and "Role-Based Access Control", and refer to the custom Bootstrap 5 dashboards as proof of a ready-to-use healthcare application.

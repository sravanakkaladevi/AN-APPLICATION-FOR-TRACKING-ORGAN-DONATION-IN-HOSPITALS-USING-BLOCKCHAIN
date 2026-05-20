# Graph Report - organ_donation  (2026-05-20)

## Corpus Check
- 67 files · ~325,637 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 412 nodes · 615 edges · 63 communities (41 shown, 22 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 149 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `96123d76`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 62|Community 62]]

## God Nodes (most connected - your core abstractions)
1. `TestBlockchainModule` - 54 edges
2. `CustomLoginView` - 26 edges
3. `User` - 22 edges
4. `DonorProfile` - 22 edges
5. `HospitalProfile` - 22 edges
6. `OrganRecord` - 22 edges
7. `DeathCertificate` - 18 edges
8. `Feedback` - 18 edges
9. `Recipient` - 17 edges
10. `ProfilePictureUploadTests` - 16 edges

## Surprising Connections (you probably didn't know these)
- `register_donor()` --calls--> `DonorRegistrationForm`  [EXTRACTED]
  backend/core/views.py → backend/core/forms.py
- `register_hospital()` --calls--> `HospitalRegistrationForm`  [EXTRACTED]
  backend/core/views.py → backend/core/forms.py
- `FormChoicesTests` --uses--> `OrganRegistrationForm`  [INFERRED]
  backend/core/tests.py → backend/core/forms.py
- `MatchOrganViewTests` --uses--> `OrganRegistrationForm`  [INFERRED]
  backend/core/tests.py → backend/core/forms.py
- `ProfilePictureUploadTests` --uses--> `OrganRegistrationForm`  [INFERRED]
  backend/core/tests.py → backend/core/forms.py

## Communities (63 total, 22 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (4): Stabilized Blockchain Unit Testing Module for Organ Donation Project.     Expand, Set up fresh connection for every test., Prints a formatted row for the MCA project output., TestBlockchainModule

### Community 1 - "Community 1"
Cohesion: 0.12
Nodes (31): AbstractUser, HospitalProfileAdmin, AdminHospitalManagementForm, AdminProfileUpdateForm, DeathCertificateForm, DonorPledgeForm, DonorProfileEditForm, DonorRegistrationForm (+23 more)

### Community 2 - "Community 2"
Cohesion: 0.11
Nodes (24): get_blockchain_status(), get_contract(), _get_contract_address(), _get_sender_account(), _load_contract_artifact(), match_organ_on_chain(), register_organ_on_chain(), transplant_organ_on_chain() (+16 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (5): AdminHospitalManagementTests, FormChoicesTests, MatchOrganViewTests, ProfilePictureUploadTests, TestCase

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (21): 🎓 Academic Info, 🔴 Admin Portal, ⛓️ Blockchain Integration, code:text (organ_donation/), code:bash (python blockchain/tests/test_blockchain.py), code:block2 (Donor/Hospital/Admin Browser), code:bash (python manage.py createsuperuser), ⚙️ Configuration (+13 more)

### Community 5 - "Community 5"
Cohesion: 0.15
Nodes (16): connect_blockchain(), get_contract_instance(), get_donor(), Verifies a transaction by its hash., Connects to the local Ganache blockchain., Loads the contract ABI and address and returns a contract instance., Registers a donor on the blockchain., Retrieves donor details from the blockchain. (+8 more)

### Community 6 - "Community 6"
Cohesion: 0.12
Nodes (16): functionDebugData, generatedSources, linkReferences, object, opcodes, sourceMap, contracts, OrganDonation.sol (+8 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (16): functionDebugData, generatedSources, linkReferences, object, opcodes, sourceMap, contracts, OrganDonation.sol (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.13
Nodes (14): 1. Prerequisites, 2. Start Local Blockchain, 3. Deploy Smart Contract, 4. Run Automated Tests, 📡 API Endpoints, ⛓️ Blockchain Integration Module, code:text (blockchain/), code:bash (pip install web3 py-solc-x) (+6 more)

### Community 9 - "Community 9"
Cohesion: 0.13
Nodes (15): code:bash (git clone <repo-url>), code:bash (pip install -r backend/requirements.txt), code:bash (python scripts/setup_all.py), code:bash (# Migrations), code:bash (python manage.py runserver), code:bat (start_project.bat), Prerequisites, ⚡ Quick Start (Windows Only) (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.18
Nodes (10): 📊 1. Overall System Completeness, 🏗️ 2. Component-by-Component Status, 📂 3. Repository Architecture & Folder Structure, 🧪 4. Test Suite Verification Summary, ⚡ 5. How to Reach 100% Live Connection, code:text (organ_donation/), code:bash (python scripts/setup_all.py), code:bash (python blockchain/tests/test_blockchain.py) (+2 more)

### Community 11 - "Community 11"
Cohesion: 0.20
Nodes (9): devDependencies, truffle, name, private, scripts, compile, migrate, migrate:reset (+1 more)

### Community 12 - "Community 12"
Cohesion: 0.22
Nodes (8): 1. Introduction, 2. Testing Objectives, 3. Testing Environment, 4. Testing Summary, 5. Result Analysis, 6. Conclusion, Project: Organ Donation Tracking System using Blockchain, PROJECT TESTING REPORT

### Community 13 - "Community 13"
Cohesion: 0.33
Nodes (5): Application Data Flow, code:text (organ_donation/), Directory Structure, Repository Architecture: Organ Donation Tracker, System Architecture Diagram

### Community 14 - "Community 14"
Cohesion: 0.70
Nodes (4): ensure_donor(), ensure_hospital(), main(), next_blockchain_id()

### Community 15 - "Community 15"
Cohesion: 0.40
Nodes (4): code:mermaid (erDiagram), Database Schema Documentation, Entity-Relationship (ER) Diagram, Schema File

### Community 16 - "Community 16"
Cohesion: 0.50
Nodes (3): git.ignoreLimitWarning, python.analysis.exclude, python.defaultInterpreterPath

### Community 62 - "Community 62"
Cohesion: 0.20
Nodes (9): args, command, type, args, command, type, mcpServers, code-review-graph (+1 more)

## Knowledge Gaps
- **97 isolated node(s):** `command`, `args`, `type`, `command`, `args` (+92 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CustomLoginView` connect `Community 1` to `Community 2`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Why does `ProfilePictureUploadTests` connect `Community 3` to `Community 1`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `CustomLoginView` (e.g. with `DonorRegistrationForm` and `HospitalRegistrationForm`) actually correct?**
  _`CustomLoginView` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `User` (e.g. with `HospitalProfileAdmin` and `DonorRegistrationForm`) actually correct?**
  _`User` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `DonorProfile` (e.g. with `HospitalProfileAdmin` and `DonorRegistrationForm`) actually correct?**
  _`DonorProfile` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `HospitalProfile` (e.g. with `HospitalProfileAdmin` and `DonorRegistrationForm`) actually correct?**
  _`HospitalProfile` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `command`, `args`, `type` to the rest of the system?**
  _116 weakly-connected nodes found - possible documentation gaps or missing edges._
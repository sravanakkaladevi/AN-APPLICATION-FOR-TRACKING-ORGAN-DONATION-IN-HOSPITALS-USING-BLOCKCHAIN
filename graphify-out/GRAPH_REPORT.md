# Graph Report - organ_donation  (2026-06-30)

## Corpus Check
- 76 files · ~1,843,535 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 14 nodes · 13 edges · 2 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0ba85218`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]

## God Nodes (most connected - your core abstractions)
1. `🫀 OrganChain — Tracking Organ Donation in Hospitals using Blockchain` - 8 edges
2. `🚀 Setup & Execution` - 6 edges
3. `📊 System Completeness & Viva Readiness` - 1 edges
4. `🛠️ Current Stack & Component Status` - 1 edges
5. `💡 Important Design Rule` - 1 edges
6. `🔄 Main Workflow` - 1 edges
7. `📂 Project Structure` - 1 edges
8. `1. Create and activate virtual environment` - 1 edges
9. `2. Install dependencies` - 1 edges
10. `3. Start Ganache` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (2 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.25
Nodes (7): 🛠️ Current Stack & Component Status, 💡 Important Design Rule, 🔄 Main Workflow, 🫀 OrganChain — Tracking Organ Donation in Hospitals using Blockchain, 📂 Project Structure, 📊 System Completeness & Viva Readiness, ✅ Useful Verification Commands

### Community 1 - "Community 1"
Cohesion: 0.33
Nodes (6): 1. Create and activate virtual environment, 2. Install dependencies, 3. Start Ganache, 4. Run Automatic Setup (Migrations, Compiling, Deployment), 5. Run server, 🚀 Setup & Execution

## Knowledge Gaps
- **11 isolated node(s):** `📊 System Completeness & Viva Readiness`, `🛠️ Current Stack & Component Status`, `💡 Important Design Rule`, `🔄 Main Workflow`, `📂 Project Structure` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `🫀 OrganChain — Tracking Organ Donation in Hospitals using Blockchain` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.808) - this node is a cross-community bridge._
- **Why does `🚀 Setup & Execution` connect `Community 1` to `Community 0`?**
  _High betweenness centrality (0.641) - this node is a cross-community bridge._
- **What connects `📊 System Completeness & Viva Readiness`, `🛠️ Current Stack & Component Status`, `💡 Important Design Rule` to the rest of the system?**
  _11 weakly-connected nodes found - possible documentation gaps or missing edges._
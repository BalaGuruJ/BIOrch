BIOrch/
│
├── contracts/                 ← WHAT the runtime must do
│   ├── tool-gateway/
│   ├── repository-agent/
│   ├── orchestrator/
│   ├── tableau-agent/
│   └── powerbi-agent/
│
├── tasks/                     ← WHAT we ask development to build
│
├── review/                    ← DID the implementation satisfy the contract?
│
├── src/                       ← HOW the runtime is actually implemented
│
├── .agents/                   ← Development-time infrastructure
│
├── .gemini/commands/          ← Development workflow commands
│   ├── biorch-sync.toml
│   ├── biorch-governance.toml
│   ├── biorch-roadmap.toml
│   └── biorch-contract.toml   ← new
│
└── docs/ROADMAP.md            ← project direction
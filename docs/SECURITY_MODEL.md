# Security Model

Treat agents as untrusted decision-makers and tools as privileged capabilities.

Agents request operations.
The Tool Gateway validates and authorizes operations.
Tools perform operations.
Results return through the gateway.

Never place API keys in source code or prompts.

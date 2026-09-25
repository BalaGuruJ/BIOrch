# BIOrch Security Architecture

Security in BIOrch is a first-class citizen, implemented through a strict architectural boundary called the **Tool Gateway**.

## Agent / Tool Separation
Agents do not have unrestricted access to the underlying system or domain engines. They are decoupled from the execution of tools. When an agent determines that an action is required, it must issue a request to the Tool Gateway. 

## The Tool Gateway
The Tool Gateway intercepts all tool execution requests from all agents. It is responsible for:

1. **Input/Schema Validation:** Ensuring the tool request conforms precisely to the tool's defined schema.
2. **Authentication & Authorization:** Verifying that the requesting agent is permitted to use the requested tool (Tool Allowlisting).
3. **Filesystem Policy:** Enforcing path restrictions (e.g., ensuring operations stay within the target project directory and preventing path traversal).
4. **Network Policy:** Enforcing rules on what external URLs or services can be contacted (if at all).
5. **Approval Policy:** Requiring explicit human approval for sensitive or mutating operations (e.g., `write_file`, `git_commit`).
6. **Auditability:** Logging all tool requests, approvals, and outcomes for transparency.

## Example Allowlist Policy
An agent's capabilities are scoped to its role. For example:
- **RepositoryAgent:** Allowed: `read_file`, `list_directory`. Requires Approval: `write_file`. Denied: `web_fetch`.
- **ResearchAgent:** Allowed: `web_fetch`. Denied: `write_file`.

*Note: The Tool Gateway is an architectural concept at this stage and is not yet implemented.*

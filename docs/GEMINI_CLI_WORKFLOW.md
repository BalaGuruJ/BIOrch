# Gemini CLI Workflow

ChatGPT designs/reviews. Gemini CLI implements/validates in Cloud Shell.

Cycle:
1. Create a task prompt under `/tmp/`.
2. Inspect repository state.
3. Implement only defined scope.
4. Run tests and validation.
5. Inspect `git diff`.
6. Commit after review.
7. Return results to ChatGPT for architecture review.

Never ask Gemini to implement the entire roadmap in one task.

---
name: exa-search
description: >-
  Neural search via Exa MCP for web, code, and company research. Use when the user needs
  web search, code examples, company intel, people lookup, or AI-powered deep research
  with Exa's neural search engine. Do not use for unrelated tasks. Inputs should include
  relevant files, constraints, and available tools. Output should be a concise plan,
  result, or verification summary.
---

# Exa Search

Neural search for web content, code, companies, and people via the Exa MCP server.

## When to Activate

- User needs current web information or news
- Searching for code examples, API docs, or technical references
- Researching companies, competitors, or market players
- Finding professional profiles or people in a domain
- Running background research for any development task
- User says "search for", "look up", "find", or "what's the latest on"

## MCP Requirement

Exa MCP server must be configured. Add to `~/.claude.json`:

```json
"exa-web-search": {
  "command": "npx",
  "args": ["-y", "exa-mcp-server"],
  "env": { "EXA_API_KEY": "YOUR_EXA_API_KEY_HERE" }
}
```

Get an API key at [exa.ai](https://exa.ai).

## Core Tools

### web_search_exa
General web search for current information, news, or facts.

```
web_search_exa(query: "latest AI developments 2026", numResults: 5)
```

**Parameters:**

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `query` | string | required | Search query |
| `numResults` | number | 8 | Number of results |

### web_search_advanced_exa
Filtered search with domain and date constraints.

```
web_search_advanced_exa(
  query: "React Server Components best practices",
  numResults: 5,
  includeDomains: ["github.com", "react.dev"],
  startPublishedDate: "2025-01-01"
)
```

**Parameters:**

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `query` | string | required | Search query |
| `numResults` | number | 8 | Number of results |
| `includeDomains` | string[] | none | Limit to specific domains |
| `excludeDomains` | string[] | none | Exclude specific domains |
| `startPublishedDate` | string | none | ISO date filter (start) |
| `endPublishedDate` | string | none | ISO date filter (end) |

### get_code_context_exa
Find code examples and documentation from GitHub, Stack Overflow, and docs sites.

```
get_code_context_exa(query: "Python asyncio patterns", tokensNum: 3000)
```

**Parameters:**

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `query` | string | required | Code or API search query |
| `tokensNum` | number | 5000 | Content tokens (1000-50000) |

### company_research_exa
Research companies for business intelligence and news.

```
company_research_exa(companyName: "Anthropic", numResults: 5)
```

**Parameters:**

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `companyName` | string | required | Company name |
| `numResults` | number | 5 | Number of results |

### people_search_exa
Find professional profiles and bios.

```
people_search_exa(query: "AI safety researchers at Anthropic", numResults: 5)
```

### crawling_exa
Extract full page content from a URL.

```
crawling_exa(url: "https://example.com/article", tokensNum: 5000)
```

**Parameters:**

| Param | Type | Default | Notes |
|-------|------|---------|-------|
| `url` | string | required | URL to extract |
| `tokensNum` | number | 5000 | Content tokens |

### deep_researcher_start / deep_researcher_check
Start an AI research agent that runs asynchronously.

```
# Start research
deep_researcher_start(query: "comprehensive analysis of AI code editors in 2026")

# Check status (returns results when complete)
deep_researcher_check(researchId: "<id from start>")
```

## Usage Patterns

### Quick Lookup
```
web_search_exa(query: "Node.js 22 new features", numResults: 3)
```

### Code Research
```
get_code_context_exa(query: "Rust error handling patterns Result type", tokensNum: 3000)
```

### Company Due Diligence
```
company_research_exa(companyName: "Vercel", numResults: 5)
web_search_advanced_exa(query: "Vercel funding valuation 2026", numResults: 3)
```

### Technical Deep Dive
```
# Start async research
deep_researcher_start(query: "WebAssembly component model status and adoption")
# ... do other work ...
deep_researcher_check(researchId: "<id>")
```

## Tips

- Use `web_search_exa` for broad queries, `web_search_advanced_exa` for filtered results
- Lower `tokensNum` (1000-2000) for focused code snippets, higher (5000+) for comprehensive context
- Combine `company_research_exa` with `web_search_advanced_exa` for thorough company analysis
- Use `crawling_exa` to get full content from specific URLs found in search results
- `deep_researcher_start` is best for comprehensive topics that benefit from AI synthesis

## Related Skills

- `deep-research` — Full research workflow using firecrawl + exa together
- `market-research` — Business-oriented research with decision frameworks

## Mock smoke test

Run `python scripts/test-external-integrations.py --mode mock` from the repository root. Mock mode must not call external services, open browsers, publish content, send messages, or process real media. It validates the Codex workflow, expected parameters, safety boundaries, and missing-dependency handling.

## Real integration test

Run `python scripts/test-external-integrations.py --mode real` only after the required tools, environment variables, and optional MCP servers are configured. Real mode must report `EXTERNAL_NOT_CONFIGURED` when dependencies are missing. Workflows with posting, messaging, payment, publishing, or other side effects remain dry-run unless the user explicitly enables side effects.

## Missing dependency behavior

If a required tool, environment variable, network path, browser, or MCP server is unavailable, return setup instructions and stop. Do not retry indefinitely, do not silently block, and do not mark real external behavior as passed.

## No silent blocking

For Codex use, finish with a compact status summary: `mock_status`, `real_status`, missing dependencies, and the next setup command. External integrations are usable in mock mode without credentials, but real provider success requires a configured environment.

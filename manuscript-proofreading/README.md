# manuscript-proofreading — cross-platform install guide

Final-stage proofreading skill for manuscripts accepted by the **Annals of
Coloproctology (ACP)**: numerical/statistical consistency, tables/figures,
Methods–Results agreement, and ACP house style, with PDF-ready annotation
comments.

Source: https://github.com/kasaha11/manuscript-proofreading-skill
Created by **Soo Young Lee** (Division of Colorectal Surgery, Chonnam National
University Medical School); revised by **Sanghee Kang** (Korea University
College of Medicine). The skill follows the open **Agent Skills** format
(`SKILL.md` + `scripts/` + `references/`), so the same folder works across agents.

```
manuscript-proofreading/
├── SKILL.md                      # entry point (Agent Skills standard)
├── README.md                     # this file
├── scripts/verify_table.py       # deterministic arithmetic / notation checker
├── references/acp_house_style.md # default house style (Annals of Coloproctology)
├── references/verify_table_schema.md
├── tests/sample_checks.json      # fixture + checks.json template (45 cases)
├── tests/run_tests.py            # python3 tests/run_tests.py → 45/45 passed
└── chatgpt/GPT_INSTRUCTIONS.md   # condensed instructions for a ChatGPT Custom GPT
```

## 1. Claude

**Claude.ai / Claude Desktop** — Settings → Capabilities → Skills → upload
`manuscript-proofreading.skill` (the zip of this folder).

**Claude Code** — copy the folder to `~/.claude/skills/manuscript-proofreading/`
(personal) or `<repo>/.claude/skills/manuscript-proofreading/` (project).
Invoke with `/manuscript-proofreading` or just ask to proofread a manuscript.

## 2. OpenAI Codex (ChatGPT's coding agent: CLI, IDE extension, and ChatGPT web Codex)

Codex reads the same `SKILL.md` format. Copy the folder to one of:

- `~/.codex/skills/manuscript-proofreading/` — personal, all repos
- `<repo>/.agents/skills/manuscript-proofreading/` — project-scoped

Then in Codex: `$manuscript-proofreading` or describe the task. Python 3 must be
available in the Codex sandbox for `scripts/verify_table.py` (it is by default).

## 3. ChatGPT app (Custom GPT or Project) — no skill loader, manual setup

ChatGPT's chat app does not read `SKILL.md`, so build a Custom GPT:

1. ChatGPT → Explore GPTs → **Create** → Configure.
2. **Name:** Manuscript Proofreader (ACP).
3. **Instructions:** paste the full contents of `chatgpt/GPT_INSTRUCTIONS.md`
   (7.1k chars; the limit is 8k).
4. **Knowledge:** upload these four files (flat, no folders):
   - `references/acp_house_style.md`
   - `references/verify_table_schema.md`
   - `scripts/verify_table.py`
   - `tests/sample_checks.json`
5. **Capabilities:** enable **Code Interpreter & Data Analysis** (required —
   this is how the GPT runs `verify_table.py` from `/mnt/data/` and renders
   PDF pages to images for figure inspection). Web browsing may stay off.
6. Save. Usage: attach the manuscript PDF (+ supplements) and say e.g.
   "이 논문 프루프 봐줘" / "Proofread this accepted manuscript."

For a **ChatGPT Project** instead of a GPT: put the same text in the project's
custom instructions and the same four files in project files; enable data
analysis.

Known differences vs. Claude/Codex: the GPT cannot read the ACP style file
"once per session" automatically — the instructions tell it to read the
knowledge files before working, but if house-style checks look skipped, say
"apply acp_house_style.md."

## 4. Other Agent Skills-compatible agents (Cursor, Gemini CLI, etc.)

Copy the folder into the agent's skills directory (commonly `.agents/skills/`
or `.cursor/skills/`). No changes needed.

## Verifying the checker

```bash
python3 tests/run_tests.py          # expects "45/45 passed"
python3 scripts/verify_table.py --show-schema
```

## Changelog

- **2.0.0** — checker no longer aborts on a malformed item (`FLAG [Input error]`);
  accepts printed strings (`"40.0%"`, `"P<0.001"`, `"1,234"`); precision-aware
  tolerances (no false flag on integer-rounded %); indeterminate P bounds
  (`<0.1`) not flagged; numeric P=0/1 detection for all spellings; test fixture;
  ChatGPT Custom GPT instructions; open-standard frontmatter.
- **1.0.0** — initial release.

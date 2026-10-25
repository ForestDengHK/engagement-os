# Connectors

## How tool references work

Skill and reference prose in this plugin says `~~category` where work happens in an external
tool, instead of naming a product. `~~email` means "whichever email tool this practice uses";
the default is in the table below. Read a placeholder as that category's tool, and substitute
your own if your practice differs.

Two forms appear:

- **Bare placeholder** — "paste it into `~~email`". The instruction holds for any tool in the category.
- **Anchored placeholder** — "`~~email` (Outlook: …)". The instruction depends on that product's
  specific behaviour or format, so the product stays named; with a different tool, expect to adapt it.

Not replaced: script names, commands, paths, code blocks, quoted examples, and a client's own
product names in examples.

## Categories

| Category | Placeholder | Default in this practice | Other options |
|---|---|---|---|
| Email | `~~email` | Outlook / Microsoft 365 | Gmail |
| Chat | `~~chat` | Microsoft Teams | Slack |
| Calendar | `~~calendar` | Outlook calendar | Google Calendar |
| Document store | `~~document store` | SharePoint / OneDrive | Google Drive, Box, Dropbox |
| Project tracker | `~~project tracker` | Azure DevOps / Jira | Asana, Linear |
| Knowledge base | `~~knowledge base` | Confluence / SharePoint pages | Notion |
| Spreadsheet | `~~spreadsheet` | Excel | Google Sheets |

Not every category is referenced by a skill today; the table is the full vocabulary so new
prose uses the same names.

## Outlook-specific paths

The email clipboard path is Outlook-specific, not generic `~~email`. `skills/eng-os/scripts/md2outlook.py`
(driven by `eng-email`) emits Outlook-compatible inline-styled HTML for the Word rendering engine and
places it on the macOS clipboard; the same applies to any `to_outlook`-style paste path. With another
`~~email` tool, use `--out FILE.html`, open it in a browser, and copy from there — then check how that
tool handles pasted tables.

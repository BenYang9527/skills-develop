<p align="right">English | <a href="README.zh-CN.md">中文</a></p>

# TD Coding Retro

By default, review one **AI coding session** and produce an **HTML report** on problems worth addressing and practices worth keeping. Explicitly request a cross-session retrospective to find evidence-backed causes shared by distinct incidents.

## 1. Retrospective results

![Retrospective and improvement workflow](assets/workflow-overview.en.svg)

<details>
<summary>View a sample report</summary>

![Retrospective report](assets/report-preview-en.png)

</details>

## 2. Getting started

**Install**

```bash
npx skills@latest add YangZhaoWeblog/skills-develop --skill td-coding-retro -g -y
```

**Review the current session**

```text
$td-coding-retro Review the current session.
```

**Review a specific session**

```text
$td-coding-retro Review session <Session ID>.
```

**Find shared causes across sessions**

```text
$td-coding-retro Review <project> across sessions from <start date> through <end date>.
```

You can also specify session IDs. The retrospective counts each incident once and reports shared causes with sources and recommendations.

**After reading the report, select improvements to implement**

```text
Implement items 1, 3 and 5. Leave the others unchanged.
```

Improvements are classified as general or project-specific. After you select items, the agent identifies where to make the changes, then implements and verifies them.

After an agent in a separate context verifies the selected changes, results are added to the original HTML report. Retained changes stay in the working tree for your Git Diff review; commit and push require your explicit authorization.

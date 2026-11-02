<p align="right">中文 | <a href="README.md">English</a></p>

# TD Harness Build

为项目构建或升级 **Harness**，提供从需求澄清到实现、验证与交付的 **多 Agent 协作工作流**。

## 一、开始使用

在项目目录安装：

```bash
npx skills@latest add YangZhaoWeblog/skills-develop --skill td-harness-build -y
```

**新项目**

```text
$td-harness-build 我想做一个 Obsidian 插件。
```

**已有项目**

```text
$td-harness-build
```

完成后检查差异，确认原有规则得到保留。

## 二、开始开发

直接说需求，AI 会按项目 **Workflow** 推进。

- **新增功能**：将选中的笔记导出为 Anki 卡片。
- **修复问题**：导出笔记时图片丢失了，帮我排查并修复。
- **改进体验**：导出设置太繁琐了，帮我重新设计一下。

## 三、工作流

1. **产品阶段**：讨论需求和方案，确认交付需求与 AC 后结束。开发可以在另一个会话启动。
2. **开发启动**：确认整体方案，并明确允许启动哪些 Task；可以只启动其中一个。
3. **Task 执行**：先做开发 Clarify；需要用户作出关键决定时暂停等待回答。核验通过后细化 Plan，范围内计划就绪即继续实现，不逐份等待 Plan 批准。
4. **提交**：验证与独立审查通过后，按有效授权执行提交；合并和发布分别核对授权。

[![产品与开发工作流](assets/workflow-overview.svg)](assets/workflow-overview.svg)

<details>
<summary>查看详细返工图</summary>

![开发工作流与反馈闭环](assets/workflow-feedback.svg)

</details>

### 并行执行

仅启动已授权且依赖就绪的 Task。上层看任务之间的依赖，下层展开一个 Task 内部的实现分工。

<p align="center">
  <a href="assets/task-relationships.svg"><img src="assets/task-relationships.svg" alt="Task 之间的并行与依赖，以及 Task 内部的实现并行与汇合" width="1200"></a>
</p>

支持一个会话协调多个 Task，也支持多个终端分别负责 Task。具体分工与资源隔离见 [Agent 职责](assets/project/agent-roles.md#1-分工)。

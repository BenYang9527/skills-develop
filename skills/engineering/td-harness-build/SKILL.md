---
name: td-harness-build
description: 为 AI Coding 项目初始化、迁移或升级协作规则、项目文档和开发任务模板。当前实现基于 Git。
---

# TD Harness Build

为 AI Coding 项目建立可复用的 Harness。先复制模板，再填项目事实；保留项目规则和历史，不让 AI 每次重新设计骨架。

## 使用入口

裸调用时，先检查当前目录，默认初始化、补缺或升级当前项目。目标明确且无冲突的操作直接执行；目录包含多个独立项目、位于用户主目录或目标不明时，先确认位置。用户只要求检查或预览时，不写文件。

| 起点 | 如何推进 |
|---|---|
| 空项目，尚无需求或技术栈 | 引导用户说明要解决的问题，复用产品 Clarify；明确足以支持选型的目标，推荐并确认技术栈。获准后建立最小工程，再接入 Harness 与检查 |
| 已有需求或原型，尚无代码 | 核对目标和约束，不把外部资料自动当作已确认需求；确认技术方案和最小工程范围后接入 |
| 已有代码或 Harness | 核实现状，保留代码、有效规则、工具与未完成任务；补缺或按授权升级 |
| 再次调用 | 核对当前文件、配置和执行结果，续做缺口；已有记录仅作线索，不重置有效成果或重复询问 |

**跨会话交接**：产品讨论和 Build 可以分会话进行。需求与 AC 保存在本轮产品文档；已确认的技术选型记入 **.harness/docs/architecture.md §6「技术选型与设计决策」**，注明尚未落地的部分，不把选型写成已实现架构。当前产品 Overview 只链接相关决策与剩余阻塞，不复制内容。

再次调用时，沿项目 AGENTS 的恢复规则定位本轮产品文档，读取已确认内容和选型依据，核对工程及工具现状后续做。目标不明才询问，不要求用户复制上一会话。产品 Confirm 不代表 Build 完成；完成接入后回到当前开发任务的 Clarify，保留任务进度与独立核验。

**先查再问**：项目中能查到的自行核对；普通实现细节自行处理。影响产品方向、技术栈或授权的决定，给出推荐与理由，将同批已知问题集中询问。只问影响当前接入的问题；新问题须有新的依据。用户暂不能决定时，说明阻塞并报告未完成，不反复追问。

根据产品需求确认应用形态及主要框架，也可以明确不采用框架；存在实质取舍时比较方案并给出推荐，用户确认后再建立工程。

技术栈未定时可以先复制通用骨架，但不能报告接入完成。最小工程只建立运行与检查基础，不实现业务功能；涉及工程创建、Git 初始化或安装工具时核对授权，不擅自创建远端、提交或发布。

## 工作流

1. 核对目标项目的 AGENTS.md、Git 状态和当前分支。多项目仓库先确定目标目录。
2. 按 [upgrade-project.md](references/upgrade-project.md) 判断文件归属和修改边界。需要确认的迁移整批列出；获准后连续执行，出现新的越界操作才停止。
3. 按 [独立初始化派发](references/init-agents.md) 先派只读 Agent，核对 API 和持久化能力。探测失败时先解决缺口，不把未知写成默认值。

   已有项目先备份原入口和定制模板，再在隔离目录运行 **scripts/build_harness.sh**，生成骨架、模板和标准 Workflow。入口中的项目独有规则按升级约定保留到 **Rules**，构建脚本不会替你判断如何合并这些内容。

   遇到 **[CONFIRM]** 迁移提示时，先取得批准，再加 **--accept-migrations** 重跑。

4. 依次派 [入口](references/init-agent-entry.md)、[架构](references/init-agent-architecture.md) 初始化 Agent，按 upgrade-project.md 融合并核对项目规则及结构。AGENTS 作为统一入口；按实际平台连接入口，保留已有内容，冲突交用户决定。
5. 按 init-agents.md 派发适用专题：独立任务并行，有依赖则等待；主 Agent 统一核对事实和索引。各 Agent 按 [文档维护指导](references/init-project-docs.md) 填项目事实；每个 Harness 必须包含术语表 `glossary.md`。空项目、局部更新及平台限制按派发规则处理，缺工具或环境明确报告。
6. 按 [检查命令接入](references/setup-checks.md) 固定项目命令并验证，再运行 `scripts/setup_hooks.sh` 启用 Git hooks。未配置的检查只准备脚本、不启用；已有 Hook、core.hooksPath 和项目脚本按授权融合，不覆盖。
7. 按 [原生 Agent 接入](references/agent-setup.md) 配置并核验项目角色，绑定实际模型与权限。配置前必读 [角色职责](assets/project/agent-roles.md)：Owner 指本 Task 的交付负责人，其职责、与主 Agent 的关系及 Reviewer 边界均以该文件为准。
8. 在隔离候选中合入项目事实和定制，核对原项目未被改写。要检查重复生成是否稳定，另用尚未融合定制的隔离目录；**已融合的候选不得再由构建脚本覆盖。**

   按已确认参数核验模板、Workflow、角色和工具结果，处理 **[MERGE]** 提示。再由未参与本轮生成的独立 **Reviewer**，按 [交付审阅](references/upgrade-project.md#5-独立交付审阅) 检查最终文件和验证证据。

   问题修正并复审通过后，再核对候选与原项目的差异，按批准范围应用变更，最后报告实际结果。


## 完成与反馈

只有以下条件全部满足，才报告 **“Harness 初始化／升级已完成”**：

- 项目方向、技术栈和运行方式已明确，适用的最小工程与 Git 基础已就绪。
- 规则、模板与项目事实已适配，引用有效，没有影响当前开发的关键占位或未决冲突；最终产物已通过独立交付审阅。
- 当前开发必需的运行、构建、测试与静态检查入口可用；适用 Hook 按约定生效。确实不适用的项说明依据，缺工具或未执行不能算不适用。
- 独立 Reviewer 已通过当前平台实际调用核验，能执行验证并审查，Owner 分工明确；模型、权限及尚需重载的状态如实记录。
- 检查入口已用通过、失败样例验证，相关错误能被发现；项目已有内容与历史保留。历史告警与接入故障按 [检查命令接入](references/setup-checks.md) 分开处理。

缺少必要条件就报告 **“初始化／升级未完成”**，列明已完成内容、缺口、影响及下一步。用户决定暂缓必要接入时仍为未完成。未来发布、尚未涉及的集成环境等可按实际需求后续补充，不要求提前建设。

每次结束都在用户可见回复中给出结论；不能仅藏在工具日志中。成功退出或复制成功不等于完整接入。只做预览时说明“仅检查，未执行初始化／升级”。

不强制新增状态文件。难以从项目重建的决定或阻塞原因，可简记在已有记录或交接文件中；再次执行先核对事实，再继续缺口。

## 生成后的项目流程

- **产品阶段**：Clarify → Design → Confirm，确定本次交付需求与 AC。
- **开发阶段**：执行顺序见下方 AGENTS 模板第二章，不在本入口另定义阶段顺序。

初始化或升级时，按 [AGENTS 模板第二章](assets/agents.md#二workflow) 接入完整流程；阶段顺序与用户确认以该章为准；角色职责、交接与返工轮次以 [角色职责模板](assets/project/agent-roles.md) 为准。项目接入后，从项目自己的 **AGENTS.md**、本地专题规则与阶段模板运行，日常任务无须安装本 Skill。下方“按需读取”供生成与升级使用。

源 Skill 更新不会自动修改已生成项目。项目升级仍按 **upgrade-project.md** 核对候选差异与授权，不强制新增版本台账；用户主动调用其他可选工具不受此边界限制。

## 边界

- 修改限于本次获准的 Harness、模板、配置及初始化最小工程；不借接入之名改动业务功能，也不执行未授权的提交或发布。
- 升级按 upgrade-project.md 保护项目内容和历史任务，规则冲突由用户决定。
- 技术栈未定的空项目可先建骨架。事实待定就标明，写生产代码前补齐技术方案和验证入口。
- 模板提供通用流程；项目集成按实际需要接入。

## 按需读取

只读取当前步骤需要的章节；下表是条件路由，不是必读清单。链接不触发递归读取，按当前问题展开；专题文档入口集中在文档维护指导中。

| 当前工作 | 读取 |
|---|---|
| 融合旧内容、处理迁移或多项目归属 | [upgrade-project.md](references/upgrade-project.md) |
| 初始化、升级或首次补齐项目文档，派发独立专题 Agent | [init-agents.md](references/init-agents.md) |
| 初始化／升级时填项目事实与术语 | [init-project-docs.md](references/init-project-docs.md) |
| 接入检查工具、固定命令及 Git hooks | [setup-checks.md](references/setup-checks.md) |
| 接入平台原生角色、核对模型与权限 | [agent-setup.md](references/agent-setup.md) |
| 探测 API 和持久化能力 | [init-agent-detect.md](references/init-agent-detect.md) |
| 接入完整流程、核对用户确认、返工及任务恢复规则 | [AGENTS 模板第二章](assets/agents.md#二workflow) |
| 核对角色分工、并行派发与返工续接 | [agent-roles.md](assets/project/agent-roles.md) |
| 核对阶段记录与完成检查 | [产品模板](assets/workflows/product/)、[开发模板](assets/workflows/development/) |
| 产品澄清或开发独立核验 | [clarify.md](assets/project/docs/clarify.md)，按产品或开发部分读取 |
| 设计行为改动的单元测试（Unit Test，UT） | [tdd.md](assets/project/docs/testing/tdd.md) |
| 选择检查、处理失败及判断复验范围 | [verification.md](assets/project/docs/verification.md) |
| 确认项目实际使用 go-zero | [framework-gozero.md](references/framework-gozero.md) |
| 识别到库项目 | [library-context.md](references/library-context.md) |

## 模板与脚本

- `assets/agents.md` 生成项目入口；`assets/project/` 复制到 `.harness/`，包含澄清与 TDD 方法。
- `assets/workflows/development/`、`assets/workflows/product/` 分别复制到 `.harness/templates/development/`、`.harness/templates/product/`。
- `assets/.golangci.yml` 是可选 Go 检查配置，接入前核对项目现有规则。
- `scripts/configure_agents.py` 按已确认参数生成原生 Agent 配置；模板在 `assets/native-agents/`，实际调用另行核验。
- `scripts/build_harness.sh` 准备骨架并更新标准 Workflow 与模板；`scripts/setup_hooks.sh` 安装 hooks。`pre_commit_check.sh`、`pre_push_check.sh`、`commit_msg_check.sh` 分别检查提交前质量、推送前质量和提交消息。

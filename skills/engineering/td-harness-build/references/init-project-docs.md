# 项目文档生成与升级

初始化、升级或首次补齐项目文档时读取。检查工具与 Hook 接入见 [setup-checks.md](setup-checks.md)。

## 1. 生成边界

按 [upgrade-project.md](upgrade-project.md) 确认内容归属、融合和迁移授权，从 **assets/project/** 复制固定骨架；已有内容按升级规则保留。专题派发按 [init-agents.md](init-agents.md)。

生成后的日常维护方法由项目本地 **04 Docs** 模板及专题文档提供。生成时同样遵循 [04-docs.md §1、§3](../assets/workflows/development/04-docs.md) 的证据、唯一来源、权限、核对日期和索引规则；专题规则按 §2 定位对应资产，不在生成指导中另设一份。

项目首次引入 API 或数据库时，缺少的规范骨架在获准的初始化或升级中补齐；日常 Docs 阶段按已有文件维护，不承担新建专题文件。

空项目先说明定位和已确认的计划，只填有证据的内容，其余保留骨架与缺口。生成骨架不代表项目事实已确认，接入完成按 [SKILL.md](../SKILL.md#完成与反馈) 判断。

## 2. 专题入口

生成专题、负责产物及启动条件统一见 [init-agents.md §3「专题与依赖」](init-agents.md#3-专题与依赖)。只选择本次适用的专题；各专题指导链接对应的规则与资产模板。

## 3. 产品资料与交付

初始化默认建立 **.harness/product/01-prd.md、02-backlog.md、03-discussion-pool.md**；依据已确认资料填写，已有文件按升级规则融合。产品与外部资料的职责和流转按 [clarify.md §2](../assets/project/docs/clarify.md#2-资料维护)，本次产品交付使用 Discussion、Delivery Requirements 和 AC 模板。

每个 Harness 保留术语表；无条目时按术语资产说明现状。理解产品时按问题读取 README、相关实现和测试。

专题返回负责文件、依据、实际核验范围与缺口，主 Agent 汇总事实和索引。独立交付审阅按 **upgrade-project.md**，不为每个专题额外增加审批。生成指导与源 Skill 更新不会自动修改已有项目；应用差异仍按升级授权执行，不新增强制版本台账。

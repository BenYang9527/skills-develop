# 单元测试规范生成指导

> **使用边界**：仅供初始化／升级。先读 [派发约定](init-agents.md#2-派发约定) 与 [共同生成方法](init-project-docs.md)，按主 Agent 指定的输入、文件范围和授权处理。

> 填写 **.harness/docs/testing/unit-tests.md** 时读取；项目测试规则和三段骨架见 [unit-tests.md](../assets/project/docs/testing/unit-tests.md)。

## 1. 核对项目事实

读取依赖与锁文件、已有测试、项目脚本和 CI 配置，确认语言、运行环境、测试框架、替身方式及实际命令。只读取对应语言参考：

| 项目语言 | 读取 |
|---|---|
| Go | [go.md](language-profiles/go.md) |
| JavaScript / TypeScript | [javascript-typescript.md](language-profiles/javascript-typescript.md) |
| Python | [python.md](language-profiles/python.md) |

已有工具沿用；其他语言或未确定的选型报告缺口，不强套 Go。项目无代码时保留通用骨架，尚未接入的入口明确标记。

## 2. 填写项目规范

- **环境与工具**：填写实际版本、锁定位置、安装及生成入口。安装示例按 Windows、macOS、Linux 和实际 Shell 调整；核对适用性后执行，不直接照抄不兼容命令。
- **测试编写**：填写隔离方式、命名与目录；保留 TDD、有效断言、测试独立性及授权边界。语言专属约定从对应参考填入，不带入其他语言工具。
- **运行与排错**：填写完整命令、工作目录、范围参数及必要前置条件。只补实际需要的检查；覆盖率门槛来自验证规则或项目明确约定，不从任意 lint 配置猜测。

Go 接口替身的 **mockgen + gomock** 规则见 **go.md**，接入 Go 项目时写入测试规范。生成与核验按测试模板的生成入口规则。初始化／升级时，已有项目方案冲突按 **[upgrade-project.md](upgrade-project.md)** 确认迁移。

接入操作按 [setup-checks.md](setup-checks.md) 执行，文档填写本身不授予接入权限；汇报实际结果、平台差异及未完成项。

## 3. 保留旧内容并核验

已有测试文档或项目专属测试规则先完整读取。按工具、编写规则、执行入口归入新骨架；权威规范保留一份，其余只引用。独有内容融合、引用修复且删除获准后，才移除旧入口；未完成就报告待迁移。

验证已填命令和链接，不能把文件复制成功当作测试接入完成；证据归属与日期按 [05 Docs](../assets/workflows/development/05-docs.md)。

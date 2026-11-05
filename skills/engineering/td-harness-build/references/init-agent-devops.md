# 环境与发布文档生成指导

> **使用边界**：仅供初始化／升级。先读 [派发约定](init-agents.md#2-派发约定) 与 [共同生成方法](init-project-docs.md)，按主 Agent 指定的输入、文件范围和授权处理。

## 1. 调查

读取 README、依赖与锁文件、构建脚本、配置和 CI/CD。仅在项目实际使用时读取容器、集群及环境工具配置，不预设语言、操作系统或部署平台。

## 2. 填写与验证

按 [local-dev.md](../assets/project/docs/devops/local-dev.md) 填本地安装、配置、启动、调试与交付入口；按 [release.md](../assets/project/docs/devops/release.md) 填发布与恢复。格式、缺口、命令来源及发布授权规则由模板维护；不为填文档搭建环境。

命令执行与记录按 [04 Docs](../assets/workflows/development/04-docs.md) 的权限与核验方法。日志引用 logging.md，测试引用测试规范。

## 3. 升级保留

完整读取已有环境文档，旧模板边界上方也可能包含真实命令。按升级授权融合，不按边界机械覆盖；脚本只补缺，已有文件保持原样。

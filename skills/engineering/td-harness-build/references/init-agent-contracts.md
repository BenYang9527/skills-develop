# 接口契约生成指导

> **使用边界**：仅供初始化／升级。先读 [派发约定](init-agents.md#2-派发约定) 与 [共同生成方法](init-project-docs.md)，按主 Agent 指定的输入、文件范围和授权处理。

## 1. 探测真实契约

先核对 proto / IDL 生成配置、服务注册、生成来源，或实际路由与接口定义；排除 vendor、第三方依赖和示例。仅发现 proto 文件不能证明它是项目契约。无对外接口时跳过生成，保留已有人工文档和历史。

## 2. 填写与核对

说明核对与索引字段按 [index.md](../assets/project/docs/contracts/index.md)，演进记录按 [change-history.md](../assets/project/docs/contracts/change-history.md)，协议与路径约定按 [api-standards.md](../assets/project/docs/contracts/api-standards.md)。清单与项目特定约定写入各自项目区。

契约注释缺口报告位置与依据，由主 Agent 按授权安排修正，不要求一次补齐历史注释。旧字段表模板不再生成；旧文档迁移按升级确认保留人工内容与可追溯历史。无明确边界的文件列为 **MERGE**，获准后融合。

# 上下游与集成关系生成指导

> **使用边界**：仅供初始化／升级。先读 [派发约定](init-agents.md#2-派发约定) 与 [共同生成方法](init-project-docs.md)，按主 Agent 指定的输入、文件范围和授权处理。

## 1. 调查与填写

读取公开入口、实际调用、依赖与锁文件、协议和配置。依赖声明不能单独证明实际调用；按调用与数据方向识别服务、库、CLI、插件宿主、SDK 和消息交互，不强套 HTTP 服务结构。

按 [dependencies.md](../assets/project/docs/dependencies.md) 四节填写上游、下游、契约和故障影响；模板维护专题规则。核对清单、协议、故障记录与真实代码一致，图与 Architecture 相符。

## 2. 旧入口迁移

已有 **.harness/docs/dependency-map.md、.harness/dependency-map.md、harness/dependency-map.md** 时完整读取，保留清单、图、故障分析及独有信息。按升级授权融合、修复引用后才删除旧入口；未获授权或尚未完成则报告待迁移。

# AutoSaddler 复现框架回顾

想起这项工作：围绕“失败轨迹能否指导 harness 改进”，搭过本地复现控制层，重点把候选生成、验证、选择、恢复与最终测试做成可审计流程。

整理日期：2026-09-30。以下是本地历史工作的回顾与后续建议；本轮归档未重跑实验。

## 当时做了什么

官方 AutoSaddler 和 Meta-ARE 作为固定依赖保留；本地实现位于 `src/autosaddler_repro/`。它包含 mini-batch 前后评估、严格改善门槛、Dev 评估、Reflection、EvoDAG、候选选择、预算、事件链、恢复和冻结后 Test。

本地 README 将最高证据等级记为 R0：用 deterministic fake 运行完整 toy 闭环。另做过真实执行入口与预算控制的加固，但当前源码仍把 live 执行标为未就绪。

## 可以复用的方法

先把论文主张拆成可观察的不变量：候选从哪个父版本生成；训练/验证/测试分别何时可见；失败是否改变当前版本；恢复会不会重复花费或破坏日志；最终测量是否绑定冻结候选。

用确定性替身验证这些规则，再用真实模型检验性能。二者需要不同验收：前者检查系统行为，后者才检查方法是否有效。对失败候选也保留理由，避免只剩获胜轨迹而无法解释选择偏差。

## 结论停在哪里

没有可据此声称的论文性能复现结果。当前 R0 的完备性不能替代真实模型、benchmark 和资源隔离验证；历史 live 尝试也不能覆盖当前入口的阻断状态。

继续真实运行前，应按现有 runbook 处理外部隔离、watchdog、信任锚和外部不可变证据等缺口，不通过修改就绪标志跳过它们。

## 下次从这里继续

1. 从 `docs/REPRODUCTION_RUNBOOK.md` 找到 R0 的当前命令与产物；先验证已有冻结协议能解析。
2. 只选一个不变量，例如“拒绝候选后 active 版本不变”，追踪实现和对应测试。
3. 在新的 toy run 中复查正常、拒绝和中断恢复三种情况，再决定是否有理由进入真实模型阶段。

**下一次完成标准：** 一条从输入、候选、门槛到 receipt 的可追踪记录，并明确它支持的结论只到 R0。

## 找回原始材料

本地根目录：`~/Desktop/AutoSaddler-Codex/`。

- 回忆入口：`README.md`、`AutoSaddler_Reproduction_Plan.md`。
- 继续入口：`docs/REPRODUCTION_RUNBOOK.md`、`reproduction/protocol/preregistration.md`。
- 本地代码：`src/autosaddler_repro/`；就绪状态在 `v1_gaia2_pilot.py`、`p2_v2_launcher.py`。
- 官方：[AutoSaddler](https://github.com/microsoft/AutoSaddler/tree/30e20ce004486c58e7ee97c66182a8d0d41ec90e)、[Meta-ARE](https://github.com/pshlego/Meta-ARE/tree/395d1dd512add1e3aeb5a6a092490768b51e3ce5)；[论文](https://arxiv.org/abs/2608.23041)。官方源码不能替代上述本地控制层。

来源文件的本地位置、内容指纹与关联原项目见 [来源索引](../sources.json)。路径以用户主目录 `~` 为起点，只是定位线索；本仓库不包含对应源码或完整原稿。

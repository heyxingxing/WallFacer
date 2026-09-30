# Harness 机制研究回顾

想起这项工作：围绕“Agent 怎样持续执行、保存状态、在中断后继续”，做过十张机制图，并分别读过 DeepSeek、Codex、pi 的固定源码，以及 Claude Code 的公开机制资料。

整理日期：2026-09-30。以下是本地历史工作的回顾与后续建议；本轮归档未重跑实验。

## 当时做了什么

- 图谱覆盖总循环、记忆、上下文、工具、技能、GUI、搜索、多 Agent、后训练，作为阅读导航。
- Codex 研究追踪上下文组装、工具执行、rollout 历史、SQLite 状态与 resume。
- pi 研究区分默认 `AgentSession → Agent → runAgentLoop` 与实验性 durable `AgentHarness`。
- DeepSeek 研究从插件与生命周期追踪长程运行；Claude Code 研究依据公开文档和 SDK，证据强度单独标注。
- llama.cpp Omni 另有底层源码导读，具体本地改动见 [Omni 修复卡](omni.md)。

## 可以复用的方法

读一个新 Harness 时固定问五件事：这一轮模型看到了什么；谁能决定和执行动作；状态保存在哪；中断后恢复哪部分；谁判断真正完成。

先追一条请求，再画模型、Harness、工具和外部系统的边界。把状态分为对话历史、执行状态、外部副作用三层，分别查“何时持久化”和“谁是事实源”。源码注释、实际代码、文档承诺和个人推断分别记录。

## 结论停在哪里

这些材料主要是静态源码研究和机制综合。图集做过的布局验收不证明 Agent 的实际效果；源码能保存会话，也不自动证明外部动作可以恰好执行一次。

pi 的默认 CLI 与实验性持久执行路径不能混写；Claude Code 的公开产品行为不能补成未公开的核心实现。这里记录的是原研究版本，不保证当前版本行为一致。

## 下次从这里继续

1. 先打开图谱首页，只选“上下文组装”或“恢复”一个问题。
2. 对照 Codex 与 pi 各一条代码路径，填写三行：对话恢复、执行恢复、外部副作用恢复；每行附实现入口。
3. 设计一个中断案例：外部写入已完成、工具结果尚未入日志。明确重试会不会重复写，以及怎样检查。

**下一次完成标准：** 一张状态流图和一个有代码出处的恢复案例。先记录待验证点，再决定是否做运行实验。

## 找回原始材料

本地根目录：`~/Desktop/Long-Horizon-Agent/`。

- 图谱：`diagrams/harness-atlas-20260910/index.html`，机制说明在各专题 `notes.md`。
- 深读：`deepseek-harness-long-horizon-research.md`、`codex-harness-source-research.md`、`pi-agent-loop-context-resume-research.md`、`claude-code-harness-mechanism-research.md`。
- 上游：[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness/tree/a66e4702047846cdaa10c66c9d3df3951f5ea70d)、[Codex](https://github.com/openai/codex/tree/728cb12fe5794b0c3a8e776fb4994b1650b973a8)、[pi](https://github.com/earendil-works/pi/tree/6aedd1066e540642165aa30fa7b4a1b863778aa7)、[Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)。

来源文件的本地位置、内容指纹与关联原项目见 [来源索引](../sources.json)。路径以用户主目录 `~` 为起点，只是定位线索；本仓库不包含对应源码或完整原稿。

# 评测与 RSI 学习回顾

想起这项工作：把 Terminal-Bench/Harbor、RSI-Exam、AI4AI-Bench 和 GUITestScape 拆开读过，重点弄清“谁在改进谁，以及最后由谁验收”。

整理日期：2026-09-30。以下是本地历史工作的回顾与后续建议；本轮归档未重跑实验。

## 当时做了什么

- Terminal-Bench/Harbor：区分任务指令、环境、Agent runtime、verifier 和结果记录，并写了源码阅读练习。
- RSI-Exam：用 2048 与 DiscoveryWorld 解释研发 Agent、被修改的程序、外层框架和评分器的四种角色。
- AI4AI-Bench：理解探索期提交方法补丁，正式阶段在固定起点重新执行方法；研发 Agent 与目标策略模型不同。
- GUITestScape：制作论文卡和代码审计，发现前作 GUITestBench 的可见代码不足以确认本论文完整 harness。

## 可以复用的方法

评测前先写“测量合同”：允许改什么、哪些数据可见、提交什么、如何重新执行、谁评分、时间和成本怎样计入。用同一张角色表比较不同 benchmark，避免仅比较分数。

研究 Agent 可能改程序、数据、harness、训练配方或模型权重。标清改进对象之后，再问“收益有没有反馈到下一代研发者”；任务侧模型变好，本身没有证明强递归自改进。

对于缺源码的论文，用“论文声明—可见代码—运行证据—未知配置”四列记录。作者团队相同或项目名字接近，都不能替代实现关联证据。

## 结论停在哪里

已完成的是协议与固定源码学习，未完整复跑上述 benchmark 或榜单。已读过评分源码的练习，应标作学习实验；不能把同一批任务重新称为未见测试集。

GUITestScape 审计当时未确认各被测 Agent 的完整提示、观测、动作解析和预算；其评测算法不能直接当作被测 Agent 的行动循环。

## 下次从这里继续

1. 从 Harbor 的 `examples/tasks/hello-world/` 阅读 task、oracle 和 verifier，先解释空解与正确解应如何区分。
2. 为 RSI-Exam 的 2048 写一页测量合同，标出开发种子和最终评测种子的边界。
3. 对照 AI4AI 的补丁跨阶段流程，回答哪些探索状态不能带入正式评测。

**下一次完成标准：** 一张四角色表、一份可执行评测合同草稿。需要运行时，再检查容器与依赖条件。

## 找回原始材料

本地根目录：`~/Desktop/ai_data_lab/`。

- `terminal-bench-study/notes/01-design-walkthrough.md`、`02-reading-and-exercises.md`；版本见 `terminal-bench-study/source-lock.json`。
- `learning-cards/rsi-exam/学习卡.md`、`learning-cards/ai4ai-bench/学习卡.md`。
- `interview-prep/guitestscape-paper-card.md`、`guitestscape-agent-harness-audit.md`。
- 原项目：[Harbor](https://github.com/harbor-framework/harbor)、[Terminal-Bench](https://github.com/harbor-framework/terminal-bench)、[RSI-Exam](https://github.com/aiming-lab/RSI-Exam)、[AI4AI-Bench](https://github.com/Einsia/AI4AI-Bench)。GUI 原文为 [GUITestScape](https://arxiv.org/abs/2605.29532)，前作代码为 [GUITestBench](https://github.com/ADaM-BJTU/GUITestBench)。

来源文件的本地位置、内容指纹与关联原项目见 [来源索引](../sources.json)。路径以用户主目录 `~` 为起点，只是定位线索；本仓库不包含对应源码或完整原稿。

# slime 两项修复回顾

想起这项工作：在异步 rollout 与训练数据传输的边界找过问题。一个是后台 worker 失败后训练侧得不到失败信号；另一个是每样本 metadata 在组装与 DP 传输时丢失。

整理日期：2026-09-30。以下是本地历史工作的回顾与后续建议；本轮归档未重跑实验。

## 当时做了什么

| 修复 | 改动与回归入口 | 本地提交 |
|---|---|---|
| 异步错误传播 | 保存首个异常，在读取结果和获取 worker 时主动抛出；失败后取消在途任务；`tests/test_fully_async_rollout.py` | `c3ae6690556f2216332fccfa5cf27f1217ec72e9` |
| metadata 保留 | 从“只看第一个样本”改为检查任意样本是否有 metadata，并在 DP 切分/传输字段中保留它；`tests/test_process_rollout_data.py` | `b882e5367f33f3f713af48faef532d17353385b5` |

两个提交都基于 `5bae5bb7928d65906e24e99f5b5d3f99a4daaf93`，属于两条独立分支。

## 可以复用的方法

审异步代码时同时追踪数据流和错误流：谁生产结果、谁消费、异常在哪里保存、等待何时结束。线程死亡后简单重启可能掩盖已消耗的任务，必须核对丢失与重放语义。

审分布式训练输入时，把字段从 Sample 一直追到打包、切分、传输和 trainer。专门构造第一条为空、后续条目非空的异构样本，避免“首项代表全体”的隐含假设。

## 结论停在哪里

本轮核对了提交差异和回归测试文件，未重新运行测试或训练。存在测试不等于整条真实 GPU 训练链路已验证，也没有吞吐或模型效果结论。

本地 refs 记录这两条分支曾在个人 fork 上；上一轮在线读取分支页失败，当前远端是否仍存在、是否被上游合并，应在继续前重新查询。

## 下次从这里继续

1. 先 `git show <提交>` 回忆差异，再核对上游当前实现是否已修复同一问题。
2. 从新增测试选一个反例，先说明修复前为什么失败，再在兼容环境验证修复后行为。
3. 若继续贡献上游，独立提交问题描述、最小复现与回归证据，避免混入两项无关改动。

**下一次完成标准：** 一份“触发条件 → 原因 → 修复 → 测试范围”说明，以及上游是否仍需要该修复的判断。

## 找回原始材料

本地：`~/Desktop/RL-训推框架/slime-audit/`、`~/Desktop/RL-训推框架/slime-audit-metadata/`。

- 上游：[THUDM/slime](https://github.com/THUDM/slime)。
- 个人 fork：[heyxingxing/slime](https://github.com/heyxingxing/slime)；本地跟踪分支名分别为 `fix/fully-async-worker-errors`、`fix/preserve-rollout-train-metadata`。
- 代码路径：`slime/rollout/fully_async_rollout.py`、`slime/ray/rollout.py`。
- 完整提交、父提交和文件列表见 [代码改动索引](../code-changes.json)。原始 coding_agent_rl / fully_async 示例来自上游，只需通过项目地址阅读。

来源文件的本地位置、内容指纹与关联原项目见 [来源索引](../sources.json)。路径以用户主目录 `~` 为起点，只是定位线索；本仓库不包含对应源码或完整原稿。

# WikiSkill 最小状态机回顾

想起这项工作：把原始经验、累积 Wiki 和可执行 Skill 分开，基于论文思想写了无网络、无模型调用的 cleanroom，用来验证技能更新的基本规则。

整理日期：2026-09-30。以下是本地历史工作的回顾与后续建议；本轮归档未重跑实验。

## 当时做了什么

本地 cleanroom 使用确定性 2 train / 2 val / 2 test 任务。Raw trace 写一次并带哈希；proposal 仅允许 create、patch 或 no_action；候选在独立快照上应用。

只有 `R_val > R_best` 才提升候选；拒绝时 active skill hash 不变；freeze 之后才允许 test。输出事件记录、环境与数据标识、指标和 receipt。社区参考实现另放在 vendor，与本地引擎分开。

## 可以复用的方法

把“积累经验”和“改写技能”分成两层。失败 proposal 可以成为知识，但不必污染当前可执行版本。候选是否应用、验证是否改善、最终测试是否成功，是三个独立状态。

先列出不变量，再构造最小接受/拒绝案例。不要因为任务里出现了训练/验证/测试三个名字，就默认数据隔离或测量有效；要看读取边界与时间顺序。

## 结论停在哪里

这是本地干净室状态机，不是论文官方实现。已有确定性烟测记录不证明真实模型能力或论文 benchmark 分数，也不构成真实 Agent 的操作系统级隔离。

## 下次从这里继续

1. 读 `engine.py`，找出候选创建、验证、提升和 freeze 的状态转换。
2. 构造一个明确较差的候选，核对拒绝后 active hash 不变、Wiki 保留原因。
3. 再检查未冻结时 test 被拒绝、冻结后只能评估确定的版本。

**下一次完成标准：** 接受和拒绝两个场景各一条可检查事件链；随后再单独设计真实 runner 接口。

## 找回原始材料

[已归档的中文译稿 PDF](../../../documents/papers/zh/2608.27454/main.pdf)。

本地根目录：`~/Desktop/rl-paper/2608.27454-src/deployment/`。

- `README.md`、`cleanroom/README.md`。
- `cleanroom/wikiskill_cleanroom/engine.py`、`cleanroom/run_smoke.py`、`cleanroom/tests/test_cleanroom.py`。
- 原文：[WikiSkill](https://arxiv.org/abs/2608.27454)；[社区参考代码](https://github.com/ashutoshsinghpr7/wikiskill/tree/02fac2c804fe156e43b12c691e4ae527614d63a1)。本地 cleanroom 不在该社区仓库中。

来源文件的本地位置、内容指纹与关联原项目见 [来源索引](../sources.json)。路径以用户主目录 `~` 为起点，只是定位线索；本仓库仅额外归档上述中文 PDF，源码与其他原始材料仍留在本地。

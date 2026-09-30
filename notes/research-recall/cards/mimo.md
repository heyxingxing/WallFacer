# MiMo 训练实践准备回顾

想起这项工作：选定 MiMo-V2.6-Distill-Qwen-9B，读报告制定实践路线，拉取官方训练组件，并编写只做检查和预览的本地启动包装器。

整理日期：2026-09-30。以下是本地历史工作的回顾与后续建议；本轮归档未重跑实验。

## 当时做了什么

核对了模型身份、配置与 revision，整理了轨迹、SFT、rollout、奖励、GRPO、评估之间的概念链。随后固定 verl、uni-agent、mimoagent 三个组件，建立 CPU 配置组合、启动预览和测试。

`workspace.py` 检查 GRPO 组大小、上下文长度、batch 整除关系；实际执行还要求显式填写硬件、模型、数据和集群条件。这样能避免无意继承上游大规模训练默认值。

## 可以复用的方法

把论文复现分成资料核实、接口验证、推理基线、训练闭环、受控比较几个阶段，每个阶段有独立产出。源码能组合配置，只说明配置路径可解析；推理能运行、训练能更新、方法有效需要分别验收。

先冻结模型与数据，再冻结 harness、解码、预算和指标。固定权重换 harness，与多 harness 训练，是两种实验。不要把参数量或权重体积当成完整训练显存需求。

## 结论停在哪里

按本地计划与 training README 的历史状态，尚未执行 GPU 训练，也没有本地模型收益结论。公开的 9B 学习对象是 SFT checkpoint；不能直接把报告中继续 RL 的结果归到它身上。

`training/vendor/verl` 与另一个 `projects/mimo-verl-study/verl` 学习副本使用不同提交，继续工作时先确认用哪个。硬件、训练数据、镜像和真实运行兼容性仍需检查。

## 下次从这里继续

1. 重读实践计划中第 7 章对应表，明确本次只检验一种能力，例如工具格式适配。
2. 查看 `workspace.py` 和已有测试，先复核配置与 preview；记录它将调用哪个官方入口，不直接启动训练。
3. 算力和依赖确定后，先做短上下文推理基线，再决定小规模 SFT 或 RL 对照。

**下一次完成标准：** 一页冻结协议，列明模型 revision、数据划分、harness、预算、指标和仍缺的资源。

## 找回原始材料

本地根目录：`~/Desktop/mulit-agent/MiMo-V2.6/`。

- `notes/9B_PRACTICE_PLAN.md`、`training/README.md`。
- `training/scripts/workspace.py`、`training/tests/test_workspace.py`、`training/sources.lock.json`。
- 模型：[MiMo-V2.6-Distill-Qwen-9B](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Distill-Qwen-9B)，计划固定 revision `2367e865d009c13ac81713a2878291d33ab28177`。
- 训练上游：[verl](https://github.com/XiaomiMiMo/verl/tree/e2b9fc03c6e01247f5d93c44201b068ea320b7de)、[uni-agent](https://github.com/XiaomiMiMo/uni-agent/tree/c63e0b01c375ebede95e01fe92bc367df24e5bf3)、[mimoagent](https://github.com/XiaomiMiMo/mimoagent/tree/467f0a19016f0ac4d63b8d17a1f0da9ba07f232c)。

来源文件的本地位置、内容指纹与关联原项目见 [来源索引](../sources.json)。路径以用户主目录 `~` 为起点，只是定位线索；本仓库不包含对应源码或完整原稿。

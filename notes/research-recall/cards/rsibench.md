# RSIBench 数据训练与评测回顾

想起这项工作：实际走过数据生成、LoRA SFT、checkpoint 评测的链路，修过消息格式、代理与预算处理，并把没有提升的结果写成了深度指南。

整理日期：2026-09-30。以下是本地历史工作的回顾与后续建议；本轮归档未重跑实验。

## 当时做了什么

以 RSIBench-Data 的固定源码为基础，做过本地消息模板统一、工具调用与停止处理、上下文限制、未知费用处理等修改，增加了相关测试和小样本评测资料。

历史指南记录：base 与 adapter 各评两题，均为 0/2，四个 trial 都有实际判分。adapter 侧出现 `RepeatedFormatError` 和上下文超限；调用更少、成本更低伴随提前失败。这是可分析的负结果。

## 可以复用的方法

排查顺序应让每一步回答一个问题：环境与 verifier 能否可靠判分 → 消息和工具协议是否一致 → 数据、loss mask、模板是否正确 → 训练更新是否按预期发生 → 未见任务表现是否变化。

训练文本、推理模板、工具解析器、停止符共同定义行为协议；只比较训练 loss 很容易漏掉协议失配。成本缺失要标成未知，不能默认为零。保留每个失败的结束类型、独立判分与调用记录，才能解释表面上相同的总分。

## 结论停在哪里

本轮历史实验执行的是 LoRA SFT。评测有 reward，不会自动把训练变成 PPO 或 GRPO。

没有观察到任务解决率提升，也没有通过单因素实验定位唯一退化原因。恢复评测使用本地 `run_pair.py`，没有因此重新验收原 runner 的完整 `final_submit` 流程。不能据此声称多轮自主改进或强 RSI 已成立。

## 下次从这里继续

1. 从指南第 8、13、15 节回忆格式链路、负结果和源码入口；先找回一条完整失败轨迹。
2. 选一个不依赖模型调用的小例子，逐步核对训练消息、tokenization、推理输入、模型输出与工具解析，要求前后协议一致。
3. 如果继续模型实验，冻结新的基线与留出任务，仅改变一个因素；记录格式错误率、任务成功率和成本，并保留失败分母。

**下一次完成标准：** 一个定位到具体阶段的反例和一项独立对照设计。若协议仍不一致，先修协议，不扩大训练。

## 找回原始材料

本地根目录：`~/Desktop/ai_data_lab/RSIBench-Data/`。

- 指南：`docs/RSIBench-Data_深度学习指南.md`；实验说明：`docs/light_experiment.md`。
- 关键代码：`backend/message_format.py`、`backend/e2b_eval/tool_proxy.py`、`backend/tinker/train_lora_sft.py`、`runner/lib/update_budget_state.py`。
- 回归入口：`tests/test_message_format.py`、`tests/test_sampling_budget.py`；历史完整证据需从指南链接进入本地 artifacts。
- [上游基线](https://github.com/evolvent-ai/RSIBench-Data/tree/4c807610243e7b481d382c5ed360c71c79a22f61)。本地修改尚未在此知识库中备份为 patch；不要仅靠重新 clone 恢复它们。

来源文件的本地位置、内容指纹与关联原项目见 [来源索引](../sources.json)。路径以用户主目录 `~` 为起点，只是定位线索；本仓库不包含对应源码或完整原稿。

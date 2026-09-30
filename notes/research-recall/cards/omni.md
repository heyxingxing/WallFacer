# llama.cpp Omni 五项改动回顾

想起这项工作：沿多模态推理的流式响应、控制决策、音频队列与播放分析做过五项独立改动，并留下源码导读。重点是把“生成了内容”和“正确交付了内容”分开。

整理日期：2026-09-30。以下是本地历史工作的回顾与后续建议；本轮归档未重跑实验。

## 当时做了什么

五项改动均从 `64d092c60db4b4ee45768476bd752f03fdcc98ea` 分出，不能把它们当作已按顺序合并的同一条分支。

| 提交 | 当时处理的问题 | 证据入口 |
|---|---|---|
| `6e2f7d7` | SSE 回调按值保留请求字段，检查最后写入并结束 chunked 响应 | `tools/server/server-omni.cpp`；此提交未附新增测试 |
| `104d9cf` | 暴露 raw logits、控制调整后 logits、sampled 三阶段观测 | `CONTROL_OBSERVABILITY.md` 与 `test_decode_observer.py` |
| `ef5bc2d` | 检查双工覆盖，并用生成时间线估计播放连续性 | `DUPLEX_PROFILING.md`、`analyze_perf.py`、`test_analyze_perf.py` |
| `4a1a8fe` | 保留 Token2Wav 队列的 turn-final 边界 | `tools/omni/test/test_t2w_queue.py` |
| `639c5a6` | WebSocket 收到完成标志时，先发送已取出的最后一个片段 | `tools/server/tests/test_ws_queue.py` |

## 可以复用的方法

流式系统要分别检查生产、入队、出队、传输与播放。完成标志和队列是否为空，需要和“当前已取出但尚未发送的数据”一起推理，否则容易漏掉最后一块。

观测机制必须先定义语义：模型原始 logits、控制规则调整后 logits、采样 token、传输成功和可听见音频，是不同事实。研究量化或控制误差时，先固定输入和 prefix；两条自由生成轨迹分叉后，同一步编号并不代表同一状态。

## 结论停在哪里

控制 observer 没有覆盖所有强制动作、TTS 采样或完整推理历史；它也没有实现量化方法或证明真实模型收益。控制契约测试使用确定性后端替身，不等于真实 GGUF 推理。

播放连续性指标是生成侧估计，不等于客户端实际听感。当前仅核对本地改动与文档，未新做编译、性能或音频实测；SSE 那项还需补针对性回归证据。

## 下次从这里继续

1. 每次只选一条分支，核对父提交和对应补丁，先查上游是否已发生相关变化。
2. 队列问题先构造“最后一块与 done 同时到达”的最小案例；观测问题先验证阶段顺序、数据生命周期和 observer 开关等价性。
3. 做真实模型对比前，固定模型、输入、prefix、控制参数与采样器；再补传输或客户端播放证据。

**下一次完成标准：** 一条边界错误的最小复现和对应验收条件。性能与模型质量收益另立实验，不从代码修复直接推断。

## 找回原始材料

本地根目录：`~/Desktop/RL-训推框架/`。

- 导读：`llama.cpp-omni-源码导读.md`。
- 五个目录：`llama.cpp-omni/`、`llama.cpp-omni-control/`、`llama.cpp-omni-playback/`、`llama.cpp-omni-turns/`、`llama.cpp-omni-ws/`。
- [上游项目](https://github.com/tc-mb/llama.cpp-omni)。本地远端 refs 未包含这五个 HEAD；未据此断言服务器上绝对不存在它们。
- 完整提交与文件位置见 [代码改动索引](../code-changes.json)。本仓库保存回顾和索引，未备份补丁正文。

来源文件的本地位置、内容指纹与关联原项目见 [来源索引](../sources.json)。路径以用户主目录 `~` 为起点，只是定位线索；本仓库不包含对应源码或完整原稿。

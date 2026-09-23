> ⚠️ **注意（仅供阅读）**：此内容为简化版 Markdown，仅供阅读和总结，
> **不可直接用于 createDocument --content 或 updateDocumentByXml**。
> 如需编辑文档，请使用 `getDocumentXml` 获取完整格式后再通过 `updateDocumentByXml` 回传。
> 直接用此内容编辑会丢失样式宏、合并表格、NodeID 等关键信息，导致文档数据损坏。

---

# DeepSeek Harness 实践分享

### 一、背景

DeepSeek Harness（以下简称 DSH）是一套开源、可组合的 Agent Runtime。它以“Everything is a Plugin”为核心设计，将模型适配、Agent Loop、工具、Session、持久化、上下文管理和 Subagent 等能力都交给插件提供和组合。通过将 Runtime 的主要能力开放为插件，DSH 支持开发者根据场景自由选择、组合和替换各项运行能力。

如果希望进一步了解 DSH，推荐阅读[《DeepSeek Harness：Everything is a plugin》](https://km.sankuai.com/collabpage/2781228283)、[《DeepSeek Harness 指南》](https://km.sankuai.com/collabpage/2780747319)和[《DeepSeek Harness 四种运行模式深度解读：插件组合如何重塑 Agent 的能力边界》](https://km.sankuai.com/collabpage/2782067563)，本文不再赘述。

本文按照“插件架构—核心机制—能力实践—平台接入”的顺序展开。第二章介绍 DSH 的插件装配方式，以及 Agent Harness 的扩展与替换机制；第三章重点说明 Agent Loop 与 Session 日志的工作原理；第四章集中介绍 Step 断点重跑、WeKnora 知识库接入、模型请求控制和 Claude Code Subagent 四项能力实践；第五章说明如何将本地 DSH 接入 Multica 作为 Agent Runtime；第六章总结 DSH 的实践价值与现阶段局限。

### 二、Everything is a Plugin：DSH 的插件化架构

#### 2.1 架构概述

DSH 不是在一个固定 Agent 产品之外增加插件系统，而是直接用插件组成 Agent Harness。底层只保留负责装配、依赖和生命周期管理的 Cordis；模型适配、Agent Loop、Tool、Session、执行环境、Host 和客户端等主要运行能力都由插件提供。开发者面对的不是一套只能外围扩展的应用，而是一个可以通过配置重新组合的 Runtime 插件树。

从架构上看，DSH 可以分为三层：

| 层级 | 主要职责 | 稳定性与变化方式 |
| --- | --- | --- |
| Cordis 内核 | 加载插件、解析依赖、划分作用域并管理插件生命周期 | 保持精简稳定，不承载具体 Agent 业务能力 |
| Harness 能力插件 | 提供模型、Agent Loop、Tool、Session、Sandbox、Subagent、权限和 UI 等运行能力 | 可以增加新实现，也可以替换已有实现 |
| 配置组合层 | 使用 Bundle、Profile、Patch 和 Agent Preset 选择插件及其配置 | 不修改内核代码即可形成不同 Agent 与产品形态 |

> **📂 折叠块（默认折叠）：Bundle、Profile、Patch 和 Preset概念**
>
> | 概念 | 一句话理解 | 实际作用 | 生效范围 | 示例 |
> | --- | --- | --- | --- | --- |
> | Bundle | 一组可以安装和复用的“能力安装包” | 把一批相关插件及其默认配置放在一起交付。安装一个 Bundle，就能向 DSH 增加一组完整能力，不需要逐个配置其中的插件 | 整个 DSH 进程 | `dsh-base` 提供模型、Tool、Session 等基础能力；`dsh-web-app` 增加 Web 界面与服务 |
> | Profile | DSH 启动时选择的“运行方案” | 决定本次启动要加载哪些 Bundle，以及使用哪些用户配置。不同 Profile 可以将同一套 DSH 启动成不同产品形态 | 整个 DSH 进程 | `web` Profile 加载 `base + web-app`，`headless` Profile 加载 `base + headless`；通过 `dsh --profile <name>` 选择 |
> | Patch | 在现有运行方案上追加的“配置修改单” | 不重新制作 Bundle 或 Profile，直接覆盖某个插件的配置，或者插入新的插件配置。多个 Patch 按顺序应用，越靠后的修改优先级越高 | 整个 DSH 进程的配置 | 更换模型 Provider、启用额外 Tool、修改权限策略，或通过 `--patch` 临时加入实验配置 |
> | Preset | 创建单个 Agent 时选择的“能力模板” | 只为当前 Agent 选择 Prompt、Persona、Tool 和其他 Agent 级插件，不改变同一进程中已经运行的其他 Agent | 单个 Agent／Session | 同一个 Web Runtime 中可以同时创建“完整编码 Agent”和“极简 Agent”，二者共享存储与沙箱，但拥有不同的 Prompt 和 Tool |

![图片](https://km.sankuai.com/api/file/cdn/2785506770/255175095576?isNewContent=false&contentType=1)

#### 2.2 Agent Harness 的扩展与替换机制

DSH 将 Agent Harness 的主要组成部分都开放为插件，包括模型请求组装、Agent Loop、Tool、Session、执行环境、权限策略、Host 和客户端。开发者可以通过插件增加新能力，也可以直接修改或替换这些组件的实现，从而控制模型如何接收上下文、任务如何循环、状态如何持久化、代码在哪里执行，以及 Agent 通过什么产品入口运行。相比 CatDesk、Claude Code 等以闭源产品形态提供的 Agent，DSH 开放了 Harness 本身的实现与装配方式；开发者除了接入 Tool、MCP 或 Hook，还可以按业务需要定制 Agent 的核心运行链路。

关于插件组合、可替换能力和主要扩展点的完整说明，参见 [DeepSeek Harness 架构](https://deepseek-harness.github.io/deepseek-harness/reference/)。

### 三、核心运行机制

#### 3.1 Agent Loop：模型与工具驱动的执行循环

Agent Loop 是 DSH 中驱动一次 Agent 执行的核心插件。`dsh-agent` 定义统一的 Agent 接口，默认的 `dsh-agent-loop` 插件实现这个接口，并依赖 Session、LLM、System Prompt 和 Tool 等服务完成实际运行。Web、Headless、ACP 和其他调用方只面向 Agent 接口创建、恢复和控制任务，不需要依赖默认循环的具体实现；如果默认行为不适合某类 Agent，也可以注册另一套实现替换它。

每次用户输入通常开启一个 Turn，Turn 从领取输入开始，到当前任务不再需要继续调用模型时结束；一个 Turn 包含零个或多个 Step，每个 Step 对应一次模型请求以及该次响应触发的 Tool 调用。模型直接给出最终回复时，Turn 通常只包含一个 Step；模型返回 Tool Call 时，Tool Result 会触发下一个 Step，直到模型给出最终回复或执行被取消。

![图片](https://km.sankuai.com/api/file/cdn/2785506770/255171972458?isNewContent=false&contentType=1)

从执行流程看，DSH 的 Agent Loop 与 ReAct（Reason + Act）类似：模型先根据上下文决定直接回复还是调用 Tool；如果调用 Tool，执行结果会加入上下文，模型在下一个 Step 中继续判断，直到给出最终回复。但DSH 不要求模型输出固定格式的 Thought、Action 和 Observation，而是接收各 Provider 的原生结构化响应，再由 LLM Adapter 统一转换为 `reasoning`、`text` 和 `tool-call` 等内容块。例如，DeepSeek API 返回的 `reasoning_content`、`content` 和 `tool_calls` 会分别转换为推理内容、回复文本和工具调用。

#### 3.2 Session：用事件日志保存和重建会话

DSH 使用事件溯源建模 Session。一个 Agent 的连续对话构成一个 Session，一份 Session 日志按照单调序号连续保存多个 Turn 产生的事件；日志只追加新记录，不会原地修改已经发生的事实。Session 因而既保存会话历史，也是恢复执行和派生模型上下文的状态来源。

当输入被接受、模型产生回复、Tool 返回结果，或者 Turn／Step 状态发生变化时，Agent Loop 会将对应事实追加到 Session 日志。持久化插件保存这些事件，界面从中生成展示状态，恢复逻辑则根据日志重建执行上下文。

DSH 运行日志说明：

![image.png](https://km.sankuai.com/api/file/cdn/2785506770/255171972460?isNewContent=false&contentType=1)

如果对模型输入如何从 Session 日志中产生感兴趣，可以阅读[Session 参考文档](https://deepseek-harness.github.io/deepseek-harness/reference/subsystems/session)。

DSH Session 日志与美团AI Agent可观测平台的对比结果：

| 维度 | DSH Session Log | 美团Agent 可观测平台 | 说明 |
| --- | --- | --- | --- |
| 定位 | Agent 的运行事实与恢复依据，可用于重放、恢复和继续执行。 | Agent 的运行观测数据，用于调用链、性能、Token 和错误分析。 | DSH 的日志是运行源数据；可观测平台的数据是分析视图。 |
| 会话 | 一份 Session Log 对应一个 DSH Session，持续记录同一对话窗口中的多轮交互。 | 一个 Session 对应一个对话窗口，包含多次用户交互。 | 两边的 Session 都是多轮交互的容器；会话可以仍在进行中。 |
| 交互 | 一次用户交互对应 Session 中的一段执行记录，通常是一轮 `turn/start → … → turn/end`。 | 一次用户交互对应 Session 中的一条 Trace / Round，即用户发起 Query 到 Agent 完成响应。 | DSH 的一段 turn 记录大致对应平台的一条 Trace。 |
| 保留内容 | 用户输入、Agent 输出、LLM 调用、工具调用、工具结果、Token 用量、子 Agent、执行状态与错误等；此外还保留模型请求配置、流式输出、重试、压缩和恢复所需事件。 | 用户输入、Agent 输出、LLM 调用、工具调用、工具结果、Token 用量、子 Agent、执行状态与错误等；此外保留 Span 父子关系、耗时、资源信息和业务属性。 | 两者都覆盖核心执行内容；DSH 偏恢复语义，平台偏链路与性能语义。 |
| 存储与使用 | 可下载/导出；以结构化 JSON 事件记录持久化（逻辑上为 JSONL，可压缩），可据此恢复对话。 | 可查看、筛选、聚合、导出 CSV/Excel 或通过 OpenAPI 获取数据，用于分析和告警。 | 即使都能导出，DSH 日志可作为恢复依据；平台 Trace 不承担恢复对话的职责。 |

### 四、DeepSeek Harness 功能实践

前三章说明了 DSH 能够修改什么，以及 Agent Loop 和 Session 如何工作。本章将这些扩展点落到四项具体实践中，分别介绍 Session 历史复用、统一知识检索、模型请求控制和 Subagent Provider 替换。

#### 4.1 基于 Session 日志实现 Step 断点重跑

##### **背景**

采集执行 Agent 采用端到端回放评测。当前评测集包含 9 个 Task，每个 Task 的正式测评默认执行 3 次 Trial，因此一次全量评测需要完成 27 次完整需求任务。每次 Trial 还要依次完成 Agent 执行、历史输入回放、评分和环境清理；如果每次修改 Skill 后都从头开始测试，时间和模型调用成本较高。

许多修改只影响流程中的某个阶段。例如只修改阶段三的 Skill 时，只要阶段一和阶段二的输入与产物仍然有效，就不需要重新生成前两阶段结果。基于 DSH 的 Session 日志，可以复用阶段三之前的消息、模型回复和 Tool Result，从阶段三首次使用该 Skill 的 Step 创建新 Session 并继续执行，从而减少 27 次 Trial 中重复运行前置流程的成本。

![image.png](https://km.sankuai.com/api/file/cdn/2785506770/255179292486?isNewContent=false&contentType=1)

##### **插件实现**

基于 DSH 的 Session 事件日志和 Session 派生能力，可以实现了 Step 重跑插件。插件读取来源 Session 的完整日志，定位一个已经结束的 Step，截取其 `step/start` 之前的事件，并补写 `turn/end(reason = interrupted)`，将事件前缀转换成完整、可恢复的历史。随后插件使用该前缀创建新的 Session，并通过当前 Preset 重新组装模型、System Prompt、Tool、Skill 和其他插件。

来源 Session 和原始日志保持不变，新 Session 使用独立的 Session ID。它不是对原请求的确定性回放，而是让相同的持久化历史前缀在当前运行环境中重新执行。

插件由 Host 和 Web 两部分组成：Host 负责读取日志、校验 Step 和创建新 Session，Web 插件负责展示重演视图并提供播放按钮。Web 包会同时安装和挂载两部分：

```Shell
// 安装命令
npx @deepseek-ai/dsh plugin --profile web add \
  @liuyangdong/dsh-client-ui-session-rerun@0.1.1-rc.6 \
  --registry=https://registry.npmjs.org/
npx @deepseek-ai/dsh web
```

##### **操作演示**

进入已有 Session 的“重演”视图，展开 Turn，选择一个已完成的 Step，然后点击右侧的播放按钮。插件会保留该 Step 之前的历史记录，并以这段事件前缀派生新的 Session，从所选 Step 继续执行；原 Session 不会被修改。

采集执行流程由主 Agent 负责任务编排和分发，需求分析、函数配置、流程配置与测试验证则由对应的子 Agent 执行。下面以修改函数配置 Agent 中的 `verify_groovy_rule.py` 脚本为例：借助 DSH 的 Session 日志回放能力，可以从任务首次调用该脚本的 Step 直接重跑，并使用修改后的脚本继续执行，无需从头运行整个需求，从而减少等待时间和 Token 消耗。

> 🎬 **视频附件**：[录屏2026-09-01 17.33.38.mov](https://km.sankuai.com/api/file/cdn/2785506770/255179767374?isNewContent=false&contentType=1)

**预期收益**

根据近一个月的14个 commit 的具体修改内容估算，如果采用 Session 断点重跑的方案预计可使全量测评的执行耗时减少约 **19%**。需要说明的是，断点重跑虽然能够降低全量测评成本，但结合 5.3 节的测试结果和 6.2 节的风险分析，DSH 当前尚未达到生产级稳定性要求，暂不具备Agent运行时迁移的条件。

采集执行小队单需求平均耗时约40分31秒，其中解析LeaderAgent平均12分46秒、需求分析Agent平均9分28秒、函数配置Agent平均10分钟、流程配置Agent平均4分48秒、流程测试Agent平均3分29秒。按照各阶段的串行执行顺序，可以估算从不同节点断点重跑预期带来的收益：

![图片](https://km.sankuai.com/api/file/cdn/2785506770/255171051415?isNewContent=false&contentType=1)

#### 4.2 使用 WeKnora 插件接入知识库

##### **背景**

采集执行小队的每个 Agent 都绑定独立的 Skill，所需业务知识和配套脚本也分别维护在各自的 Skill 中。如图所示，不同 Skill 之间重复维护相同的业务知识，也各自保留功能相似的脚本，这样不仅维护成本高，而且对执行效率、可靠性与可维护性也会有一定影响。

![图片](https://km.sankuai.com/api/file/cdn/2785506770/255176371758?isNewContent=false&contentType=1)

##### **接入DSH**

WeKnora 支持 FAQ、文档和 Wiki 三种知识库形态。知识内容可以通过本地文件或文件夹、URL、在线录入构建，也可以从外部数据源同步；导入内容经过解析、分块和索引后，形成可按问题检索的知识单元。

| 能力 | 现状问题 | 应用价值 |
| --- | --- | --- |
| 集中管理知识，支持文件、URL 和外部数据源 | 同一业务知识分散或复制在多个 Skill、脚本和 Reference 中 | 多个 Agent 共享同一知识来源，规则只需统一更新，降低漏改和版本不一致的风险 |
| 文档解析、分块、索引和混合检索 | Agent 需要加载整篇文档，大量无关内容进入上下文 | 根据当前问题按需加载相关片段，减少重复读取和 Token 消耗 |
| `weknora_search` 返回检索范围、排序后的原文片段、文档与分块标识以及相关度 | 现有知识读取结果缺少统一结构，执行异常时难以定位原因 | 可以区分知识缺失、检索未命中和 Agent 理解偏差，使检索过程可复盘 |
| `weknora_read_document` 按命中文档继续读取正文，`weknora_ask` 为综合回答提供引用 | 单个命中片段可能缺少上下文，跨文档问题需要多轮查找 | Agent 可以按需补充上下文，或获得带引用的跨文档答案，无需预先加载全部资料 |
| 通过 DSH 插件将 Tool Call 和 Tool Result 写入 Session 日志 | 不同 Agent 使用了哪些知识、获得了哪些证据难以追踪 | 查询与证据随执行历史保存，便于复现结果和定位知识缺口 |

WeKnora 官方提供 [dsh-weknora插件](https://github.com/Tencent/WeKnora/blob/main/packages/dsh-weknora/README_CN.md)，用于将 WeKnora 的知识检索和问答能力接入 DSH。插件通过 WeKnora API 访问已有知识库，不负责知识导入，也不会修改知识库内容。

> **📂 折叠块（默认折叠）：插件向 DSH 注册的四个知识访问工具**
>
> | 工具 | 用途 | 返回给 Agent 的主要证据 |
> | --- | --- | --- |
> | `weknora_list_knowledge_bases` | 查看当前凭证可访问的知识库 | 知识库名称和 ID |
> | `weknora_search` | 对指定或全部知识库执行混合检索 | 原始片段、相关度、文档 ID 和分块位置 |
> | `weknora_read_document` | 在命中片段后继续读取完整文档 | 按顺序重组的分块、标题和摘要 |
> | `weknora_ask` | 将跨文档综合问题交给 WeKnora 回答 | WeKnora 的结论、引用和可续接 Session ID |

##### **演示**

1. 在 WeKnora 中准备知识库

首先在 WeKnora 中创建或选择“采集执行 Agent”知识库，将全量 UDF 文档上传到 `UDF/functions` 目录。WeKnora 会对文档执行解析、分块、向量化和索引构建；所有文档状态变为“已完成”后，文档即可被稳定检索。

![image.png](https://km.sankuai.com/api/file/cdn/2785506770/255168022795?isNewContent=false&contentType=1)

2. 在 DSH 中验证检索效果

完成知识库准备后，以查询某个UDF 的功能和输入参数为例，向 Agent 提问：

> `afterPromotionPriceRestoration` 这个 UDF 是做什么的？有哪些输入参数？

DSH 调用 `weknora_search` 按函数名检索知识库，并通过 `weknora_list_knowledge_bases` 确认检索范围。命中文档后，Agent 使用 `weknora_read_document` 读取完整内容，最终返回函数用途、调用形式、Java 签名、输入参数、返回类型和源码位置。整个过程先检索定位，再按命中文档补充上下文，不需要预先将全部 UDF 文档加载进模型上下文。

![图片](https://km.sankuai.com/api/file/cdn/2785506770/255170214626?isNewContent=false&contentType=1)

#### 4.3 使用插件扩展模型 API 请求参数

##### **问题与目标**

在此前使用 CatDesk、Claude Code 等通用 Agent 产品建设采集执行 Agent 时，我们主要通过 Skill 描述业务规则和任务步骤。虽然这些产品也支持 Tool、MCP、Hook、Subagent 及部分模型和上下文设置，但 Agent Loop、上下文压缩和 Memory 注入主要由Agent运行时定义。我们通常只能在应用层增加 Skill 和 Tool，无法调整这些底层机制，也难以验证它们如何共同影响最终执行结果。

DSH 将模型请求链路和 LLM Adapter 开放为插件扩展点。插件可以增加模型调用参数，按 Agent、任务或 Step 设置取值，并在 Adapter 中完成校验和请求序列化；实际生效的值还可以记录到 Session 日志，便于核对和复现模型请求。

##### **页面不开放的 API 参数**

DSH的UI菜单一般只提供 Provider、Model、Reasoning Effort，并不将每个提供方的所有 API 字段都变成通用 UI 选项。以 [OpenAI Responses API](https://developers.openai.com/api/reference/cli/resources/responses/methods/create) 和 [Chat Completions API](https://developers.openai.com/api/reference/cli/resources/chat/subresources/completions) 为例，下列参数均可通过插件进行修改。

| OpenAI API 参数 | 功能 | 插件接入方式 |
| --- | --- | --- |
| `temperature` | 控制采样随机性；值越低，输出越集中 | 可由 `agent/request` 插件按 Agent、任务或 Step 自动设置，最后由 Adapter 写入请求 |
| `max_output_tokens` / `max_completion_tokens` | 限制可见输出与推理使用的 Token 预算 | DSH 已用 `maxTokens` 建模；`agent/request` 插件可按 Agent、任务或 Step 设置，不需要增加前端控件 |
| `stop` | 生成指定字符串时停止输出 | DSH 已用 `stop` 建模；插件可为固定格式、分段协议或生成任务注入停止序列 |
| `top_p` | 通过核采样限制候选 Token 的累积概率范围 | 可由 LLM Adapter 插件在序列化请求时注入；OpenAI 建议通常只调整 `top_p` 或 `temperature` 之一 |
| `tool_choice` | 允许自行选择、禁止或强制 Tool Call，也可指定工具 | 可由 Agent 策略插件决定，再由 LLM Adapter 转换为提供方字段 |
| `parallel_tool_calls` | 允许模型在一次响应中生成多个并行 Tool Call | 可由插件按 Tool 的并发安全性和任务类型选择，并由 Adapter 写入请求 |
| `text.format` / `response_format` | 要求普通文本、JSON 或符合 JSON Schema 的结构化输出 | 可由领域插件同时提供输出 Schema、请求参数和结果校验，避免只依赖 Prompt 约束格式 |
| `text.verbosity` | 选择回复的简洁或详细程度 | 可由插件按任务阶段设置，例如计划阶段使用详细输出、结果回传使用简洁输出 |
| `service_tier` | 选择提供方的延迟、成本和处理等级 | 适合作为 Adapter 或部署策略插件的配置，由任务优先级决定，而不是交给每个用户手动选择 |
| `prompt_cache_key` | 将相似请求归入稳定的 Prompt Cache 分组 | 可由插件根据 Agent、Preset 或任务类型派生，无需进入模型前端 |
| `top_logprobs` | 返回每个位置的高概率候选 Token，用于评测与诊断 | 需要 Adapter 插件同时扩展响应解析和遥测记录，不只是向请求中增加一个字段 |

##### **实验：不同 Temperature 执行相同需求分析任务**

选择采集执行Agent接入工作流的阶段 1 需求分析任务，分别使用 Temperature 0、0.5 和 1，每个参数重复执行 3 次。9 次正式运行使用相同的 Prompt、PRD 和 Context，权限均为 Full access，每次运行使用独立目录，避免既有文件互相影响。

| Temperature | 成功运行 | 本地校验通过 | 3 次运行中的不同语义输出数 | 执行步数范围 | 耗时范围 |
| --- | --- | --- | --- | --- | --- |
| 0 | 3/3 | 3/3 | 3 | 55–118 | 9 分 12 秒–18 分 34 秒 |
| 0.5 | 2/3 | 2/3 | 3 | 29–91 | 5 分 49 秒–12 分 54 秒 |
| 1 | 3/3 | 3/3 | 3 | 53–106 | 7 分 19 秒–14 分 13 秒 |

三个参数下都没有出现两次完全一致的结果。每个参数的三次运行在原始文件、路径归一化结果和语义归一化结果上均形成 3 个不同输出。Temperature 0 的三组两两比较仍有 54、102 和 104 个语义叶子字段不同，执行步数为 55–118；渠道和规则标识、数据类型顺序、测试用例以及是否遵循强制流程均发生变化。

##### **结论**

Temperature 是采样参数，不是 Agent Loop 的确定性开关。设置为 0 可以收窄当前一步的候选输出，但不能保证模型服务逐字返回相同内容，也不能固定 Tool 返回、外部服务状态、上下文装配和后续 Agent 决策。长程任务会将每一步的差异写回上下文，使后续模型请求不再相同，最终把局部偏差放大为执行路径和结果文件的差异。

实验结果没有验证“关闭推理并将 Temperature 设置为 0 可以稳定复现长程任务”的最初猜想，但这次实践仍提供了一条新的优化思路：借助 DSH 的插件化架构，我们不必只在 Skill 中增加文本约束，还可以通过插件直接对 Agent 底层的大模型 API 调用进行调参，记录实际请求值，并通过重复实验验证不同参数对执行路径和结果的影响。

#### 4.4 使用 Claude Code 替换 Subagent Provider

##### **背景**

在 DSH 之前，开发者可以通过插件、CLI 或 SDK 让 CatDesk、Claude Code、Codex 等产品相互调用。例如[《Claude Code 调用 Codex：一次性子进程与常驻 App Server》](https://zhuanlan.zhihu.com/p/2051577899338281083)介绍了两条路径：通过 `codex exec` 启动一次性子进程，或者通过 Codex App Server 复用会话并支持恢复、中断等交互。这些方案可以实现 Agent 协作，但通常需要针对具体产品组合分别适配任务传递、进程生命周期和结果返回。

DSH 将 Subagent 的公共调用接口、具体执行后端和模型侧 Tool 拆成独立插件。上层 Agent 始终调用同一个 `subagent` Tool，只需替换 Provider，就能在进程内 DSH Agent、Claude Code、Codex 等实现之间切换，而不需要修改 Tool 和 Agent Loop：

```
// 代码块
点对点集成：采集执行 Agent → 专用插件／脚本 → Claude Code
统一能力接口：采集执行 Agent → subagent Tool → Subagent Service → Claude Code Provider
                                                               ├─ Codex Provider
                                                               └─ DSH In-process Provider
```

##### **安装与使用**

首先使用 DSH CLI 从 npm 安装 Claude Code Provider：

```Shell
// 代码块
dsh plugin --profile web add \
  @deepseek-ai/dsh-subagent-claude-code@0.1.1-rc.2
```

安装完成后重启 Web Profile：

```Shell
// 代码块
dsh web
```

然后在 Agent Preset 中启用 Subagent Tool，并将其绑定到 `claude-code` Provider：

```YAML
// 代码块
- id: tool-subagent-claude-code
  name: '@deepseek-ai/dsh-tool-subagent'
  config:
    provider: claude-code
    toolName: subagent
    backgroundMode: one-shot
    maxDepth: provider-managed
```

同一个 Agent Preset 可以注册多个 Subagent Tool 实例，为每个实例设置不同的 `toolName` 和 Provider。主 Agent 根据任务类型选择对应的 Tool，即可将编码、检索或其他任务派发给不同的 Subagent。

### 五、将 DSH 接入 Multica 作为本地 Runtime

#### 5.1 接入方式

Multica 可以继续负责 Issue、小队和任务调度，只把底层 Agent Runtime 替换为本机 DSH。接入时需要升级 Multica CLI、安装 DSH、为 `multica` Profile 安装 Runtime 插件并重启 daemon，具体命令和配置见[《本地 DeepSeek Harness 接入 Multica》](https://km.sankuai.com/collabpage/2782280286)。

接入完成后，Multica 负责选择任务、准备工作目录并注入项目上下文，daemon 通过标准输入输出协议启动 `dsh --profile multica --stdio`。模型配置、凭证、Agent Loop 和 Session 持久化由本地 DSH 管理。

#### 5.2 Session 日志的区别

Multica 与 DSH 记录的是不同层次的状态：Multica 日志以 Run 为单位，记录任务调度和执行状态；DSH Session 日志记录一次 Agent 会话中的用户消息、模型回复和 Tool 调用，是恢复上下文和继续执行的状态来源。

每次 Multica Run 都会启动一个本地 DSH 进程，但不一定创建新的 Session。请求携带 `resume_session_id` 时，DSH 从已有 Session 日志恢复上下文并追加新的 Turn；未携带时则创建新 Session。因此，一个 DSH Session 可以跨多个续跑 Run，同一 Issue 的不同 Run 也可能对应多个独立 Session；子 Issue 会作为独立任务创建自己的 Session。

#### 5.3 测试结果

选取采集执行领域 5 个任务进行测试，均在阶段一执行超时（超40min）后仍未完成，基本不可用；正常情况下类似任务的阶段一平均完成时间约为 9 分 37 秒。

读取执行日志分析原因，可以分为以下几类：

| 分类 | 表现 | 原因分析 |
| --- | --- | --- |
| 父子任务工作目录隔离 | 子任务需要把 `stage1_result.json` 写入父任务目录，但 5 个任务均返回 `Operation not permitted`，父任务最终没有收到阶段一结果 | DSH 将 Session 的 cwd 固定为唯一主要可写根目录，目前不支持额外的目录级可写白名单；Multica 又为父子任务提供独立的 Session root，导致结果路径位于子任务沙箱之外。[DSH 官方沙箱说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/sandbox/sandbox-policy/README.md)、[Multica DSH Runtime](https://github.com/multica-ai/dsh-multica-runtime)，这即是 DSH 单根目录权限模型的限制，也是 Multica Bridge 未适配现有产物协议的问题。[DSH 目录授权讨论 #4701](https://github.com/deepseek-ai/deepseek-harness/discussions/4701) |
| Agent Loop 缺少收敛约束 | Agent 反复核对在线 v1、灰度 v2、L3/L4、`task_code` 和 `method_code`，并多次跨 workspace 搜索；已经获得相似结果后仍继续查询 | Prompt 没有限制检索范围、查询次数和业务冲突的终止条件；DSH Agent Loop 只要模型继续请求 Tool 就会继续执行，缺少内置的 maxSteps 或任务级资源预算等异常循环止损机制。[无上限 Agent Loop 讨论 #2821](https://github.com/deepseek-ai/deepseek-harness/discussions/2821)、[Harness 循环案例 #3228](https://github.com/deepseek-ai/deepseek-harness/discussions/3228) |
| Tool 输出持续积累 | 执行约 34 次 `zbmanager` 查询、23 次跨 workspace 检索和 55 条 Python 命令，累计产生约 278 KB Tool 输出，后续请求逐渐变慢 | 重复查询产生的 Tool 结果会保留在 DSH Session 中。DSH 默认在上下文达到 80% 后才触发 Compaction，Tool Result Pruning 也只有在该条件满足后才运行，低压力时不会独立裁剪大输出。[DSH Compaction 官方说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/compaction/compaction-basic/README.md)、[相同版本实测 #5150](https://github.com/deepseek-ai/deepseek-harness/discussions/5150)[长程上下文讨论 #5310](https://github.com/deepseek-ai/deepseek-harness/discussions/5310)  ps：Claude Code会在上下文管理时优先清理旧 Tool 输出、Codex经过性能和成本调优后将GPT‑5.6 Sol的默认上下文窗口设置成272K。 |

作为 Multica Agent Runtime 使用时，默认配置下的 DSH 对长程、Headless 及多 Agent 协作场景的运行保障仍不充分，尚未达到生产级 Runtime 所要求的稳定性与可控性。正式应用前，需要在 Multica–DSH 接入层完善跨 Session 产物交付、异常循环熔断、查询与资源预算控制，以及上下文生命周期治理等机制。

### 六、总结与展望

#### 6.1 总结

Claude Code、Codex 和 CatDesk 都提供面向用户的 Agent 工作流，并通过 Skill、Tool、MCP、Hook 或 SDK 等机制开放扩展能力。DSH 同样采用插件化扩展，但可扩展对象进一步覆盖 Agent Runtime 本身，使开发者能够重新组合底层运行能力。

具体来看，DSH 将模型适配、Agent Loop、Session、上下文管理、Tool Pipeline、Subagent Provider 和客户端组装等运行能力开放为插件扩展点。本文通过 Session 断点重跑、WeKnora 知识库接入、模型请求参数扩展、Claude Code Subagent 和 Multica Runtime Bridge，验证了这些扩展点在执行历史复用、知识统一管理、模型调用控制、执行后端替换和外部平台集成中的可行性。对于领域 Agent，DSH 的价值在于提供更细粒度的 Runtime 控制，使团队能够复用底层运行机制，并围绕具体业务流程进行定制。

#### 6.2 现阶段问题与迁移限制

DSH 当前仍处于开发者预览阶段，整体成熟度不足，在接口稳定性、插件恢复、长任务资源治理、执行止损和安全审计等方面尚未形成生产级保障。现阶段更适合用于扩展机制验证和领域 Agent 原型实践，**尚不具备将既有 Agent Runtime 整体迁移到 DSH 的条件**。

| 风险项 | 现状与依据 | 影响 |
| --- | --- | --- |
| 插件兼容与故障恢复 | [官方 README](https://github.com/deepseek-ai/deepseek-harness#developer-preview) 明确说明后续会出现兼容性破坏性变更。社区已有 Adapter 接口变化导致[第三方插件失效](https://github.com/deepseek-ai/deepseek-harness/discussions/4013)，以及导出移除、接口调整和客户端 Runtime 包删除等[升级案例](https://github.com/deepseek-ai/deepseek-harness/discussions/5271)。目前没有证据证明“大量插件已经失效”，但一个加载失败的条目可能触发[整组插件配置回滚](https://github.com/deepseek-ai/deepseek-harness/discussions/5106)，客户端也[缺少页面内恢复入口](https://github.com/deepseek-ai/deepseek-harness/discussions/2229)。 | 实际使用时发现，更新 DSH 版本后，旧插件在新版本容易出现不兼容。 |
| 长 Session 资源上界 | Session 会在内存中保留完整事件序列，Compaction 只缩减模型输入，不裁剪原始日志；恢复时还需要读取并重放历史事件。社区已有长 Session 叠加大量并发 Subagent 后，进程内存增长至约 4 GB 并崩溃的[报告](https://github.com/deepseek-ai/deepseek-harness/discussions/4722)。持久化层虽然会批量、压缩写入，但并发任务仍会放大内存、日志压缩和磁盘读写压力。 | 实际测试中发现，如果并发开启 5 个 Session跑采集执行需求，dsh web Node 进程的 CPU 占用升至约 59%，暂不具备稳定承载多个长程任务的条件。（[讨论 #4530](https://github.com/deepseek-ai/deepseek-harness/discussions/4530) 报告dsh在多个并发任务持续产生事件时，主 Node 进程约 **100% 单核**，每秒执行约 400 次 `writev`，最终事件循环被占满，HTTP 请求全部超时。） |
| 异常循环与成本控制 | Agent Loop 主要依赖模型主动结束执行，缺少统一的任务级 Step 上限、Token 或费用预算以及异常输出熔断。除 5.3 节中的重复查询外，社区还报告过模型重复输出约 10 分钟、只能依靠 Token 上限或人工终止的[案例](https://github.com/deepseek-ai/deepseek-harness/discussions/2848)。 | 模型异常可能演变为长时间资源占用、额外费用和无人值守任务失控，不适合直接用于 Headless 和批量评测。 |
| 安全与部署边界 | [官方安全说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/SAFETY.zh.md)指出项目尚未经过安全审计，不应被视为安全或可用于生产环境的软件；沙箱、审批和权限控制也不保证隔离。Web Server 本身[不提供服务器级 TLS、认证或来源策略](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/host/webserver/README.zh.md#%E5%B7%B2%E7%9F%A5%E9%99%90%E5%88%B6%E4%B8%8E%E5%BB%B6%E6%9C%9F%E5%B7%A5%E4%BD%9C)。 | 现阶段仅适合本地或隔离环境，不适合直接承载敏感数据、共享服务或不可信工作负载。 |

#### 6.3 展望

DSH 的优势在于将 Agent Runtime 的关键环节开放为可组合的插件，使模型、Agent Loop、Session、知识检索、Tool、Subagent 和客户端都可以按场景扩展或替换。基于统一的 Session 日志，执行过程还可以被记录、检查、恢复和重放，为领域 Agent 的调试、评测和持续迭代提供基础。随着项目逐步成熟，DSH 有望成为连接不同模型、执行后端和业务平台的通用 Runtime，使团队能够复用底层运行机制，将更多精力投入领域知识和业务流程建设。

---

**注释：**

- 事件溯源：事件溯源（Event Sourcing）是一种以事件记录状态的方法。系统不只保存当前状态，而是按照发生顺序记录用户输入、模型回复、Tool Result 和执行状态变化等事实；需要恢复当前状态时，再读取这些事件进行重建或投影。因为历史事件会被保留，系统也可以从某个节点恢复、分支或重新执行。
- 美团AI Agent可观测平台：用于追踪(Tracing)和分析 CatDesk、CatX、Claude Code 等 AI Agent 产品的运行全过程，并以统一格式展示这些Agent平台的Trace可视化及分析流程 [https://km.sankuai.com/collabpage/2772835399](https://km.sankuai.com/collabpage/2772835399)
- 19%：统计范围为 2026 年 8 月 2 日至 9 月 2 日的 18 个 commit。其中，12 个 commit 涉及四阶段主链，3 个属于渠道复用，2 个只修改评测 Task，1 个只修改 Agent 组织配置。由于后 6 个 commit 不适用四阶段执行链路，本次仅统计其余 12 个 commit。 按照 commit 的主要修改内容分类，7 个集中在需求分析阶段，主要涉及 PRD/KM 提取、验证数据生成和阶段上下文；4 个集中在函数配置阶段，主要涉及 Groovy 生成、知识检索和 UDF 验证；1 个集中在流程测试阶段，主要涉及测试结果定位与比较。 需求分析阶段的修改仍需从头执行；函数配置阶段的修改可以复用需求分析及此前的解析 Leader 执行，单次约节省 14 分 34 秒；流程测试阶段的修改可以复用前三个阶段及其编排过程，单次约节省 34 分 29 秒。综合估算预计平均节约时间为19%。
- WeKnora：[WeKnora](https://weknora.weixin.qq.com) 是腾讯开源的、基于大语言模型的知识管理框架，面向企业文档理解、语义检索和智能推理场景。它提供 RAG 快速问答、ReAct Agent 多步推理和自动 Wiki 三项核心能力，并覆盖文档解析、分块、向量化、混合检索、引用回答和知识图谱等知识处理环节。项目源码与完整功能说明见 [WeKnora GitHub 仓库](https://github.com/Tencent/WeKnora)。
- 性能和成本调优后：官方解释，超过约 272K 后，整体输出质量差别不大。更大的窗口主要优势是减少上下文压缩等待、能一次处理超大输入。但工具调用会反复读取、传递已有上下文；窗口越大，每次调用涉及的缓存读取量越大，使用额度和系统成本增长更快。
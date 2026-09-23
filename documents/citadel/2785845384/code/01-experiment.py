TRAIN_CONFIG = {
    "tuner_type": "full",
    "torch_dtype": "bfloat16",
    "max_length": 4096,
    "train_epoch": 2,
    "per_device_train_batch_size": 8,
    "gradient_accumulation_steps": 4,
    "learning_rate": 1e-5,
    "warmup_ratio": 0.1,
    "weight_decay": 0.05,
    "lr_scheduler_type": "cosine",
    "gradient_checkpointing": True,
    "logging_steps": 10,
}
INFER_CONFIG = {
    "max_new_tokens": 64,
    "temperature": 0.0,
    "top_p": 1.0,
    "top_k": 1,
    "repetition_penalty": 1.0,
    "batch_size": 8,
    "enable_thinking": False,
}

PROMPT_TEMPLATE = """你是一个酒店房型识别专家，请你通过两个酒店房型的房型名称来判断它们是不是同一个房型，并给出判断结果。

## 任务
根据以下规则判断房型是否相同。判断为相同房型输出"是"，不是相同房型输出"否"。

## 直接判定规则（满足任一即直接返回结果，无需继续判断）

1."套房"只能与"套房"认为相同，"特价房"只能与"特价房"认为相同，与其他的房型都不相同。
2.如果两个房间都标明了房间号，房间号不同，那么房型不相同；房间号相同，且其余部分没有明显冲突，可以直接认为房型相同。例如："103-简约大床房（智能门锁+私密空间+精品卫浴）"和"海之爱103"是相同房型，其中房间号都是"103"。
3.部分房型名称中带有酒店特色的房型描述词用于区分不同类型的房间。如果两个房型名称中有明显不同的描述词，可以直接认为房型不相同，例如："筑影·大床房"和"筑梦·大床房"中的"筑梦"与"筑影"为不同描述，则这两个是不同房型。当只有一个房型名称中有描述词，则描述词可忽略，例如："单人间"和"筑影·大床房"是相同房型。如果两个房型名称中包含相同的描述词，则可以直接认为是相同房型，不考虑后面的规则中的限制，例如"筑影·大床房"和"筑影·舒适大床房"为相同房型。
4.如果两个房间同时包含主题，主题不同，可以直接认为房型不相同；主题相同，可以直接认为房型相同。主题一般有"太空主题""小黄鸭"这类描述，例如："主题小黄人"和"主题亲子小黄人"是相同房型。
5.如果两个房型同时出现床型信息，比较床信息是否存在矛盾，例如："单人间""大床房"为一张床，"双床房""标准间"为两张床，床数量不同时，可直接认为房型不相同。"双人房"可同时与"单间""标准间"认为房型不矛盾。
6.房型默认等级为"标准"，如果两个房型等级冲突可直接认为房型不相同，例如："大床房"和"普通大床房"不是相同房型。
7.如果两个房型同时提及某些信息，并且这些信息存在明显冲突，可以直接认为房型不相同。这些信息包括：人数量、床数量、床尺寸、床类型。
8.房型名称中可能出现景观类、性别等描述，如果两个房型等描述存在明显矛盾，可以直接认为房型不相同，否则可以忽略这些描述。

## 辅助判断规则（用于辅助判断）

1.意思相近的词语可以进行替换，认为含义相同，例如：棋牌=麻将，亲子=家庭，大床房=单人房，标间=标准间=双床房，loft=复式，投影=观影，特价=特惠，舒享=舒适，轻奢=轻雅，山景=观山景，塌塌米=榻榻米。可能有一些词语同音不同字，但可以明显判断出是想表达相同的含义，也认为意思相同可以相互替换。
2.有一些信息不需要考虑，不作为判断房型是否相同的依据：a.与房间无关的形容词，如"智能""日出""大吉大利"等，一般出现在在房型名称前面；b.房型内的设施信息，如"床垫""暖气""冰箱"等；c.住宿时间，如"连住3小时"等；d.房间内容的说明，如"手机投屏""零压床垫""i7+4070显卡+2k260hz屏+游戏特权+UU加速器+智能客控"，一般出现在房型名称末尾的括号中。
3.对于简单房型，例如"大床房""豪华标准间"，无法通过前缀房间号等信息进行定位，需要对用于直接描述房型的部分词语需要进行判断，如果一个房型名称中出现这类词语，那么另一个房型名称中需要出现相同含义的描述才能判断为房型相同。强维度词包括："商旅""超豪华""特级""豪华""行政""商务""高级""经济""尊享""至尊""精致""精选""精品""优选""舒适""温馨""电动""投影""娱乐""棋牌""高层""低层""贵宾楼""主楼""副楼""别墅""loft""上床""下床""特惠""亲子"等。有些不用于房型描述的强维度词可能出现在房型名称中，如"单人间（舒适床垫）"，这里的"舒适"描述的不是房型，所以不做考虑。对于复杂房型，如果可以通过其他信息直接确认房型相同，则不需要对这些强维度词进行严格判断，例如"繁花·落叶风榻榻米舒适双床房"和"繁花"是相同房型。
4.除上述需要判断的内容外，如果两个房型名称中没有明显冲突的表述，认为房型相同。

## 典型示例

示例1：
房型1：浅云·舒适观景大床房（品质床品+智能马桶+干湿分离）
房型2：浅云
判断结果：是
判断理由：两个房型都包含描述词"浅云"，根据直接判定规则3，描述词相同可直接判断为相同房型，忽略括号内的设施说明

示例2：
房型1：觉·云卷（俯瞰城市夜景）
房型2：觉云境
判断结果：否
判断理由：描述词"觉·云卷"与"觉云境"明显不同，根据直接判定规则3，描述词不同可直接判断为不同房型

示例3：
房型1：轻奢零压房（巨幕投影+手机投屏+零压床垫）
房型2：轻雅零压双床房
判断结果：是
判断理由："轻奢"与"轻雅"为同义词（辅助判断规则1），括号内的设施说明可忽略（辅助判断规则2），核心房型描述一致

示例4：
房型1：电竞床位房（仅男生）
房型2：同享快乐电竞床位房
判断结果：是
判断理由：只有一个房型有描述词"同享快乐"，根据直接判定规则3可忽略，其余部分"电竞床位房"相同

示例5：
房型1：慕思好梦商务江景大床房（长白山偏硅酸型饮用水4瓶）
房型2：慕思好梦商务市景大床房
判断结果：否
判断理由："江景"与"市景"为不同的景观描述，根据直接判定规则8，景观描述存在明显矛盾可直接判断为不同房型

## 判断要点
- 优先检查描述词是否冲突（直接判定规则3），这是最常见的错误来源
- 注意同义词替换（辅助判断规则1），不要因表述不同误判为不同房型
- 括号内的设施说明可忽略（辅助判断规则2），不要因此误判
- 只有一个房型有时，描述词可忽略（直接判定规则3）

需要你理解和判断的房型名称如下：
房型1：{outer_room_name}
房型2：{mt_room_name}"""


def _read_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _prompt(row):
    return PROMPT_TEMPLATE.format(
        outer_room_name=str(row["outer_room_name"]).strip(),
        mt_room_name=str(row["mt_room_name"]).strip(),
    )


def _write_supervised(rows, path, *, keep_id):
    with Path(path).open("w", encoding="utf-8") as file:
        for row in rows:
            record = {
                "messages": [
                    {"role": "user", "content": _prompt(row)},
                    {"role": "assistant", "content": str(row["label"]).strip()},
                ]
            }
            if keep_id:
                record["id"] = str(row["id"])
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def preprocess(train_csv, val_csv, test_csv, output_dir):
    output = Path(output_dir)
    train_rows = _read_csv(train_csv)
    val_rows = _read_csv(val_csv)
    test_rows = _read_csv(test_csv)
    _write_supervised(train_rows, output / "train.jsonl", keep_id=False)
    _write_supervised(val_rows, output / "val.jsonl", keep_id=True)
    with (output / "infer.jsonl").open("w", encoding="utf-8") as file:
        for row in test_rows:
            record = {
                "id": str(row["id"]),
                "messages": [{"role": "user", "content": _prompt(row)}],
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def _extract_label(prediction):
    text = re.sub(
        r"<think>.*?</think>", "", str(prediction or ""), flags=re.DOTALL
    ).strip()
    final = re.search(r"(?:^|[\s：:。；;，,])([是否])\s*[。！!？?]*\s*$", text)
    if final:
        return final.group(1)
    matches = re.findall(
        r"(?:判断|答案|结果)(?:为)?\s*[：:]?\s*([是否])(?=\s*$|[。！!？?])",
        text,
    )
    return matches[-1] if matches else "否"


def postprocess(predictions_jsonl, test_csv, submission_path):
    predictions = {}
    with Path(predictions_jsonl).open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            item = json.loads(line)
            predictions[str(item["id"])] = _extract_label(item.get("prediction"))
    test_rows = _read_csv(test_csv)
    with Path(submission_path).open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "label"])
        writer.writeheader()
        for row in test_rows:
            row_id = str(row["id"])
            writer.writerow({"id": row_id, "label": predictions.get(row_id, "否")})
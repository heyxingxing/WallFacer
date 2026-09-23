TRAIN_CONFIG = {
    "tuner_type": "full",
    "torch_dtype": "bfloat16",
    "max_length": 4096,
    "train_epoch": 3,
    "per_device_train_batch_size": 16,
    "gradient_accumulation_steps": 2,
    "learning_rate": 1e-05,
    "warmup_ratio": 0.1,
    "weight_decay": 0.01,
    "lr_scheduler_type": "cosine",
    "gradient_checkpointing": True,
    "logging_steps": 10,
}
INFER_CONFIG = {
    "max_new_tokens": 4,
    "temperature": 0.0,
    "top_p": 1.0,
    "top_k": 1,
    "repetition_penalty": 1.0,
    "batch_size": 64,
    "enable_thinking": False,
}

PROMPT_TEMPLATE = """你是一个酒店房型识别专家，请你通过两个酒店房型的房型名称来判断它们是不是同一个房型，并给出判断结果。

## 任务
根据以下规则按顺序判断房型是否相同，部分规则可直接返回判断结果，无需继续判断。判断为相同房型输出"是"，不是相同房型输出"否"。

## 相同房型判断规则
1.意思相近的词语可以进行替换，认为含义相同，例如：棋牌=麻将，亲子=家庭，大床房=单人房，标间=标准间=双床房，loft=复式，投影=观影，特价=特惠。可能有一些词语同音不同字，但可以明显判断出是想表达相同的含义，例如"榻榻米"和"塌塌米"，这种情况下认为意思相同可以相互替换。
2.有一些信息不需要考虑，不作为判断房型是否相同的依据：a.与房间无关的形容词，如"智能""日出""大吉大利"等，一般出现在在房型名称前面；b.房型内的设施信息，如"床垫""暖气""冰箱"等；c.住宿时间，如"连住3小时"等；d.房间内容的说明，如"手机投屏""零压床垫""i7+4070显卡+2k260hz屏+游戏特权+UU加速器+智能客控"，一般出现在房型名称末尾的括号中。
3.如果两个房型同时出现床型信息，比较床信息是否存在矛盾，例如："单人间""大床房"为一张床，"双床房""标准间"为两张床，床数量不同时，可直接认为房型不相同。"双人房"可同时与"单间""标准间"认为房型不矛盾。
4."套房"只能与"套房"认为相同，"特价房"只能与"特价房"认为相同，与其他的房型都不相同。
5.如果两个房间都标明了房间号，房间号不同，那么房型不相同；房间号相同，且其余部分没有明显冲突，可以直接认为房型相同。例如："103-简约大床房（智能门锁+私密空间+精品卫浴）"和"海之爱103"是相同房型，其中房间号都是"103"。
6.部分房型名称中带有酒店特色的房型描述词用于区分不同类型的房间。如果两个房型名称中有明显不同的描述词，可以直接认为房型不相同，例如："筑影·大床房"和"筑梦·大床房"中的"筑梦"与"筑影"为不同描述，则这两个是不同房型。当只有一个房型名称中有描述词，则描述词可忽略，例如："单人间"和"筑影·大床房"是相同房型。如果两个房型名称中包含相同的描述词，则可以直接认为是相同房型，不考虑后面的规则中的限制，例如"筑影·大床房"和"筑影·舒适大床房"为相同房型。
7.如果两个房间同时包含主题，主题不同，可以直接认为房型不相同；主题相同，可以直接认为房型相同。主题一般有"太空主题""小黄鸭"这类描述，例如："主题小黄人"和"主题亲子小黄人"是相同房型。
8.房型名称中可能出现景观类、性别等描述，如果两个房型等描述存在明显矛盾，可以直接认为房型不相同，否则可以忽略这些描述。
9.对于简单房型，例如"大床房""豪华标准间"，无法通过前缀房间号等信息进行定位，需要对用于直接描述房型的部分词语需要进行判断，如果一个房型名称中出现这类词语，那么另一个房型名称中需要出现相同含义的描述才能判断为房型相同。强维度词包括："商旅""超豪华""特级""豪华""行政""商务""高级""经济""尊享""至尊""精致""精选""精品""优选""舒适""温馨""电动""投影""娱乐""棋牌""高层""低层""贵宾楼""主楼""副楼""别墅""loft""上床""下床""特惠""亲子"等。有些不用于房型描述的强维度词可能出现在房型名称中，如"单人间（舒适床垫）"，这里的"舒适"描述的不是房型，所以不做考虑。对于复杂房型，如果可以通过其他信息直接确认房型相同，则不需要对这些强维度词进行严格判断，例如"繁花·落叶风榻榻米舒适双床房"和"繁花"是相同房型。
10.如果两个房型同时提起某些信息，并且这些信息存在明显冲突，可以直接认为房型不相同。这些信息包括：人数量、床数量、床尺寸、床类型。
11.房型默认等级为"标准"，如果两个房型等级冲突可直接认为房型不相同，例如："大床房"和"普通大床房"不是相同房型。
12.除上述需要判断的内容外，如果两个房型名称中没有明显冲突的表述，认为房型相同。

需要你理解和判断的房型名称如下：
房型1：{outer_room_name}
房型2：{mt_room_name}"""

DIFFICULT_NEG_KEYWORDS = [
    "套房",
    "特价",
    "别墅",
    "温泉",
    "商旅",
    "超豪华",
    "特级",
    "豪华",
    "行政",
    "商务",
    "高级",
    "经济",
    "尊享",
    "至尊",
    "精致",
    "精选",
    "精品",
    "优选",
    "舒适",
    "温馨",
    "电动",
    "投影",
    "娱乐",
    "棋牌",
    "高层",
    "低层",
    "贵宾",
    "主楼",
    "副楼",
    "loft",
    "上床",
    "下床",
    "特惠",
    "亲子",
    "高低床",
    "上下铺",
    "普通",
]


def _read_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _prompt(row):
    return PROMPT_TEMPLATE.format(
        outer_room_name=str(row["outer_room_name"]).strip(),
        mt_room_name=str(row["mt_room_name"]).strip(),
    )


def _is_difficult_neg(row):
    text = (
        str(row.get("outer_room_name", "")) + str(row.get("mt_room_name", ""))
    ).lower()
    return any(kw in text for kw in DIFFICULT_NEG_KEYWORDS)


def preprocess(train_csv, val_csv, test_csv, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    train_rows = _read_csv(train_csv)
    rng = random.Random(42)
    rng.shuffle(train_rows)
    with (out / "train.jsonl").open("w", encoding="utf-8") as f:
        for row in train_rows:
            label = row["label"].strip()
            if label not in ("是", "否"):
                continue
            record = {
                "messages": [
                    {"role": "user", "content": _prompt(row)},
                    {"role": "assistant", "content": label},
                ]
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            if label == "是":
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            elif label == "否" and _is_difficult_neg(row):
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    val_rows = _read_csv(val_csv)
    with (out / "val.jsonl").open("w", encoding="utf-8") as f:
        for row in val_rows:
            record = {
                "id": str(row["id"]).strip(),
                "messages": [
                    {"role": "user", "content": _prompt(row)},
                    {"role": "assistant", "content": str(row["label"]).strip()},
                ],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    test_rows = _read_csv(test_csv)
    with (out / "infer.jsonl").open("w", encoding="utf-8") as f:
        for row in test_rows:
            record = {
                "id": str(row["id"]).strip(),
                "messages": [{"role": "user", "content": _prompt(row)}],
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _extract_label(prediction):
    text = str(prediction or "")
    answer = text.rsplit("\n\n", 1)[-1]
    labels = re.findall(r"[是否]", answer)
    if not labels:
        labels = re.findall(r"[是否]", text)
    return labels[-1] if labels else "否"


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

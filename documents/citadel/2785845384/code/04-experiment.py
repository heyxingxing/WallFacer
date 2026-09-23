TRAIN_CONFIG = {
    "tuner_type": "full",
    "torch_dtype": "bfloat16",
    "max_steps": 350,
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "learning_rate": 2e-5,
    "max_length": 2048,
    "warmup_ratio": 0.1,
    "weight_decay": 0.01,
    "logging_steps": 10,
}

INFER_CONFIG = {
    "max_new_tokens": 8,
    "temperature": 0.1,
    "top_p": 0.9,
    "top_k": 50,
    "repetition_penalty": 1.0,
    "batch_size": 16,
}

SYSTEM_PROMPT = """你是酒店房型匹配专家。根据以下规则判断两个房型名称是否指同一房型，只回答"是"或"否"。

规则：
1. 同义归一：棋牌=麻将，亲子=家庭，大床房=单人房，标间=标准间=双床房，loft=复式，投影=观影，特价=特惠。
2. 忽略营销词、设施描述、住宿时长及括号内说明。
3. 专属类型一致：套房只匹配套房，特价/特惠只匹配同类。
4. 硬冲突判否：入住人数、床数量、床尺寸、床型、房型等级（未标默认标准）、景观、性别限制矛盾时判否。单人间/大床房通常一张床，双床房/标准间通常两张床；"双人房"仅表人数不限床数。
5. 房间号是强锚点：两侧都有房间号且不同判否；相同且无更高冲突判是。
6. 酒店特色名/主题是强锚点：两侧都有且相同判是，不同判否；仅一侧出现可忽略。
7. 简单房型看修饰维度词：豪华、商务、行政、经济、舒适、投影、棋牌、亲子、楼层、楼栋、别墅、复式等需语义一致；仅修饰括号内设施的忽略。
8. 无冲突默认判是。"""


def preprocess(train_csv: str, test_csv: str, output_dir: str) -> None:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 读取训练数据并过采样"是"类
    yes_rows = []
    no_rows = []
    with open(train_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["label"] == "是":
                yes_rows.append(row)
            else:
                no_rows.append(row)

    # 过采样：每个"是"样本重复一次
    train_rows = no_rows + yes_rows + yes_rows
    random.seed(42)
    random.shuffle(train_rows)

    # 动态调整max_steps以保持约2个epoch
    total_rows = len(train_rows)
    global_batch = (
        TRAIN_CONFIG["per_device_train_batch_size"]
        * TRAIN_CONFIG["gradient_accumulation_steps"]
        * 8  # world_size=8
    )
    max_steps = round(2 * total_rows / global_batch)
    TRAIN_CONFIG["max_steps"] = max_steps

    # 写入训练数据
    train_lines = []
    for row in train_rows:
        msg = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"房型A：{row['outer_room_name']}\n房型B：{row['mt_room_name']}",
                },
                {"role": "assistant", "content": row["label"]},
            ]
        }
        train_lines.append(json.dumps(msg, ensure_ascii=False))

    with open(out_path / "train.jsonl", "w", encoding="utf-8") as f:
        f.write("\n".join(train_lines))

    # 推理数据
    infer_lines = []
    with open(test_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            msg = {
                "id": row["id"],
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"房型A：{row['outer_room_name']}\n房型B：{row['mt_room_name']}",
                    },
                ],
            }
            infer_lines.append(json.dumps(msg, ensure_ascii=False))

    with open(out_path / "infer.jsonl", "w", encoding="utf-8") as f:
        f.write("\n".join(infer_lines))


def _extract_label(text: str) -> str:
    if not text:
        return "是"
    text = text.strip()
    m = re.search(r"(是|否)", text)
    if m:
        return m.group(1)
    if text.startswith("是"):
        return "是"
    if text.startswith("否"):
        return "否"
    return "是"


def postprocess(predictions_jsonl: str, test_csv: str, submission_path: str) -> None:
    preds = {}
    with open(predictions_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            preds[obj["id"]] = _extract_label(obj.get("prediction", ""))

    ids = []
    with open(test_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ids.append(row["id"])

    with open(submission_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "label"])
        for id_ in ids:
            writer.writerow([id_, preds.get(id_, "是")])
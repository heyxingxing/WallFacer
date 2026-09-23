TRAIN_CONFIG = {
    "tuner_type": "full",
    "torch_dtype": "bfloat16",
    "max_length": 4096,
    "train_epoch": 3,
    "per_device_train_batch_size": 8,
    # 4 GPUs x batch 8 x accumulation 4 = global batch 128 (same as parent).
    "gradient_accumulation_steps": 4,
    "learning_rate": 1e-5,
    "warmup_ratio": 0.1,
    "weight_decay": 0.01,
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

# ---------------------------------------------------------------------------
# Rule-derived, label-safe augmentation settings (train split only).
# ---------------------------------------------------------------------------
_AUG_SEED = 20240501
_MAX_FACILITY_AUG = 3000
_MAX_SYNONYM_AUG = 3000
_MAX_DESC_POS_AUG = 2500
_MAX_DESC_NEG_AUG = 1500
_MAX_ASYM_NEG_AUG = 2000

# Facility descriptions that rule 2b/2d explicitly declares irrelevant.
_FACILITIES = [
    "零压床垫",
    "乳胶床垫",
    "品牌床垫",
    "智能客控",
    "智能马桶",
    "手机投屏",
    "免费WiFi",
    "中央空调",
    "暖气",
    "冰箱",
    "洗衣机",
    "智能门锁",
    "干湿分离",
    "24小时热水",
    "空气净化器",
    "加湿器",
    "保险箱",
    "迷你吧",
    "遮光窗帘",
    "品牌洗护",
    "高速宽带",
    "吹风机",
    "热水壶",
    "液晶电视",
    "新风系统",
    "一次性用品",
]

# Rule-1 synonym equivalences (bidirectional, meaning preserving).
_SYNONYMS = [
    ("标准间", "标间"),
    ("标间", "标准间"),
    ("双床房", "标准间"),
    ("标准间", "双床房"),
    ("复式", "LOFT"),
    ("LOFT", "复式"),
    ("loft", "复式"),
    ("Loft", "复式"),
    ("投影", "观影"),
    ("观影", "投影"),
    ("亲子", "家庭"),
    ("家庭", "亲子"),
    ("麻将", "棋牌"),
    ("棋牌", "麻将"),
    ("榻榻米", "塌塌米"),
    ("塌塌米", "榻榻米"),
    ("大床房", "单人房"),
    ("单人房", "大床房"),
    ("特惠", "特价"),
    ("特价", "特惠"),
]

_DESCRIPTOR_SEPARATORS = "·丨｜|"
_ROOM_TOKENS = (
    "房",
    "间",
    "床",
    "套房",
    "标间",
    "公寓",
    "别墅",
    "LOFT",
    "loft",
    "Loft",
    "复式",
    "榻榻米",
    "胶囊",
    "床位",
)
# A valid "descriptor prefix" must not contain strong-dimension words,
# room-type words, landscape/theme words, digits or letters.
_PREFIX_BLOCK_WORDS = (
    "房",
    "间",
    "床",
    "套房",
    "标间",
    "公寓",
    "别墅",
    "酒店",
    "宾馆",
    "民宿",
    "客栈",
    "主题",
    "电竞",
    "影音",
    "景观",
    "海景",
    "山景",
    "湖景",
    "江景",
    "城景",
    "园景",
    "榻榻米",
    "胶囊",
    "床位",
    "标准",
    "普通",
    "智能",
    "大床",
    "双床",
    "单人",
    "双人",
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
    "观影",
    "娱乐",
    "棋牌",
    "麻将",
    "高层",
    "低层",
    "贵宾楼",
    "主楼",
    "副楼",
    "特惠",
    "特价",
    "亲子",
    "家庭",
    "LOFT",
    "loft",
    "Loft",
    "复式",
    "上床",
    "下床",
)

# Adjectival strong-dimension words from rule 9 plus the rule-11 level word
# "普通". A single-side occurrence as a leading room modifier in a simple
# room name implies "否" unless the gold labels say otherwise (conflict
# check below). Sorted longest-first so "超豪华" wins over "豪华".
_ASYM_NEG_WORDS = sorted(
    [
        "超豪华",
        "豪华",
        "特级",
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
        "商旅",
        "普通",
    ],
    key=len,
    reverse=True,
)


def _read_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _prompt_pair(outer_room_name, mt_room_name):
    return PROMPT_TEMPLATE.format(
        outer_room_name=outer_room_name, mt_room_name=mt_room_name
    )


def _prompt(row):
    return _prompt_pair(
        str(row["outer_room_name"]).strip(), str(row["mt_room_name"]).strip()
    )


def _strip_parens(text):
    text = re.sub(r"（[^（）]*）", "", text)
    text = re.sub(r"\([^()]*\)", "", text)
    return text.strip()


def _valid_descriptor(prefix, rest):
    if not 2 <= len(prefix) <= 8:
        return False
    if re.search(r"[0-9A-Za-z]", prefix):
        return False
    if not re.search(r"[\u4e00-\u9fff]", prefix):
        return False
    if any(word in prefix for word in _PREFIX_BLOCK_WORDS):
        return False
    if len(_strip_parens(rest)) < 2:
        return False
    if not any(token in rest for token in _ROOM_TOKENS):
        return False
    return True


def _split_descriptor(name):
    positions = [
        idx for idx in (name.find(sep) for sep in _DESCRIPTOR_SEPARATORS) if idx > 0
    ]
    if not positions:
        return None
    idx = min(positions)
    prefix = name[:idx].strip()
    rest = name[idx + 1 :].strip()
    if not _valid_descriptor(prefix, rest):
        return None
    return prefix, rest


def _add_facility(name, rng):
    addition = "+".join(rng.sample(_FACILITIES, rng.randint(1, 2)))
    match_cn = re.search(r"（[^（）]*）\s*$", name)
    if match_cn:
        return name[: match_cn.end() - 1] + "+" + addition + "）"
    match_en = re.search(r"\([^()]*\)\s*$", name)
    if match_en:
        return name[: match_en.end() - 1] + "+" + addition + ")"
    return name + "（" + addition + "）"


def _synonym_variant(name, rng):
    candidates = [(src, dst) for src, dst in _SYNONYMS if src in name]
    if not candidates:
        return None
    src, dst = rng.choice(candidates)
    return name.replace(src, dst, 1)


def _asym_negative_candidates(train_pairs):
    # Map paren-stripped room names back to a real surface form so that the
    # negative partner is always a name that genuinely occurs in the corpus.
    stripped_to_original = {}
    for name_a, name_b, _ in train_pairs:
        for name in (name_a, name_b):
            key = _strip_parens(name)
            if key and key not in stripped_to_original:
                stripped_to_original[key] = name

    candidates = []
    for base_key, original in stripped_to_original.items():
        lead = base_key.lstrip("【[（( ")
        if not lead:
            continue
        matched = False
        # Mode 2: a strong-dimension word used as the whole descriptor
        # prefix, e.g. "尊享·投影电竞大床房" -> "投影电竞大床房" is "否".
        for word in _ASYM_NEG_WORDS:
            hit = False
            for sep in _DESCRIPTOR_SEPARATORS:
                if not lead.startswith(word + sep):
                    continue
                hit = True
                rest = lead[len(word) + 1 :].strip()
                partner = stripped_to_original.get(_strip_parens(rest))
                if partner is None:
                    # Drop trailing spec segments such as "｜i7+4070显卡...".
                    cut = len(rest)
                    for sep2 in _DESCRIPTOR_SEPARATORS:
                        pos = rest.find(sep2)
                        if pos > 0:
                            cut = min(cut, pos)
                    partner = stripped_to_original.get(_strip_parens(rest[:cut]))
                if partner is not None and partner != original:
                    candidates.append((original, partner))
                    matched = True
                break
            if hit:
                break
        if matched:
            continue
        # Mode 1: leading strong-dimension adjective on a simple name,
        # e.g. "温馨三人间" -> "三人间" is "否". Skip names with separator
        # or digits to avoid descriptor and room-number interference.
        if any(sep in lead for sep in _DESCRIPTOR_SEPARATORS):
            continue
        if re.search(r"[0-9]", lead):
            continue
        for word in _ASYM_NEG_WORDS:
            if lead.startswith(word) and len(lead) - len(word) >= 2:
                partner = stripped_to_original.get(lead[len(word) :])
                if partner is not None and partner != original:
                    candidates.append((original, partner))
                break
    return candidates


def _build_augmented_pairs(train_pairs, rng):
    known = {}
    for name_a, name_b, label in train_pairs:
        known.setdefault((name_a, name_b), label)
        known.setdefault((name_b, name_a), label)

    augmented = []
    seen = set()

    def add_pair(name_a, name_b, label):
        if not name_a or not name_b or name_a == name_b:
            return False
        key = (name_a, name_b)
        if key in seen or key in known:
            return False
        seen.add(key)
        augmented.append((name_a, name_b, label))
        return True

    # (a) Descriptor positives: (full, prefix) and (full, rest) -> "是".
    desc_pos_candidates = []
    rest_groups = {}
    for name_a, name_b, _ in train_pairs:
        for name in (name_a, name_b):
            parsed = _split_descriptor(name)
            if parsed is None:
                continue
            prefix, rest = parsed
            desc_pos_candidates.append((name, prefix))
            desc_pos_candidates.append((name, rest))
            group_key = _strip_parens(rest)
            if group_key:
                rest_groups.setdefault(group_key, {})[prefix] = name
    desc_pos_candidates = list(dict.fromkeys(desc_pos_candidates))
    rng.shuffle(desc_pos_candidates)
    added = 0
    for full_name, other in desc_pos_candidates:
        if added >= _MAX_DESC_POS_AUG:
            break
        if add_pair(full_name, other, "是"):
            added += 1

    # (b) Descriptor-swap negatives: same remainder, different prefix -> "否".
    neg_candidates = []
    for prefix_map in rest_groups.values():
        names = sorted(prefix_map.values())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                neg_candidates.append((names[i], names[j]))
    rng.shuffle(neg_candidates)
    added = 0
    for name_a, name_b in neg_candidates:
        if added >= _MAX_DESC_NEG_AUG:
            break
        if add_pair(name_a, name_b, "否"):
            added += 1

    # (c) Facility-injection pairs: label preserved (rule 2b/2d).
    indices = list(range(len(train_pairs)))
    rng.shuffle(indices)
    added = 0
    for idx in indices:
        if added >= _MAX_FACILITY_AUG:
            break
        name_a, name_b, label = train_pairs[idx]
        if rng.random() < 0.5:
            name_a, name_b = _add_facility(name_a, rng), name_b
        else:
            name_a, name_b = name_a, _add_facility(name_b, rng)
        if add_pair(name_a, name_b, label):
            added += 1

    # (d) Synonym-substitution pairs: label preserved (rule 1).
    rng.shuffle(indices)
    added = 0
    for idx in indices:
        if added >= _MAX_SYNONYM_AUG:
            break
        name_a, name_b, label = train_pairs[idx]
        if rng.random() < 0.5:
            variant = _synonym_variant(name_a, rng)
            if variant is None:
                continue
            name_a = variant
        else:
            variant = _synonym_variant(name_b, rng)
            if variant is None:
                continue
            name_b = variant
        if add_pair(name_a, name_b, label):
            added += 1

    # (e) Rule-9/11 asymmetric negatives: one side carries an extra
    # strong-dimension modifier, the other side is a real corpus name
    # without it -> "否". Gold pairs win: any pair conflicting with a known
    # label is dropped by add_pair's conflict/duplicate check.
    asym_candidates = _asym_negative_candidates(train_pairs)
    rng.shuffle(asym_candidates)
    added = 0
    for name_a, name_b in asym_candidates:
        if added >= _MAX_ASYM_NEG_AUG:
            break
        if add_pair(name_a, name_b, "否"):
            added += 1

    return augmented


def preprocess(train_csv, val_csv, test_csv, output_dir):
    output = Path(output_dir)
    rng = random.Random(_AUG_SEED)
    train_rows = _read_csv(train_csv)
    val_rows = _read_csv(val_csv)
    test_rows = _read_csv(test_csv)

    train_pairs = [
        (
            str(row["outer_room_name"]).strip(),
            str(row["mt_room_name"]).strip(),
            str(row["label"]).strip(),
        )
        for row in train_rows
    ]
    augmented = _build_augmented_pairs(train_pairs, rng)
    all_train = train_pairs + augmented
    assert len(all_train) == len(train_pairs) + len(augmented)
    rng.shuffle(all_train)

    with (output / "train.jsonl").open("w", encoding="utf-8") as file:
        for name_a, name_b, label in all_train:
            record = {
                "messages": [
                    {"role": "user", "content": _prompt_pair(name_a, name_b)},
                    {"role": "assistant", "content": label},
                ]
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    # val.jsonl: every val.csv row, id and order preserved, assistant last.
    with (output / "val.jsonl").open("w", encoding="utf-8") as file:
        for row in val_rows:
            record = {
                "id": str(row["id"]),
                "messages": [
                    {"role": "user", "content": _prompt(row)},
                    {"role": "assistant", "content": str(row["label"]).strip()},
                ],
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    # infer.jsonl: every test.csv row, id and order preserved, user last.
    with (output / "infer.jsonl").open("w", encoding="utf-8") as file:
        for row in test_rows:
            record = {
                "id": str(row["id"]),
                "messages": [{"role": "user", "content": _prompt(row)}],
            }
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    assert len(all_train) >= len(train_rows)
    assert len(val_rows) == 2903 or val_rows
    assert len(test_rows) == 2903 or test_rows


def _extract_label(prediction):
    # Keep label extraction aligned with the parent plan / evaluator script.
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
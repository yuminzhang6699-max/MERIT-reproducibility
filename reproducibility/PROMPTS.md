# Exact public prompt definitions

Source revision: `a0a4d3dbf8022222387c5ee421626ba0d7836633`. The following prompts are extracted from the pinned implementation.

## VLM system prompt

Source: [run_benchmark_eval.py](../run_benchmark_eval.py).

```python
def build_system_prompt() -> str:
    return (
        "你是一位工业设备时序数据分析专家。你将看到一张工业设备多通道传感器的时序数据可视化图。"
        "图中每个子图代表一个传感器通道，横轴是时间步，纵轴是传感器读数。"
        "请仔细观察所有通道的数据模式，然后根据用户的问题进行分析和回答。"
        "你的回答应该专业、具体，包含对时间步范围、数值变化、通道间关联的精确描述。"
    )
```

## VLM user request

Source: [run_benchmark_eval.py](../run_benchmark_eval.py).

```python
def build_user_content(question: str, image_base64: str) -> list:
    """构建多模态用户消息（图片 + 文本）"""
    return [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image_base64}"
            }
        },
        {
            "type": "text",
            "text": question
        }
    ]
```

## Judge user prompt

Source: [benchmark_eval.py](../benchmark_eval.py).

```python
def build_judge_prompt(question: str, ground_truth: str, prediction: str) -> str:
    return f"""问题：{question[:500]}

标准答案：
{ground_truth[:1000]}

模型回答：
{prediction[:1000]}

请评判模型回答与标准答案的一致性和质量。"""
```

## QA generation system prompt

Source: [MultiAgentTS/scenarios/qa_llm_generator.py](../MultiAgentTS/scenarios/qa_llm_generator.py).

```python
def _build_system_prompt(self) -> str:
        return """你是一位工业时序数据分析领域的资深专家，同时也是一位优秀的考试题目出题人。

你的任务是为工业设备的时序监测数据生成高质量的推理问答题（QA对），用于评测大型语言模型对工业时序数据的理解和推理能力。

你需要生成4个层级的问题，每个层级代表不同深度的推理能力：

**L1 - 描述性推理**：考察模型对时序数据整体模式的理解
- 要求模型描述设备运行的全局特征（趋势、波动、周期性、通道间关系）
- 问题应该自然、专业，像运维工程师的日常工作对话
- 答案应详细描述各通道的统计特征和运行模式

**L2 - 定位推理（大海捞针）**：考察模型在长序列中精确定位异常的能力
- 要求模型判断是否存在异常，并精确给出异常的时间步范围
- 这是最核心的能力：在几千甚至上万步的数据中找到占比很小的异常区间
- 答案必须包含精确的时间步范围和异常在各通道上的具体表现

**L3 - 因果推理**：考察模型分析故障根因和多变量关联的能力
- 要求模型分析异常的物理原因，解释传感器间的因果传播路径
- 问题应引导模型进行多步推理（如：温度升高 → 为什么？ → 哪些证据支持？）
- 答案应包含完整的因果链和支撑证据

**L4 - 决策推理**：考察模型给出运维决策建议的能力
- 要求模型基于数据分析结果给出具体的处置建议
- 应包含风险评估、优先级判断、具体措施
- 答案应体现工程师的专业判断

输出格式要求：严格按照JSON数组格式输出，不要包含任何其他内容。
每个QA对包含：level, question, answer, reasoning_chain(推理步骤列表), required_interval(异常区间[start,end]或null)

重要：
- 问题措辞要自然多样，不要使用模板化的句式
- 答案中的数值必须与"实际数据统计"中提供的真实统计量一致。当提供了正常/故障区间的 mean/std/min/max 等数据时，答案中引用的具体数值必须来自这些统计，不得凭空编造
- 因果链要符合物理规律
- 对于正常运行的数据（无故障），也要生成L1、L2（判断无异常）和L4（预防性建议）
- 不要使用英文变量名如 seal_leak，要用自然的中文描述如 密封泄漏
- L1 答案需描述各通道在正常区间和故障区间的统计变化（如"电流从均值50A升至67A"），确保数值准确
- L2 答案的时间步范围必须与注入事件的 time_range 一致
"""
```

## QA generation user prompt

Source: [MultiAgentTS/scenarios/qa_llm_generator.py](../MultiAgentTS/scenarios/qa_llm_generator.py).

```python
def _build_user_prompt(self, metadata: GenerationMetadata,
                           data_profile: Optional[Dict] = None) -> str:
        """构建包含完整元数据 + 实际数据统计的用户提示"""

        # 通道描述
        channel_desc = ""
        for ch in metadata.channels:
            channel_desc += (
                f"  - {ch.name}（{ch.display_name}）：{ch.physical_meaning}，"
                f"单位{ch.unit}，正常范围{ch.normal_range[0]}-{ch.normal_range[1]}{ch.unit}"
            )
            if ch.alarm_threshold:
                channel_desc += f"，报警阈值{ch.alarm_threshold}{ch.unit}"
            channel_desc += "\n"

        # 事件描述
        if metadata.injected_events:
            events_desc = ""
            for i, ev in enumerate(metadata.injected_events):
                events_desc += f"""
事件{i+1}：
  - 类型：{ev.fault_name}
  - 严重程度：{ev.severity}
  - 时间范围：第{ev.time_range[0]}步 到 第{ev.time_range[1]}步
  - 受影响通道：{', '.join(ev.affected_channels)}
  - 参数：{json.dumps(ev.parameters, ensure_ascii=False)}
  - 因果链：
    {'→ '.join(ev.causal_chain)}
  - 描述：{ev.description}
"""
        else:
            events_desc = "  无异常事件，设备全程正常运行。\n"

        # 实际数据统计（来自 data_profile）
        data_stats_section = ""
        if data_profile and "channels" in data_profile:
            data_stats_section = "\n## 实际数据统计（来自真实生成数据，答案数值必须基于以下统计量）\n\n"
            for ch_name, ch_data in data_profile["channels"].items():
                ch_display = ch_name
                for ch in metadata.channels:
                    if ch.name == ch_name:
                        ch_display = f"{ch_name}（{ch.display_name}）"
                        break

                line = f"**{ch_display}**：\n"

                if "normal" in ch_data:
                    ns = ch_data["normal"]
                    line += f"  - 正常区间：均值={ns['mean']}, 标准差={ns['std']}, 范围=[{ns['min']}, {ns['max']}]\n"

                if "fault" in ch_data:
                    fs = ch_data["fault"]
                    line += f"  - 故障区间：均值={fs['mean']}, 标准差={fs['std']}, 范围=[{fs['min']}, {fs['max']}]\n"

                if "change" in ch_data:
                    ch_change = ch_data["change"]
                    affected_tag = " [受影响通道]" if ch_change.get("is_affected") else ""
                    line += f"  - 变化趋势{affected_tag}：{ch_change['description']}\n"

                data_stats_section += line + "\n"

        # 持续时间
        total_seconds = metadata.total_length * metadata.sampling_seconds
        if total_seconds < 3600:
            dur = f"{total_seconds // 60}分钟"
        elif total_seconds < 86400:
            dur = f"{total_seconds / 3600:.1f}小时"
        else:
            dur = f"{total_seconds / 86400:.1f}天"

        prompt = f"""请为以下工业设备的时序监测数据生成高质量的QA对。

## 设备信息

- 设备类型：{metadata.domain_display}
- 场景名称：{metadata.scenario_name}
- 数据总长度：{metadata.total_length}个时间步（约{dur}）
- 采样间隔：{metadata.sampling_rate}
- 传感器通道（{len(metadata.channels)}个）：
{channel_desc}

## 基础运行状态

{metadata.base_description}

## 注入的异常事件

{events_desc}
{data_stats_section}
## 难度信息

- 难度等级：{metadata.difficulty}
- 异常占比：{metadata.needle_ratio:.1%}（异常区间长度 / 总长度）

## 要求

请生成{'5-6' if metadata.injected_events else '3'}个QA对：
- L1（描述性推理）：1个
- L2（定位推理）：1个{'（需要精确定位异常区间）' if metadata.injected_events else '（判断为正常）'}
- L3（因果推理）：{'1-2个（分析故障原因和传播路径）' if metadata.injected_events else '跳过（无异常事件）'}
- L4（决策推理）：1个

⚠️ 重要：答案中的所有数值（均值、变化量、范围等）必须直接来自上面"实际数据统计"中的数值，不得虚构。

请直接输出JSON数组，格式如下：
```json
[
  {{
    "level": "L1",
    "question": "...",
    "answer": "...",
    "reasoning_chain": ["步骤1", "步骤2", ...],
    "required_interval": null
  }},
  ...
]
```"""
        return prompt
```

## Judge system prompt

```text
你是工业时序数据分析领域的资深评估专家。你的任务是对比模型的回答与标准答案，从两个维度进行评判。

## 维度1：方向对齐 (Direction Alignment)
模型的回答在核心结论/判断方向上是否与标准答案一致？

- "aligned"：核心结论完全一致（如都指出了异常、都定位到了正确的时间区间、都给出了相同方向的判断）
- "partial"：大方向正确但细节有偏差（如定位到了异常但时间范围不够精确，或原因分析方向正确但不完整）
- "wrong"：核心结论与标准答案矛盾（如标准答案说有异常但模型说正常，或判断方向完全相反）

## 维度2：答案质量 (1-5分)
综合评估模型回答的质量：

- 5分：覆盖了标准答案的所有关键信息，可能还补充了正确的额外细节。专业、完整、准确。
- 4分：覆盖了大部分关键信息，有少量遗漏但整体回答质量好。
- 3分：覆盖了核心信息，但缺少一些重要细节或数值不够精确。
- 2分：部分相关但遗漏了重要信息，或数值偏差较大。
- 1分：基本不相关或内容大部分错误。

重要规则：
- 如果模型的回答比标准答案更详细，但所有额外内容都是正确的，应给4-5分
- 关注语义等价而非字面匹配
- 时间步定位误差在10%以内视为可接受
- 温度/电流等数值误差在20%以内视为可接受

严格按以下JSON格式输出（不要包含任何其他文字）：
{"direction": "aligned|partial|wrong", "quality": 1-5, "reason": "一句话评判理由"}
```

# Design Template

## Problem

Hệ thống xử lý các câu hỏi nghiên cứu dài, cần thu thập nguồn, rút ra nhận định chính, và viết câu trả lời cuối cùng có thể kiểm chứng.

## Why multi-agent?

Single-agent phù hợp làm baseline nhanh, nhưng dễ trộn lẫn việc tìm nguồn, phân tích, và viết thành một prompt khó debug. Multi-agent tách vai trò để từng bước có output, trace, và failure mode riêng.

## Agent roles

| Agent | Responsibility | Input | Output | Failure mode |
|---|---|---|---|---|
| Supervisor | Chọn route tiếp theo và dừng đúng lúc | Shared state | `route_history` | Loop quá lâu hoặc route sai |
| Researcher | Tìm nguồn và viết research notes | Query, audience, max sources | `sources`, `research_notes` | Nguồn yếu hoặc thiếu citation |
| Analyst | Tổng hợp claim, evidence, open questions | Research notes | `analysis_notes` | Bỏ sót trade-off hoặc đánh giá chứng cứ quá tự tin |
| Writer | Viết câu trả lời cuối cùng | Research notes, analysis notes | `final_answer` | Văn bản thiếu nguồn hoặc quá chung chung |

## Shared state

Shared state gồm `request`, `iteration`, `route_history`, `sources`, `research_notes`, `analysis_notes`, `final_answer`, `agent_results`, `trace`, và `errors`. Các field này đủ để replay luồng chạy, kiểm tra agent nào đã đóng góp gì, và benchmark kết quả.

## Routing policy

Luồng mặc định:

```text
supervisor -> researcher -> supervisor -> analyst -> supervisor -> writer -> supervisor -> done
```

Supervisor ưu tiên bổ sung phần còn thiếu: chưa có source hoặc research notes thì gọi Researcher; chưa có analysis thì gọi Analyst; chưa có final answer thì gọi Writer; đủ output thì dừng.

## Guardrails

- Max iterations: `MAX_ITERATIONS`, mặc định 6.
- Timeout: `TIMEOUT_SECONDS`, mặc định 60 giây cho client thật.
- Retry: OpenAI client retry tối đa 3 lần với exponential backoff.
- Fallback: Không có API key thì dùng mock LLM/search để demo offline.
- Validation: Pydantic schema kiểm tra query, max sources, và metric range.

## Benchmark plan

- Queries: dùng danh sách trong `configs/lab_default.yaml`.
- Metrics: latency, heuristic quality score, source count, agent count, route count, error count.
- Expected outcome: single-agent nhanh hơn; multi-agent có trace tốt hơn và điểm quality cao hơn khi có đủ research, analysis, writer output.

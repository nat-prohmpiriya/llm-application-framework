# LiteLLM Complete Features Reference

> **Last Updated:** December 2024
> **LiteLLM Version:** v1.77.5+
> **Purpose:** รวม Features ทั้งหมดของ LiteLLM พร้อม Use Cases สำหรับ RAG Agent Platform

---

## Table of Contents

1. [LLM Providers](#1-llm-providers)
2. [Embedding Providers](#2-embedding-providers)
3. [Routing & Load Balancing](#3-routing--load-balancing)
4. [Caching](#4-caching)
5. [Virtual Keys & Authentication](#5-virtual-keys--authentication)
6. [Cost Tracking & Budgets](#6-cost-tracking--budgets)
7. [Rate Limiting](#7-rate-limiting)
8. [Guardrails & Safety](#8-guardrails--safety)
9. [MCP Gateway](#9-mcp-gateway)
10. [Observability & Logging](#10-observability--logging)
11. [Batch Processing](#11-batch-processing)
12. [Responses API](#12-responses-api)
13. [Proxy Features](#13-proxy-features)
14. [SDK Features](#14-sdk-features)

---

## 1. LLM Providers

**รองรับ 80+ providers:**

LiteLLM เป็น unified interface ที่ช่วยให้เราเรียก LLM จากหลาย providers ด้วย format เดียวกัน (OpenAI format)

| Category | Providers | คำอธิบาย |
|----------|-----------|----------|
| **Major Cloud** | OpenAI, Azure OpenAI, Google (Vertex AI, AI Studio), Anthropic, AWS (Bedrock, Sagemaker) | Cloud providers หลักที่นิยมใช้ |
| **Fast Inference** | Groq, Together AI, Fireworks AI, DeepInfra, Replicate | เน้นความเร็วสูง latency ต่ำ |
| **Specialized** | Mistral AI, Cohere, Perplexity, xAI (Grok), Deepseek | มีความเชี่ยวชาญเฉพาะด้าน |
| **Enterprise** | Databricks, Snowflake, Oracle Cloud, WatsonX, SambaNova | สำหรับองค์กรขนาดใหญ่ |
| **Open Source/Local** | Ollama, VLLM, LM Studio, Llamafile, Xinference | รันบนเครื่องตัวเอง ไม่ต้องส่งข้อมูลออก |
| **Regional** | OVHCloud, Novita AI, Lambda AI | Providers เฉพาะภูมิภาค |
| **Aggregators** | OpenRouter, HuggingFace | รวม models จากหลาย providers |

**Use Cases สำหรับโปรเจคนี้:**

| Use Case | Providers แนะนำ | เหตุผล |
|----------|-----------------|--------|
| Chat เร็ว | Groq, Gemini Flash | Latency ต่ำ ตอบไว |
| คุณภาพสูงสุด | Claude, GPT-4, Gemini Pro | Reasoning ดี ตอบแม่นยำ |
| ความเป็นส่วนตัว | Ollama, VLLM | ข้อมูลไม่ออกนอกเครื่อง |
| ประหยัดค่าใช้จ่าย | Deepseek, Together AI | ราคาถูกกว่า |

---

## 2. Embedding Providers

**Embedding Models ที่รองรับ:**

Embedding คือการแปลงข้อความเป็น vector สำหรับใช้ใน RAG, semantic search

| Provider | Models | คำอธิบาย |
|----------|--------|----------|
| **OpenAI** | text-embedding-3-small, text-embedding-3-large, ada-002 | มาตรฐานอุตสาหกรรม |
| **Google** | text-embedding-004 (Gemini), textembedding-gecko | ใช้กับ Gemini ecosystem |
| **Cohere** | embed-english-v3.0, embed-multilingual-v3.0 | รองรับหลายภาษา |
| **Voyage AI** | voyage-01, voyage-lite-01 | เน้น retrieval quality |
| **Mistral** | mistral-embed | Mistral ecosystem |
| **NVIDIA** | NV-Embed-QA, Arctic-Embed, BGE-M3 | High performance |
| **Bedrock** | Amazon Titan, Cohere | AWS ecosystem |
| **HuggingFace** | All feature-extraction models | Open source models |

**สถานะโปรเจคปัจจุบัน:**
- ใช้อยู่: `gemini/text-embedding-004` (768 dimensions)
- เก็บใน: pgvector

---

## 3. Routing & Load Balancing

**การกระจาย traffic และจัดการ failover:**

Routing ช่วยให้ระบบมี high availability และประหยัดค่าใช้จ่าย

**Routing Strategies:**

| Strategy | คำอธิบาย | เหมาะกับ |
|----------|----------|----------|
| **simple-shuffle** | สุ่มเลือกตาม weight (DEFAULT) | Production ทั่วไป |
| **rate-limit-aware-v2** | เลือก deployment ที่ใช้ TPM น้อยสุด | Traffic สูง |
| **latency-based** | เลือก model ที่ตอบเร็วที่สุด | Real-time apps |
| **least-busy** | เลือกที่มี concurrent requests น้อยสุด | กระจาย load เท่ากัน |
| **cost-based** | เลือก model ถูกที่สุดก่อน | ประหยัดค่าใช้จ่าย |
| **custom** | เขียน logic เอง | ความต้องการพิเศษ |

**Reliability Features:**

| Feature | คำอธิบาย |
|---------|----------|
| **Fallbacks** | สลับ provider อัตโนมัติเมื่อ fail (เช่น Gemini -> Groq) |
| **Cooldowns** | พัก deployment ที่ fail ชั่วคราว |
| **Retries** | ลองใหม่แบบ fixed หรือ exponential backoff |
| **Pre-call checks** | ตรวจสอบ context window, region ก่อนเรียก |
| **Max parallel** | จำกัด concurrent requests ต่อ deployment |
| **Alerting** | แจ้งเตือน Slack/webhook เมื่อ fail |

**ตัวอย่าง Config:**
```yaml
router_settings:
  routing_strategy: "usage-based-routing"
  fallbacks: [{"gemini-2.0-flash": ["groq/llama-3.3-70b"]}]
  num_retries: 3          # ลองใหม่ 3 ครั้ง
  retry_after: 5          # รอ 5 วินาทีก่อนลองใหม่
  allowed_fails: 3        # fail 3 ครั้งถึง cooldown
  cooldown_time: 60       # พัก 60 วินาที
```

**Use Cases สำหรับโปรเจค:**
- [ ] High availability: Gemini fail -> ใช้ Groq แทน
- [ ] ประหยัด: ใช้ model ถูกก่อน แพงเป็น fallback
- [ ] Rate limit: สลับ provider อัตโนมัติเมื่อโดน limit

---

## 4. Caching

**การ cache response เพื่อลด latency และค่าใช้จ่าย:**

| Type | คำอธิบาย | เหมาะกับ |
|------|----------|----------|
| **In-Memory** | Cache ในหน่วยความจำ (default) | Development |
| **Redis** | Distributed cache | Production |
| **Redis Semantic** | Cache ตาม similarity ของ prompt | RAG dedup |
| **Qdrant Semantic** | Vector similarity cache | Advanced RAG |
| **S3** | เก็บบน AWS | Long-term storage |
| **GCS** | เก็บบน Google Cloud | Long-term storage |
| **Azure Blob** | เก็บบน Azure | Long-term storage |
| **Disk** | เก็บบน local file | Offline use |

**Cache Controls:**

| Control | คำอธิบาย |
|---------|----------|
| `no-cache` | ไม่ใช้ cached response |
| `no-store` | ไม่ cache response นี้ |
| `ttl` | กำหนดเวลาหมดอายุ (วินาที) |
| `s-maxage` | รับเฉพาะ cache ที่ใหม่กว่า |

**Semantic Caching:**
- ใช้ embedding หา prompt ที่คล้ายกัน
- Similarity threshold: 0-1
- ถ้าคล้ายเกิน threshold -> คืน cached response
- ประหยัดค่า API เยอะมากสำหรับคำถามซ้ำๆ

**Use Cases สำหรับโปรเจค:**
- [ ] Redis cache สำหรับ query ซ้ำ
- [ ] Semantic cache สำหรับคำถาม RAG คล้ายกัน
- [ ] ลด embedding API calls

---

## 5. Virtual Keys & Authentication

**ระบบจัดการ API keys และ access control:**

Virtual Keys ช่วยให้เราสร้าง API key ให้ user/team แยกกัน พร้อม track usage

| Feature | คำอธิบาย |
|---------|----------|
| **Virtual Keys** | สร้าง API key ให้แต่ละ user/team |
| **Teams** | รวม users เป็นกลุ่ม แชร์ budget |
| **Key Rotation** | เปลี่ยน key อัตโนมัติหรือ manual |
| **Model Aliases** | Map ชื่อ model (เช่น "gpt-4" -> "gemini-2.0-flash") |
| **Block/Unblock** | เปิด/ปิด key |
| **Custom Headers** | ใช้ header อื่นแทน Authorization |

**โครงสร้างองค์กร:**
```
Organization (บริษัท)
  └── Teams (ทีม - แชร์ budget)
        └── Users (ผู้ใช้ - track แยก)
              └── Keys (API keys)
```

**API Endpoints:**
- `POST /key/generate` - สร้าง key ใหม่
- `GET /key/info` - ดูข้อมูล key
- `POST /key/block` - ปิดการใช้งาน key
- `POST /key/unblock` - เปิดการใช้งาน key
- `POST /key/delete` - ลบ key

**Use Cases สำหรับโปรเจค:**
- [ ] สร้าง key ให้แต่ละ user
- [ ] สร้าง team สำหรับแต่ละ project
- [ ] Track spend แยกตาม team

---

## 6. Cost Tracking & Budgets

**ระบบติดตามค่าใช้จ่ายและกำหนด budget:**

**Tracking Levels:**

| Level | คำอธิบาย |
|-------|----------|
| **Per Key** | Track ค่าใช้จ่ายแต่ละ API key |
| **Per User** | รวมค่าใช้จ่ายต่อ user |
| **Per Team** | Budget ระดับ team |
| **Per Tag** | Tag แบบ custom (เช่น ตาม feature) |
| **Per Model** | แยกตาม model ที่ใช้ |

**Budget Controls:**

| Feature | คำอธิบาย |
|---------|----------|
| **Max Budget** | วงเงินสูงสุด (hard limit) |
| **Budget Duration** | รอบ reset (รายวัน/รายเดือน) |
| **Soft Limit** | เตือนที่ 80% (ไม่ block) |
| **Temporary Boost** | เพิ่มวงเงินชั่วคราว |

**API Endpoints:**
- `GET /spend/logs` - ดู logs ค่าใช้จ่ายละเอียด
- `GET /spend/keys` - ค่าใช้จ่ายแยกตาม key
- `GET /spend/users` - ค่าใช้จ่ายแยกตาม user
- `GET /spend/teams` - ค่าใช้จ่ายแยกตาม team
- `GET /spend/tags` - ค่าใช้จ่ายแยกตาม tag

**Use Cases สำหรับโปรเจค:**
- [ ] Dashboard แสดงค่าใช้จ่ายแต่ละ user
- [ ] แจ้งเตือนเมื่อใช้ 80% ของ budget
- [ ] Block เมื่อถึง limit
- [ ] รายงานค่าใช้จ่ายรายเดือน

---

## 7. Rate Limiting

**การจำกัด request เพื่อป้องกัน abuse:**

| Type | คำอธิบาย |
|------|----------|
| **TPM** | Tokens per minute (จำกัด tokens) |
| **RPM** | Requests per minute (จำกัดจำนวน request) |
| **Per Key** | Limit ต่อ API key |
| **Per User** | Limit ต่อ user |
| **Per Team** | Limit ต่อ team |
| **Per Model** | Limit ต่อ model |

**Features เด่น:**
- Multi-instance tracking แม่นยำ (v1.72+)
- ใช้ Redis สำหรับ distributed limiting
- 0 spillover ที่ 250 RPS

**ตัวอย่าง Config:**
```yaml
general_settings:
  master_key: sk-xxx
  database_url: postgresql://...

litellm_settings:
  max_budget: 100        # USD ต่อเดือน
  budget_duration: monthly
```

**Use Cases สำหรับโปรเจค:**
- [ ] จำกัด free users 100 requests/วัน
- [ ] จำกัด tokens เพื่อป้องกัน abuse
- [ ] Limit ต่างกันตาม tier (Free/Pro/Enterprise)

---

## 8. Guardrails & Safety

**ระบบป้องกันและกรองเนื้อหา:**

| Guardrail | คำอธิบาย |
|-----------|----------|
| **Azure Content Safety** | Content moderation จาก Microsoft |
| **Prompt Injection** | ตรวจจับ jailbreak attempts |
| **PII Scrubbing** | ลบข้อมูลส่วนตัว (ชื่อ, เบอร์โทร, บัตรประชาชน) |
| **Custom Rules** | เขียน validation เอง |

**Modes:**
- `pre_call` - ตรวจก่อนส่งไป LLM
- `during_call` - ตรวจขณะ streaming
- `post_call` - ตรวจ response

**ตัวอย่าง Config:**
```yaml
guardrails:
  - guardrail_name: "azure-content-safety"
    litellm_params:
      guardrail: azure_content_safety
      mode: "during_call"
      api_key: os.environ/AZURE_KEY

  - guardrail_name: "pii-masking"
    litellm_params:
      guardrail: presidio
      mode: "pre_call"
```

**เปรียบเทียบกับ Presidio:**

| Feature | LiteLLM Guardrails | Presidio |
|---------|-------------------|----------|
| Setup | ง่าย (config) | ซับซ้อน (code) |
| Thai PII | ไม่รองรับ | รองรับ (custom) |
| Streaming | รองรับ | ต้อง buffer |
| Cost | ฟรี หรือมี Azure cost | ฟรี |

**แนะนำ:** ใช้ LiteLLM Guardrails + Presidio (สำหรับ Thai PII) ร่วมกัน

**Use Cases สำหรับโปรเจค:**
- [ ] Block prompt injection
- [ ] Mask PII ภาษาไทย (ใช้ Presidio)
- [ ] Content moderation

---

## 9. MCP Gateway

**Model Context Protocol - เชื่อมต่อ external tools:**

MCP เป็น protocol มาตรฐานสำหรับให้ LLM เรียกใช้ tools ภายนอก

| Feature | คำอธิบาย |
|---------|----------|
| **Unified Endpoint** | Gateway เดียวสำหรับทุก tools |
| **OAuth 2.0** | Authentication แบบ secure |
| **Permission Control** | กำหนดสิทธิ์ระดับ Key/Team/Org |
| **OpenAPI -> MCP** | แปลง OpenAPI spec เป็น MCP tools อัตโนมัติ |
| **Namespace Servers** | Client เลือก MCP server ได้ |

**Supported Transports:**
- Streamable HTTP
- Server-Sent Events (SSE)
- Standard I/O (stdio)

**Use Cases สำหรับโปรเจค:**
- [ ] web_search tool ผ่าน MCP
- [ ] sql_query tool ผ่าน MCP
- [ ] เชื่อมต่อ External APIs

---

## 10. Observability & Logging

**ระบบ monitoring และ logging:**

| Category | Integrations | คำอธิบาย |
|----------|--------------|----------|
| **AI Platforms** | Langfuse, LangSmith, Lunary, Helicone | เน้น LLM observability |
| **Tracing** | OpenTelemetry, Traceloop, Arize, Phoenix | Distributed tracing |
| **Monitoring** | DataDog, Sentry, PostHog | General monitoring |
| **ML Ops** | MLflow, Weights & Biases, Comet | ML experiment tracking |
| **Cloud** | Google Cloud Storage, Azure Blob | Log storage |
| **Other** | Slack, Prometheus, Greenscale | Alerts & metrics |

**Callback Types:**
- `input_callbacks` - ก่อนเรียก LLM
- `success_callbacks` - เมื่อสำเร็จ
- `failure_callbacks` - เมื่อ error

**ตัวอย่าง Config:**
```yaml
litellm_settings:
  success_callback: ["langfuse", "prometheus"]
  failure_callback: ["slack", "sentry"]
```

**Use Cases สำหรับโปรเจค:**
- [ ] Langfuse สำหรับ tracing LLM calls
- [ ] Prometheus metrics
- [ ] Slack alerts เมื่อ error

---

## 11. Batch Processing

**การประมวลผลแบบ batch:**

| Feature | คำอธิบาย |
|---------|----------|
| Batch embedding | ส่ง embeddings หลายรายการพร้อมกัน |
| Batch completion | ส่ง completions หลายรายการพร้อมกัน |
| Input-based rate limiting | จำกัดตาม input size |
| Async processing | ประมวลผลแบบ asynchronous |

**Use Cases สำหรับโปรเจค:**
- [ ] Bulk document embedding (upload หลายไฟล์)
- [ ] Batch summarization
- [ ] Parallel RAG queries

---

## 12. Responses API

**Unified API format สำหรับทุก provider:**

| Feature | คำอธิบาย |
|---------|----------|
| Unified OpenAI format | ใช้ format เดียวกันทุก provider |
| Consistent output | Response structure เหมือนกัน |
| Structured outputs | JSON schema validation (Claude 4.5+) |
| Multi-modal | รองรับ image, audio |

**Providers ที่รองรับ:**
- Anthropic (Claude)
- Google (Gemini)
- Groq
- และ providers อื่นๆ ทั้งหมด

**Use Cases สำหรับโปรเจค:**
- [ ] เขียน code ที่ไม่ผูกกับ provider
- [ ] เปลี่ยน model ง่าย
- [ ] JSON schema validation

---

## 13. Proxy Features

**Features สำหรับ Admin:**

| Feature | คำอธิบาย |
|---------|----------|
| **Admin UI** | Web dashboard สำหรับจัดการ |
| **Health Check** | `/health` endpoint |
| **Model List** | `/v1/models` ดู models ทั้งหมด |
| **Audit Logs** | Track การเปลี่ยนแปลง key/team |
| **SSO** | Login ผ่าน Microsoft, Google, Okta |
| **SCIM** | สร้าง user อัตโนมัติจาก identity provider |

**Performance (v1.77.5):**
- 54% RPS เพิ่มขึ้น (1,040 -> 1,602 RPS)
- 50% P99 latency ลดลงเมื่อใช้ Redis
- 50ms overhead ที่ 250 RPS

**Deployment Options:**
- Docker
- Docker Compose
- Kubernetes (Helm)
- AWS/GCP/Azure

---

## 14. SDK Features

**Python SDK Functions:**

| Function | คำอธิบาย |
|----------|----------|
| `completion()` | Chat completion (sync) |
| `acompletion()` | Chat completion (async) |
| `embedding()` | Generate embeddings |
| `image_generation()` | Generate images |
| `transcription()` | Audio to text |
| `text_to_speech()` | Text to audio |

**Exception Handling:**
- Unified exceptions (OpenAI format)
- Retry logic built-in
- Timeout handling

---

## Implementation Priority สำหรับโปรเจค

### Phase 1: Quick Wins (ทำได้เลย)

| Feature | Effort | Impact | Status |
|---------|--------|--------|--------|
| Fallback config | LOW | HIGH | [ ] |
| Usage logging | LOW | HIGH | [ ] |
| Redis caching | LOW | MEDIUM | [ ] |
| เพิ่ม models ใหม่ | LOW | MEDIUM | [ ] |

### Phase 2: Core Features

| Feature | Effort | Impact | Status |
|---------|--------|--------|--------|
| Virtual keys per user | MEDIUM | HIGH | [ ] |
| Cost tracking dashboard | MEDIUM | HIGH | [ ] |
| Rate limiting per user | MEDIUM | HIGH | [ ] |
| Budget alerts | MEDIUM | MEDIUM | [ ] |

### Phase 3: Advanced

| Feature | Effort | Impact | Status |
|---------|--------|--------|--------|
| MCP gateway | HIGH | HIGH | [ ] |
| Guardrails | MEDIUM | HIGH | [ ] |
| Semantic caching | HIGH | MEDIUM | [ ] |
| Langfuse tracing | MEDIUM | MEDIUM | [ ] |

---

## Mapping กับ Project Phases

| Project Phase | LiteLLM Features |
|---------------|------------------|
| Phase 3: PII Protection | Guardrails + Presidio |
| Phase 5: sql_query tool | MCP Gateway |
| Phase 6: Advanced Tools | MCP + Batch API |
| Phase 7: Usage Tracking | Cost Tracking + Virtual Keys + Rate Limiting |

---

## สถานะการใช้งานปัจจุบัน

**ใช้อยู่แล้ว:**
- [x] LiteLLM Proxy (port 4000)
- [x] Chat completion (`/chat/completions`)
- [x] Streaming
- [x] Embedding (`gemini/text-embedding-004`)
- [x] User parameter สำหรับ tracking

**ยังไม่ได้ใช้:**
- [ ] Fallback routing
- [ ] Redis caching
- [ ] Virtual keys
- [ ] Cost tracking API
- [ ] Rate limiting
- [ ] Guardrails
- [ ] MCP
- [ ] Observability callbacks

---

## References

- [LiteLLM Docs](https://docs.litellm.ai/)
- [Providers](https://docs.litellm.ai/docs/providers)
- [Routing](https://docs.litellm.ai/docs/routing)
- [Caching](https://docs.litellm.ai/docs/caching/all_caches)
- [Virtual Keys](https://docs.litellm.ai/docs/proxy/virtual_keys)
- [Cost Tracking](https://docs.litellm.ai/docs/proxy/cost_tracking)
- [Guardrails](https://docs.litellm.ai/docs/proxy/guardrails)
- [MCP](https://docs.litellm.ai/docs/mcp)
- [Callbacks](https://docs.litellm.ai/docs/observability/callbacks)
- [Release Notes](https://docs.litellm.ai/release_notes)
- [GitHub](https://github.com/BerriAI/litellm)

---

*Document synced with LiteLLM v1.77.5 (December 2025)*

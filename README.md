# 🎬 English-Translator v2.5.0

### BLUE JEANS PICTURES — 6-Stage Native Polish Pipeline

한국어 시나리오를 **네이티브 수준의 영문 시나리오**로 변환하는 AI 번역 엔진.  
단순 번역이 아닌, **번역체 제거 → 문체 리라이팅 → 대사 현지화 → 품질 검증 → 최종 정리**까지 6단계 파이프라인을 실행합니다.

---

## 🚀 핵심 특징

### 6-Stage Pipeline

| Stage | 이름 | 모델 | 역할 |
|-------|------|------|------|
| **1** | Raw Translation | Sonnet | 한국어 → 영어 충실한 직역 |
| **2** | Format Conversion | 규칙 기반 | 한국 시나리오 포맷 → 할리우드/BBC/국제 포맷 변환 |
| **3** | Voice Rewrite | Opus | 번역체 제거, 네이티브 영어 시나리오 문체로 리라이팅 |
| **4** | Dialogue Polish | Opus | 캐릭터별 대사 현지화, 톤 태그 적용 |
| **5** | QA Check | Sonnet | 포맷/일관성/언어/스토리 검증 + 점수화 리포트 |
| **6** | Final Revision | Sonnet | QA 지적 중 서식·표기 통일만 자동 반영 → 최종 원고 |

### 4개 타겟 지역

| 지역 | 포맷 | 특징 |
|------|------|------|
| 🇺🇸 **US** | 쿨리 포맷 (US Letter) | American English, em dash, 호칭 평탄화 |
| 🇬🇧 **UK** | BBC 스타일 (A4) | British English, hyphen, 클래스 기반 격식 |
| 🇮🇩 **Indonesia** | 국제 포맷 (A4) | Mas/Mbak/Pak/Bu 호칭 보존, 문화 용어 유지 |
| 🇻🇳 **Vietnam** | 국제 포맷 (A4) | anh/chị/em 호칭 보존, VND, 베트남어 문장 생성 금지 (v2.5.0) |

### 두 가지 작업 유형 (v2.5.0)

| 유형 | 원고 | 설정 | 결과 |
|------|------|------|------|
| **A. 현지화** | 한국 무대 한국 시나리오 | 타겟 지역 Vietnam · 무대 보존 **끔** | 서울 → 호찌민, 한국 인물 → 베트남 인물, 제사 → giỗ |
| **B. 무대 보존** | 이미 베트남 무대인 한·베 공동제작 원고 | **공동제작 — 무대 보존 켬** | 호찌민은 호찌민, 서울 장면은 서울, 언어만 영어로 |

- 무대 보존 체크박스는 자동으로 켜지지 않습니다. 원고에서 `(베트남어)` 표기가 감지되면 켜기를 권장하는 안내만 표시합니다.
- 무대 보존 모드에서는 원래 지역 규칙(LOCALIZATION_RULES) 대신 무대 보존 규칙이 들어가고, AP-8(문화 등가물 치환)은 "문화 요소 보존"으로 바뀝니다.

### 캐릭터 톤 태그

| 태그 | 용도 | 예시 |
|------|------|------|
| `formal` | 교수, 재벌, 법조인 | 완전한 문장, 축약 없음, 격식 어휘 |
| `casual` | 일반인, 직장인, 친구 | 자연스러운 축약, 중간 길이, 편안한 톤 |
| `street` | 조폭, 범죄자, 10대 | 단문, 슬랭, 문법 파괴, 지역별 분기 |

---

## 🌐 대사 언어 표기 변환 (v2.5.0)

Writer Engine v4.1.0 원고의 언어 표기를 영문 시나리오 관례로 옮깁니다. 표기가 있는 원고에만 적용됩니다.

| 한국어 원고 | 영문 원고 |
|-------------|-----------|
| 괄호 없음 | 괄호 없음 (첫 페이지 노트로 1회 고지) |
| `(베트남어)` | `(in Vietnamese)` — 캐릭터 큐 아래 별도 줄 |
| `(베트남어, 작게)` | `(in Vietnamese, quietly)` |
| `(영어)` | `(in English)` — 생략 금지, 서툰 영어는 그대로 서툴게 |
| `[문자 · 베트남어] '…'` | `ON SCREEN — TEXT MESSAGE (IN VIETNAMESE): "…"` |
| `INSERT — … · 베트남어` | `INSERT — TEXT MESSAGE (IN VIETNAMESE)` … `BACK TO SCENE` |

- 베트남어 문장은 생성하지 않습니다. 대사는 영어로만 씁니다.
- Stage 1·3·4·6은 페이지마다 언어 괄호 수를 원고와 대조합니다. 다르면 1회 재시도하고, 그래도 다르면 저장하지 않습니다.
- 첫 페이지 노트: 무대 보존 → `NOTE: Unless otherwise noted, dialogue is spoken in Korean. Non-English dialogue is subtitled.` / 베트남 현지화 → `… spoken in Vietnamese.`

---

## 👤 인물 이름 (v2.5.0)

- **무대 보존**: 한글 음차(린, 투안)는 원어로 정확히 되돌릴 수 없습니다. 대조표에 원어 표기를 넣어 주세요. 대조표에 없는 이름은 실행 전에 목록으로 안내합니다.
- **베트남 현지화**: "베트남 이름 후보 만들기" 버튼으로 이름을 한 번에 정하고, 표에서 고친 뒤 확정하면 Stage 1~6에 대조표처럼 적용됩니다. CSV로 저장해 다음 작업에 다시 쓸 수 있습니다.
- 대조표에 없는 베트남 이름은 성조 부호 없이 씁니다(LINH, TUAN). 검수 화면에서 `Tuan` ↔ `Tuấn` 혼용을 찾아 줍니다.

```csv
한국이름,영어이름,톤태그
민수,MINSU,casual
린,LINH,casual
투안,TUAN,formal
호찌민,Ho Chi Minh City,
```

> 베트남 공안 인물은 `투안 → TUAN`처럼 이름만 매핑할 것을 권장합니다. 원문에 없는 직급(DETECTIVE 등)은 붙이지 않습니다.

---

## 📁 파일 구조

```
english-translator/
├── main.py          # Streamlit UI + 파이프라인 오케스트레이션
├── prompt.py        # 6단계 시스템 프롬프트 + 지역/톤/스타일/무대 보존 룰셋
├── requirements.txt # 의존성 패키지
├── .streamlit/
│   └── config.toml  # 라이트 모드 테마 설정
│   └── secrets.toml # API 키 (로컬 전용, git 제외)
└── README.md
```

---

## ⚙️ 설치 및 실행

### 로컬 실행

```bash
# 1. 클론
git clone https://github.com/cinepark-1974/english-translator.git
cd english-translator

# 2. 의존성 설치
pip install -r requirements.txt

# 3. API 키 설정
mkdir -p .streamlit
echo 'ANTHROPIC_API_KEY = "sk-ant-your-key-here"' > .streamlit/secrets.toml

# 4. 실행
streamlit run main.py
```

### Streamlit Cloud 배포

1. GitHub에 push
2. [share.streamlit.io](https://share.streamlit.io) 에서 앱 생성
3. Secrets에 `ANTHROPIC_API_KEY` 추가
4. 배포 완료

---

## 📋 requirements.txt

```
streamlit>=1.30.0
anthropic>=0.40.0
python-docx>=1.1.0
pymupdf>=1.24.0
openpyxl
```

---

## 🎛️ 파이프라인 모드

| 모드 | 실행 단계 | 용도 | 예상 비용 |
|------|----------|------|----------|
| **🚀 Full Pipeline** | 1→2→3→4→5→6 | 최종 제출용. 최고 품질 | ~$15–25 |
| **⚡ Quick Translation** | 1→2 | 초벌 확인용. 빠르고 저렴 | ~$3–5 |
| **✍️ Rewrite Only** | 3→4 | 이미 번역된 시나리오 폴리시 | ~$10–18 |
| **🔍 QA Only** | 5 | 완성된 영문 시나리오 검증 | ~$0.5–1 |

> 비용은 120페이지 기준 추정치입니다.

---

## 🔧 번역체 안티패턴 룰셋 (Stage 3)

| 코드 | 이름 | Bad → Good |
|------|------|------------|
| AP-1 | 감정 직접 서술 | "She is angry" → "She slams the folder shut" |
| AP-2 | 수동태 과다 | "is opened by" → "throws the door open" |
| AP-3 | 주어 반복 | "She stands. She walks. She looks." → "She stands. Crosses to the window." |
| AP-4 | 설명적 지문 | "showing that he is depressed" → "Takeout containers. Unopened mail." |
| AP-5 | 대사 필러 | "I think that we should probably" → "We should go" |
| AP-6 | 한국어 문장 리듬 | 긴 수식어 체인 → 짧고 끊어치는 영어 리듬 |
| AP-7 | 비트 중복 | "She pauses. A beat. She takes a moment." → "A beat." |
| AP-8 | 문화적 직역 | 라면 = 외로움 → 타겟 문화권 등가물 (무대 보존 모드: 문화 요소 그대로 보존) |
| AP-9 | 지문 길이 초과 | 3줄 이상 → 분할 |

---

## 🌏 지역별 문화 코드 변환 예시 (현지화 모드)

| 한국 원문 | 🇺🇸 US | 🇬🇧 UK | 🇮🇩 Indonesia | 🇻🇳 Vietnam |
|----------|---------|---------|--------------|-------------|
| 회식 | team dinner / work drinks | work do / drinks after work | makan-makan | nhậu / team dinner |
| PC방 | gaming café | internet café | warnet | internet café (quán net) |
| 편의점 | convenience store / bodega | corner shop | minimarket / Indomaret | Circle K / FamilyMart / WinMart+ |
| 제사 | — | — | — | giỗ (가정 제단 bàn thờ, 향) |
| 형/오빠 | (first name) / bro | (first name) / mate | Mas / Bang / Kak | anh |
| 누나/언니 | (first name) / sis | (first name) | Mbak / Kak | chị |
| -씨 | Mr./Ms. or first name | Mr./Ms. or surname | Pak/Bu / Mas/Mbak | anh/chị + 이름 |
| 선배 | senior / first name | first name | Senior / Kak | anh/chị + 이름 |

> 베트남은 2025년 7월 1일부터 군·구(district) 단위를 폐지하고 phường(ward)·xã(commune) 체계로 바뀌었습니다. 현재 배경의 원고는 ward 또는 동네 이름을 씁니다. 대사에서 "District 1"이라고 부르는 것은 일상 표현으로 허용합니다.

---

## 🧹 입력 안전망 (v2.5.0)

입력 원고에 Writer 엔진 메타 블록이 섞여 있으면 번역 전에 제거하고 화면에 알립니다.

`<LOCAL_VERIFY>` · `<RATING_CHECK>` · `<WRITER_NOTES_BEGIN>…<WRITER_NOTES_END>` · `[MARKET_LENS_BEGIN]…[MARKET_LENS_END]`

---

## 📊 듀얼 모델 정책

- **Sonnet**: 번역(Stage 1), QA(Stage 5), 최종 정리(Stage 6), 베트남 이름 후보
- **Opus**: Voice Rewrite(Stage 3), Dialogue Polish(Stage 4)

Stage 2(Format Conversion)는 규칙 기반이므로 API 호출 없이 즉시 처리됩니다.

---

## 🔁 호환성

| 입력·설정 | 엔진 동작 |
|-----------|-----------|
| 무대 보존 끔 + 언어 표기 없음 + US/UK/Indonesia | v2.4.0과 프롬프트 동일 |
| 무대 보존 끔 + 언어 표기 있음 | 언어 표기 규칙만 추가 작동, 이식은 기존대로 |
| 무대 보존 켬 | 무대 보존 규칙 · 이름 규칙 · AP-8 보존 작동 |
| 기존 대조표 CSV/TXT/XLSX · 세션 백업 JSON | 형식 변경 없음, 그대로 사용 |

---

## 📝 라이선스

BLUE JEANS PICTURES 내부 프로덕션 도구.  
Powered by Anthropic Claude API.

---

<p align="center">
  <strong>BLUE JEANS PICTURES</strong><br>
  <em>YOUNG · VINTAGE · FREE · INNOVATIVE</em>
</p>

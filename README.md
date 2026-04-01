# 🎬 English-Translator v2.0

### BLUE JEANS PICTURES — 5-Stage Native Polish Pipeline

한국어 시나리오를 **네이티브 수준의 영문 시나리오**로 변환하는 AI 번역 엔진.  
단순 번역이 아닌, **번역체 제거 → 문체 리라이팅 → 대사 현지화 → 품질 검증**까지 5단계 파이프라인을 자동 실행합니다.

---

## 🚀 핵심 특징

### 5-Stage Pipeline

| Stage | 이름 | 모델 | 역할 |
|-------|------|------|------|
| **1** | Raw Translation | Sonnet | 한국어 → 영어 충실한 직역 |
| **2** | Format Conversion | 규칙 기반 | 한국 시나리오 포맷 → 할리우드/BBC/국제 포맷 변환 |
| **3** | Voice Rewrite | Opus | 번역체 제거, 네이티브 영어 시나리오 문체로 리라이팅 |
| **4** | Dialogue Polish | Opus | 캐릭터별 대사 현지화, 톤 태그 적용 |
| **5** | QA Check | Sonnet | 포맷/일관성/언어/스토리 검증 + 점수화 리포트 |

### 3개 타겟 지역

| 지역 | 포맷 | 특징 |
|------|------|------|
| 🇺🇸 **US** | 쿨리 포맷 (US Letter) | American English, em dash, 호칭 평탄화 |
| 🇬🇧 **UK** | BBC 스타일 (A4) | British English, hyphen, 클래스 기반 격식 |
| 🇮🇩 **Indonesia** | 국제 포맷 (A4) | Mas/Mbak/Pak/Bu 호칭 보존, 문화 용어 유지 |

### 캐릭터 톤 태그

| 태그 | 용도 | 예시 |
|------|------|------|
| `formal` | 교수, 재벌, 법조인 | 완전한 문장, 축약 없음, 격식 어휘 |
| `casual` | 일반인, 직장인, 친구 | 자연스러운 축약, 중간 길이, 편안한 톤 |
| `street` | 조폭, 범죄자, 10대 | 단문, 슬랭, 문법 파괴, 지역별 분기 |

---

## 📁 파일 구조

```
english-translator/
├── main.py          # Streamlit UI + 파이프라인 오케스트레이션 (1,212줄)
├── prompt.py        # 5단계 시스템 프롬프트 + 지역/톤/스타일 룰셋 (738줄)
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
```

---

## 🎛️ 파이프라인 모드

| 모드 | 실행 단계 | 용도 | 예상 비용 |
|------|----------|------|----------|
| **🚀 Full Pipeline** | 1→2→3→4→5 | 최종 제출용. 최고 품질 | ~$15–25 |
| **⚡ Quick Translation** | 1→2 | 초벌 확인용. 빠르고 저렴 | ~$3–5 |
| **✍️ Rewrite Only** | 3→4 | 이미 번역된 시나리오 폴리시 | ~$10–18 |
| **🔍 QA Only** | 5 | 완성된 영문 시나리오 검증 | ~$0.5–1 |

> 비용은 120페이지 기준 추정치입니다.

---

## 👤 인물표 (Character Map)

### CSV 형식 (3번째 열: 톤 태그 — 선택)

```csv
한국이름,영어이름,톤태그
정섬,DETECTIVE JUNG,casual
김회장,CHAIRMAN KIM,formal
독수리,EAGLE,street
이수연,SUYEON LEE,casual
```

### TXT 형식

```
정섬 → DETECTIVE JUNG → casual
김회장 → CHAIRMAN KIM → formal
독수리 → EAGLE → street
```

톤 태그를 CSV에 넣지 않아도 UI에서 수동으로 설정할 수 있습니다.

---

## 🔧 번역체 안티패턴 룰셋 (Stage 3)

Voice Rewrite 단계에서 자동으로 감지·교정하는 번역체 패턴 9가지:

| 코드 | 이름 | Bad → Good |
|------|------|------------|
| AP-1 | 감정 직접 서술 | "She is angry" → "She slams the folder shut" |
| AP-2 | 수동태 과다 | "is opened by" → "throws the door open" |
| AP-3 | 주어 반복 | "She stands. She walks. She looks." → "She stands. Crosses to the window." |
| AP-4 | 설명적 지문 | "showing that he is depressed" → "Takeout containers. Unopened mail." |
| AP-5 | 대사 필러 | "I think that we should probably" → "We should go" |
| AP-6 | 한국어 문장 리듬 | 긴 수식어 체인 → 짧고 끊어치는 영어 리듬 |
| AP-7 | 비트 중복 | "She pauses. A beat. She takes a moment." → "A beat." |
| AP-8 | 문화적 직역 | 라면 = 외로움 → 타겟 문화권 등가물 |
| AP-9 | 지문 길이 초과 | 3줄 이상 → 분할 |

---

## 🌏 지역별 문화 코드 변환 예시

| 한국 원문 | 🇺🇸 US | 🇬🇧 UK | 🇮🇩 Indonesia |
|----------|---------|---------|--------------|
| 회식 | team dinner / work drinks | work do / drinks after work | makan-makan |
| PC방 | gaming café | internet café | warnet |
| 편의점 | convenience store / bodega | corner shop | minimarket / Indomaret |
| 형/오빠 | (first name) / bro | (first name) / mate | Mas / Bang / Kak |
| 누나/언니 | (first name) / sis | (first name) | Mbak / Kak |
| -씨 | Mr./Ms. or first name | Mr./Ms. or surname | Pak/Bu / Mas/Mbak |
| 선배 | senior / first name | first name | Senior / Kak |

---

## 📊 듀얼 모델 정책

- **Sonnet**: 번역(Stage 1), QA(Stage 5) — 정확도와 속도의 균형
- **Opus**: Voice Rewrite(Stage 3), Dialogue Polish(Stage 4) — 창의적 리라이팅에 최고 품질 필수

Stage 2(Format Conversion)는 규칙 기반이므로 API 호출 없이 즉시 처리됩니다.

---

## 🗺️ 로드맵

### v2.1 (예정)
- [ ] 단계별 중간 저장 / 이어하기 기능
- [ ] 소설(Novel) 번역 모드 추가
- [ ] 스트리밍 출력 (타임아웃 방지)

### v2.5 (예정)
- [ ] 캐릭터 speech pattern 풀 프로필 (교육수준/나이/지역/성격)
- [ ] 타겟 지역 확장: 말레이시아, 싱가포르, 필리핀
- [ ] 대사 비교 뷰 (원문 vs 번역 나란히)

### v3.0 (예정)
- [ ] 자동 캐릭터 분석 (톤 태그 자동 추천)
- [ ] 역번역 검증 (English → Korean back-translation QA)
- [ ] 소설 챕터 단위 번역 파이프라인

---

## 📝 라이선스

BLUE JEANS PICTURES 내부 프로덕션 도구.  
Powered by Anthropic Claude API.

---

<p align="center">
  <strong>BLUE JEANS PICTURES</strong><br>
  <em>YOUNG · VINTAGE · FREE · INNOVATIVE</em>
</p>

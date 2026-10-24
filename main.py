"""
BLUE JEANS PICTURES — English-Translator
한국어 시나리오 → 영어 번역 (5-Stage Native Polish Pipeline)
Powered by Anthropic Claude API

Pipeline:
  Stage 1: Raw Translation (Sonnet) — 충실한 직역
  Stage 2: Format Conversion (Rule-based) — 포맷 변환
  Stage 3: Voice Rewrite (Opus) — 번역체 제거, 네이티브 문체
  Stage 4: Dialogue Polish (Opus) — 대사 현지화
  Stage 5: QA Check (Sonnet) — 품질 검증 리포트

─────────────────────────────────────────────
CHANGELOG (최신이 위)
─────────────────────────────────────────────
v2.5.0 (2026-10-24)
  - 기능 추가: 베트남 시장 대응 — 두 가지 작업 유형
    A. 현지화: 한국 무대 원고 → 베트남 이식 (타겟 지역 Vietnam, 무대 보존 끔)
    B. 무대 보존: 이미 베트남 무대인 한·베 공동제작 원고 (무대 보존 켬)
  - SETTINGS — "공동제작 — 무대 보존" 체크박스 (자동으로 켜지지 않음, 작가 선택)
  - 언어 표기 — (베트남어)·(영어)·· 베트남어 표기 감지 시
    · 감지 안내 + 무대 보존 권장 안내
    · Stage 1·3·4·6 페이지마다 언어 괄호 수 대조 (불일치 시 재시도 → 저장 안 함)
    · 신설: count_lang_tags_ko() / count_lang_tags_en() / check_language_tags()
  - 대조표에 없는 한글 인물명 사전 점검 — find_unmapped_korean_names()
    · 무대 보존: 베트남 인물 원어 표기 입력 안내 (실행은 막지 않음)
    · 베트남 현지화: 베트남 이름 후보 1회 생성 → 표에서 수정 → 대조표에 고정
      (페이지마다 다른 이름이 붙는 문제 방지) — parse_vn_name_candidates()
  - 메타 블록 제거 — strip_meta_blocks()
    <LOCAL_VERIFY> <RATING_CHECK> <WRITER_NOTES_BEGIN> [MARKET_LENS_BEGIN]
  - LOCALIZATION AUDIT — 무대 보존 모드에서 한국 지명·원화·문화어 패턴 점검 끔,
    언어 괄호 씬별 대조표, 이름 성조 부호 혼용 점검 check_name_diacritics()
  - Stage 2 — 화면 텍스트 "· Vietnamese" 잔존 → "(IN VIETNAMESE)" 정규식 치환
  - DOCX — 대사와 같은 줄에 붙은 언어 괄호를 Parenthetical 줄로 분리
  - FINAL OUTPUT — 언어 표기가 있는 원고에 첫 페이지 노트 1회 삽입
    ("Unless otherwise noted, dialogue is spoken in …")
  - 세션 백업 — 무대 보존 설정·베트남 이름 확정본 저장/복구

v2.4.0 (2026-10-04)
  - 기능 추가: STAGE 6 — Final Revision (QA 자동 반영 → 최종 원고)
    ① normalize_layout() — 규칙 기반 정리(왼쪽 정렬 통일, -- → —, 빈 줄 정리) · 무료
    ② 표기 통일 기준표 1회 작성 (장소명·씬 헤딩·용어·시각·트랜지션)
    ③ 페이지별 기계적 수정 — 허용 F1~F9만, 대사 표현·설정 수정 금지
       · 기등장 인물 목록을 페이지마다 전달 (대문자 재표기 해제)
       · 검사 모드 "fix": 분량 90~115% · 씬 헤딩 유지 · 고정 대사 보존 확인
       · v2.3.0 이어하기·자동 재시도 그대로 적용
  - 최종 DOCX/TXT·검수·완료 배너가 Stage 6 결과 기준으로 동작
  - 진행 배지 6단계(번역·포맷·문체·대사·QA·최종), 백업 진행도 N/6
  - Stage 5를 다시 돌리면 Stage 6 결과·기준표 자동 초기화

v2.3.2 (2026-10-04)
  - 기능 개선: 완료 상태를 한눈에 표시
    · PIPELINE 상단 진행 배지(번역·포맷·문체·대사·QA) + 배너
      진행 중: "⏳ 진행 중 — N/5 단계 완료 · 다음 할 일"
      완료:   "✅ 번역 완료 · 원작 씬 N개 전부 번역 · 최종 원고 N자 · QA 점수 · 판정"
    · 각 단계 제목 옆 "✅ 완료" 표시
    · FINAL OUTPUT 상단에도 완료 배너
  - 신설: parse_qa_summary() / pipeline_status() / render_status_board() / stage_title()

v2.3.1 (2026-10-04)
  - Stage 5 QA 길이 한도 초과 수정 — prompt.py MODEL_POLICY·STAGE_5 지침 변경
    (main.py 코드 변경 없음, 변경 기록만 추가)

v2.3.0 (2026-10-04)
  - 완결성 검사 신설 — 페이지마다 씬 누락(S# 번호 대조)·분량 부족 검사
    실패 시 1회 자동 재시도, 재실패 시 저장하지 않고 사유 표시
    (v2.2.2 이전 Stage 1에서 각 페이지 뒷부분이 잘려 씬 절반이 사라진 사고 방지)
  - 이어하기 — 완료된 페이지를 세션·백업 JSON에 보관, 실패 지점부터 재개
  - 앞 단계를 다시 실행하면 뒤 단계 결과 자동 초기화 (낡은 결과 혼입 방지)
  - 원고가 바뀌었는데 이전 결과가 남아 있으면 경고
  - Stage 5 QA — 원고 전체 검토 (앞뒤 1만5천 자만 보내던 방식 폐기 →
    '[...중간 생략...]' 오탐 제거), 원작 씬 수를 함께 전달
  - API 일시 오류 자동 재시도 5회 (make_client)
  - 대조표 파서 개선 (parse_translation_workbook)
    · 약칭 열과 영문 대사 헤드 열 혼동 수정 (만복 → 만복 같은 한→한 매핑 제거)
    · 영문이 없는 매핑 폐기
    · '화면 텍스트·소품' '수치·단위 환산' 시트 → 현지화 항목
    · '핵심 대사 고정 번역' 시트 → fixed_lines / '말투 지침' 시트 → voice_notes
    · 약칭이 용어와 겹치면(교주) 용어 매핑 우선
  - UI — 대조표 집계에 고정 대사·말투 지침 추가, 확인 탭 추가
  - 검수 — 고정 대사 반영 여부, 제작사 오표기(Blue Gene) 탐지 추가

v2.2.3 (2026-10-04)
  - 버그 수정: Stage 5 QA 리포트 빈 결과 저장 → 백업 진행도 4/5 표기 문제
  - call_api(): 응답 종료 사유 검사 신설
    · 본문 없음(사고만 하고 종료) → 오류
    · max_tokens 도달로 본문 절단 → 오류 (잘린 번역문 저장 방지)
    · refusal(응답 거부) → 오류
  - 단계별 max_tokens를 prompt.py MODEL_POLICY에서 받아 사용
    (기존 하드코딩 8,000 / Stage 5 4,000 → 32,000 / 16,000)

v2.2.2 (2026-10-04)
  - 버그 수정: 퇴역 모델 ID로 인한 API 404 오류 — prompt.py MODEL_POLICY 교체
    (main.py 코드 변경 없음, 변경 기록만 추가)

v2.2.1 (2026-10-04)
  - 버그 수정: 톤 태그 수동 설정 화면 StreamlitDuplicateElementKey 오류
    · 원인: 서로 다른 한국명이 같은 영문명으로 매핑될 때
      (약칭→대사 헤드, 장로1·2·3 → ELDER 1 / 2 / 3 등)
      같은 key의 선택 상자가 중복 생성됨
    · 수정: 영문명 기준으로 중복을 걸러 한 번만 표시

v2.2 (2026-09-16)
  - 로컬라이징 대조표(XLSX) 업로드 지원
    · 다중 시트 자동 인식 (주요 인물 / 조·단역 / 지명·기관명)
    · 헤더명 자동 매칭 (한국명·영문명·v1 오표기·톤태그)
  - loc_map(extras/places/corrections)을 Stage 1·3·4 프롬프트에 강제 주입
  - Stage 5 QA에 매핑 원본 동봉 → 미적용 항목 지적
  - 신설: apply_glossary_enforcement() — v1 오표기 영문 강제 치환
  - 신설: check_glossary_residue() — 한국 고유 요소 잔존 검수 리포트
  - 신설 UI: 🔎 LOCALIZATION AUDIT 섹션
  - 세션 백업에 loc_map 포함

v2.1 (2026-06-04)
  - 프로젝트 세션 백업 (JSON 중간 저장/불러오기)

v2.0
  - 5-Stage Native Polish Pipeline 최초 구성
"""

import streamlit as st
import anthropic
import re
import io
import csv
import json
import time
from datetime import datetime

from prompt import (
    ENGINE_VERSION,
    ENGINE_BUILD_DATE,
    REGION_PROFILES,
    STYLE_PRESETS,
    CHARACTER_TONE_TAGS,
    MODEL_POLICY,
    STAGE_2_FORMAT_RULES,
    build_stage1_prompt,
    build_stage3_prompt,
    build_stage4_prompt,
    build_stage5_prompt,
    build_stage6_style_prompt,   # ★ v2.4.0
    build_stage6_fix_prompt,     # ★ v2.4.0
    build_vn_name_suggest_prompt,  # ★ v2.5.0
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title=f"English-Translator | BLUE JEANS PICTURES",
    page_icon="🎬",
    layout="wide",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

/* ── Global background ── */
.stApp {
    background-color: #F7F7F5 !important;
}

/* ── Main Header ── */
.main-header {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
}
.main-header .brand-name {
    font-size: 0.85rem;
    color: #191970;
    letter-spacing: 0.35em;
    font-weight: 600;
    margin-bottom: 0.3rem;
}
.main-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: #191970;
    margin: 0.2rem 0 0;
    letter-spacing: 0.02em;
    display: inline-block;
    border-bottom: 4px solid #f5c842;
    padding-bottom: 0.3rem;
}
.main-header .tagline {
    font-size: 0.78rem;
    color: #999;
    letter-spacing: 0.3em;
    margin-top: 0.7rem;
    font-weight: 400;
}
.main-header .version-badge {
    display: inline-block;
    background: #191970;
    color: #f5c842;
    font-size: 0.7rem;
    padding: 0.15rem 0.6rem;
    border-radius: 10px;
    margin-top: 0.5rem;
    letter-spacing: 0.1em;
    font-weight: 600;
}

/* ── Section headers (yellow bar) ── */
.section-header {
    background: #f5c842;
    color: #191970;
    padding: 0.5rem 1.1rem;
    border-radius: 6px;
    font-weight: 700;
    font-size: 0.95rem;
    margin: 1.5rem 0 0.8rem 0;
    letter-spacing: 0.03em;
}

/* ── Stage indicator ── */
.stage-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 700;
    margin: 0.3rem 0.2rem;
    letter-spacing: 0.02em;
}
.stage-active {
    background: #191970;
    color: #f5c842;
}
.stage-done {
    background: #2ecc71;
    color: #fff;
}
.stage-pending {
    background: #ddd;
    color: #999;
}

/* ── ★ v2.3.2 완료 배너 ── */
.done-banner {
    background: #E8F7EE;
    border: 2px solid #2ecc71;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin: 0.6rem 0 1rem 0;
}
.done-banner .big {
    font-size: 1.45rem;
    font-weight: 800;
    color: #1E8449;
    letter-spacing: 0.02em;
}
.done-banner .sub {
    font-size: 0.92rem;
    color: #333;
    margin-top: 0.35rem;
    line-height: 1.6;
}
.progress-banner {
    background: #EEEEF6;
    border: 2px solid #191970;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin: 0.6rem 0 1rem 0;
}
.progress-banner .big {
    font-size: 1.15rem;
    font-weight: 800;
    color: #191970;
}
.progress-banner .sub {
    font-size: 0.88rem;
    color: #444;
    margin-top: 0.3rem;
}
.verdict-pass { color: #1E8449; font-weight: 700; }
.verdict-minor { color: #B7950B; font-weight: 700; }
.verdict-major { color: #C0392B; font-weight: 700; }

/* ── Result box ── */
.result-box {
    background: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1.2rem;
    font-family: 'Courier New', monospace;
    font-size: 0.88rem;
    line-height: 1.7;
    white-space: pre-wrap;
    max-height: 600px;
    overflow-y: auto;
}

/* ── QA Report box ── */
.qa-box {
    background: #FFFEF5;
    border: 2px solid #f5c842;
    border-radius: 8px;
    padding: 1.2rem;
    font-family: 'Courier New', monospace;
    font-size: 0.85rem;
    line-height: 1.6;
    white-space: pre-wrap;
    max-height: 500px;
    overflow-y: auto;
}

/* ── Page chip ── */
.page-chip {
    display: inline-block;
    background: #191970;
    color: #f5c842;
    padding: 0.2rem 0.7rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

/* ── Character map table ── */
.char-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.5rem 0;
    font-size: 0.85rem;
}
.char-table th {
    background: #191970;
    color: #f5c842;
    padding: 0.45rem 0.8rem;
    text-align: left;
    font-weight: 600;
}
.char-table td {
    padding: 0.4rem 0.8rem;
    border-bottom: 1px solid #e8e8e0;
}
.char-table tr:nth-child(even) td {
    background: #EEEEF6;
}

/* ── Pipeline info box ── */
.pipeline-info {
    background: #EEEEF6;
    border-left: 4px solid #191970;
    padding: 0.8rem 1rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.85rem;
    margin: 0.5rem 0;
    color: #333;
}

/* ── Cost estimate ── */
.cost-chip {
    display: inline-block;
    background: #FFF8E1;
    color: #8B6914;
    padding: 0.2rem 0.7rem;
    border-radius: 10px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid #f5c842;
}

/* ── Progress ── */
.progress-text {
    text-align: center;
    color: #666;
    font-size: 0.85rem;
    padding: 0.5rem 0;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #bbb;
    font-size: 0.72rem;
    margin-top: 2.5rem;
    padding: 1rem 0;
    border-top: 1px solid #ddd;
    letter-spacing: 0.08em;
}

/* ── Streamlit overrides ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: #fff !important;
    border-color: #ddd !important;
}
div[data-testid="stFileUploader"] {
    background-color: #fff !important;
    border-radius: 8px;
}
.stExpander {
    background-color: #fff !important;
    border-color: #ddd !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
MAX_CHARS_PER_PAGE = 8000
VERSION = ENGINE_VERSION  # prompt.py 단일 출처 — 버전 표기 일원화

# ═══════════════════════════════════════════════════
# ★ v2.1 — 프로젝트 세션 백업 (JSON 저장/불러오기)
# 단계 중단 시 그 시점까지의 원고·결과 전체를 JSON으로 저장하고,
# 불러오면 멈춘 지점부터 그대로 이어서 진행할 수 있게 한다.
# ═══════════════════════════════════════════════════

# 백업 대상 키 — 원고 입력 + 5단계 결과 전체
# (타겟 지역/장르/지시사항/인물표는 실행 시 위젯에서 다시 읽는 구조라 제외.
#  파일 업로드 원고도 텍스트 변환 후 세션에 남지 않아 제외 — 결과는 복원됨.)
_BACKUP_KEYS = [
    # 원고 입력
    "project_title", "paste_pages",
    # 5단계 번역 결과
    "stage_1_result", "stage_2_result", "stage_3_result",
    "stage_4_result", "stage_5_result",
    # ★ v2.4.0 — Stage 6 최종 수정본 · 스타일 시트
    "stage_6_result", "stage_6_style_sheet", "partial_stage_6",
    # ★ v2.2 — 로컬라이징 매핑 (대조표 재업로드 없이 복구)
    "saved_char_map", "saved_char_tones", "saved_loc_map",
    # ★ v2.3.0 — 원고 식별·씬 수 · 단계별 이어하기 보관분
    "source_sig", "source_scene_count",
    "partial_stage_1", "partial_stage_3", "partial_stage_4",
    # ★ v2.5.0 — 무대 보존 설정 · 베트남 이름 확정본 · 원고 언어 표기 감지 여부
    "saved_preserve_setting", "vn_name_overrides", "lang_tags_detected",
]


def export_session_backup() -> bytes:
    """현재 세션 상태(원고 + 단계 결과)를 JSON bytes로 직렬화한다."""
    session = {k: st.session_state.get(k) for k in _BACKUP_KEYS}

    # 붙여넣기 페이지(paste_page_0, paste_page_1 ...)는 동적 키라 따로 수집
    pages = {}
    page_count = st.session_state.get("paste_pages", 1) or 1
    for i in range(page_count):
        key = f"paste_page_{i}"
        if key in st.session_state:
            pages[key] = st.session_state.get(key, "")
    session["_paste_pages_data"] = pages

    # 진행도 계산 (완료된 단계 수 / 6) — ★ v2.4.0 Stage 6 포함
    done = sum(
        1 for k in [
            "stage_1_result", "stage_2_result", "stage_3_result",
            "stage_4_result", "stage_5_result", "stage_6_result",
        ]
        if st.session_state.get(k)
    )

    payload = {
        "_meta": {
            "engine_version": ENGINE_VERSION,
            "build_date": ENGINE_BUILD_DATE,
            "saved_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "title": st.session_state.get("project_title", "") or "Untitled",
            "stage_progress": f"{done}/6",
        },
        "session": session,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def import_session_backup(raw_bytes: bytes) -> dict:
    """백업 JSON bytes를 받아 세션에 복원한다. 복원된 메타 정보 dict를 반환한다."""
    raw = raw_bytes.decode("utf-8")
    data = json.loads(raw)

    session_data = data.get("session", {})
    meta = data.get("_meta", {})

    # 일반 키 복원
    for k in _BACKUP_KEYS:
        if k in session_data:
            st.session_state[k] = session_data[k]

    # 붙여넣기 페이지 본문 복원
    pages = session_data.get("_paste_pages_data", {})
    if isinstance(pages, dict):
        for key, val in pages.items():
            st.session_state[key] = val

    # ★ v2.5.0 — 무대 보존 체크박스는 이미 화면에 그려진 위젯이라 지금 값을 바꿀 수 없다.
    #   다음 실행에서 체크박스를 그리기 직전에 반영하도록 예약만 해 둔다.
    if "saved_preserve_setting" in session_data:
        st.session_state["_pending_preserve"] = bool(session_data.get("saved_preserve_setting"))

    return meta


def make_backup_filename(title: str, done_count: int) -> str:
    """백업 파일명 생성 — 제목/진행도/시각 포함."""
    base = (title or "Untitled").strip()[:30]
    for ch in '<>:"/\\|?*':
        base = base.replace(ch, "_")
    base = base.replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    return f"TranslateEngine_{base}_{done_count}of6_{ts}.json"


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

# ═══════════════════════════════════════════════════
# ★ v2.2 — LOCALIZATION WORKBOOK (XLSX 대조표)
# ═══════════════════════════════════════════════════

# 시트 분류 키워드 (시트명에 포함되면 해당 분류)
# ★ v2.3.0 — 판정 순서: 고정 대사 → 말투 지침 → 조·단역 → 현지화 항목 → 인물
_SHEET_FIXED_KEYS = ["고정", "핵심 대사", "핵심대사", "locked", "fixed"]
_SHEET_VOICE_KEYS = ["말투", "보이스", "voice", "어투", "화법"]
_SHEET_EXTRAS_KEYS = ["단역", "조역", "조연", "extra", "minor", "bit"]
_SHEET_PLACES_KEYS = ["지명", "기관", "장소", "용어", "명칭", "법률", "place", "location", "term",
                      # ★ v2.3.0 — 화면 텍스트·소품 / 수치·단위 시트도 현지화 항목으로 분류
                      "화면", "소품", "텍스트", "자막", "prop", "insert",
                      "수치", "단위", "환산", "통화", "unit", "currency"]

# 헤더 컬럼 인식 키워드
_COL_KO_KEYS = ["한국명", "한국이름", "한국판", "한국어", "원문", "korean", "국문"]
_COL_EN_KEYS = ["영문명", "영어이름", "영문판", "english", "영문"]
_COL_WRONG_KEYS = ["v1", "수정 전", "수정전", "오표기", "before"]
_COL_TONE_KEYS = ["톤", "tone"]
_COL_SHORT_KEYS = ["약칭", "short"]        # 극중 축약 호칭 (석훈, 도현 …)
_COL_CUE_KEYS = ["대사 헤드", "대사헤드", "cue", "헤드"]  # 대사 헤드 표기 (EARL …)
_COL_SPEAKER_KEYS = ["화자", "인물", "speaker", "character"]   # ★ v2.3.0
_COL_SCENE_KEYS = ["씬", "scene"]                              # ★ v2.3.0
_COL_NOTE_KEYS = ["비고", "note", "메모"]                      # ★ v2.3.0

_HANGUL_RE = re.compile(r"[가-힣]")


def _has_latin(s: str) -> bool:
    return bool(re.search(r"[A-Za-z]", s or ""))


def _pick_cue_column(headers: list, exclude: set) -> int:
    """영문 대사 헤드 열을 찾는다. (v2.3.0)

    '약칭 (대사 헤드)'처럼 한국어 약칭 열에도 '대사 헤드'가 들어가는 경우가 있어,
    약칭 열은 제외하고 '영/english/en'이 들어간 헤더를 우선한다.
    일본어 대사 헤드 열('대사 헤드 (일)')은 제외한다.
    """
    best, best_score = -1, -1
    for idx, h in enumerate(headers):
        if idx in exclude:
            continue
        hn = _norm_header(h)
        if not hn or not any(_norm_header(k) in hn for k in _COL_CUE_KEYS):
            continue
        if "(일)" in hn or "일본" in hn or "japan" in hn or "약칭" in hn:
            continue
        score = 1
        if "(영)" in hn or "영문" in hn or "english" in hn or "(en)" in hn:
            score += 2
        if score > best_score:
            best, best_score = idx, score
    return best


def _norm_header(v) -> str:
    return str(v or "").strip().lower().replace(" ", "")


def _pick_column(headers: list, keys: list, exclude_keys: list = None) -> int:
    """헤더 리스트에서 키워드에 맞는 컬럼 인덱스를 찾는다. 없으면 -1."""
    exclude_keys = exclude_keys or []
    best = -1
    best_score = -1
    for idx, h in enumerate(headers):
        hn = _norm_header(h)
        if not hn:
            continue
        if any(_norm_header(x) in hn for x in exclude_keys):
            continue
        for k in keys:
            if _norm_header(k) in hn:
                # '확정' / 'v2' 가 붙은 열을 우선한다
                score = 1
                if "확정" in hn:
                    score += 2
                if "v2" in hn:
                    score += 1
                if score > best_score:
                    best_score = score
                    best = idx
    return best


def _clean_term(v, strip_kr_note: bool = False) -> str:
    """셀 값을 문자열로 정리한다.

    strip_kr_note=True 이면 영문 값 뒤에 붙은 한글 괄호 주석을 제거한다.
    예) "MAJOR CRIMES INVESTIGATION BUREAU (단일화)" → "MAJOR CRIMES INVESTIGATION BUREAU"
    """
    if v is None:
        return ""
    t = str(v).strip()
    if t in {"—", "-", "–", "N/A", "n/a", "없음", "변경 없음"}:
        return ""
    if strip_kr_note:
        t = re.sub(r"\s*\((?=[^)]*[가-힣])[^)]*\)", "", t).strip()
    return t


def _split_variants(text: str) -> list:
    """'A / B, C (4종 혼용)' 같은 셀을 개별 표기로 분해한다.

    콤마는 숫자 자릿점($100,000,000)에도 쓰이므로,
    콤마로 잘린 조각은 충분히 길고 알파벳을 포함할 때만 채택한다.
    """
    if not text:
        return []

    # 한글 괄호 주석 제거
    t = re.sub(r"\s*\((?=[^)]*[가-힣])[^)]*\)", " ", text)

    out = []
    for chunk in re.split(r"\s*/\s*", t):          # 1차: 슬래시
        chunk = chunk.strip(" .·\t")
        if not chunk:
            continue
        if "," in chunk:                            # 2차: 콤마 (보수적)
            pieces = [p.strip(" .·\t") for p in chunk.split(",")]
            safe = [
                p for p in pieces
                if len(p) >= 8 and re.search(r"[A-Za-z]{3,}", p)
            ]
            candidates = safe if len(safe) >= 2 else [chunk]
        else:
            candidates = [chunk]

        for p in candidates:
            p = p.strip(" .·\t")
            if len(p) >= 4 and re.search(r"[A-Za-z]{3,}", p) and p not in out:
                out.append(p)
    return out


def _flexible_pattern(term: str) -> "re.Pattern":
    """표기 차이를 흡수하는 검색 패턴을 만든다. (v2.2)

    번역 결과물은 아포스트로피( ' vs ’ ), 대시( - vs – vs — ), 줄바꿈 공백이
    대조표와 다르게 나오는 경우가 많다. 그 차이 때문에 치환이 누락되지 않도록
    해당 문자들을 유연하게 매칭한다.
    """
    esc = re.escape(term)
    esc = re.sub(r"\\?['’‘`´]", "['’‘`´]", esc)
    esc = re.sub(r"\\?[-–—−]", "[-–—−]", esc)
    esc = re.sub(r"(?:\\\s|\s)+", r"\\s+", esc)
    return re.compile(esc, re.IGNORECASE)


def _is_safe_correction(bad: str, good: str) -> bool:
    """기계 치환해도 안전한 교정쌍인지 판정한다.

    - 같은 표기면 제외
    - 확정 표기가 오표기를 포함하면 제외 (재귀 치환·부분 일치 사고 방지)
      예) "Los Angeles" → "Los Angeles / Las Vegas"
    - 숫자·기호만으로 이뤄진 조각 제외
    """
    if not bad or not good:
        return False
    b, g = bad.strip(), good.strip()
    if b.lower() == g.lower():
        return False
    if b.lower() in g.lower():
        return False
    if not re.search(r"[A-Za-z]{3,}", b):
        return False
    # 확정 표기가 여러 표기의 묶음이면(예: "Los Angeles / Las Vegas")
    # 1:1 대응이 성립하지 않으므로 기계 치환에서 제외한다.
    # (프롬프트에는 places 항목으로 이미 전달된다)
    if "/" in g:
        return False
    return True


def _match_char_name(name: str, char_map: dict) -> str:
    """'서광명 목사' 같은 표기를 인물표의 영문명으로 연결한다. (v2.3.0)"""
    name = (name or "").strip()
    if not name:
        return ""
    if name in char_map:
        return char_map[name]
    compact = name.replace(" ", "")
    # 긴 한국명부터 비교해 부분 일치 오매칭을 줄인다
    for ko in sorted(char_map.keys(), key=len, reverse=True):
        k = ko.replace(" ", "")
        if len(k) >= 2 and (k in compact or compact in k):
            return char_map[ko]
    return ""


def parse_translation_workbook(uploaded_file):
    """XLSX 로컬라이징 대조표를 파싱한다. (v2.2 → v2.3.0 확장)

    반환: (char_map, char_tones, loc_map)
      char_map  : {한국명/약칭: 영문명}        — 주요 등장인물
      char_tones: {영문명: tone}              — 톤 태그 열이 있을 때
      loc_map   : {
            "extras":      {한국명: 영문명},                 # 조·단역
            "places":      {한국어 원문: 확정 영문},          # 지명·기관·용어·화면 텍스트·수치
            "corrections": {v1 오표기 영문: 확정 영문},
            "fixed_lines": [{"scene","speaker","ko","en"}],  # ★ v2.3.0 핵심 대사 고정 번역
            "voice_notes": {인물 표기: 영문판 말투 지침},     # ★ v2.3.0 말투 지침
        }

    ★ v2.3.0 수정
      - 약칭 열과 영문 대사 헤드 열을 혼동하던 문제 수정 (만복 → 만복 같은 한→한 매핑 제거)
      - 한국어 → 한국어 매핑, 영문 칸에 영문이 없는 매핑은 버린다
      - 고정 대사 / 말투 지침 시트를 인물표로 잘못 읽던 문제 수정
    """
    try:
        import openpyxl
    except ImportError:
        raise RuntimeError("openpyxl이 설치되어 있지 않습니다. requirements.txt를 확인하세요.")

    data = uploaded_file.read()
    uploaded_file.seek(0)
    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)

    char_map, char_tones = {}, {}
    loc_map = {"extras": {}, "places": {}, "corrections": {},
               "fixed_lines": [], "voice_notes": {}}
    pending_voice = []   # 인물표를 다 읽은 뒤 영문명과 연결
    short_keys = set()   # 약칭으로 추가된 키

    for ws in wb.worksheets:
        sheet_name = str(ws.title).lower()

        if any(k in sheet_name for k in _SHEET_FIXED_KEYS):
            bucket = "fixed_lines"
        elif any(k in sheet_name for k in _SHEET_VOICE_KEYS):
            bucket = "voice_notes"
        elif any(k in sheet_name for k in _SHEET_EXTRAS_KEYS):
            bucket = "extras"
        elif any(k in sheet_name for k in _SHEET_PLACES_KEYS):
            bucket = "places"
        else:
            bucket = "characters"

        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            continue

        # 헤더 행 탐색 (앞 5행 안에서 KO/EN 열이 모두 잡히는 행)
        header_idx, headers = -1, []
        for i, row in enumerate(rows[:5]):
            cand = list(row)
            ko_i = _pick_column(cand, _COL_KO_KEYS)
            en_i = _pick_column(cand, _COL_EN_KEYS, exclude_keys=_COL_WRONG_KEYS)
            if ko_i >= 0 and en_i >= 0:
                header_idx, headers = i, cand
                break
        if header_idx < 0:
            continue

        ko_i = _pick_column(headers, _COL_KO_KEYS)
        en_i = _pick_column(headers, _COL_EN_KEYS, exclude_keys=_COL_WRONG_KEYS)
        data_rows = rows[header_idx + 1:]

        def _cell(row, i, strip=False):
            return _clean_term(row[i], strip_kr_note=strip) if (i >= 0 and len(row) > i) else ""

        # ── ★ v2.3.0 고정 대사 시트 ──
        if bucket == "fixed_lines":
            sp_i = _pick_column(headers, _COL_SPEAKER_KEYS)
            sc_i = _pick_column(headers, _COL_SCENE_KEYS)
            for row in data_rows:
                if not row:
                    continue
                ko, en = _cell(row, ko_i), _cell(row, en_i)
                if ko and en and _has_latin(en):
                    loc_map["fixed_lines"].append({
                        "scene": _cell(row, sc_i),
                        "speaker": _cell(row, sp_i),
                        "ko": ko,
                        "en": en,
                    })
            continue

        # ── ★ v2.3.0 말투 지침 시트 ──
        if bucket == "voice_notes":
            sp_i = _pick_column(headers, _COL_SPEAKER_KEYS)
            note_i = _pick_column(headers, _COL_NOTE_KEYS)
            for row in data_rows:
                if not row:
                    continue
                who, en = _cell(row, sp_i), _cell(row, en_i)
                if who and en:
                    note = _cell(row, note_i)
                    pending_voice.append((who, en + (f" — {note}" if note else "")))
            continue

        tone_i = _pick_column(headers, _COL_TONE_KEYS)
        short_i = _pick_column(headers, _COL_SHORT_KEYS)
        cue_i = _pick_cue_column(headers, exclude={short_i, ko_i, en_i})

        # v1 오표기 열: 'v1 대비 변경'(설명문)과 'v1 영문판'(표기)을 구분한다.
        # 반드시 '영문/english'가 함께 들어있는 헤더만 인정.
        wrong_i = -1
        for idx, h in enumerate(headers):
            hn = _norm_header(h)
            if not hn or idx == en_i:
                continue
            if any(_norm_header(k) in hn for k in _COL_WRONG_KEYS) and \
               ("영문" in hn or "english" in hn):
                wrong_i = idx
                break

        for row in data_rows:
            if not row or len(row) <= max(ko_i, en_i):
                continue
            ko = _clean_term(row[ko_i])
            en = _clean_term(row[en_i], strip_kr_note=True)
            if not ko or not en:
                continue
            # ★ v2.3.0 — 영문 칸에 영문이 없거나 한국어 그대로인 매핑은 버린다
            if ko == en or not _has_latin(en):
                continue

            if bucket == "characters":
                char_map[ko] = en

                # 약칭(만복) → 영문 대사 헤드(WALT). 영문 대사 헤드가 없으면 영문명.
                cue = _cell(row, cue_i, strip=True)
                if not _has_latin(cue) or _HANGUL_RE.search(cue):
                    cue = ""
                short = _cell(row, short_i)
                if short and short != ko and short not in char_map and not _has_latin(short):
                    char_map[short] = cue or en
                    short_keys.add(short)

                if tone_i >= 0 and len(row) > tone_i:
                    tone = _clean_term(row[tone_i]).lower()
                    if tone in CHARACTER_TONE_TAGS:
                        char_tones[en] = tone
            else:
                loc_map[bucket][ko] = en

            # v1 오표기 → 확정 영문 (교정 매핑)
            if wrong_i >= 0 and len(row) > wrong_i:
                wrong_raw = _clean_term(row[wrong_i])
                for variant in _split_variants(wrong_raw):
                    if _is_safe_correction(variant, en):
                        loc_map["corrections"][variant] = en

    # 약칭이 용어 시트에도 있으면(예: 교주 → ELIAS / 교주 → the Prophet)
    # 지문·대사 속 호칭은 용어 쪽(the Prophet)이 맞으므로 약칭 매핑을 뺀다.
    # 정식 한국명(박성광 → PROPHET ELIAS BRIGHT)은 그대로 남는다.
    for ko in list(loc_map["places"].keys()):
        if ko in short_keys:
            char_map.pop(ko, None)
        elif ko in char_map:
            del loc_map["places"][ko]

    # 말투 지침을 영문 인물명에 연결
    for who, note in pending_voice:
        en_name = _match_char_name(who, char_map)
        label = f"{en_name} ({who})" if en_name else who
        loc_map["voice_notes"][label] = note

    return char_map, char_tones, loc_map


def count_loc_entries(loc_map: dict) -> int:
    """loc_map 총 항목 수."""
    if not loc_map:
        return 0
    return sum(len(v or {}) for v in loc_map.values())


def apply_glossary_enforcement(text: str, loc_map: dict) -> tuple:
    """번역 결과에 남은 '이전 판 오표기 영문'을 확정 표기로 강제 치환한다. (v2.2)

    한국어 → 영문 치환은 문맥 판단이 필요하므로 여기서 다루지 않는다.
    영문 → 영문(오표기 → 확정) 치환만 기계적으로 수행하므로 안전하다.

    반환: (치환된 텍스트, [(오표기, 확정, 횟수), ...])
    """
    if not text or not loc_map:
        return text, []

    corrections = loc_map.get("corrections") or {}
    if not corrections:
        return text, []

    log = []
    placeholders = {}

    # 1단계: 긴 표기부터 플레이스홀더로 치환한다.
    #        (A→B, B→C 가 동시에 있을 때 연쇄 치환되는 사고를 막는다)
    for i, bad in enumerate(sorted(corrections.keys(), key=len, reverse=True)):
        good = corrections[bad]
        pattern = _flexible_pattern(bad)
        found = len(pattern.findall(text))
        if found:
            token = f"\x00BJP{i}\x00"
            text = pattern.sub(token, text)
            placeholders[token] = good
            log.append((bad, good, found))

    # 2단계: 플레이스홀더를 확정 표기로 되돌린다.
    for token, good in placeholders.items():
        text = text.replace(token, good)

    return text, log


# 한국 고유 요소 잔존 탐지 패턴
_RESIDUE_PATTERNS = [
    (r"[가-힣]+", "한글 원문 잔존"),
    (r"\b\w+-(?:gu|dong|si|ro|gil)\b", "행정구역 로마자 (-gu/-dong/-si/-ro/-gil)"),
    (r"\b(?:Sejong|Gangnam|Nowon|Jongno|Yeouido|Itaewon|Hongdae|Myeongdong)\b", "한국 지명 로마자"),
    (r"\b\d[\d,\.]*\s*(?:won|WON|₩)\b", "원화 표기"),
    (r"\$[\d,]+\s*WON", "통화 혼용 오류 ($...WON)"),
    (r"\b(?:20\d\d)-?(?:GoHap|고합)", "한국식 사건번호"),
    (r"\b(?:Kimchi|Soju|Hanbok|Chuseok|Seollal)\b", "미현지화 문화어"),
    (r"\bBlue\s*Gene\b|\bBluejeans?\b(?!\s*PICTURES)", "제작사 표기 오류 (BLUE JEANS PICTURES)"),  # ★ v2.3.0
]

# ★ v2.5.0 — 무대 보존 모드에서는 한국 장면의 한국 요소가 정상이므로 끄는 패턴
#   (한글 원문 잔존·통화 혼용·사건번호·제작사 표기는 어떤 모드에서도 점검)
_RESIDUE_SKIP_IN_PRESERVE = {
    "행정구역 로마자 (-gu/-dong/-si/-ro/-gil)",
    "한국 지명 로마자",
    "원화 표기",
    "미현지화 문화어",
}


def check_glossary_residue(text: str, char_map: dict, loc_map: dict,
                           preserve_setting: bool = False) -> dict:
    """번역 결과에 한국 고유 요소·미적용 매핑이 남아있는지 검수한다. (v2.2)

    반환: {
        "unapplied": [(한국어, 목표 영문, 분류)],   # 한국어 원문이 그대로 남은 항목
        "missing":   [(한국어, 목표 영문, 분류)],   # 목표 영문이 한 번도 안 나온 항목
        "residue":   [(라벨, 샘플[:8], 총 건수)],   # 패턴 기반 잔존
        "corrections_left": [(오표기, 확정, 건수)],
    }
    """
    result = {"unapplied": [], "missing": [], "residue": [], "corrections_left": []}
    if not text:
        return result

    buckets = [("주요 인물", char_map or {})]
    if loc_map:
        buckets.append(("조·단역", loc_map.get("extras") or {}))
        buckets.append(("지명·기관·용어", loc_map.get("places") or {}))

    for label, mapping in buckets:
        for ko, en in mapping.items():
            if ko and ko in text:
                result["unapplied"].append((ko, en, label))
            # 목표 영문이 전혀 등장하지 않으면 미반영 의심
            head = re.split(r"\s*/\s*", str(en))[0].strip()
            if head and len(head) >= 3 and head.lower() not in text.lower():
                result["missing"].append((ko, en, label))

    for pattern, label in _RESIDUE_PATTERNS:
        if preserve_setting and label in _RESIDUE_SKIP_IN_PRESERVE:   # ★ v2.5.0
            continue
        hits = re.findall(pattern, text)
        if hits:
            uniq = []
            for h in hits:
                h = str(h).strip()
                if h and h not in uniq:
                    uniq.append(h)
            result["residue"].append((label, uniq[:8], len(hits)))

    # ★ v2.3.0 — 고정 대사가 실제로 들어갔는지 (첫 구절 기준 유연 매칭)
    for f in (loc_map or {}).get("fixed_lines") or []:
        en = str(f.get("en") or "")
        first = re.split(r"\s*/\s*", en)[0].strip().strip(".").strip()
        probe = " ".join(first.split()[:6])
        if probe and not _flexible_pattern(probe).search(text):
            tag = f"고정 대사 S#{f.get('scene')}" if f.get("scene") else "고정 대사"
            result["missing"].append((f.get("ko"), en, tag))

    corrections = (loc_map or {}).get("corrections") or {}
    for bad, good in corrections.items():
        n = len(_flexible_pattern(bad).findall(text))
        if n:
            result["corrections_left"].append((bad, good, n))

    return result


# ═══════════════════════════════════════════════════
# ★ v2.5.0 — 다국어 원고 · 무대 보존 · 베트남 이름 보조 함수
# ═══════════════════════════════════════════════════

# 원고(한국어)의 언어 이름 → 영문 언어 이름
_LANG_NAMES = {
    "베트남어": "Vietnamese", "영어": "English", "한국어": "Korean",
    "인도네시아어": "Indonesian", "자바어": "Javanese", "일본어": "Japanese",
    "중국어": "Chinese", "광둥어": "Cantonese", "태국어": "Thai",
    "프랑스어": "French", "스페인어": "Spanish", "러시아어": "Russian",
}
_LANG_EN_CANON = {v.lower(): v for v in _LANG_NAMES.values()}

# 한국어 원고: (베트남어) (베트남어, 낮게) [문자 · 베트남어] INSERT — … · 베트남어
_KO_LANG_RE = re.compile(
    r"(?:\(|·)[ \t]*(" + "|".join(sorted(_LANG_NAMES, key=len, reverse=True)) + r")(?:로)?"
    r"(?=[ \t]*[,)\]]|[ \t]*$)",
    re.MULTILINE,
)
# 영문 원고: (in Vietnamese) (in Vietnamese, quietly) (IN VIETNAMESE) (Vietnamese) (speaking Vietnamese)
_EN_LANG_RE = re.compile(
    r"\([ \t]*(?:in[ \t]+|speaking[ \t]+)?(" + "|".join(_LANG_NAMES.values()) + r")\b(?=[ \t]*[),;])",
    re.IGNORECASE,
)

_SCENE_SPLIT_RE = re.compile(
    r'^[ \t]*(?:S[ \t]*#[ \t]*\d+|INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.|I/E\.)',
    re.MULTILINE | re.IGNORECASE,
)

_META_BLOCKS = [
    (r"<LOCAL_VERIFY>.*?</LOCAL_VERIFY>", "LOCAL_VERIFY (고증 체크리스트)"),
    (r"<RATING_CHECK>.*?</RATING_CHECK>", "RATING_CHECK (등급 점검)"),
    (r"<WRITER_NOTES_BEGIN>.*?<WRITER_NOTES_END>", "WRITER_NOTES (작가 노트)"),
    (r"\[MARKET_LENS_BEGIN\].*?\[MARKET_LENS_END\]", "MARKET_LENS (시장 렌즈)"),
]


def count_lang_tags_ko(text: str) -> dict:
    """한국어 원고의 대사·화면 텍스트 언어 표기를 언어별로 센다. {"Vietnamese": 2, ...}"""
    out = {}
    for ko in _KO_LANG_RE.findall(text or ""):
        en = _LANG_NAMES[ko]
        out[en] = out.get(en, 0) + 1
    return out


def count_lang_tags_en(text: str) -> dict:
    """영문 원고의 언어 괄호를 언어별로 센다. 표기 변형(대소문자·in 생략)도 같은 것으로 센다."""
    out = {}
    for name in _EN_LANG_RE.findall(text or ""):
        en = _LANG_EN_CANON.get(name.lower(), name.title())
        out[en] = out.get(en, 0) + 1
    return out


def lang_tag_problem(src: str, out: str, mode: str) -> str:
    """페이지 단위 언어 괄호 수 대조. 문제가 없으면 빈 문자열."""
    a = count_lang_tags_ko(src) if mode == "ko2en" else count_lang_tags_en(src)
    b = count_lang_tags_en(out)
    if a == b:
        return ""
    diffs = [f"{lang} 입력 {a.get(lang, 0)} / 출력 {b.get(lang, 0)}"
             for lang in sorted(set(a) | set(b)) if a.get(lang, 0) != b.get(lang, 0)]
    return "언어 표기 불일치 — " + " · ".join(diffs)


def _split_scenes(text: str) -> list:
    """씬 헤딩(S#n / INT. / EXT.) 기준으로 (헤딩, 본문) 목록을 만든다. 첫 헤딩 앞부분은 제외."""
    text = text or ""
    starts = [m.start() for m in _SCENE_SPLIT_RE.finditer(text)]
    scenes = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(text)
        block = text[s:e]
        head = block.split("\n", 1)[0].strip()
        scenes.append((head, block))
    return scenes


def check_language_tags(src: str, out: str, src_is_korean: bool = True) -> dict:
    """원고와 번역 결과의 언어 괄호를 언어별·씬별로 대조한다. 자동 수정은 하지 않는다.

    반환: {
        "totals": [(언어, 원고 수, 결과 수)],
        "scenes": [(씬 순번, 결과 씬 헤딩, 언어, 원고 수, 결과 수)],   # 불일치 씬만
        "scene_compare": True/False,   # 씬 수가 같아 씬별 대조를 했는지
        "ok": True/False,
    }
    """
    counter_src = count_lang_tags_ko if src_is_korean else count_lang_tags_en
    a, b = counter_src(src), count_lang_tags_en(out)
    totals = [(lang, a.get(lang, 0), b.get(lang, 0)) for lang in sorted(set(a) | set(b))]
    res = {"totals": totals, "scenes": [], "scene_compare": False,
           "ok": all(x == y for _, x, y in totals)}

    s_src, s_out = _split_scenes(src), _split_scenes(out)
    if s_src and len(s_src) == len(s_out):
        res["scene_compare"] = True
        for i, ((_, bs), (ho, bo)) in enumerate(zip(s_src, s_out), start=1):
            ca, cb = counter_src(bs), count_lang_tags_en(bo)
            for lang in sorted(set(ca) | set(cb)):
                if ca.get(lang, 0) != cb.get(lang, 0):
                    res["scenes"].append((i, ho, lang, ca.get(lang, 0), cb.get(lang, 0)))
    return res


def strip_meta_blocks(text: str) -> tuple:
    """Writer 엔진 메타 블록(고증·등급·작가 노트·시장 렌즈)을 원고에서 제거한다.

    반환: (정리된 원고, [(블록 이름, 개수)])  — 블록이 없으면 원고를 그대로 돌려준다.
    """
    if not text:
        return text, []
    removed = []
    for pattern, label in _META_BLOCKS:
        text, n = re.subn(pattern, "", text, flags=re.DOTALL)
        if n:
            removed.append((label, n))
    if removed:
        text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text, removed


_KO_CUE_RE = re.compile(
    r'^[ \t]*([가-힣][가-힣0-9]{0,9})[ \t]*(?:\([^)\n]*\))?[ \t]*(?:\t|[:：])',
    re.MULTILINE,
)


def find_unmapped_korean_names(text: str, char_map: dict, loc_map: dict = None) -> list:
    """대사 큐(이름 + 탭 / 이름 :)로 쓰인 한글 이름 중 대조표에 없는 것. [(이름, 대사 수)]"""
    known = dict(char_map or {})
    known.update((loc_map or {}).get("extras") or {})
    counts = {}
    for name in _KO_CUE_RE.findall(text or ""):
        if name in known or _match_char_name(name, known):
            continue
        counts[name] = counts.get(name, 0) + 1
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))


def collect_name_context(text: str, names: list, per_name: int = 3) -> dict:
    """이름 후보를 만들 때 함께 보낼 대사 몇 줄을 모은다. {이름: [줄, ...]}"""
    ctx = {n: [] for n in names}
    for line in (text or "").split("\n"):
        m = _KO_CUE_RE.match(line)
        if m and m.group(1) in ctx and len(ctx[m.group(1)]) < per_name:
            ctx[m.group(1)].append(re.sub(r"\s+", " ", line.strip())[:160])
    return ctx


def fold_ascii(s: str) -> str:
    """성조 부호를 뗀 형태 (Tuấn → Tuan, Đà → Da)."""
    import unicodedata
    s = (s or "").replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def parse_vn_name_candidates(raw: str, names: list = None) -> list:
    """이름 후보 응답 '한국이름 | CUE | 풀네임 | 메모' 를 표 행으로 바꾼다."""
    rows, seen = [], set()
    wanted = set(names or [])
    for line in (raw or "").split("\n"):
        line = line.strip().strip("`").strip()
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        ko = cells[0]
        if not _HANGUL_RE.search(ko) or ko in seen:
            continue        # 머리글·설명 줄 제외
        if wanted and ko not in wanted:
            continue
        cue = re.sub(r"[^A-Z0-9 .'\-]", "", fold_ascii(cells[1]).upper()).strip()
        cue = re.sub(r"\s+", " ", cue)
        if not cue:
            continue
        seen.add(ko)
        rows.append({
            "한국이름": ko,
            "영문 큐": cue,
            "베트남 풀네임": cells[2] if len(cells) > 2 and cells[2] not in {"-", "—"} else "",
            "메모": cells[3] if len(cells) > 3 else "",
        })
    return rows


def check_name_diacritics(text: str, char_map: dict) -> list:
    """대조표 이름과 성조 부호만 다른 표기가 섞여 있는지 찾는다. [(대조표 표기, [다른 표기, ...])]"""
    if not text or not char_map:
        return []
    forms = {}
    for w in re.findall(r"[^\W\d_]+", text):
        forms.setdefault(fold_ascii(w).lower(), set()).add(w)
    report = []
    for en in sorted({v for v in char_map.values() if _has_latin(v)}):
        variants = set()
        for word in re.findall(r"[^\W\d_]+", en):
            if len(word) < 3:
                continue
            for f in forms.get(fold_ascii(word).lower(), ()):
                if f.lower() != word.lower():
                    variants.add(f)
        if variants:
            report.append((en, sorted(variants)))
    return report


_LANG_NOTE_HEAD = "NOTE: Unless otherwise noted, dialogue is spoken in"


def base_dialogue_language(region_id: str, preserve_setting: bool) -> str:
    """괄호 없는 대사의 언어. 영어권 이식(US/UK)이면 노트가 필요 없으므로 빈 문자열."""
    if preserve_setting:
        return "Korean"
    return {"vn": "Vietnamese", "id": "Indonesian"}.get(region_id, "")


def apply_language_note(text: str, base_lang: str, subtitled: bool = True) -> str:
    """첫 페이지 언어 노트를 1회 넣는다 (이미 있으면 그대로)."""
    if not text or not base_lang or text.lstrip().startswith(_LANG_NOTE_HEAD):
        return text
    note = f"{_LANG_NOTE_HEAD} {base_lang}."
    if subtitled:
        note += " Non-English dialogue is subtitled."
    return note + "\n\n" + text


def parse_character_map(uploaded_file) -> dict:
    """Parse character name mapping from CSV or TXT file.
    Supports optional tone tag column: 한국이름,영어이름,톤태그
    """
    name = uploaded_file.name.lower()

    # ★ v2.2 — XLSX 로컬라이징 대조표는 전용 파서로 넘긴다
    if name.endswith((".xlsx", ".xlsm")):
        cm, ct, _lm = parse_translation_workbook(uploaded_file)
        return cm, ct

    content = uploaded_file.read().decode("utf-8", errors="replace")
    uploaded_file.seek(0)

    char_map = {}
    char_tones = {}
    skip_headers = {"한국이름", "한국명", "korean", "name", "이름"}

    if name.endswith(".csv"):
        reader = csv.reader(io.StringIO(content))
        for row in reader:
            if len(row) >= 2:
                ko = row[0].strip()
                en = row[1].strip()
                if ko and en and ko.lower() not in skip_headers:
                    char_map[ko] = en
                    # Optional tone tag (3rd column)
                    if len(row) >= 3:
                        tone = row[2].strip().lower()
                        if tone in CHARACTER_TONE_TAGS:
                            char_tones[en] = tone
    else:
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for sep in ["→", "->", "=>", "=", ",", ":", "\t"]:
                if sep in line:
                    parts = line.split(sep)
                    ko = parts[0].strip()
                    en = parts[1].strip() if len(parts) > 1 else ""
                    if ko and en and ko.lower() not in skip_headers:
                        char_map[ko] = en
                        if len(parts) >= 3:
                            tone = parts[2].strip().lower()
                            if tone in CHARACTER_TONE_TAGS:
                                char_tones[en] = tone
                    break

    return char_map, char_tones


def read_uploaded_file(uploaded_file) -> str:
    """Read text from uploaded .txt, .pdf, or .docx file."""
    name = uploaded_file.name.lower()

    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="replace")

    elif name.endswith(".pdf"):
        try:
            import pymupdf
            pdf_bytes = uploaded_file.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            doc.close()
            return "\n".join(text_parts)
        except ImportError:
            st.error("PDF 처리를 위해 pymupdf가 필요합니다.")
            return ""

    elif name.endswith(".docx"):
        try:
            from docx import Document
            docx_bytes = io.BytesIO(uploaded_file.read())
            doc = Document(docx_bytes)
            return "\n".join([p.text for p in doc.paragraphs])
        except ImportError:
            st.error("DOCX 처리를 위해 python-docx가 필요합니다.")
            return ""

    else:
        st.error("지원하지 않는 파일 형식입니다. (.txt / .pdf / .docx)")
        return ""


def split_into_pages(text: str, max_chars: int = MAX_CHARS_PER_PAGE) -> list:
    """Split text into pages, trying to break at scene boundaries."""
    if len(text) <= max_chars:
        return [text]

    pages = []
    remaining = text

    while remaining:
        if len(remaining) <= max_chars:
            pages.append(remaining)
            break

        chunk = remaining[:max_chars]
        scene_pattern = r'\n\s*(?:S\s*#?\s*\d+|씬\s*#?\s*\d+|SCENE\s*\d+|#\s*\d+[\.\)]|INT\.|EXT\.)'
        matches = list(re.finditer(scene_pattern, chunk))

        if matches:
            cut_point = matches[-1].start()
            if cut_point > max_chars * 0.3:
                pages.append(remaining[:cut_point].rstrip())
                remaining = remaining[cut_point:].lstrip("\n")
                continue

        last_break = chunk.rfind("\n\n")
        if last_break > max_chars * 0.3:
            pages.append(remaining[:last_break].rstrip())
            remaining = remaining[last_break:].lstrip("\n")
        else:
            pages.append(chunk)
            remaining = remaining[max_chars:]

    return pages


# ─────────────────────────────────────────────
# STAGE 2: FORMAT CONVERSION (Rule-based)
# ─────────────────────────────────────────────

def apply_format_conversion(text: str, region_id: str) -> str:
    """Apply rule-based format conversion to translated text.
    Converts Korean screenplay format markers to target region format.
    """
    result = text

    # ── Scene heading cleanup ──
    # Remove Korean scene numbering prefixes: S#1, 씬1, etc.
    result = re.sub(
        r'^(S\s*#?\s*\d+\.?\s*)',
        '',
        result,
        flags=re.MULTILINE | re.IGNORECASE
    )

    # ── Korean direction markers → English ──
    marker_map = {
        r'\(N\)': '(V.O.)',
        r'\(나레이션\)': '(V.O.)',
        r'\(소리\)': '(O.S.)' if region_id != 'uk' else '(O.O.V.)',
        r'\(독백\)': '(V.O.)',
        r'\(전화\)': '(ON PHONE)',
        r'\(계속\)': "(CONT'D)",
        r'\(회상\)': 'FLASHBACK:',
        r'\(몽타주\)': 'MONTAGE:',
        r'\(타이틀\)': 'TITLE CARD:',
        r'\(자막\)': 'SUPER:',
        r'\(F\.I\)': 'FADE IN:',
        r'\(F\.O\)': 'FADE OUT.',
    }
    for pattern, replacement in marker_map.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # ── ★ v2.5.0 화면 텍스트 언어 표기 잔존: "· 베트남어" / "· Vietnamese" → "(IN VIETNAMESE)" ──
    #    (가운뎃점 + 언어 이름 조합에만 반응하므로 일반 원고에는 영향 없음)
    for _ko, _en in _LANG_NAMES.items():
        result = re.sub(
            rf"[ \t]*·[ \t]*(?:{_ko}|{_en})(?![^\W\d_])",
            f" (IN {_en.upper()})",
            result,
            flags=re.IGNORECASE,
        )

    # ── Dash standardization ──
    if region_id == 'us':
        # US: em dash in scene headings
        result = re.sub(
            r'^((?:INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.)\s+.+?)\s*[-–]\s*',
            r'\1 — ',
            result,
            flags=re.MULTILINE
        )
    else:
        # UK/International: hyphen
        result = re.sub(
            r'^((?:INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.)\s+.+?)\s*[—–]\s*',
            r'\1 - ',
            result,
            flags=re.MULTILINE
        )

    # ── Scene heading ALL CAPS ──
    def uppercase_scene_heading(match):
        return match.group(0).upper()

    result = re.sub(
        r'^(INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.).*$',
        uppercase_scene_heading,
        result,
        flags=re.MULTILINE | re.IGNORECASE
    )

    return result


# ─────────────────────────────────────────────
# API CALL FUNCTION
# ─────────────────────────────────────────────

def call_api(client, text: str, system_prompt: str, model_id: str,
             max_tokens: int = 32000, page_info: str = "") -> str:
    """Call Claude API with streaming to prevent timeout."""
    # 페이지 정보는 시스템 프롬프트에 추가 (본문에 섞이면 출력에 포함됨)
    full_system = system_prompt
    if page_info:
        full_system += f"\n\n[Internal context for consistency: {page_info}. Do NOT include this note in your output.]"

    collected = []
    with client.messages.stream(
        model=model_id,
        max_tokens=max_tokens,
        system=full_system,
        messages=[
            {
                "role": "user",
                "content": text
            }
        ]
    ) as stream:
        for text_chunk in stream.text_stream:
            collected.append(text_chunk)
        final = stream.get_final_message()

    output = "".join(collected)

    # ★ v2.2.3 — 응답 검사. 문제가 있으면 예외를 던져 결과가 저장되지 않게 한다.
    stop = getattr(final, "stop_reason", None)
    if stop == "max_tokens":
        raise RuntimeError(
            f"응답이 길이 한도({max_tokens:,} 토큰)에 걸려 중간에 끊겼습니다. "
            "잘린 결과는 저장하지 않았습니다. prompt.py MODEL_POLICY의 max_tokens를 늘려 주세요."
        )
    if stop == "refusal":
        raise RuntimeError("모델이 이 페이지의 응답을 거부했습니다 (stop_reason: refusal).")
    if not output.strip():
        raise RuntimeError(
            f"모델이 본문 없이 응답을 끝냈습니다 (stop_reason: {stop}). "
            "빈 결과는 저장하지 않았습니다. 다시 실행해 주세요."
        )

    return output


# ═══════════════════════════════════════════════════
# ★ v2.3.0 — 완결성 검사 · 이어하기 · 재시도
# ═══════════════════════════════════════════════════

_SCENE_NUM_RE = re.compile(r'^\s*S\s*#\s*(\d+)', re.MULTILINE | re.IGNORECASE)
_SCENE_HEAD_RE = re.compile(r'^\s*(?:S\s*#?\s*\d+\.?\s*)?(?:INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.|I/E\.)',
                            re.MULTILINE | re.IGNORECASE)

# 출력 분량 하한 (입력 대비 글자 수 비율). 이보다 짧으면 장면이 빠졌다고 본다.
#   한→영: 영어가 한국어보다 길어지는 것이 정상 (실측 약 1.9배)
#   영→영: 리라이트로 다소 줄 수 있으나 절반 이하로 줄면 누락
_MIN_RATIO = {"ko2en": 0.8, "en2en": 0.5, "fix": 0.9}
# ★ v2.4.0 — 기계적 수정(Stage 6)은 분량이 거의 변하지 않아야 한다
_MAX_RATIO = {"fix": 1.15}


def count_scenes(text: str) -> int:
    """씬 수를 센다. S#번호 기준, 없으면 INT./EXT. 헤딩 기준."""
    if not text:
        return 0
    nums = _SCENE_NUM_RE.findall(text)
    if nums:
        return len(set(nums))
    return len(_SCENE_HEAD_RE.findall(text))


def check_completeness(src: str, out: str, mode: str, locked: list = None,
                       lang_check: bool = False) -> str:
    """페이지 단위 완결성 검사. 문제가 없으면 빈 문자열, 있으면 사유를 돌려준다.

    ★ v2.4.0 — locked: 고정 대사 영문 목록. 입력에 있던 고정 대사가 출력에서 사라지면 실패.
    ★ v2.5.0 — lang_check: 언어 괄호((in Vietnamese) 등) 수가 입력과 다르면 실패.
    """
    if lang_check:
        problem = lang_tag_problem(src, out, mode)
        if problem:
            return problem

    src_nums = set(_SCENE_NUM_RE.findall(src or ""))
    if src_nums:
        out_nums = set(_SCENE_NUM_RE.findall(out or ""))
        missing = sorted(src_nums - out_nums, key=int)
        # S#가 빠졌어도 INT./EXT. 헤딩 수가 충분하면 통과
        if missing and len(_SCENE_HEAD_RE.findall(out or "")) < len(src_nums):
            shown = ", ".join(f"S#{n}" for n in missing[:12])
            more = f" 외 {len(missing) - 12}개" if len(missing) > 12 else ""
            return f"씬 누락 — {shown}{more}"
    else:
        src_heads = len(_SCENE_HEAD_RE.findall(src or ""))
        out_heads = len(_SCENE_HEAD_RE.findall(out or ""))
        if src_heads and out_heads < src_heads:
            return f"씬 헤딩 수 부족 — 입력 {src_heads}개 / 출력 {out_heads}개"

    src_len = len((src or "").strip())
    out_len = len((out or "").strip())
    ratio = _MIN_RATIO.get(mode, 0.5)
    if src_len >= 1500 and out_len < src_len * ratio:
        return f"분량 부족 — 입력 {src_len:,}자 대비 출력 {out_len:,}자 (기준 {int(ratio*100)}% 미만)"
    max_r = _MAX_RATIO.get(mode)
    if max_r and src_len >= 1500 and out_len > src_len * max_r:
        return f"변경 과다 — 입력 {src_len:,}자 대비 출력 {out_len:,}자 (기계적 수정 범위 초과)"

    for en in locked or []:
        probe = " ".join(re.split(r"\s*/\s*", str(en))[0].split()[:6]).strip()
        if len(probe) >= 8:
            pat = _flexible_pattern(probe)
            if pat.search(src or "") and not pat.search(out or ""):
                return f"고정 대사 훼손 — \"{probe}…\""
    return ""


# ═══════════════════════════════════════════════════
# ★ v2.4.0 — Stage 6 보조 함수
# ═══════════════════════════════════════════════════

def normalize_layout(text: str) -> str:
    """규칙 기반 정리 (API 비용 없음).

    - 모든 줄 왼쪽 정렬 (들여쓰기 방식 혼용 제거 — DOCX 서식은 생성 단계에서 입힌다)
    - "--" → em dash "—"
    - 3줄 이상 빈 줄 → 1줄
    """
    if not text:
        return text
    lines = [ln.strip() for ln in text.replace("\t", " ").split("\n")]
    out = "\n".join(lines)
    out = re.sub(r"[ ]*--[ ]*", " — ", out)   # 줄바꿈은 건드리지 않는다
    out = re.sub(r"(?m)^ — ", "— ", out)
    out = re.sub(r" — $", " —", out, flags=re.M)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + "\n"


def scene_heading_list(text: str) -> list:
    return [ln.strip() for ln in (text or "").split("\n") if _SCENE_HEAD_RE.match(ln)]


def introduced_before(full_text: str, offset: int, char_map: dict) -> list:
    """offset 이전에 이미 등장한 인물 영문명 목록 (대문자 해제 대상)."""
    names = sorted({v for v in (char_map or {}).values() if _has_latin(v)}, key=len)
    head = (full_text or "")[:offset]
    found = []
    for n in names:
        if re.search(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])", head, re.IGNORECASE):
            found.append(n)
    return found


def make_client(key: str):
    """일시적 서버 혼잡(429/529 등)에 자동 재시도하는 클라이언트."""
    return anthropic.Anthropic(api_key=key, max_retries=5)


def _job_signature(system_prompt: str, pages: list) -> str:
    import hashlib
    h = hashlib.sha256()
    h.update(system_prompt.encode("utf-8"))
    for p in pages:
        h.update(b"\x00")
        h.update(p.encode("utf-8"))
    return h.hexdigest()[:16]


def text_signature(text: str) -> str:
    import hashlib
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


def run_stage_on_pages(client, pages: list, system_prompt: str,
                       model_id: str, stage_name: str,
                       progress_bar, status_area,
                       max_tokens: int = 32000,
                       stage_key: str = "",
                       check_mode: str = "en2en",
                       page_notes: list = None,
                       locked: list = None,
                       lang_check: bool = False) -> list:
    """Run an API-based stage on multiple pages with progress tracking.

    ★ v2.3.0
      - 페이지마다 완결성 검사(씬 누락·분량 부족). 실패하면 1회 자동 재시도, 그래도 실패하면 중단.
      - 완료된 페이지는 세션에 보관. 중간에 실패해도 다시 실행하면 실패한 페이지부터 이어서 진행.
        (설정·대조표·원고가 바뀌면 보관분은 자동 폐기하고 처음부터 진행)
    """
    total = len(pages)
    sig = _job_signature(system_prompt, pages)
    partial_key = f"partial_{stage_key}" if stage_key else ""

    results = []
    if partial_key:
        saved = st.session_state.get(partial_key) or {}
        if saved.get("sig") == sig:
            results = list(saved.get("results") or [])
        if results:
            st.info(f"↪️ 이전 실행에서 완료된 {len(results)}/{total} 페이지를 이어서 사용합니다.")
            progress_bar.progress(len(results) / total)

    for idx in range(len(results), total):
        page = pages[idx]
        page_num = idx + 1
        result = None
        last_problem = ""

        for attempt in (1, 2):
            retry_note = " · 재시도" if attempt == 2 else ""
            status_area.markdown(
                f'<div class="progress-text">🔄 {stage_name} — 페이지 {page_num}/{total} 처리 중{retry_note}... (모델: {model_id})</div>',
                unsafe_allow_html=True
            )
            try:
                out = call_api(
                    client, page, system_prompt, model_id,
                    max_tokens=max_tokens,
                    page_info=f"Page {page_num} of {total}. Maintain consistency. "
                              f"Process this page COMPLETELY, from its first line to its last line"
                              + (f". {page_notes[idx]}" if page_notes and idx < len(page_notes) and page_notes[idx] else ""),
                )
            except anthropic.APIError as e:
                error_msg = f"❌ API 오류 ({stage_name}, 페이지 {page_num}): {e}"
                st.error(error_msg)
                st.session_state["last_error"] = error_msg
                return None
            except Exception as e:
                last_problem = f"{type(e).__name__}: {e}"
                continue

            problem = check_completeness(page, out, check_mode, locked=locked,
                                         lang_check=lang_check)
            if not problem:
                result = out
                break
            last_problem = problem

        if result is None:
            done_note = (f" 완료된 {len(results)}페이지는 보관했습니다. 다시 실행하면 {page_num}페이지부터 이어서 진행합니다."
                         if partial_key and results else "")
            error_msg = (f"❌ {stage_name} — 페이지 {page_num}/{total} 결과가 불완전해 저장하지 않았습니다 "
                         f"(2회 시도). 사유: {last_problem}.{done_note}")
            st.error(error_msg)
            st.session_state["last_error"] = error_msg
            return None

        results.append(result)
        if partial_key:
            st.session_state[partial_key] = {"sig": sig, "results": list(results)}
        progress_bar.progress(page_num / total)

    if partial_key:
        st.session_state.pop(partial_key, None)
    st.session_state.pop("last_error", None)
    return results


_STAGE_KEYS = ["stage_1_result", "stage_2_result", "stage_3_result",
               "stage_4_result", "stage_5_result", "stage_6_result"]


def clear_downstream(stage_num: int):
    """★ v2.3.0 — 앞 단계를 다시 돌리면 그 뒤 단계 결과는 낡은 결과이므로 지운다."""
    for n in range(stage_num + 1, 7):   # ★ v2.4.0 Stage 6 포함
        st.session_state[f"stage_{n}_result"] = None
        st.session_state.pop(f"partial_stage_{n}", None)
    if stage_num < 6:
        st.session_state.pop("stage_6_style_sheet", None)
    for k in ("audit_report", "enforced_result", "enforce_log"):
        st.session_state.pop(k, None)


# ─────────────────────────────────────────────
# DOCX GENERATION
# ─────────────────────────────────────────────

def generate_docx(text: str) -> bytes:
    """Generate formatted screenplay DOCX from translated text."""
    from docx import Document
    from docx.shared import Pt, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()

    # ── Page Setup ──
    section = doc.sections[0]
    section.page_width = Cm(21.0)    # A4
    section.page_height = Cm(29.7)   # A4
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

    # ── Styles ──
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Courier New'
    style_normal.font.size = Pt(12)
    style_normal.paragraph_format.space_after = Pt(0)
    style_normal.paragraph_format.space_before = Pt(0)
    style_normal.paragraph_format.line_spacing = 1.0

    style_scene = doc.styles.add_style('SceneHeader', 1)
    style_scene.font.name = 'Courier New'
    style_scene.font.size = Pt(12)
    style_scene.font.bold = True
    style_scene.font.all_caps = True
    style_scene.paragraph_format.space_before = Pt(36)   # 씬 사이 빈 줄 효과
    style_scene.paragraph_format.space_after = Pt(12)
    style_scene.paragraph_format.line_spacing = 1.0

    style_char = doc.styles.add_style('CharacterName', 1)
    style_char.font.name = 'Courier New'
    style_char.font.size = Pt(12)
    style_char.font.bold = True
    style_char.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_char.paragraph_format.space_before = Pt(12)
    style_char.paragraph_format.space_after = Pt(0)
    style_char.paragraph_format.line_spacing = 1.0

    style_dial = doc.styles.add_style('Dialogue', 1)
    style_dial.font.name = 'Courier New'
    style_dial.font.size = Pt(12)
    style_dial.paragraph_format.left_indent = Inches(1.5)
    style_dial.paragraph_format.right_indent = Inches(1.5)
    style_dial.paragraph_format.space_after = Pt(0)
    style_dial.paragraph_format.space_before = Pt(0)
    style_dial.paragraph_format.line_spacing = 1.0

    style_paren = doc.styles.add_style('Parenthetical', 1)
    style_paren.font.name = 'Courier New'
    style_paren.font.size = Pt(12)
    style_paren.paragraph_format.left_indent = Inches(2.0)
    style_paren.paragraph_format.right_indent = Inches(2.0)
    style_paren.paragraph_format.space_after = Pt(0)
    style_paren.paragraph_format.space_before = Pt(0)
    style_paren.paragraph_format.line_spacing = 1.0

    style_action = doc.styles.add_style('Action', 1)
    style_action.font.name = 'Courier New'
    style_action.font.size = Pt(12)
    style_action.paragraph_format.space_before = Pt(12)
    style_action.paragraph_format.space_after = Pt(0)
    style_action.paragraph_format.line_spacing = 1.0

    style_trans = doc.styles.add_style('Transition', 1)
    style_trans.font.name = 'Courier New'
    style_trans.font.size = Pt(12)
    style_trans.font.bold = True
    style_trans.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    style_trans.paragraph_format.space_before = Pt(12)
    style_trans.paragraph_format.space_after = Pt(12)
    style_trans.paragraph_format.line_spacing = 1.0

    # ── Parse and format ──
    SCENE_RE = re.compile(
        r'^(?:S\s*#?\s*\d+\.?\s*)?'
        r'(INT\.|EXT\.|INT\./EXT\.|EXT\./INT\.|I/E\.|E/I\.)',
        re.IGNORECASE
    )
    TRANSITION_RE = re.compile(
        r'^(FADE\s+IN:|FADE\s+OUT\.?|CUT\s+TO:|SMASH\s+CUT:|MATCH\s+CUT:|'
        r'DISSOLVE\s+TO:|JUMP\s+CUT:|TIME\s+CUT:|FADE\s+TO\s+BLACK\.?|'
        r'THE\s+END\.?)$',
        re.IGNORECASE
    )
    CHAR_RE = re.compile(r'^([A-Z][A-Z0-9\s\.\-\']+?)(\s*\(.*\))?\s*$')
    PAREN_RE = re.compile(r'^\(.*\)\s*$')
    # ★ v2.5.0 — "(in Vietnamese) Say it again." 처럼 언어 괄호가 대사 줄에 붙은 경우
    INLINE_LANG_RE = re.compile(
        r'^(\((?:in|speaking)\s+[A-Za-z]+[^)]*\))\s+(\S.*)$', re.IGNORECASE)

    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if SCENE_RE.match(stripped):
            doc.add_paragraph(stripped, style='SceneHeader')
            i += 1
            continue

        if TRANSITION_RE.match(stripped):
            doc.add_paragraph(stripped, style='Transition')
            i += 1
            continue

        if CHAR_RE.match(stripped) and len(stripped) < 60:
            next_i = i + 1
            while next_i < len(lines) and not lines[next_i].strip():
                next_i += 1

            if next_i < len(lines):
                next_line = lines[next_i].strip()
                is_dialogue_follows = (
                    PAREN_RE.match(next_line) or
                    (next_line and not SCENE_RE.match(next_line)
                     and not TRANSITION_RE.match(next_line)
                     and not CHAR_RE.match(next_line))
                )
                if is_dialogue_follows:
                    doc.add_paragraph(stripped, style='CharacterName')
                    i += 1
                    while i < len(lines):
                        dl = lines[i].strip()
                        if not dl:
                            break
                        if SCENE_RE.match(dl) or TRANSITION_RE.match(dl):
                            break
                        if CHAR_RE.match(dl) and len(dl) < 60:
                            peek = i + 1
                            while peek < len(lines) and not lines[peek].strip():
                                peek += 1
                            if peek < len(lines) and lines[peek].strip():
                                break
                        _inl = INLINE_LANG_RE.match(dl)
                        if _inl:
                            doc.add_paragraph(_inl.group(1), style='Parenthetical')
                            doc.add_paragraph(_inl.group(2), style='Dialogue')
                        elif PAREN_RE.match(dl):
                            doc.add_paragraph(dl, style='Parenthetical')
                        else:
                            doc.add_paragraph(dl, style='Dialogue')
                        i += 1
                    continue

        doc.add_paragraph(stripped, style='Action')
        i += 1

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()



# ═══════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════

# ── Header ──
st.markdown(f"""
<div class="main-header">
    <div class="brand-name">B L U E &nbsp; J E A N S &nbsp; P I C T U R E S</div>
    <h1>ENGLISH-TRANSLATOR</h1>
    <div class="tagline">Y O U N G &nbsp; · &nbsp; V I N T A G E &nbsp; · &nbsp; F R E E &nbsp; · &nbsp; I N N O V A T I V E</div>
    <div class="version-badge">v{VERSION} — 5-Stage Native Polish Pipeline</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── API Key ──
api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
if api_key:
    st.success("🔑 API Key 연결됨 (Secrets)")
else:
    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        help="Claude API 키를 입력하세요. (sk-ant-...)"
    )

# ═══════════════════════════════════════════════════
# SETTINGS PANEL
# ═══════════════════════════════════════════════════

st.markdown('<div class="section-header">⚙️ SETTINGS — 번역 설정</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    # ── Region ──
    st.markdown("**타겟 지역**")
    region_choice = st.selectbox(
        "타겟 지역을 선택하세요:",
        list(REGION_PROFILES.keys()),
        index=0,
        label_visibility="collapsed",
    )
    selected_region = REGION_PROFILES[region_choice]
    st.caption(f"📌 {selected_region['desc']} · {selected_region['format_note']}")

with col_right:
    # ── Style ──
    st.markdown("**장르 스타일**")
    style_choice = st.selectbox(
        "장르/스타일 프리셋:",
        list(STYLE_PRESETS.keys()),
        index=0,
        label_visibility="collapsed",
    )
    selected_style = STYLE_PRESETS[style_choice]
    st.caption(f"📌 {selected_style['desc']}")

# ── ★ v2.5.0 무대 보존 (공동제작) ──
# 백업 복원 직후에는 체크박스를 그리기 전에 저장된 값을 반영한다
if "_pending_preserve" in st.session_state:
    st.session_state["preserve_setting_widget"] = st.session_state.pop("_pending_preserve")

preserve_setting = st.checkbox(
    "🤝 공동제작 — 무대 보존 (지명·기관·문화 요소를 옮기지 않음)",
    key="preserve_setting_widget",
    help=(
        "끔(기본): 원고를 타겟 지역으로 이식합니다. 예) 한국 원고 + Vietnam → 서울이 호찌민으로, "
        "인물이 베트남 인물로 바뀝니다.\n\n"
        "켬: 원고의 무대를 그대로 두고 언어만 영어로 바꿉니다. 예) 이미 호찌민이 무대인 "
        "한·베 공동제작 원고 → 호찌민은 호찌민, 서울 장면은 서울로 남습니다."
    ),
)
st.session_state["saved_preserve_setting"] = preserve_setting
if preserve_setting:
    st.caption("📌 무대 보존 — 장소·기관·통화·의례를 원고 그대로 두고 영어로만 옮깁니다. "
               "타겟 지역은 '어떤 영어로 쓸지'만 정합니다.")
elif selected_region["id"] == "vn":
    st.caption("📌 베트남 현지화 — 한국 무대·인물·문화를 베트남으로 옮깁니다. "
               "이미 베트남이 무대인 원고라면 위 무대 보존을 켜 주세요.")

# ── Custom Instructions ──
custom_instructions = st.text_area(
    "✏️ 추가 번역 지시사항 (선택)",
    height=80,
    placeholder="예: 대사에서 존댓말/반말 구분을 sir/ma'am으로 표현해줘 / 특정 용어는 이렇게 번역해줘...",
)

# ── Pipeline Info ──
st.markdown(
    '<div class="pipeline-info"><strong>5-Stage Pipeline (단계별 실행):</strong><br>'
    'Stage 1: Raw Translation → Sonnet (번역)<br>'
    'Stage 2: Format Conversion → 규칙 기반 (무료)<br>'
    'Stage 3: Voice Rewrite → Opus (문체 리라이트)<br>'
    'Stage 4: Dialogue Polish → Opus (대사 폴리시)<br>'
    'Stage 5: QA Check → Sonnet (품질 검증)<br>'
    'Stage 6: Final Revision → Sonnet (QA 자동 반영 · 최종 원고)<br>'
    '<br>💡 각 단계별로 독립 실행 · 결과 저장 · 이어서 진행 가능</div>',
    unsafe_allow_html=True
)


# ═══════════════════════════════════════════════════
# CHARACTER MAP
# ═══════════════════════════════════════════════════

st.markdown('<div class="section-header">👤 LOCALIZATION MAP — 로컬라이징 대조표</div>', unsafe_allow_html=True)

st.info(
    "💡 **XLSX 대조표**를 올리면 주요 인물 · 조단역 · 지명/기관/법률/통화까지 한 번에 반영됩니다. "
    "기존 CSV/TXT 인물표도 그대로 사용할 수 있습니다."
)

char_map_file = st.file_uploader(
    "대조표 파일 업로드",
    type=["xlsx", "xlsm", "csv", "txt"],
    help="XLSX: 다중 시트 대조표 (권장) | CSV: 한국이름,영어이름,톤태그 | TXT: 한국이름 → 영어이름",
    key="char_map_upload"
)

char_map = {}
char_tones = {}
loc_map = {"extras": {}, "places": {}, "corrections": {},
           "fixed_lines": [], "voice_notes": {}}

if char_map_file:
    fname = char_map_file.name.lower()
    try:
        if fname.endswith((".xlsx", ".xlsm")):
            char_map, char_tones, loc_map = parse_translation_workbook(char_map_file)
        else:
            char_map, char_tones = parse_character_map(char_map_file)
    except Exception as e:
        st.error(f"❌ 대조표를 읽는 중 오류가 발생했습니다: {e}")
        char_map, char_tones = {}, {}

    if char_map or count_loc_entries(loc_map):
        # 세션에 저장 (백업/복구용)
        st.session_state["saved_char_map"] = char_map
        st.session_state["saved_char_tones"] = char_tones
        st.session_state["saved_loc_map"] = loc_map

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("주요 인물", f"{len(char_map)}")
        c2.metric("조·단역", f"{len(loc_map.get('extras') or {})}")
        c3.metric("지명·기관·용어", f"{len(loc_map.get('places') or {})}")
        c4.metric("고정 대사", f"{len(loc_map.get('fixed_lines') or [])}")
        c5.metric("말투 지침", f"{len(loc_map.get('voice_notes') or {})}")
        c6.metric("교정 매핑", f"{len(loc_map.get('corrections') or {})}")

        st.success(
            f"✅ 총 {len(char_map) + count_loc_entries(loc_map)}건 로드 "
            f"· 톤 태그 {len(char_tones)}건"
        )

        with st.expander("📑 로드된 매핑 확인", expanded=False):
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["주요 인물", "조·단역", "지명·기관·용어", "교정 매핑", "고정 대사·말투"]
            )
            with tab1:
                if char_map:
                    rows = []
                    for ko, en in char_map.items():
                        tone = char_tones.get(en, "—")
                        tone_label = CHARACTER_TONE_TAGS[tone]["label"] if tone in CHARACTER_TONE_TAGS else "—"
                        rows.append(f"<tr><td>{ko}</td><td>→</td><td><strong>{en}</strong></td><td>{tone_label}</td></tr>")
                    st.markdown(f"""
                    <table class="char-table">
                        <tr><th>한국이름</th><th></th><th>English Name</th><th>Tone</th></tr>
                        {"".join(rows)}
                    </table>
                    """, unsafe_allow_html=True)
                else:
                    st.caption("없음")
            with tab2:
                extras = loc_map.get("extras") or {}
                if extras:
                    st.table([{"한국어": k, "English": v} for k, v in extras.items()])
                else:
                    st.caption("없음")
            with tab3:
                places = loc_map.get("places") or {}
                if places:
                    st.table([{"한국어 원문": k, "확정 영문": v} for k, v in places.items()])
                else:
                    st.caption("없음")
            with tab4:
                corrections = loc_map.get("corrections") or {}
                if corrections:
                    st.caption("이전 판 오표기 → 확정 표기. 번역 결과에서 자동 치환 가능합니다.")
                    st.table([{"오표기": k, "확정 표기": v} for k, v in corrections.items()])
                else:
                    st.caption("없음")
            with tab5:
                fixed = loc_map.get("fixed_lines") or []
                voice = loc_map.get("voice_notes") or {}
                if fixed:
                    st.markdown("**핵심 대사 고정 번역** — 번역문에 그대로 들어갑니다")
                    st.table([{"씬": f.get("scene"), "화자": f.get("speaker"),
                               "한국어": f.get("ko"), "고정 영문": f.get("en")} for f in fixed])
                if voice:
                    st.markdown("**말투 지침** — Stage 3·4에 전달됩니다")
                    st.table([{"인물": k, "영문판 지침": v} for k, v in voice.items()])
                if not (fixed or voice):
                    st.caption("없음")
    else:
        st.warning("⚠️ 매핑을 읽을 수 없습니다. 시트 헤더에 '한국명'과 '영문명' 열이 있는지 확인해 주세요.")

# 대조표를 다시 올리지 않아도 세션 복구본을 사용한다
if not char_map and st.session_state.get("saved_char_map"):
    char_map = st.session_state.get("saved_char_map") or {}
    char_tones = st.session_state.get("saved_char_tones") or {}
    loc_map = st.session_state.get("saved_loc_map") or loc_map
    st.caption(
        f"↩️ 이전 세션 매핑 사용 중 — 인물 {len(char_map)}건 · 기타 {count_loc_entries(loc_map)}건"
    )

# ★ v2.5.0 — 확정한 베트남 이름(현지화 모드)을 인물 매핑에 더한다.
#   업로드한 대조표에 이미 있는 이름은 대조표가 우선한다.
_vn_over = st.session_state.get("vn_name_overrides") or {}
if _vn_over:
    char_map = dict(char_map)   # 세션 보관본을 직접 바꾸지 않도록 복사
    _added = 0
    for _ko, _en in _vn_over.items():
        if _ko and _en and _ko not in char_map:
            char_map[_ko] = _en
            _added += 1
    if _added:
        st.caption(f"🇻🇳 확정한 베트남 이름 {_added}건을 인물 매핑에 함께 적용 중입니다 "
                   "(PIPELINE의 '대조표에 없는 인물 이름'에서 수정·해제할 수 있습니다).")

# Manual tone assignment for unmapped characters
if char_map and not char_tones:
    with st.expander("🎭 캐릭터별 톤 태그 수동 설정 (선택)"):
        st.caption("CSV 3번째 열 없이 여기서 직접 설정할 수 있어요.")
        # ★ v2.2.1 — 같은 영문명이 여러 한국명에 매핑된 경우(약칭→대사 헤드,
        #   장로1·2·3 → ELDER 1 / 2 / 3 등) 선택 상자가 중복 생성되어
        #   StreamlitDuplicateElementKey 오류가 났다. 톤 태그는 영문명 기준으로
        #   저장되므로 영문명당 한 번만 표시한다.
        _seen_tone_en = set()
        for ko, en in char_map.items():
            if en in _seen_tone_en or not _has_latin(en):
                continue
            _seen_tone_en.add(en)
            tone = st.selectbox(
                f"{en}",
                ["—", "formal", "casual", "street"],
                index=0,
                key=f"tone_{en}",
            )
            if tone != "—":
                char_tones[en] = tone

with st.expander("📋 XLSX 대조표 양식 안내", expanded=False):
    st.markdown("""
**시트 구성** — 시트명에 아래 단어가 들어가면 자동 분류됩니다.

| 시트명 예시 | 분류 | 인식 키워드 |
|---|---|---|
| 주요 등장인물 (확정) | 주요 인물 | (그 외 전부) |
| 조·단역 | 조·단역 | 단역 · 조역 · 조연 |
| 지명·기관명 정정 | 지명·기관·용어 | 지명 · 기관 · 장소 · 용어 · 명칭 · 법률 |

**열 구성** — 헤더 이름으로 자동 인식합니다. 순서는 상관없습니다.

| 열 | 인식 키워드 | 용도 |
|---|---|---|
| 한국명 / 한국판 원문 | 한국명 · 한국이름 · 한국판 · 원문 | 치환 대상 |
| 영문명 (확정) / v2 영문판 (확정) | 영문명 · 영문판 · 영어이름 | 확정 표기 |
| v1 영문판 (수정 전) | v1 + 영문 | 오표기 → 확정 자동 치환 |
| 약칭 / 대사 헤드 | 약칭 / 대사 헤드 | 축약 호칭도 함께 매핑 |
| 톤태그 | 톤 · tone | formal / casual / street |

- 확정 영문 뒤의 한글 주석 `(단일화)` 같은 표기는 자동 제거됩니다.
- `v1 대비 변경` 처럼 설명문만 담긴 열은 치환에 쓰이지 않습니다.
""")

with st.expander("📋 CSV / TXT 인물표 예시 보기"):
    st.code("""# CSV 형식 (characters.csv) — 3번째 열: 톤 태그 (선택)
한국이름,영어이름,톤태그
정섬,DETECTIVE JUNG,casual
김회장,CHAIRMAN KIM,formal
독수리,EAGLE,street
이수연,SUYEON LEE,casual

# TXT 형식 (characters.txt)
정섬 → DETECTIVE JUNG → casual
김회장 → CHAIRMAN KIM → formal
독수리 → EAGLE → street""", language="text")


# ═══════════════════════════════════════════════════
# INPUT
# ═══════════════════════════════════════════════════

# ═══════════════════════════════════════════════════
# ★ v2.1 — 프로젝트 세션 백업 (중단 시 복구용)
# ═══════════════════════════════════════════════════
with st.expander("💾 프로젝트 세션 백업 (중단 시 복구용)", expanded=False):
    st.caption(
        "현재까지의 원고와 단계별 번역 결과를 JSON으로 저장하거나 불러옵니다. "
        "번역 도중 멈추거나 다음 날 이어서 작업할 때 사용하세요. "
        "불러오면 멈춘 단계부터 그대로 이어서 진행할 수 있습니다."
    )

    col_b1, col_b2 = st.columns(2)

    # ── 저장 ──
    with col_b1:
        st.markdown("**📥 백업 저장**")
        _done = sum(
            1 for _k in [
                "stage_1_result", "stage_2_result", "stage_3_result",
                "stage_4_result", "stage_5_result", "stage_6_result",
            ]
            if st.session_state.get(_k)
        )
        _backup_title = st.session_state.get("project_title", "") or "Untitled"
        _backup_bytes = export_session_backup()
        _backup_fname = make_backup_filename(_backup_title, _done)
        st.download_button(
            label=f"💾 JSON 다운로드 ({_done}/6 단계)",
            data=_backup_bytes,
            file_name=_backup_fname,
            mime="application/json",
            use_container_width=True,
            key="backup_download_btn",
        )
        st.caption(f"파일명: `{_backup_fname}`")

    # ── 불러오기 ──
    with col_b2:
        st.markdown("**📤 백업 불러오기**")
        backup_file = st.file_uploader(
            "백업 JSON 파일",
            type=["json"],
            key="backup_uploader",
            label_visibility="collapsed",
        )
        load_backup_btn = st.button(
            "📂 백업 적용 (현재 작업 덮어쓰기)",
            use_container_width=True,
            disabled=(backup_file is None),
            key="backup_load_btn",
        )

        if load_backup_btn and backup_file is not None:
            try:
                meta = import_session_backup(backup_file.read())

                saved_ver = meta.get("engine_version", "?")
                saved_at = meta.get("saved_at", "?")
                progress = meta.get("stage_progress", "?")
                title = meta.get("title", "(무제)")

                if saved_ver != ENGINE_VERSION:
                    st.warning(
                        f"⚠️ 백업 버전({saved_ver})이 현재 엔진({ENGINE_VERSION})과 다릅니다. "
                        "복원은 시도되었으나 일부 신규 기능은 반영되지 않을 수 있습니다."
                    )

                st.success(
                    f"✅ 백업 복원 완료\n\n"
                    f"**프로젝트**: {title}\n\n"
                    f"**저장 시각**: {saved_at}\n\n"
                    f"**엔진 버전**: {saved_ver}\n\n"
                    f"**진행도**: {progress} 단계"
                )
                st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"JSON 파싱 실패: {e}")
            except Exception as e:
                st.error(f"복원 중 오류: {e}")


st.markdown('<div class="section-header">📥 INPUT — 시나리오 입력 (한국어)</div>', unsafe_allow_html=True)

# Project title for filename
project_title = st.text_input(
    "🎬 프로젝트 제목 (파일명에 사용됩니다)",
    value=st.session_state.get("project_title", ""),
    placeholder="예: TAKEOFF, 왕게임, 물귀신...",
    help="다운로드 파일명이 Screenplay_제목_translated 형태로 생성됩니다.",
)
if project_title:
    st.session_state["project_title"] = project_title

input_method = st.radio(
    "입력 방식:",
    ["📎 파일 업로드", "📝 텍스트 붙여넣기"],
    horizontal=True,
)

source_text = ""

if input_method == "📎 파일 업로드":
    uploaded = st.file_uploader(
        "시나리오 파일을 업로드하세요",
        type=["txt", "pdf", "docx"],
        help=".txt / .pdf / .docx 파일 지원",
        key="screenplay_upload"
    )
    if uploaded:
        with st.spinner("파일 읽는 중..."):
            source_text = read_uploaded_file(uploaded)
        if source_text:
            # 파일명에서 제목 추출 (확장자 제거, 날짜/버전 태그 정리)
            import os
            raw_name = os.path.splitext(uploaded.name)[0]
            # 간단 정리: 언더스코어/하이픈 → 공간으로, 앞뒤 공백 제거
            clean_title = re.sub(r'[\s_-]+', '_', raw_name).strip('_')
            st.session_state["project_title"] = clean_title

            st.success(f"✅ 파일 로드 완료 — {len(source_text):,}자")
            with st.expander("📄 원문 미리보기", expanded=False):
                st.text(source_text[:3000] + ("..." if len(source_text) > 3000 else ""))
else:
    if "paste_pages" not in st.session_state:
        st.session_state.paste_pages = 1

    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("➕ 페이지 추가", use_container_width=True):
            st.session_state.paste_pages += 1
            st.rerun()
    with col_remove:
        if st.session_state.paste_pages > 1:
            if st.button("➖ 페이지 제거", use_container_width=True):
                st.session_state.paste_pages -= 1
                st.rerun()

    page_texts = []
    for i in range(st.session_state.paste_pages):
        st.markdown(f'<span class="page-chip">Page {i+1}</span>', unsafe_allow_html=True)
        txt = st.text_area(
            f"시나리오 텍스트 (페이지 {i+1})",
            height=250,
            key=f"paste_page_{i}",
            placeholder=f"페이지 {i+1}의 시나리오 텍스트를 붙여넣으세요...",
            label_visibility="collapsed"
        )
        page_texts.append(txt)

    source_text = "\n\n".join([t for t in page_texts if t.strip()])
    if source_text:
        st.caption(f"총 {len(source_text):,}자 입력됨")

# ★ v2.5.0 — Writer 엔진 메타 블록 안전망 (원고 본문이 아니므로 번역 전에 뗀다)
source_text, _meta_removed = strip_meta_blocks(source_text)
if _meta_removed:
    st.info("🧹 원고 본문이 아닌 메타 블록을 번역 대상에서 제외했습니다 — "
            + " · ".join(f"{label} {n}개" for label, n in _meta_removed))

# ★ v2.5.0 — 원고의 대사·화면 텍스트 언어 표기 감지 (정규식으로만 판단)
_lang_counts_src = count_lang_tags_ko(source_text)
if source_text.strip():
    st.session_state["lang_tags_detected"] = bool(_lang_counts_src)


# ═══════════════════════════════════════════════════
# STEP-BY-STEP PIPELINE
# ═══════════════════════════════════════════════════

st.markdown('<div class="section-header">🔄 PIPELINE — 단계별 실행</div>', unsafe_allow_html=True)

can_run = bool(api_key and source_text.strip())

if not api_key:
    st.warning("⬆️ API Key를 먼저 입력하세요.")
elif not source_text.strip():
    st.warning("⬆️ 시나리오 텍스트를 입력하세요.")

# ★ v2.3.0 — 원고가 바뀌었는데 이전 원고의 결과가 남아 있으면 경고
if source_text.strip() and st.session_state.get("stage_1_result") \
        and st.session_state.get("source_sig") \
        and st.session_state.get("source_sig") != text_signature(source_text):
    st.warning(
        "⚠️ 지금 입력된 원고가 Stage 1을 실행했던 원고와 다릅니다. "
        "아래 결과는 이전 원고 기준입니다. 새 원고로 진행하려면 Stage 1을 다시 실행하세요 "
        "(Stage 2~5 결과는 자동으로 비워집니다)."
    )

if source_text.strip():
    _sc = count_scenes(source_text)
    if _sc:
        st.caption(f"🎬 원고 씬 수: {_sc}개 — 각 단계는 페이지마다 씬 누락을 검사합니다.")


# ═══════════════════════════════════════════════════
# ★ v2.5.0 — 다국어 표기 · 이름 사전 점검
# ═══════════════════════════════════════════════════
def is_multilingual(stage_input: str = "") -> bool:
    """원고(한국어) 또는 이번 단계 입력(영문)에 언어 표기가 있으면 True."""
    if source_text.strip():
        src_flag = bool(_lang_counts_src)
    else:
        src_flag = bool(st.session_state.get("lang_tags_detected"))
    return src_flag or bool(count_lang_tags_en(stage_input or ""))


if _lang_counts_src:
    st.info(
        "🌐 대사·화면 텍스트 언어 표기가 감지되었습니다 — "
        + " · ".join(f"{lang} {n}곳" for lang, n in sorted(_lang_counts_src.items()))
        + ". 각 단계가 언어 괄호((in Vietnamese) 등)를 하나씩 그대로 옮겼는지 페이지마다 대조합니다."
    )
    if _lang_counts_src.get("Vietnamese") and not preserve_setting:
        st.warning(
            "베트남어 표기가 감지되었습니다. 무대 보존 모드를 권장합니다. "
            "베트남이 이미 무대인 공동제작 원고라면 SETTINGS의 '공동제작 — 무대 보존'을 켜 주세요. "
            "지금 상태(끔)로 실행하면 무대가 타겟 지역으로 옮겨집니다."
        )

_unmapped_names = []
if source_text.strip() and (preserve_setting or selected_region["id"] == "vn"):
    _unmapped_names = find_unmapped_korean_names(source_text, char_map, loc_map)

if _unmapped_names:
    _vn_relocate = (selected_region["id"] == "vn" and not preserve_setting)
    with st.expander(f"🔤 대조표에 없는 인물 이름 {len(_unmapped_names)}명 — 실행 전 확인 권장",
                     expanded=True):
        st.caption("대사 큐에 쓰인 한글 이름 중 대조표에 없는 이름입니다: "
                   + ", ".join(f"{n}({c})" for n, c in _unmapped_names[:40]))
        if not _vn_relocate:
            st.warning(
                "베트남 인물이면 대조표에 원어 표기를 넣어 주세요 (예: 린,LINH / 투안,TUAN). "
                "한글 음차는 원어로 정확히 되돌릴 수 없어서(린 → Linh일 수도, Lin일 수도 있음) "
                "대조표가 없으면 엔진이 가장 흔한 표기를 고릅니다. 한국인 인물은 그대로 두셔도 됩니다."
            )
        else:
            st.markdown(
                "**베트남 현지화** — 한국 인물이 베트남 인물이 됩니다. 페이지마다 다른 이름이 붙지 않도록 "
                "실행 전에 이름을 한 번 정해 대조표로 고정하는 것을 권장합니다."
            )
            if api_key and st.button("🇻🇳 베트남 이름 후보 만들기 (Sonnet 1회 호출)",
                                     key="btn_vn_names", use_container_width=True):
                _names = [n for n, _ in _unmapped_names[:60]]
                _ctx = collect_name_context(source_text, _names)
                _req = "\n\n".join(
                    f"{n}\n" + "\n".join(f"  {ln}" for ln in _ctx.get(n, [])) for n in _names
                )
                try:
                    _raw = call_api(
                        make_client(api_key), _req, build_vn_name_suggest_prompt(),
                        MODEL_POLICY["stage_1"]["model"], max_tokens=8000,
                    )
                    _rows = parse_vn_name_candidates(_raw, _names)
                    if _rows:
                        st.session_state["vn_name_candidates"] = _rows
                    else:
                        st.error("이름 후보를 읽지 못했습니다. 다시 실행해 주세요.")
                except Exception as e:
                    st.error(f"❌ 이름 후보 생성 오류: {e}")

        _cands = st.session_state.get("vn_name_candidates")
        if _vn_relocate and _cands:
            import pandas as pd
            st.caption("영문 큐(대사 헤드에 쓰일 이름)를 직접 고칠 수 있습니다. "
                       "확정하면 대조표처럼 Stage 1~6에 적용됩니다.")
            _edited = st.data_editor(
                pd.DataFrame(_cands), key="vn_name_editor",
                hide_index=True, num_rows="fixed",
                disabled=["한국이름"],
            )
            _rows_now = _edited.to_dict("records")
            _cue_list = [str(r.get("영문 큐") or "").strip().upper() for r in _rows_now]
            _dups = sorted({c for c in _cue_list if c and _cue_list.count(c) > 1})
            if _dups:
                st.warning("같은 영문 큐가 두 인물에 붙어 있습니다: " + ", ".join(_dups))
            cb1, cb2 = st.columns(2)
            with cb1:
                if st.button("✅ 이 이름으로 확정 (대조표에 추가)", key="btn_vn_names_apply",
                             use_container_width=True):
                    st.session_state["vn_name_overrides"] = {
                        str(r["한국이름"]).strip(): str(r.get("영문 큐") or "").strip().upper()
                        for r in _rows_now if str(r.get("영문 큐") or "").strip()
                    }
                    st.rerun()
            with cb2:
                _csv = io.StringIO()
                _w = csv.writer(_csv)
                _w.writerow(["한국이름", "영어이름", "톤태그"])
                for r in _rows_now:
                    _w.writerow([r.get("한국이름"), str(r.get("영문 큐") or "").upper(), ""])
                st.download_button("💾 대조표 CSV로 저장 (다음 작업에 재사용)",
                                   data=_csv.getvalue().encode("utf-8-sig"),
                                   file_name="vn_character_map.csv", mime="text/csv",
                                   use_container_width=True, key="dl_vn_names")

if st.session_state.get("vn_name_overrides"):
    if st.button("↩️ 확정한 베트남 이름 해제", key="btn_vn_names_clear"):
        st.session_state.pop("vn_name_overrides", None)
        st.rerun()

# ── Initialize session state for each stage ──
for key in ["stage_1_result", "stage_2_result", "stage_3_result", "stage_4_result",
            "stage_5_result", "stage_6_result"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ═══════════════════════════════════════════════════
# ★ v2.3.2 — 진행 상황 · 완료 표시
# ═══════════════════════════════════════════════════
_STAGE_LABELS = {1: "번역", 2: "포맷", 3: "문체", 4: "대사", 5: "QA", 6: "최종"}
_VERDICT_KO = {
    "PASS": ("제출 가능", "verdict-pass"),
    "MINOR REVISION": ("경미한 수정 권장", "verdict-minor"),
    "MAJOR REVISION": ("대폭 수정 필요", "verdict-major"),
}


def parse_qa_summary(report: str) -> tuple:
    """QA 리포트에서 점수와 판정을 뽑는다. 없으면 (None, None)."""
    if not report:
        return None, None
    m_score = re.search(r"SCORE:\s*\[?(\d+(?:\.\d+)?)\]?\s*/\s*10", report, re.IGNORECASE)
    m_rec = re.search(r"RECOMMENDATION:\s*\[?\s*(PASS|MINOR REVISION|MAJOR REVISION)",
                      report, re.IGNORECASE)
    score = m_score.group(1) if m_score else None
    rec = m_rec.group(1).upper() if m_rec else None
    return score, rec


def pipeline_status() -> dict:
    done = [n for n in range(1, 7) if st.session_state.get(f"stage_{n}_result")]
    nxt = next((n for n in range(1, 7) if n not in done), None)
    score, rec = parse_qa_summary(st.session_state.get("stage_5_result") or "")
    src_scenes = st.session_state.get("source_scene_count") or 0
    s1 = st.session_state.get("stage_1_result") or ""
    tr_scenes = len(set(_SCENE_NUM_RE.findall(s1))) if s1 else 0
    final = (st.session_state.get("stage_6_result")
             or st.session_state.get("stage_4_result") or "")
    return {"done": done, "next": nxt, "complete": len(done) == 6,
            "score": score, "rec": rec, "src_scenes": src_scenes,
            "tr_scenes": tr_scenes, "final_len": len(final)}


def render_status_board(where: str = "top"):
    """5단계 진행 배지 + 완료/진행 배너."""
    stt = pipeline_status()
    badges = "".join(
        f'<span class="stage-badge {"stage-done" if n in stt["done"] else ("stage-active" if n == stt["next"] else "stage-pending")}">'
        f'{"✓" if n in stt["done"] else n} {_STAGE_LABELS[n]}</span>'
        for n in range(1, 7)
    )

    if stt["complete"]:
        parts = ["6단계 모두 끝났습니다 — QA 자동 반영본이 최종 원고입니다"]
        if stt["src_scenes"] and stt["tr_scenes"]:
            if stt["tr_scenes"] >= stt["src_scenes"]:
                parts.append(f"원작 씬 {stt['src_scenes']}개 전부 번역")
            else:
                parts.append(f"⚠️ 씬 {stt['tr_scenes']}/{stt['src_scenes']}")
        if stt["final_len"]:
            parts.append(f"최종 원고 {stt['final_len']:,}자")
        verdict = ""
        if stt["score"]:
            parts.append(f"QA {stt['score']}/10 (자동 반영 전 기준)")
        if stt["rec"] in _VERDICT_KO:
            ko, css = _VERDICT_KO[stt["rec"]]
            verdict = f' · 판정 <span class="{css}">{ko} ({stt["rec"]})</span>'
        tail = ("<br>아래 FINAL OUTPUT에서 최종 DOCX를 받으세요." if where == "top"
                else "<br>서식·표기 통일은 반영됐습니다. 대사 표현·설정 관련 QA 제안은 작가 판단 사항으로 남겨 두었습니다.")
        st.markdown(
            f'<div class="done-banner"><div class="big">✅ 번역 완료</div>'
            f'<div class="sub">{" · ".join(parts)}{verdict}{tail}</div>'
            f'<div style="margin-top:0.5rem">{badges}</div></div>',
            unsafe_allow_html=True,
        )
    elif stt["done"]:
        nxt = stt["next"]
        st.markdown(
            f'<div class="progress-banner"><div class="big">⏳ 진행 중 — {len(stt["done"])}/6 단계 완료</div>'
            f'<div class="sub">다음 할 일: Stage {nxt} ({_STAGE_LABELS[nxt]}) 실행</div>'
            f'<div style="margin-top:0.5rem">{badges}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f'<div style="margin:0.4rem 0 0.8rem 0">{badges}</div>', unsafe_allow_html=True)


def stage_title(n: int, title: str):
    """단계 제목 옆에 완료 표시."""
    mark = " ✅ 완료" if st.session_state.get(f"stage_{n}_result") else ""
    st.markdown(f"### {title}{mark}")


render_status_board("top")

# Helper: Show stage result with download
def show_stage_result(stage_num: int, stage_name: str, result_key: str):
    """Display stage result with download button."""
    result = st.session_state.get(result_key)
    if result:
        with st.expander(f"📄 Stage {stage_num} 결과 — {stage_name}", expanded=False):
            st.text(result[:5000] + ("..." if len(result) > 5000 else ""))
        st.download_button(
            f"💾 Stage {stage_num} 결과 저장 (TXT)",
            data=result.encode("utf-8"),
            file_name=f"stage_{stage_num}_{stage_name.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            key=f"dl_stage_{stage_num}",
        )

# Helper: Upload previous stage result
def upload_previous_result(stage_num: int, prev_stage_name: str, result_key: str):
    """Allow uploading previous stage result to continue pipeline."""
    prev_result = st.session_state.get(result_key)
    if prev_result:
        st.success(f"✅ 이전 단계 결과 있음 ({len(prev_result):,}자) — 자동 연결됩니다.")
        return prev_result
    else:
        st.info(f"💡 이전 단계({prev_stage_name}) 결과가 없으면 파일을 업로드하세요.")
        prev_file = st.file_uploader(
            f"Stage {stage_num - 1} 결과 파일 업로드",
            type=["txt"],
            key=f"prev_upload_{stage_num}",
        )
        if prev_file:
            text = prev_file.read().decode("utf-8", errors="replace")
            st.success(f"✅ 파일 로드 완료 — {len(text):,}자")
            return text
    return None


# ═══════════════════════════════════════════════════
# STAGE 1: Raw Translation
# ═══════════════════════════════════════════════════
st.markdown("---")
stage_title(1, "① Raw Translation (Sonnet)")
st.caption("한국어 → 영어 직역. 충실한 번역이 목표.")

if can_run:
    if st.button("▶️ Stage 1 실행", key="btn_stage1", use_container_width=True):
        client = make_client(api_key)
        region_id = selected_region["id"]

        _ml = is_multilingual()   # ★ v2.5.0
        system_prompt = build_stage1_prompt(
            region_id=region_id,
            char_map=char_map,
            style_prompt=selected_style["prompt"],
            custom_instructions=custom_instructions,
            loc_map=loc_map,
            preserve_setting=preserve_setting,   # ★ v2.5.0
            multilingual=_ml,                    # ★ v2.5.0
        )
        model_id = MODEL_POLICY["stage_1"]["model"]
        pages = split_into_pages(source_text)

        progress_bar = st.progress(0)
        status_area = st.empty()

        results = run_stage_on_pages(
            client, pages, system_prompt, model_id,
            "Stage 1: Raw Translation", progress_bar, status_area,
            max_tokens=MODEL_POLICY["stage_1"]["max_tokens"],
            stage_key="stage_1", check_mode="ko2en",
            lang_check=_ml,                      # ★ v2.5.0
        )

        if results is not None:
            st.session_state["stage_1_result"] = "\n\n".join(results)
            st.session_state["source_sig"] = text_signature(source_text)
            st.session_state["source_scene_count"] = count_scenes(source_text)
            clear_downstream(1)
            status_area.markdown('<div class="progress-text">✅ Stage 1 완료!</div>', unsafe_allow_html=True)
            st.rerun()

show_stage_result(1, "Raw Translation", "stage_1_result")


# ═══════════════════════════════════════════════════
# STAGE 2: Format Conversion
# ═══════════════════════════════════════════════════
st.markdown("---")
stage_title(2, "② Format Conversion (규칙 기반)")
st.caption("S#번호 제거, 한국식 지시어 → 영어 표준 변환. API 호출 없음 (무료).")

stage_2_input = st.session_state.get("stage_1_result")
if stage_2_input:
    if st.button("▶️ Stage 2 실행", key="btn_stage2", use_container_width=True):
        region_id = selected_region["id"]
        st.session_state["stage_2_result"] = apply_format_conversion(stage_2_input, region_id)
        clear_downstream(2)
        st.rerun()
elif st.session_state.get("stage_2_result") is None:
    st.caption("⏳ Stage 1을 먼저 완료하세요.")

show_stage_result(2, "Format", "stage_2_result")


# ═══════════════════════════════════════════════════
# STAGE 3: Voice Rewrite
# ═══════════════════════════════════════════════════
st.markdown("---")
stage_title(3, "③ Voice Rewrite (Opus)")
st.caption("번역체 제거, 네이티브 문체로 리라이트. 가장 시간과 비용이 많이 드는 단계.")

stage_3_input = upload_previous_result(3, "Stage 2 Format", "stage_2_result")
if stage_3_input and api_key:
    if st.button("▶️ Stage 3 실행", key="btn_stage3", use_container_width=True):
        client = make_client(api_key)
        region_id = selected_region["id"]

        _ml = is_multilingual(stage_3_input)   # ★ v2.5.0
        system_prompt = build_stage3_prompt(
            region_id=region_id,
            char_map=char_map,
            char_tones=char_tones,
            style_prompt=selected_style["prompt"],
            custom_instructions=custom_instructions,
            loc_map=loc_map,
            preserve_setting=preserve_setting,   # ★ v2.5.0
            multilingual=_ml,                    # ★ v2.5.0
        )
        model_id = MODEL_POLICY["stage_3"]["model"]
        pages = split_into_pages(stage_3_input)

        progress_bar = st.progress(0)
        status_area = st.empty()

        results = run_stage_on_pages(
            client, pages, system_prompt, model_id,
            "Stage 3: Voice Rewrite", progress_bar, status_area,
            max_tokens=MODEL_POLICY["stage_3"]["max_tokens"],
            stage_key="stage_3", check_mode="en2en",
            lang_check=_ml,                      # ★ v2.5.0
        )

        if results is not None:
            st.session_state["stage_3_result"] = "\n\n".join(results)
            clear_downstream(3)
            status_area.markdown('<div class="progress-text">✅ Stage 3 완료!</div>', unsafe_allow_html=True)
            st.rerun()
elif st.session_state.get("stage_3_result") is None:
    st.caption("⏳ Stage 2를 먼저 완료하세요.")

show_stage_result(3, "Voice Rewrite", "stage_3_result")


# ═══════════════════════════════════════════════════
# STAGE 4: Dialogue Polish
# ═══════════════════════════════════════════════════
st.markdown("---")
stage_title(4, "④ Dialogue Polish (Opus)")
st.caption("대사 전문 폴리시. 캐릭터 톤 태그 반영.")

stage_4_input = upload_previous_result(4, "Stage 3 Voice Rewrite", "stage_3_result")
if stage_4_input and api_key:
    if st.button("▶️ Stage 4 실행", key="btn_stage4", use_container_width=True):
        client = make_client(api_key)
        region_id = selected_region["id"]

        _ml = is_multilingual(stage_4_input)   # ★ v2.5.0
        system_prompt = build_stage4_prompt(
            region_id=region_id,
            char_map=char_map,
            char_tones=char_tones,
            style_prompt=selected_style["prompt"],
            custom_instructions=custom_instructions,
            loc_map=loc_map,
            preserve_setting=preserve_setting,   # ★ v2.5.0
            multilingual=_ml,                    # ★ v2.5.0
        )
        model_id = MODEL_POLICY["stage_4"]["model"]
        pages = split_into_pages(stage_4_input)

        progress_bar = st.progress(0)
        status_area = st.empty()

        results = run_stage_on_pages(
            client, pages, system_prompt, model_id,
            "Stage 4: Dialogue Polish", progress_bar, status_area,
            max_tokens=MODEL_POLICY["stage_4"]["max_tokens"],
            stage_key="stage_4", check_mode="en2en",
            lang_check=_ml,                      # ★ v2.5.0
        )

        if results is not None:
            st.session_state["stage_4_result"] = "\n\n".join(results)
            clear_downstream(4)
            status_area.markdown('<div class="progress-text">✅ Stage 4 완료!</div>', unsafe_allow_html=True)
            st.rerun()
elif st.session_state.get("stage_4_result") is None:
    st.caption("⏳ Stage 3를 먼저 완료하세요.")

show_stage_result(4, "Dialogue Polish", "stage_4_result")


# ═══════════════════════════════════════════════════
# STAGE 5: QA Check
# ═══════════════════════════════════════════════════
st.markdown("---")
stage_title(5, "⑤ QA Check (Sonnet)")
st.caption("최종 품질 검증. 포맷/일관성/언어/스토리 체크리스트.")

stage_5_input = upload_previous_result(5, "Stage 4 Dialogue Polish", "stage_4_result")
if stage_5_input and api_key:
    if st.button("▶️ Stage 5 실행", key="btn_stage5", use_container_width=True):
        client = make_client(api_key)
        region_id = selected_region["id"]

        system_prompt = build_stage5_prompt(
            region_id=region_id,
            char_map=char_map,
            loc_map=loc_map,
            preserve_setting=preserve_setting,             # ★ v2.5.0
            multilingual=is_multilingual(stage_5_input),   # ★ v2.5.0
        )
        model_id = MODEL_POLICY["stage_5"]["model"]

        status_area = st.empty()
        status_area.markdown(
            '<div class="progress-text">🔍 QA 검증 중...</div>',
            unsafe_allow_html=True
        )

        try:
            # ★ v2.3.0 — 원고 전체를 검토한다 (앞뒤만 잘라 보내던 방식 폐기)
            qa_input = stage_5_input
            _exp = st.session_state.get("source_scene_count") or 0
            _qa_info = (f"Expected scene count from the Korean original: {_exp}"
                        if _exp else "")

            qa_report = call_api(
                client, qa_input, system_prompt,
                model_id, max_tokens=MODEL_POLICY["stage_5"]["max_tokens"],
                page_info=_qa_info,
            )
            st.session_state["stage_5_result"] = qa_report
            status_area.markdown('<div class="progress-text">✅ Stage 5 완료!</div>', unsafe_allow_html=True)
            st.rerun()
        except Exception as e:
            st.error(f"❌ QA 오류: {e}")
elif st.session_state.get("stage_5_result") is None:
    st.caption("⏳ Stage 4를 먼저 완료하세요.")

# Show QA report
if st.session_state.get("stage_5_result"):
    st.markdown("**🔍 QA Report**")
    st.markdown(f'<div class="qa-box">{st.session_state["stage_5_result"]}</div>', unsafe_allow_html=True)
    st.download_button(
        "💾 QA Report 저장 (TXT)",
        data=st.session_state["stage_5_result"].encode("utf-8"),
        file_name="qa_report.txt",
        mime="text/plain",
        use_container_width=True,
        key="dl_qa",
    )


# ═══════════════════════════════════════════════════
# ★ v2.4.0 — STAGE 6: Final Revision (QA 자동 반영)
# ═══════════════════════════════════════════════════
st.markdown("---")
stage_title(6, "⑥ Final Revision — QA 자동 반영 (Sonnet)")
st.caption(
    "QA 지적 중 서식·표기 통일 항목만 자동으로 고쳐 최종 원고를 만듭니다 "
    "(씬 헤딩·장소명·용어·시각 표기·대시·(CONT'D)·인물 대문자·레이아웃). "
    "대사 표현·농담·설정·타임라인 제안은 반영하지 않습니다."
)

_s6_src = st.session_state.get("stage_4_result")
_s6_qa = st.session_state.get("stage_5_result")
if _s6_src and _s6_qa and api_key:
    if st.button("▶️ Stage 6 실행 — 최종 원고 만들기", key="btn_stage6", use_container_width=True):
        client = make_client(api_key)
        region_id = selected_region["id"]
        policy = MODEL_POLICY["stage_6"]
        status_area = st.empty()
        progress_bar = st.progress(0)

        # ① 규칙 기반 정리 (무료)
        base_text = normalize_layout(_s6_src)

        # ② 표기 통일 기준표 (한 번만 만들고 재실행 시 재사용)
        style_sheet = st.session_state.get("stage_6_style_sheet")
        if not style_sheet:
            status_area.markdown('<div class="progress-text">📐 표기 통일 기준표 작성 중...</div>',
                                 unsafe_allow_html=True)
            try:
                heads = "\n".join(scene_heading_list(base_text))
                style_sheet = call_api(
                    client,
                    f"## QA REPORT\n{_s6_qa}\n\n## SCENE HEADINGS (in order)\n{heads}",
                    build_stage6_style_prompt(region_id, loc_map=loc_map,
                                              preserve_setting=preserve_setting),  # ★ v2.5.0
                    policy["model"],
                    max_tokens=policy.get("style_max_tokens", 16000),
                )
                st.session_state["stage_6_style_sheet"] = style_sheet
            except Exception as e:
                st.error(f"❌ 기준표 작성 오류: {e}")
                style_sheet = None

        # ③ 페이지별 기계적 수정
        if style_sheet:
            _ml6 = is_multilingual(base_text)   # ★ v2.5.0
            system_prompt = build_stage6_fix_prompt(
                region_id, style_sheet, qa_report=_s6_qa, loc_map=loc_map,
                preserve_setting=preserve_setting,   # ★ v2.5.0
                multilingual=_ml6,                   # ★ v2.5.0
            )
            pages = split_into_pages(base_text)
            notes, pos = [], 0
            for pg in pages:
                _at = base_text.find(pg[:200], pos)
                _at = _at if _at >= 0 else pos
                intro = introduced_before(base_text, _at, char_map)
                notes.append(
                    "ALREADY INTRODUCED (normal case in action lines): " + ", ".join(intro)
                    if intro else "No character has been introduced before this page"
                )
                pos = _at + len(pg)
            locked = [f.get("en") for f in (loc_map.get("fixed_lines") or []) if f.get("en")]

            results = run_stage_on_pages(
                client, pages, system_prompt, policy["model"],
                "Stage 6: Final Revision", progress_bar, status_area,
                max_tokens=policy["max_tokens"],
                stage_key="stage_6", check_mode="fix",
                page_notes=notes, locked=locked,
                lang_check=_ml6,                     # ★ v2.5.0
            )
            if results is not None:
                st.session_state["stage_6_result"] = normalize_layout("\n\n".join(results))
                for k in ("audit_report", "enforced_result", "enforce_log"):
                    st.session_state.pop(k, None)
                status_area.markdown('<div class="progress-text">✅ Stage 6 완료 — 최종 원고가 만들어졌습니다!</div>',
                                     unsafe_allow_html=True)
                st.rerun()
elif st.session_state.get("stage_6_result") is None:
    st.caption("⏳ Stage 5 (QA)를 먼저 완료하세요.")

if st.session_state.get("stage_6_style_sheet"):
    with st.expander("📐 표기 통일 기준표 (Stage 6이 따른 기준)", expanded=False):
        st.text(st.session_state["stage_6_style_sheet"])
show_stage_result(6, "Final Revision", "stage_6_result")


# ═══════════════════════════════════════════════════
# ★ v2.2 — LOCALIZATION AUDIT (용어집 잔존 검수)
# ═══════════════════════════════════════════════════
st.markdown("---")
st.markdown("### 🔎 LOCALIZATION AUDIT — 로컬라이징 검수")
st.caption("대조표가 실제로 반영됐는지 기계적으로 대조합니다. 한국 지명·기관·통화 잔존을 잡아냅니다.")

_audit_source = (
    st.session_state.get("stage_6_result")   # ★ v2.4.0
    or st.session_state.get("stage_4_result")
    or st.session_state.get("stage_3_result")
    or st.session_state.get("stage_2_result")
    or st.session_state.get("stage_1_result")
)

# ★ v2.5.0 — 언어 괄호 대조 (대조표 없이도 동작 · 표시만 하고 자동 수정하지 않음)
if _audit_source and source_text.strip() and _lang_counts_src:
    _lt = check_language_tags(source_text, _audit_source, src_is_korean=True)
    st.markdown("**🌐 언어 표기 대조 — 원고 (베트남어)·(영어) ↔ 결과 (in Vietnamese)·(in English)**")
    st.table([{"언어": lang, "원고": a, "결과": b, "판정": "✅ 일치" if a == b else "❌ 불일치"}
              for lang, a, b in _lt["totals"]])
    if _lt["scenes"]:
        st.error("씬별로 언어 괄호 수가 다른 곳이 있습니다 (씬 헤딩 순서 기준).")
        st.table([{"씬 순번": i, "씬 헤딩": h, "언어": lang, "원고": a, "결과": b}
                  for i, h, lang, a, b in _lt["scenes"][:60]])
    elif not _lt["scene_compare"]:
        st.caption("원고와 결과의 씬 수가 달라 씬별 대조는 건너뛰고 전체 수만 비교했습니다.")
    elif _lt["ok"]:
        st.caption("모든 씬에서 언어 괄호 수가 원고와 같습니다.")

if not (char_map or count_loc_entries(loc_map)):
    st.caption("⏳ 대조표를 먼저 업로드하세요.")
elif not _audit_source:
    st.caption("⏳ 번역 결과가 있어야 검수할 수 있습니다.")
else:
    if preserve_setting:   # ★ v2.5.0
        st.caption("🤝 무대 보존 모드 — 한국 장면의 지명·원화·문화어는 정상으로 보고 점검하지 않습니다. "
                   "한글 원문 잔존·통화 혼용·제작사 표기는 계속 점검합니다.")
    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🔎 검수 실행", key="btn_audit", use_container_width=True):
            st.session_state["audit_report"] = check_glossary_residue(
                _audit_source, char_map, loc_map,
                preserve_setting=preserve_setting,   # ★ v2.5.0
            )
            # ★ v2.5.0 — 이름 성조 부호 혼용 (Tuan ↔ Tuấn)
            st.session_state["audit_report"]["diacritics"] = check_name_diacritics(
                _audit_source, char_map)

    with col_b:
        if st.button("🛠 오표기 강제 치환", key="btn_enforce", use_container_width=True):
            fixed, log = apply_glossary_enforcement(_audit_source, loc_map)
            st.session_state["enforced_result"] = fixed
            st.session_state["enforce_log"] = log

    # ── 검수 리포트 ──
    report = st.session_state.get("audit_report")
    if report:
        n_unapplied = len(report["unapplied"])
        n_residue = sum(cnt for _, _, cnt in report["residue"])
        n_corr = len(report["corrections_left"])

        m1, m2, m3 = st.columns(3)
        m1.metric("한국어 원문 잔존", n_unapplied)
        m2.metric("패턴 잔존 건수", n_residue)
        m3.metric("오표기 잔존", n_corr)

        if report["unapplied"]:
            st.error("**대조표 항목이 한국어 그대로 남아 있습니다**")
            st.table([
                {"분류": g, "한국어": ko, "적용되어야 할 영문": en}
                for ko, en, g in report["unapplied"][:60]
            ])

        if report["residue"]:
            st.warning("**한국 고유 요소 패턴이 검출되었습니다**")
            st.table([
                {"유형": label, "검출 예": ", ".join(samples), "건수": cnt}
                for label, samples, cnt in report["residue"]
            ])

        if report["corrections_left"]:
            st.warning("**이전 판 오표기가 남아 있습니다** — 아래 '오표기 강제 치환'으로 정리할 수 있습니다")
            st.table([
                {"오표기": bad, "확정 표기": good, "건수": n}
                for bad, good, n in report["corrections_left"][:60]
            ])

        if report["missing"]:
            with st.expander(f"⚠️ 확정 영문이 한 번도 등장하지 않은 항목 ({len(report['missing'])}건)", expanded=False):
                st.caption("원고에 해당 인물·장소가 아예 안 나오는 경우일 수도 있습니다. 참고용입니다.")
                st.table([
                    {"분류": g, "한국어": ko, "확정 영문": en}
                    for ko, en, g in report["missing"][:80]
                ])

        if report.get("diacritics"):   # ★ v2.5.0
            st.warning("**이름 표기가 성조 부호 유무로 섞여 있습니다** — 대조표 표기로 통일해 주세요")
            st.table([{"대조표 표기": en, "원고에 섞인 다른 표기": ", ".join(v)}
                      for en, v in report["diacritics"]])

        if not (report["unapplied"] or report["residue"] or report["corrections_left"]
                or report.get("diacritics")):
            st.success("✅ 검출된 문제가 없습니다. 로컬라이징이 일관되게 적용되었습니다.")

    # ── 강제 치환 결과 ──
    if st.session_state.get("enforced_result"):
        log = st.session_state.get("enforce_log") or []
        if log:
            st.success(f"✅ {len(log)}종 · 총 {sum(n for _, _, n in log)}건 치환했습니다.")
            st.table([
                {"오표기": bad, "확정 표기": good, "건수": n}
                for bad, good, n in log
            ])
        else:
            st.info("치환할 오표기가 없습니다.")

        st.download_button(
            "💾 치환본 저장 (TXT)",
            data=st.session_state["enforced_result"].encode("utf-8"),
            file_name="localized_enforced.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_enforced",
        )
        if st.button("↪️ 치환본을 최신 결과로 반영", key="btn_apply_enforced", use_container_width=True):
            for _k in ["stage_6_result", "stage_4_result", "stage_3_result", "stage_2_result", "stage_1_result"]:
                if st.session_state.get(_k):
                    st.session_state[_k] = st.session_state["enforced_result"]
                    break
            st.session_state["enforced_result"] = None
            st.session_state["enforce_log"] = None
            st.session_state["audit_report"] = None
            st.rerun()


# ═══════════════════════════════════════════════════
# FINAL OUTPUT — DOCX
# ═══════════════════════════════════════════════════

# Determine the latest completed result for DOCX
final_result = (
    st.session_state.get("stage_6_result")   # ★ v2.4.0
    or st.session_state.get("stage_4_result")
    or st.session_state.get("stage_3_result")
    or st.session_state.get("stage_2_result")
    or st.session_state.get("stage_1_result")
)

if final_result:
    st.markdown("---")
    st.markdown('<div class="section-header">📤 FINAL OUTPUT — 최종 다운로드</div>', unsafe_allow_html=True)

    # Build filename with project title
    title_slug = st.session_state.get("project_title", "").strip()
    if title_slug:
        # 안전한 파일명으로 변환
        title_slug = re.sub(r'[^\w\s\-]', '', title_slug).strip()
        title_slug = re.sub(r'[\s]+', '_', title_slug)
        base_filename = f"Screenplay_{title_slug}_translated"
    else:
        base_filename = "Screenplay_translated"

    # ★ v2.5.0 — 언어 표기가 있는 원고: 첫 페이지 언어 노트 1회 (다운로드 파일에만 넣는다)
    _note_lang = base_dialogue_language(selected_region["id"], preserve_setting)
    if is_multilingual(final_result) and _note_lang:
        final_result = apply_language_note(final_result, _note_lang, subtitled=preserve_setting)
        st.caption(f"🌐 다운로드 파일 첫머리에 언어 노트를 넣었습니다 — "
                   f"\"{final_result.split(chr(10), 1)[0]}\"")

    # ★ v2.3.2 — 완료 배너
    if pipeline_status()["complete"]:
        render_status_board("final")

    # Show which stage this is from
    if st.session_state.get("stage_6_result"):
        st.caption("✅ Stage 6 (Final Revision — QA 자동 반영) 최종 원고 기준")
    elif st.session_state.get("stage_4_result"):
        st.caption("✅ Stage 4 (Dialogue Polish) 결과 기준")
    elif st.session_state.get("stage_3_result"):
        st.caption("⚠️ Stage 3 (Voice Rewrite) 결과 기준 — Stage 4 미완료")
    elif st.session_state.get("stage_2_result"):
        st.caption("⚠️ Stage 2 (Format) 결과 기준 — Stage 3~4 미완료")
    else:
        st.caption("⚠️ Stage 1 (Raw Translation) 결과 기준 — 추가 폴리시 권장")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📥 TXT 다운로드",
            data=final_result.encode("utf-8"),
            file_name=f"{base_filename}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_final_txt",
        )

    with col2:
        try:
            docx_bytes = generate_docx(final_result)
            st.download_button(
                "📥 DOCX 다운로드 (할리우드 포맷)",
                data=docx_bytes,
                file_name=f"{base_filename}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="dl_final_docx",
            )
        except Exception as e:
            st.error(f"DOCX 생성 오류: {e}")

    # Reset button
    st.markdown("")
    if st.button("🗑️ 전체 초기화 (새 프로젝트)", use_container_width=True):
        for key in ["stage_1_result", "stage_2_result", "stage_3_result",
                     "stage_4_result", "stage_5_result", "last_error",
                     # ★ v2.3.0
                     "partial_stage_1", "partial_stage_3", "partial_stage_4",
                     "source_sig", "source_scene_count",
                     # ★ v2.4.0
                     "stage_6_result", "stage_6_style_sheet", "partial_stage_6",
                     "audit_report", "enforced_result", "enforce_log",
                     # ★ v2.5.0
                     "vn_name_overrides", "vn_name_candidates", "lang_tags_detected"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Show last error if any
if "last_error" in st.session_state:
    st.error(st.session_state["last_error"])


# ── Footer ──
st.markdown(f"""
<div class="footer">
    BLUE JEANS PICTURES — English-Translator v{VERSION}<br>
    5-Stage Native Polish Pipeline · Powered by Anthropic Claude API
</div>
""", unsafe_allow_html=True)

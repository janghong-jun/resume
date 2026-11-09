#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
장홍준 이력서 / 포트폴리오 / 자기소개서 / 입사지원서 PDF 빌드 스크립트 (v6)

사용법
    pip install weasyprint
    python build_pdf.py
    python build_pdf.py --only resume
    python build_pdf.py --out ./dist

PDF만 생성하며 HTML 중간 파일은 저장하지 않습니다.
문서별 페이지 배치, 여백, 글자 크기, 표와 카드의 페이지 분할을 조정합니다.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# ============================================================== 1. CONFIG
NAME = "장홍준"
ROLE = "Frontend UI Developer"
TAGLINE = "React · Next.js · TypeScript · Vue · Web Accessibility"
SITE_URL = "https://janghong-jun.github.io/resume/"
SITE_LABEL = "janghong-jun.github.io/resume"
PRODUCTIVITY = "하루 평균 6~8페이지, 최대 20~30페이지"
YEARS_LABEL = "13년 이상"
FONT_STACK = (
    "'Noto Sans CJK KR','Noto Sans KR','Pretendard',"
    "'Malgun Gothic','Apple SD Gothic Neo',sans-serif"
)
SECTORS = {"finance": "금융 · 보험", "public": "공공", "enterprise": "일반 기업 · 기타"}
EXPECTED = {"total": 40, "finance": 12, "public": 8, "enterprise": 24, "react": 3, "vue": 2}


# ============================================================== 2. CONTENT
@dataclass(frozen=True)
class Featured:
    role_full: str
    share: str
    stack: tuple[str, ...]
    duties: tuple[str, ...]
    results: tuple[str, ...]
    period_note: str = ""
    a11y100: bool = False


@dataclass(frozen=True)
class Project:
    period: str
    client: str
    title: str
    role: str
    sector: str
    framework: str = ""
    featured: Featured | None = None

F_HANWHA = Featured(
    role_full="React UI 개발 (PA)", share="융자모바일 100% (단독 진행)", period_note=" (예정, 진행 중)", a11y100=True,
    stack=("React 19", "TypeScript", "Vite", "pnpm", "TanStack Router", "Radix UI",
           "Tailwind CSS", "SCSS Modules", "Storybook", "ESLint", "Lighthouse"),
    duties=(
        "융자모바일 UI 개발 단독 수행 (프로젝트 초기 세팅부터 실무 UI 개발까지)",
        "React 19·TypeScript·Vite·pnpm 기반 개발환경 구성",
        "TanStack Router 기반 라우팅 및 Storybook 기반 컴포넌트 관리 환경 구성",
        "디자인 시스템 재구성 및 공통 컴포넌트 **37종(업무 로직 포함 7종)** 설계·구현 (검색·분류 선택 등)",
        "외부 데이터 주입만으로 다양한 화면에서 재사용할 수 있도록 UI와 처리 로직 분리",
        "제작한 컴포넌트를 기반으로 ODS(디자인 시스템) 구성",
        "UI 상태 변화에 따른 애니메이션 인터랙션 구현",
        "웹 접근성을 고려한 UI 구현 및 Lighthouse 기반 검수, 점검 결과 문서화",
        "관리자 화면은 as-is 소스를 활용하여 오류 수정 및 대응",
    ),
    results=(
        "반복적으로 구현되는 업무 UI를 공통 컴포넌트 37종으로 구성해 프로젝트 전반의 화면에서 재사용할 수 있는 구조 마련",
        "데이터와 UI 처리 로직을 분리해 컴포넌트의 확장성과 활용성 확보",
        "제작한 컴포넌트가 ODS(디자인 시스템)의 기반으로 활용되어 후속 UI 개발 기반 마련",
        "**WBS 기준 개발 일정 약 1개월 반 단축**에 기여",
        "프로젝트 전체 파일 기준 화면별 검수를 통해 Lighthouse Accessibility 100점 달성",
    ),
)
F_GYEONGGI = Featured(
    role_full="UI 개발 (단독 수행)", share="100%", a11y100=True,
    stack=("Thymeleaf", "HTML", "CSS", "KRDS", "KWCAG 2.2", "Lighthouse"),
    duties=("UI 개발 전반 단독 수행", "KRDS 적용 및 KWCAG 2.2를 고려한 화면 구현",
            "Thymeleaf 기반 화면 개발 및 반응형 UI 구현", "마크업·레이아웃 오류 개선",
            "Lighthouse 기반 웹 접근성 검수 및 점검 결과 문서화"),
    results=("UI 개발 전반을 단독 수행하며 화면 구현부터 품질 검수까지 담당",
             "웹 접근성 점검 대응 및 UI 개발 가이드 작성",
             "프로젝트 전체 파일 기준 Lighthouse Accessibility 100점 달성"),
)
F_MIRAE = Featured(
    role_full="React UI 개발 (단독 수행)", share="100%", stack=("React", "Next.js"),
    duties=("ChatGPT 스타일의 생성형 AI 대화 서비스 UI 개발",
            "LLM 입력 상황(대기·스트리밍·오류·입력 중 등)별 인터랙션 UI 구현",
            "React 기반 화면 및 사용자 인터랙션 개발",
            "React 경험이 없는 백엔드 개발자 참여자에게 데이터 바인딩 위치 가이드 제공"),
    results=("생성형 AI 대화형 서비스의 UI 개발 전반 단독 수행",
             "LLM 입력 상황별 인터랙션 UI를 단독 구현",
             "React 경험이 없는 백엔드 개발자 **2명**에게 데이터 바인딩 가이드를 제공해 UI와 데이터 연동 작업 지원"),
)
F_DONGYANG = Featured(
    role_full="Vue UI 개발 (PA)", share="40%", stack=("Vue", "Vuetify", "Lighthouse"), a11y100=True,
    duties=("Vue·Vuetify 기반 컴포넌트 개발", "화면 구현 및 공통 UI 컴포넌트 일부 제작 및 기존 컴포넌트 개선",
            "Lighthouse 기반 웹 접근성 검수 및 점검 결과 문서화", "담당 업무 외 팀원 개발 지원"),
    results=("재사용 가능한 공통 컴포넌트 제작", "담당 업무 외 팀원 개발 지원으로 UI 개발 업무에 기여",
             "프로젝트 전체 파일 기준 Lighthouse Accessibility 100점 달성",
             "웹 접근성 인증 심사 대응 및 웹 접근성 품질인증 마크 획득"),
)
F_SHINHAN = Featured(
    role_full="모바일 UI 개발 (PA)", share="100%", stack=("HTML", "SCSS"),
    duties=("모바일 UI 개발 전반 단독 수행",
            "신규 구축이었으나 기존(AS-IS) 소스가 존재해, 이를 기반으로 UI 컴포넌트 통일",
            "공통 UI 가이드 작성 및 적용", "UI 개발 범위 및 일정 관리"),
    results=("모바일 UI 영역 전체 단독 담당",
             "UI 컴포넌트를 통일하며 **337개 화면**에 공통 UI 가이드 적용",
             "개발 범위 외 연계 채널 **3개**를 추가 대응하고도 일정 내 완료"),
)
F_HYUNDAI = Featured(
    role_full="UI 개발 (PA)", share="60%", stack=("HTML", "SCSS", "jQuery", "Gulp"),
    duties=("모바일 UI 개발 및 가이드 제작", "PC UI 가이드 및 레이아웃 제작"),
    results=("모바일 UI 개발을 함께 수행하고, PC는 UI 가이드와 레이아웃 제작을 담당",
             "모바일 UI 가이드를 기반으로 PC 가이드를 확장해 모바일·PC 간 일관성 확보",
             "후속 개발 및 UI 구현 기준 마련을 통해 프로젝트 일정 준수에 기여"),
)
F_HANA = Featured(
    role_full="UI 개발 (PA)", share="30%", stack=("HTML", "SCSS"),
    duties=("계좌조회·입금·이체·자산관리·신규 메뉴 등 주요 서비스 UI 개발", "큰글씨 모드 UI 개발",
            "프로젝트 전체 화면 대상 aria 속성 추가 작업 수행", "담당 채널의 UI 개발 업무 인수 및 진행",
            "담당 화면 외 타 화면에 대한 개발 지원 및 수정 병행"),
    results=("**약 2,400페이지 이상** 규모의 대형 프로젝트에서 인수 채널 250개 화면을 포함해 **약 500페이지**를 직접 개발하며 주요 화면 구조와 개발 히스토리를 폭넓게 파악, 이를 바탕으로 PL의 업무 대응 지원",
             "채널 담당 리더의 갑작스러운 교체로 발생한 업무 공백을 인수해 해당 채널의 UI 개발 업무(**250개 화면**)를 이어받아 일정 차질 없이 완료",
             "프로젝트 전체 화면을 대상으로 aria 속성을 추가해 웹 접근성 개선"),
)

PROJECTS: tuple[Project, ...] = (
    Project("2026.05 ~ 2027.01", "한화생명", "융자 차세대 시스템 구축", "React UI (PA)", "finance", "react", F_HANWHA),
    Project("2025.12 ~ 2026.04", "경기도교육청", "하이코칭시스템 구축", "UI (단독 수행)", "public", "", F_GYEONGGI),
    Project("2025.08 ~ 2025.10", "미래에셋증권", "AI Multi Agent 프레임워크 구축", "React UI (단독 수행)", "finance", "react", F_MIRAE),
    Project("2025.07 ~ 2025.07", "라이나생명", "라이나ONE 기업 홈페이지 개선", "UI (단독 수행)", "finance"),
    Project("2024.09 ~ 2025.03", "동양생명", "마이엔젤 서비스 통합 구축", "Vue UI (PA)", "finance", "vue", F_DONGYANG),
    Project("2024.07 ~ 2024.08", "한국교과서협회", "AIDT", "Vue UI (단독 수행)", "enterprise", "vue"),
    Project("2023.11 ~ 2024.05", "신한라이프", "GA 영업지원시스템", "모바일 UI (단독 수행)", "finance", "", F_SHINHAN),
    Project("2023.01 ~ 2023.07", "현대해상", "다이렉트 고도화", "UI (PA)", "finance", "", F_HYUNDAI),
    Project("2022.04 ~ 2022.08", "삼성화재", "다이렉트 리뉴얼", "UI (PA)", "finance"),
    Project("2022.01 ~ 2022.03", "SK텔레콤", "0한동 리뉴얼 구축", "UI (PA)", "enterprise"),
    Project("2021.12 ~ 2021.12", "AIG", "디지털 플랫폼 개선", "UI (PA)", "finance"),
    Project("2021.10 ~ 2021.12", "EBS", "명의 리뉴얼 구축", "UI (단독 수행)", "enterprise"),
    Project("2021.06 ~ 2021.08", "SK텔레콤", "T월드 운영", "UI (PA)", "enterprise"),
    Project("2021.03 ~ 2021.05", "SEMES", "SEMES 리뉴얼 구축", "UI (PA)", "enterprise"),
    Project("2020.12 ~ 2021.01", "LG화학", "ESS 개선 프로젝트", "UI (PA)", "enterprise"),
    Project("2020.11 ~ 2020.12", "조달청", "공유누리 모바일앱 구축", "UI (단독 수행)", "public"),
    Project("2020.07 ~ 2020.11", "행정안전부", "보조금24 구축", "UI (단독 수행)", "public"),
    Project("2020.02 ~ 2020.06", "하나은행", "원큐 리뉴얼 구축", "UI (PA)", "finance", "", F_HANA),
    Project("2019.12 ~ 2020.01", "캐롯손해보험", "신규 구축", "React UI (PA)", "finance", "react"),
    Project("2019.09 ~ 2019.12", "DB손해보험", "리뉴얼 구축", "UI (PA)", "finance"),
    Project("2019.06 ~ 2019.09", "삼성SDS", "Cloud EMM 가이드 컨설팅", "UI (PA)", "enterprise"),
    Project("2019.03 ~ 2019.05", "암웨이", "긴급 개선", "UI (PA)", "enterprise"),
    Project("2018.10 ~ 2019.02", "삼성생명", "경영지원 서비스(MIS) 구축", "UI (단독 수행)", "finance"),
    Project("2018.06 ~ 2018.09", "에어아시아나IDT", "에어부산 리뉴얼 구축", "UI (PA)", "enterprise"),
    Project("2018.01 ~ 2018.03", "애경", "FFlow 구축", "UI (PA)", "enterprise"),
    Project("2017.11 ~ 2018.01", "삼성전자", "삼성 모바일 캠퍼스 리뉴얼", "UI (PA)", "enterprise"),
    Project("2016.07 ~ 2017.06", "넷마블게임즈", "신규 브랜드사이트 구축", "UI (PA)", "enterprise"),
    Project("2016.07 ~ 2017.05", "넷마블게임즈", "넷마블 오피셜 운영", "UI (PA)", "enterprise"),
    Project("2016.04 ~ 2016.07", "넷마블게임즈", "게임운영툴 구축", "UI (PA)", "enterprise"),
    Project("2015.11 ~ 2016.01", "한국무역보험공사", "한국무역보험공사 구축", "UI (PA)", "public"),
    Project("2015.08 ~ 2016.01", "KCC", "KCC Refinish 구축", "UI (PA)", "enterprise"),
    Project("2015.07 ~ 2015.09", "한국창의재단", "메이크올 웹진 구축·운영", "UI (PA)", "enterprise"),
    Project("2015.06 ~ 2015.10", "과학기술정보통신부", "2015 세계과학정상회의 구축", "UI (PA)", "public"),
    Project("2015.06 ~ 2015.06", "동작구시설관리공단", "동작휴양소 구축", "UI (PA)", "public"),
    Project("2015.04 ~ 2015.05", "짙은", "내부 R&D 사업", "UI (PA)", "enterprise"),
    Project("2014.10 ~ 2015.02", "NHN Technology Service", "네이버 카페·지식인·블로그 운영, 포스트 리뉴얼", "UI (PA)", "enterprise"),
    Project("2014.08 ~ 2014.10", "NHN Entertainment", "한게임·TOAST 운영, 프로모션 제작", "UI (PA)", "enterprise"),
    Project("2013.07 ~ 2014.05", "삼성전자", "삼성 N닷컴 운영", "UI (PA)", "enterprise"),
    Project("2013.05 ~ 2013.06", "KT", "KT 미디어허브 구축", "UI (PA)", "enterprise"),
    Project("2013.04 ~ 2013.05", "동화면세점", "모바일웹 구축", "UI (PA)", "enterprise"),
    Project("2013.03 ~ 2013.04", "부천시", "부천시립도서관 리뉴얼", "UI (PA)", "public"),
    Project("2012.12 ~ 2013.02", "삼성생명", "패밀리사이트 리뉴얼", "UI (PA)", "enterprise"),
    Project("2012.10 ~ 2012.10", "한화S&C", "웹 접근성 개선", "UI (PA)", "enterprise"),
    Project("2012.09 ~ 2012.09", "부천시", "오정구청 리뉴얼 구축", "UI (PA)", "public"),
)

INTRO = (
    "금융·보험·공공·기업·게임 등 다양한 산업 분야에서 **40건 이상의 SI 프로젝트**를 수행한 Frontend UI Developer입니다.",
    "HTML/CSS 기반 웹 퍼블리싱으로 경력을 시작해 React·TypeScript·Vue 기반 UI 개발로 업무 영역을 확장해 왔습니다.",
    "프로젝트 초기 개발환경 구성, 공통 컴포넌트 설계, 업무 화면 구현, UI 품질 관리와 웹 접근성 검수까지 UI 개발 전반을 수행합니다.",
    "반복되는 업무 UI를 재사용 가능한 컴포넌트로 구조화하고, 데이터와 화면 처리 로직을 분리해 확장성과 유지보수성을 높이는 데 강점이 있습니다.",
    "한화생명 프로젝트에서 공통 컴포넌트 37종을 설계·구현하고 WBS 대비 약 1개월 반의 일정 단축에 기여했으며, 신한라이프 337개 화면의 공통 UI 가이드 적용과 하나은행 250개 화면의 업무 인수 경험을 보유하고 있습니다.",
)

COMPETENCIES = (
    ("UI 구조 설계 및 개발환경 구성", ("React·TypeScript·Vue 기반 UI 개발 및 화면 구현",
     "프로젝트 초기 개발환경·라우팅·컴포넌트 관리 환경 구성",
     "공통 컴포넌트 설계 및 데이터와 UI 처리 로직 분리",
     "기존 코드 분석, 오류 수정 및 UI 구조 개선",
     "Storybook 기반 컴포넌트 관리 및 UI 개발 가이드 작성")),
    ("업무 UI 구현 및 도메인 이해", ("은행·생명보험·손해보험·영업지원 시스템 등 금융 UI 개발",
     "검색·분류 선택 등 업무 로직을 포함한 컴포넌트 구현",
     "복잡한 업무 규칙과 화면 상태를 사용자 관점의 UI로 구현",
     "대규모 프로젝트의 화면 구조와 개발 히스토리 파악 및 업무 인수")),
    ("웹 접근성 및 UI 품질", ("KWCAG 2.2 기반 시맨틱 마크업 및 키보드·스크린리더 대응",
     "Lighthouse 기반 접근성 진단·개선 및 결과 문서화",
     "웹 접근성 인증 심사 대응 및 품질인증 마크 획득 경험",
     "KRDS 적용 공공 서비스, 반응형·모바일 UI 및 크로스 브라우징")),
    ("인터랙션 및 사용자 경험", ("CSS transition·animation과 JavaScript를 활용한 UI 인터랙션",
     "마이크로인터랙션을 활용한 상태 변화 및 사용자 피드백 구현",
     "재사용 가능한 애니메이션 인터랙션 구현 (한화생명)",
     "LLM 대기·스트리밍·오류 등 상태별 대화형 UI 구현 (미래에셋증권)")),
    ("독립 수행 및 협업", ("UI 파트 단독 수행 및 화면 구현부터 품질 검수까지 담당",
     "담당 UI 범위·우선순위·일정 관리 및 추가 요청 대응",
     "백엔드 개발자 대상 데이터 바인딩 위치와 UI 연동 방식 안내",
     "하루 평균 6~8페이지, 집중 작업 시 최대 20~30페이지 개발")),
    ("AI 활용 및 개발 자동화", ("AI를 코드 작성 보조와 오류 분석·개선 과정에 활용",
     "AI 도움을 받아 GitHub Actions CI/CD 워크플로 작성·개선",
     "VitePress 기반 개인 온라인 이력서 구성 및 GitHub Pages 자동 배포",
     "생성된 코드와 설정을 직접 검토·수정하고 프로젝트 환경에 맞게 적용")),
)
STACK = (
    ("UI 개발", "React, Next.js, TypeScript, JavaScript, Vue, Thymeleaf"),
    ("스타일링", "HTML5, CSS3, SCSS Modules, Tailwind CSS"),
    ("UI 라이브러리", "Radix UI, Vuetify"),
    ("컴포넌트·라우팅", "Storybook, TanStack Router, Next.js"),
    ("표준·접근성", "웹 표준, KWCAG 2.2, KRDS, 시맨틱 마크업, Lighthouse, 키보드·스크린리더 대응"),
    ("다국어·다국가", "i18n, l10n, 언어 전환, 다국어 UI 대응"),
    ("반응형 UI", "반응형 웹, 모바일 웹, 크로스 브라우징"),
    ("환경·도구", "Vite, Node.js, pnpm, npm, Gulp, Git, SVN, ESLint, Prettier"),
    ("빌드·배포", "GitHub Actions, GitHub Pages, VitePress, gh-pages"),
    ("협업", "Jira, Confluence, Figma, PMS"),
    ("AI 활용", "AI 기반 코드 작성 보조·오류 분석, CI/CD 워크플로 구성 및 개선"),
)
CAREER = (
    ("2022.12 ~ 현재", "네티브", "React·TypeScript 기반 UI 개발, 공통 컴포넌트 설계 및 구현, 프로젝트 개발환경 구성"),
    ("2017.11 ~ 2022.12", "재인컴퍼니 (前 유아이랩)", "금융·공공·기업 분야 웹 UI 개발, 반응형·모바일 화면 구현, 웹 표준 및 웹 접근성 준수"),
    ("2016.02 ~ 2017.06", "넷마블", "게임 브랜드 웹사이트 및 서비스 운영 화면 개발, 게임 운영 도구 UI 구현"),
    ("2015.03 ~ 2016.01", "짙은", "웹 UI 개발 및 사내 R&D 프로젝트 수행"),
    ("2014.08 ~ 2015.02", "하이브랩", "웹 서비스 운영 및 프로모션 페이지 제작·개선"),
    ("2012.09 ~ 2014.07", "하이웹솔루션", "기업·서비스 웹사이트 구축 및 UI 개발, 웹 표준 및 접근성을 고려한 마크업"),
)
AWARDS = (("2013 웹어워드 코리아 미디어·정보서비스 부문 최우수상", "부천시립도서관"),
          ("2013 웹어워드 코리아 일반기업 부문 우수상", "유니온스틸"))
EDUCATION = (
    ("국가평생교육진흥원", "사회복지학 학사 (2019.03 ~ 2023.08 졸업 / 3.54 / 4.5)"),
    ("동원대학교", "컴퓨터애니메이션과 전문학사(공학) (2007.03 ~ 2009.02 졸업 / 3.85 / 4.5)"),
    ("덕수정보산업고등학교", "정보처리과 (2007 졸업)"),
)
CERTIFICATES = (
    ("사회복지사 2급", "한국사회복지사협회", "2020.03"),
    ("웹디자인기능사", "한국산업인력공단", "2008.12"),
    ("정보처리기능사", "한국산업인력공단", "2008.02"),
    ("컴퓨터그래픽스운용기능사", "한국산업인력공단", "2006.07"),
    ("워드프로세서 1급", "대한상공회의소", "2006.02"),
)
TRAININGS = (("GIS 플랫폼과 HTML5 및 Server Side JavaScript 과정", "대한상공회의소", "2013.05 ~ 2013.06"),
             ("GIS 소프트웨어 UI/UX 및 기획 과정", "대한상공회의소", "2013.06"))
RESUME_ENV = ("**Markdown** 기반 콘텐츠 작성 및 관리", "**pnpm** 기반 패키지 관리",
              "**VitePress** 기반 온라인 이력서 구성", "**Prettier** 기반 코드 포맷팅",
              "**AI 활용** CI/CD 워크플로 작성 및 개선",
              "**GitHub Actions · GitHub Pages** 기반 빌드·배포 자동화",
              "**gh-pages**를 활용한 배포 스크립트 구성")
COVER_QUOTE = "좋아하는 일을 오래도록 잘하고 싶습니다."
COVER_LEAD = (
    "다양한 산업의 SI 프로젝트에서 쌓은 UI 개발 경험을 바탕으로, 요구사항을 정확히 파악하고 안정적인 화면 구조와 재사용 가능한 컴포넌트로 구현하는 개발자입니다. "
    "기술을 적용하는 데 그치지 않고 반복 업무를 구조화하고 UI 품질을 높여 프로젝트 결과에 기여해 왔습니다."
)
COVER_LETTER = (
    ("지원동기 | 사용자에게 필요한 UI를 완성하는 개발자", (
        "웹은 기획과 디자인의 의도를 실제 사용자가 경험하는 결과물로 연결하는 분야라는 점에서 매력을 느껴 시작했습니다. HTML/CSS 기반 퍼블리싱으로 경력을 쌓은 뒤 React·TypeScript·Vue 등 새로운 기술을 프로젝트에 적용하며 UI 개발 역량을 확장해 왔습니다.",
        "다양한 산업의 프로젝트를 경험하며 중요한 것은 특정 기술을 사용하는 데 그치지 않고, 업무와 사용자의 맥락을 이해해 안정적이고 일관된 UI로 구현하는 것임을 배웠습니다. 앞으로도 기본기를 바탕으로 새로운 기술을 익히고, 실제 서비스의 완성도에 기여하고자 합니다.",
    )),
    ("업무역량 | UI 구조화와 독립적인 실행", (
        "프로젝트 초기 개발환경 구성부터 공통 컴포넌트 설계, 화면 구현, 품질 검수까지 UI 개발 전반을 수행해 왔습니다. 금융·보험 분야의 복잡한 업무 규칙과 다양한 화면 상태를 이해하고, 검색·분류 선택 등 업무 기능을 포함한 컴포넌트로 구현하는 데 강점이 있습니다.",
        "한화생명 융자 차세대 시스템에서는 React 19·TypeScript·Vite 기반 환경과 라우팅·Storybook 구성을 마련하고, 공통 컴포넌트 37종을 설계·구현했습니다. 데이터와 UI 처리 로직을 분리해 여러 화면에서 재사용할 수 있는 구조를 만들었으며 WBS 대비 약 1개월 반의 일정 단축에 기여했습니다.",
    )),
    ("문제 해결 | 품질과 개발 연속성 확보", (
        "신한라이프 GA 영업지원시스템에서는 모바일 UI 영역을 단독으로 담당하고 337개 화면에 공통 UI 가이드를 적용했습니다. 담당 범위 외 연계 채널 3개를 추가로 대응하면서도 계획된 일정 내 개발을 마무리했습니다.",
        "하나은행 원큐 리뉴얼에서는 담당 채널의 리더 교체로 발생한 업무 공백을 인수해 250개 화면의 UI 개발을 이어갔습니다. 기존 화면 구조와 개발 히스토리를 파악하고 담당 화면 외 작업도 지원해 개발 연속성 확보에 기여했습니다.",
        "KWCAG 2.2를 고려한 시맨틱 마크업과 키보드·스크린리더 대응을 실무에 적용해 왔으며, 한화생명·경기도교육청·동양생명 프로젝트에서 Lighthouse Accessibility 100점을 달성했습니다. 동양생명 프로젝트에서는 웹 접근성 인증 심사에 대응해 품질인증 마크를 획득했습니다.",
    )),
    ("입사 후 목표 | 기본기와 자동화를 함께 발전시키는 개발자", (
        "입사 후에는 먼저 서비스의 구조와 업무 흐름, 개발 규칙을 빠르게 파악하고 팀의 기준에 맞춰 안정적으로 결과물을 내겠습니다. 반복되는 UI와 공통 기능은 재사용 가능한 구조로 정리하고, 접근성과 사용성을 함께 고려해 유지보수하기 좋은 UI를 구현하겠습니다.",
        "AI는 코드 작성 보조와 오류 분석, 개발 자동화에 활용하되 결과를 그대로 적용하기보다 직접 검토하고 프로젝트 환경에 맞게 개선하겠습니다. 개인 온라인 이력서를 VitePress로 구성하고 GitHub Actions·GitHub Pages 배포 자동화를 구축한 경험을 바탕으로 개발 과정의 반복 작업도 꾸준히 개선하겠습니다.",
        "어제보다 조금이라도 더 나은 결과물을 만든다는 기준으로 기본기를 지키면서 새로운 기술을 익히고, 맡은 업무를 끝까지 책임지는 UI 개발자로 기여하겠습니다.",
    )),
)


# ============================================================== 3. STYLE
CSS = r"""
:root {
  --ink: #334155; --ink-strong: #1f2937; --muted: #64748b; --sub: #475569;
  --line: #d7e5f2; --surface: #f7fbff; --surface-2: #eaf3ff;
  --accent: #2878e5; --accent-ink: #334155; --accent-soft: #eef6ff; --accent-on-dark: #fff;
  --chip-bg: #f3f6fa; --chip-ink: #475569; --chip-line: #dbe3ec;
  --ok: #12a594; --ok-ink: #334155; --ok-soft: #effaf7;
  --font: __FONT__;
}
@page {
  size: A4;
  margin: 10.5mm 12mm 13mm 12mm;
  @bottom-left { content: "__FOOTER__"; font-family: __FONT__; font-size: 7pt; color: #64748b; }
  @bottom-right { content: "Page " counter(page) " of " counter(pages); font-family: __FONT__; font-size: 7pt; color: #64748b; }
}
* { box-sizing: border-box; }
html { font-size: 8.5pt; }
body {
  font-family: var(--font); font-size: 8.7pt; line-height: 1.46; color: var(--ink);
  margin: 0; word-break: keep-all; overflow-wrap: break-word;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
b, strong { font-weight: 700; color: var(--ink-strong); }
a { color: inherit; text-decoration: none; }
ul { margin: 1px 0 2px; padding-left: 13px; }
li { margin: 0 0 1px; padding-left: 1px; }
p { margin: 0 0 4px; orphans: 3; widows: 3; }
.muted { color: var(--muted); }
.break { break-before: page; page-break-before: always; }
.keep { break-inside: avoid; page-break-inside: avoid; }

.banner {
  display: flex; justify-content: space-between; align-items: flex-end; gap: 10px;
  background: linear-gradient(110deg, #2878e5 0%, #4567d9 58%, #6657cc 100%);
  color: #fff; padding: 12px 16px;
  border-radius: 6px; margin-bottom: 9px; break-inside: avoid;
}
.banner .t { font-size: 17pt; font-weight: 700; line-height: 1.2; }
.banner .s { font-size: 8.7pt; font-weight: 700; color: var(--accent-on-dark); margin-top: 2px; }
.banner .meta { font-size: 7.5pt; color: #fff; text-align: right; line-height: 1.4; }
.summary {
  background: linear-gradient(100deg, #eff7ff 0%, #f6f9ff 100%);
  border-left: 3px solid var(--accent);
  padding: 7px 11px; margin-bottom: 8px;
}
.summary p { margin: 0 0 3px; }
.summary p:last-child { margin-bottom: 0; }
h2 {
  font-size: 11.5pt; font-weight: 700; color: var(--ink-strong);
  margin: 12px 0 6px; padding: 3px 8px;
  background: linear-gradient(90deg, #edf5ff 0%, #f8fbff 70%, #fff 100%);
  border-left: 3px solid var(--accent);
  break-after: avoid; page-break-after: avoid;
}
h3 {
  font-size: 9.2pt; font-weight: 700; color: var(--ink-strong);
  margin: 0 0 3px; break-after: avoid; page-break-after: avoid;
}
.sec { break-inside: auto; page-break-inside: auto; }
.sec.keep { break-inside: avoid; page-break-inside: avoid; }
.sec > h2 { break-after: avoid; page-break-after: avoid; }

.card {
  border: 1px solid var(--line); border-left: 2px solid #8fc1f4;
  border-radius: 5px; padding: 7px 10px;
  margin: 0 0 6px; background: #fff; font-size: 8.1pt; line-height: 1.4;
  break-inside: avoid; page-break-inside: avoid;
}
.card .head {
  display: flex; justify-content: space-between; align-items: baseline;
  gap: 7px; margin-bottom: 2px; break-after: avoid; page-break-after: avoid;
}
.card .name { font-size: 9.3pt; font-weight: 700; color: var(--accent-ink); }
.card .date { white-space: nowrap; font-size: 7.4pt; color: var(--muted); }
.card .role { font-size: 7.8pt; color: var(--sub); margin-bottom: 2px; }
.lab {
  font-weight: 700; font-size: 7.9pt; margin: 3px 0 1px;
  color: var(--ink-strong); break-after: avoid; page-break-after: avoid;
}
.chips { margin-bottom: 1px; }
.chips span {
  display: inline-block; background: var(--chip-bg); color: var(--chip-ink);
  border: 1px solid var(--chip-line); border-radius: 3px; font-size: 6.8pt;
  padding: 0 4px; margin: 0 2px 2px 0; line-height: 1.35;
}
.result {
  background: var(--ok-soft); border-left: 3px solid var(--ok);
  padding: 3px 7px; margin-top: 4px; break-inside: avoid; page-break-inside: avoid;
}
.result .lab { color: var(--ok-ink); margin-top: 0; }
.badge {
  display: inline-block; background: #dcfce7; color: var(--ink-strong);
  border-radius: 3px; font-size: 7pt; font-weight: 700; padding: 0 4px; margin-left: 5px;
}
.note { font-size: 7.6pt; margin: -1px 0 5px; break-after: avoid; page-break-after: avoid; }

.stats { width: 100%; border-collapse: collapse; margin-bottom: 5px; break-inside: avoid; page-break-inside: avoid; }
.stats th {
  background: var(--surface-2); font-size: 7.1pt; color: var(--sub);
  font-weight: 500; padding: 3px 2px; border: 1px solid var(--line); text-align: center;
}
.stats td {
  font-size: 9.4pt; font-weight: 700; color: var(--accent-ink);
  padding: 3px 2px; border: 1px solid var(--line); text-align: center;
}
.stats td.wide { font-size: 6.9pt; line-height: 1.27; }
.grid { width: 100%; border-collapse: separate; border-spacing: 4px; margin: 0 -4px; }
.grid tr { break-inside: avoid; page-break-inside: avoid; }
.grid td {
  width: 50%; vertical-align: top; border: 1px solid var(--line);
  border-top: 2px solid #8fc1f4; border-radius: 4px;
  padding: 6px 8px; font-size: 7.5pt; line-height: 1.36;
}
.grid td h3 { font-size: 8.9pt; margin-bottom: 3px; }
.grid td.cols { width: 100%; }
.grid ul { margin-bottom: 0; padding-left: 12px; }
.grid li { margin-bottom: 0.5px; }
table.kv { width: 100%; border-collapse: collapse; }
table.kv tr { break-inside: avoid; page-break-inside: avoid; }
table.kv td { padding: 2.5px 6px; border-bottom: 1px solid var(--line); vertical-align: top; }
table.kv td:first-child { width: 24%; font-weight: 700; color: var(--accent-ink); background: var(--surface-2); }
table.list { width: 100%; border-collapse: collapse; font-size: 7.7pt; line-height: 1.3; }
table.list th { background: linear-gradient(90deg, #2878e5, #4567d9); color: #fff; text-align: left; padding: 4px 6px; font-weight: 700; }
table.list td { padding: 2.5px 6px; border-bottom: 1px solid var(--line); vertical-align: top; }
table.list tbody tr:nth-child(even) td { background: var(--surface); }
table.list thead { display: table-header-group; }
table.list tr { break-inside: avoid; page-break-inside: avoid; }

.env-panel {
  background: #f1f9ff; border: 1px solid #cfe4f4; border-left: 3px solid var(--accent);
  border-radius: 4px; margin: 7px 0 9px; padding: 6px 9px; break-inside: avoid;
}
.env-panel h3 { color: var(--ink-strong); margin-bottom: 3px; font-size: 8.8pt; }
.env-panel ul { columns: 2; column-gap: 16px; margin: 0; padding-left: 13px; font-size: 7.3pt; }
.env-panel li { break-inside: avoid; margin-bottom: 1px; }
.cols ul { column-count: 2; column-gap: 14px; }
.cols li { break-inside: avoid; page-break-inside: avoid; }

.qa {
  border: 1px solid var(--line); border-radius: 4px; padding: 8px 11px;
  margin-bottom: 7px; break-inside: avoid; page-break-inside: avoid;
}
.qa h3 { font-size: 9.6pt; margin-bottom: 4px; }
.qa h3 .no {
  display: inline-block; width: 17px; height: 17px; line-height: 17px;
  margin-right: 7px; border-radius: 50%; background: #e7f2ff;
  color: var(--accent-ink); text-align: center; font-size: 7.5pt; font-weight: 700;
}
.qa p { margin: 0 0 5px; text-align: justify; line-height: 1.48; }
.qa p:last-child { margin-bottom: 0; }
.quote { font-style: italic; color: var(--accent-ink); font-weight: 700; font-size: 9.7pt; margin: 0 0 7px; }
.prose p { margin: 0 0 6px; text-align: justify; }
.cl .summary { padding: 8px 11px; margin-bottom: 9px; }
.cl .summary p { font-size: 9.1pt; line-height: 1.5; margin: 0; }
.cl .quote { font-size: 10.3pt; margin-bottom: 8px; }
.cl .qa { padding: 9px 12px; margin-bottom: 8px; }
.cl .qa h3 { font-size: 9.8pt; margin-bottom: 4px; }
.cl .qa p { font-size: 8.9pt; line-height: 1.52; margin: 0 0 6px; }

.cover { text-align: center; margin-top: 50mm; break-after: page; page-break-after: always; }
.cover .pill {
  display: inline-block; background: #e5f4ff; color: var(--accent-ink);
  border: 1px solid #b8def8;
  border-radius: 12px; padding: 3px 12px; font-size: 8pt; font-weight: 700;
}
.cover .big { font-size: 25pt; font-weight: 700; color: var(--ink-strong); margin: 12px 0 4px; }
.cover .sub { font-size: 10pt; color: var(--sub); margin-bottom: 22px; }
.cover table.kv { width: 72%; margin: 0 auto; text-align: left; }

@media screen {
  body { max-width: 182mm; margin: 20px auto; padding: 0 10px; background: #fff; }
}
@media print {
  body { width: auto; margin: 0; padding: 0; }
  a { text-decoration: none; }
}
"""


def build_css(footer_label: str) -> str:
    return CSS.replace("__FONT__", FONT_STACK).replace("__FOOTER__", f"{NAME} - {footer_label}")


# ============================================================== 4. RENDER
_BOLD = re.compile(r"\*\*(.+?)\*\*")


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def rich(text: str) -> str:
    """HTML 이스케이프 후 **굵게** 문법만 허용."""
    safe = esc(text)
    return _BOLD.sub(r"<b>\1</b>", safe)


def ul(items) -> str:
    return "<ul>" + "".join(f"<li>{rich(i)}</li>" for i in items) + "</ul>"


def chips(items) -> str:
    return "<div class='chips'>" + "".join(f"<span>{esc(i)}</span>" for i in items) + "</div>"


def banner(title: str, sub: str, meta: str = "") -> str:
    meta_html = f"<div class='meta'>{meta}</div>" if meta else ""
    return f"<div class='banner'><div><div class='t'>{esc(title)}</div><div class='s'>{esc(sub)}</div></div>{meta_html}</div>"


def h2(text: str, cls: str = "") -> str:
    return f"<h2 class='{cls}'>{esc(text)}</h2>"


def compute_stats() -> dict[str, int]:
    sectors = Counter(p.sector for p in PROJECTS)
    frameworks = Counter(p.framework for p in PROJECTS if p.framework)
    a11y = sum(1 for p in PROJECTS if p.featured and p.featured.a11y100)
    return {"total": len(PROJECTS), "finance": sectors["finance"], "public": sectors["public"],
            "enterprise": sectors["enterprise"], "react": frameworks["react"], "vue": frameworks["vue"], "a11y": a11y}


def count_label() -> str:
    return f"{len(PROJECTS) // 10 * 10}건 이상"


def check_stats(stats: dict[str, int]) -> None:
    for key, expected in EXPECTED.items():
        actual = stats[key]
        valid = actual >= expected if key == "total" else actual == expected
        if not valid:
            baseline = f"{expected}건 이상" if key == "total" else expected
            print(f"[경고] 통계 '{key}': 데이터={actual} / 기준={baseline}", file=sys.stderr)


def stats_table() -> str:
    s = compute_stats()
    heads = ["총 경력", "총 프로젝트", SECTORS["finance"], SECTORS["public"], SECTORS["enterprise"], "React", "Vue"]
    vals = [YEARS_LABEL, count_label(), f"{s['finance']}건", f"{s['public']}건",
            f"{s['enterprise']}건", f"{s['react']}건", f"{s['vue']}건"]
    return (
        "<table class='stats'>"
        f"<tr>{''.join(f'<th>{esc(h)}</th>' for h in heads)}</tr>"
        f"<tr>{''.join(f'<td>{esc(v)}</td>' for v in vals)}</tr>"
        "<tr><th colspan='3'>웹 접근성</th><th colspan='2'>화면 개발 생산성</th><th colspan='2'>주요 경험</th></tr>"
        "<tr><td class='wide' colspan='3'>기준 준수 · 품질 검수 · 인증 심사 대응 및 인증 마크 획득 · 개선 경험</td>"
        f"<td class='wide' colspan='2'>{esc(PRODUCTIVITY)}</td>"
        "<td class='wide' colspan='2'>공통 컴포넌트 개발 · UI 파트 단독 수행 · 개발환경 구성</td></tr></table>"
    )


def intro_box() -> str:
    return "<div class='summary'>" + "".join(f"<p>{rich(line)}</p>" for line in INTRO) + "</div>"


def competency_grid(start: int = 0, end: int | None = None) -> str:
    """지정한 역량 카드만 출력해 문서 페이지 단위로 분리한다."""
    items = COMPETENCIES[start:end]
    cells = [f"<td><h3>{esc(title)}</h3>{ul(lines)}</td>" for title, lines in items]
    rows = [f"<tr>{''.join(cells[i:i + 2])}</tr>" for i in range(0, len(cells), 2)]
    return "<table class='grid'><colgroup><col style='width:50%'><col style='width:50%'></colgroup><tbody>" + "".join(rows) + "</tbody></table>"


def resume_env_panel() -> str:
    return "<div class='env-panel'><h3>개인 이력서 개발 환경</h3>" + ul(RESUME_ENV) + "</div>"


def kv_table(rows) -> str:
    return "<table class='kv'>" + "".join(f"<tr><td>{esc(k)}</td><td>{v}</td></tr>" for k, v in rows) + "</table>"


def stack_table() -> str:
    return kv_table((k, esc(v)) for k, v in STACK)


def project_card(p: Project, brk: bool = False) -> str:
    f = p.featured
    assert f is not None
    return (
        f"<article class='card{' break' if brk else ''}'>"
        f"<div class='head'><div class='name'>{esc(p.client)} {esc(p.title)}</div>"
        f"<div class='date'>{esc(p.period + f.period_note)}</div></div>"
        f"<div class='role'>역할: {esc(f.role_full)} &nbsp;|&nbsp; 기여도: UI 개발 {esc(f.share)}</div>"
        f"{chips(f.stack)}"
        f"<div class='lab'>담당 범위 및 실행</div>{ul(f.duties)}"
        f"<div class='result'><div class='lab'>주요 성과</div>{ul(f.results)}</div>"
        "</article>"
    )


def featured_cards(start: int = 0, end: int | None = None) -> str:
    featured = [p for p in PROJECTS if p.featured]
    note = "<div class='note muted'>※ 기여도는 해당 프로젝트 내 UI 개발 파트 기준입니다.</div>"
    return note + "".join(project_card(p) for p in featured[start:end])


def project_table() -> str:
    rows = "".join(f"<tr><td>{esc(p.period)}</td><td>{esc(p.client)}</td><td>{esc(p.title)}</td><td>{esc(p.role)}</td></tr>" for p in PROJECTS)
    return ("<table class='list'><thead><tr><th style='width:20%'>기간</th><th style='width:18%'>고객사</th>"
            "<th>프로젝트명</th><th style='width:19%'>담당</th></tr></thead><tbody>" + rows + "</tbody></table>")


def career_table() -> str:
    rows = "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in CAREER)
    return ("<table class='list'><thead><tr><th style='width:22%'>기간</th><th style='width:26%'>회사명</th>"
            "<th>주요 업무</th></tr></thead><tbody>" + rows + "</tbody></table>")


def cover_letter_blocks() -> str:
    out = []
    for n, (title, paragraphs) in enumerate(COVER_LETTER, 1):
        body = "".join(f"<p>{rich(p)}</p>" for p in paragraphs)
        out.append(f"<section class='qa'><h3><span class='no'>{n:02d}</span>{esc(title)}</h3>{body}</section>")
    return "".join(out)


def education_block() -> str:
    return kv_table((k, esc(v)) for k, v in EDUCATION)


def credentials_block() -> str:
    def line(a, b, c):
        return f"{esc(a)} — {esc(b)} ({esc(c)})"
    certs = "<br>".join(line(*c) for c in CERTIFICATES)
    trains = "<br>".join(line(*t) for t in TRAININGS)
    awards = "<br>".join(f"{esc(a)} ({esc(b)})" for a, b in AWARDS)
    return kv_table((("자격증", certs), ("교육", trains), ("수상", awards)))


def site_link() -> str:
    return f"<a href='{esc(SITE_URL)}'>{esc(SITE_LABEL)}</a>"


# ============================================================== 5. DOCUMENTS
def sec(title: str, body: str, *, keep: bool = False) -> str:
    keep_class = " keep" if keep else ""
    return f"<section class='sec{keep_class}'>{h2(title)}{body}</section>"


def resume_body() -> str:
    # 이력서는 빠른 검토가 목적이므로 핵심 성과와 대표 프로젝트를 앞에 배치한다.
    head = (
        banner(NAME, ROLE, f"{site_link()}<br>{esc(TAGLINE)}")
        + intro_box()
        + h2("핵심 성과")
        + stats_table()
    )
    projects = sec("대표 프로젝트 및 성과", featured_cards(0, 7))
    profile = sec(
        "핵심 역량 및 기술 스택",
        competency_grid() + h2("기술 스택") + stack_table(),
    )
    career = sec("회사 경력", career_table(), keep=True)
    credentials = sec("학력 · 자격 · 교육 · 수상", education_block() + credentials_block())
    return f"<section class='sec'>{head}</section>" + projects + profile + career + credentials


def portfolio_body() -> str:
    head = (
        banner("PROJECT PORTFOLIO", f"{NAME} | {ROLE}", f"{site_link()}<br>{esc(TAGLINE)}")
        + intro_box()
        + h2("프로젝트 수행 현황") + stats_table()
    )
    # 대표 프로젝트는 임의의 주제별 섹션으로 나누지 않고 한 흐름으로 보여준다.
    featured = sec("대표 프로젝트", featured_cards(0, 7))
    all_projects = sec(f"전체 프로젝트 이력 ({count_label()})", project_table())
    return f"<section class='sec'>{head}</section>" + featured + all_projects



def cover_letter_body() -> str:
    return "<div class='cl'>" + _cover_letter_inner() + "</div>"


def _cover_letter_inner() -> str:
    return (banner("COVER LETTER", f"{NAME} | 프론트엔드 & UI 개발자 자기소개서")
            + f"<div class='quote'>“{esc(COVER_QUOTE)}”</div>"
            + f"<div class='summary'><p>{rich(COVER_LEAD)}</p></div>"
            + cover_letter_blocks())


def doc_resume() -> str:
    return resume_body()


def doc_portfolio() -> str:
    return portfolio_body()


def doc_cover_letter() -> str:
    return cover_letter_body()


def doc_application() -> str:
    cover = (
        "<div class='cover'>"
        f"<span class='pill'>{esc(ROLE)}</span>"
        "<div class='big'>입사지원서</div>"
        f"<div class='sub'>{esc(NAME)} | 이력서 · 자기소개서</div>"
        + kv_table((("성명", f"<b>{esc(NAME)}</b>"), ("직무", esc(ROLE)),
                    ("핵심 스택", "React, Next.js, TypeScript, Vue, HTML5, CSS3, SCSS Modules, Tailwind CSS, Web Accessibility, i18n"),
                    ("온라인 이력서", f"<b>{site_link()}</b>")))
        + "</div>"
    )
    return cover + f"<div class='break'>{resume_body()}</div>" + f"<div class='break'>{cover_letter_body()}</div>"


DOCUMENTS = {
    "resume": ("장홍준_프론트엔드_이력서", "이력서", "프론트엔드/UI 개발자 이력서", doc_resume),
    "portfolio": ("장홍준_프론트엔드_포트폴리오", "포트폴리오", "프론트엔드/UI 개발자 포트폴리오", doc_portfolio),
    "cover": ("장홍준_프론트엔드_자기소개서", "자기소개서", "프론트엔드/UI 개발자 자기소개서", doc_cover_letter),
    "application": ("장홍준_프론트엔드_입사지원서", "입사지원서", "입사지원서", doc_application),
}


def wrap_page(title: str, footer_label: str, body: str) -> str:
    return ("<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>{esc(title)}</title><style>{build_css(footer_label)}</style></head>"
            f"<body>{body}</body></html>")


# ============================================================== 6. BUILD
def main() -> int:
    ap = argparse.ArgumentParser(description="이력서/포트폴리오/자기소개서/입사지원서 PDF 빌드")
    ap.add_argument("--only", choices=DOCUMENTS.keys(), help="특정 PDF만 생성")
    ap.add_argument(
        "--out", type=Path, default=Path(__file__).resolve().parent / "pdf",
        help="PDF 출력 폴더 (기본값: 스크립트 폴더/pdf)",
    )
    args = ap.parse_args()

    check_stats(compute_stats())
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        from weasyprint import HTML
    except ImportError:
        print("weasyprint가 필요합니다: pip install weasyprint", file=sys.stderr)
        return 1

    selected = [args.only] if args.only else list(DOCUMENTS)
    base_url = str(Path(__file__).resolve().parent)
    for key in selected:
        filename, title, footer, render = DOCUMENTS[key]
        source = wrap_page(title, footer, render())
        pdf_path = args.out / f"{filename}.pdf"
        try:
            HTML(string=source, base_url=base_url).write_pdf(str(pdf_path))
        except Exception as exc:
            print(f"[오류] {title} PDF 생성 실패: {exc}", file=sys.stderr)
            return 1
        print(f"PDF  {pdf_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

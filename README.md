# TOSG-400M Pattern Signal Viewer

> TOSG-400M 패턴 생성기의 신호를 시각화·편집하고 OTD/Excel 파일로 입출력하는 Python GUI 도구

[![버전](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)
[![라이선스](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

---

## 목차

- [개요](#개요)
- [개발 배경](#개발-배경)
- [주요 기능](#주요-기능)
- [프로젝트 구조](#프로젝트-구조)
- [요구사항](#요구사항)
- [실행 방법](#실행-방법)
- [사용법](#사용법)
- [기술 스택](#기술-스택)
- [버전 히스토리](#버전-히스토리)
- [문의](#문의)
- [라이선스](#라이선스)

---

## 개요

TOSG-400M 패턴 생성기로 정의한 신호 파라미터를 GUI 환경에서 시각화·편집하고,  
OTD 및 Excel 형식으로 불러오거나 내보내는 도구입니다.  
다중 모델을 동시에 관리하며 타이밍 다이어그램으로 실시간 파형을 확인할 수 있습니다.

## 개발 배경

패턴 생성기 설정값(신호 이름, 전압, 타이밍 파라미터)을 텍스트 파일로만 확인하던 불편함을  
해소하기 위해 개발되었습니다. 여러 모델의 신호를 비교하고 OTD 파일로 바로 내보낼 수 있어  
TFT 패널 구동 신호 검토 시간을 단축합니다.

## 주요 기능

- **신호 편집** — 신호 추가/수정/삭제, 순서 이동, 색상 지정
- **타이밍 다이어그램** — 실시간 파형 시각화 (프레임 수 1~10 조절 가능)
- **SIG MODE / INVERSION** — 4가지 모드 조합으로 파형 패턴 생성
- **DC 모드** — Delay=Width=Period=0 시 프레임별 DC 전압 출력
- **다중 모델 관리** — ModelStore 기반으로 여러 모델 동시 관리
- **OTD 파일 입출력** — OTD 파일 불러오기 / 내보내기
- **Excel 파일 입출력** — Excel(.xlsx) 불러오기 / 파형 내보내기
- **MULTIREMOTE** — 다중 리모트 그룹 편집
- **패턴 데이터** — 패턴 데이터 패널에서 원시 데이터 확인
- **SyncData 자동 계산** — 주파수 선택 시 SyncData(1/주파수) 자동 산출

## SIG MODE 상세

### 일반 모드 (Delay, Width, Period > 0)

| MODE | INVERSION | 파형 규칙 |
|------|-----------|-----------|
| 0 | 0 | 모든 프레임에서 V1(Low) / V2(High) |
| 0 | 1 | 홀수 프레임 V1/V2, 짝수 프레임 V2/V1 |
| 1 | 0 | 홀수 프레임 V1/V2, 짝수 프레임 V3/V4 |
| 1 | 1 | 홀수 프레임 V1/V2, 짝수 프레임 V4/V3 |

### DC 모드 (Delay=Width=Period=0)

| MODE | INVERSION | 파형 규칙 |
|------|-----------|-----------|
| 0 | 0 | V1 고정 DC |
| 0 | 1 | 프레임별 V1 ↔ V2 반복 |
| 1 | 0 | 프레임별 V1 ↔ V3 반복 |
| 1 | 1 | 프레임별 V1 ↔ V4 반복 |

## 프로젝트 구조

```
tosg-pattern-viewer/
├── main.py                         # 메인 애플리케이션 진입점
├── requirements.txt                # 의존성 목록
├── setup.py                        # 패키지 설치 설정
├── build_exe.bat                   # Windows 실행 파일 빌드 스크립트
├── README.md
├── REQUIREMENTS.md                 # 기능 요구사항 명세
│
├── core/                           # 핵심 비즈니스 로직
│   ├── signal_model.py             # Signal 데이터 클래스, SignalManager, SignalStorage
│   ├── model_store.py              # 다중 모델 중앙 관리 (ModelStore)
│   └── sync_data.py                # SyncData / 주파수 관리 (SyncDataManager)
│
├── utils/                          # 입출력 유틸리티
│   ├── otd_parser.py               # OTD 파일 파싱
│   ├── otd_exporter.py             # OTD 파일 내보내기
│   ├── excel_importer.py           # Excel 파일 불러오기
│   └── excel_waveform_exporter.py  # Excel 파형 내보내기
│
├── src/                            # UI 컴포넌트
│   ├── control_panel.py            # 상단 제어 패널 (파일 I/O, 뷰 제어)
│   ├── model_list_panel.py         # 모델 목록 패널
│   ├── signal_table_widget.py      # 신호 목록 테이블 위젯
│   ├── signal_editor_panel.py      # 신호 편집기 패널
│   ├── pattern_data_panel.py       # 패턴 데이터 패널
│   ├── multiremote_panel.py        # MULTIREMOTE 패널
│   └── timing_viewer.py            # 타이밍 다이어그램 뷰어
│
├── config/                         # 설정 파일
│   ├── models_config.json          # 모델별 주파수·SyncData 설정
│   └── TOSG-400M_signals.json      # TOSG-400M 기본 신호 정의
│
├── data/                           # 데이터 저장소
│   └── signal_data/                # 모델별 신호 JSON 저장 디렉토리
│
├── tests/                          # 테스트 코드
└── docs/                           # 문서
    ├── decisions/                  # 기술 결정 기록
    ├── failures/                   # 실패 사례 기록
    └── domain/                     # 도메인 용어 사전
```

## 요구사항

- Python 3.8 이상
- 의존성 패키지 (`requirements.txt` 참조):

| 패키지 | 버전 | 용도 |
|--------|------|------|
| pandas | ≥ 2.0.0 | Excel 데이터 처리 |
| openpyxl | ≥ 3.0.0 | Excel 파일 입출력 |
| matplotlib | 최신 | 타이밍 다이어그램 렌더링 |
| numpy | 최신 | 파형 수치 계산 |

## 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 실행
python main.py
```

### Windows 실행 파일 빌드

```bat
build_exe.bat
```

## 사용법

### 1. OTD / Excel 불러오기

- 상단 제어 패널의 **"OTD 불러오기"** 또는 **"Excel 불러오기"** 버튼 클릭
- 불러온 모델이 좌측 모델 목록에 자동 추가됨

### 2. 신호 편집

- 좌측 **"신호 편집"** 탭에서 신호 선택 후 수정
- **"신호 추가"** 버튼으로 새 신호 생성
- 신호 파라미터: 이름, SIG MODE, INVERSION, V1~V4(V), DELAY/WIDTH/PERIOD(μs)

### 3. 타이밍 다이어그램 확인

- 우측 다이어그램이 신호 변경 즉시 실시간 갱신
- 상단 스핀박스에서 표시 프레임 수(1~10) 조절

### 4. 내보내기

- **"OTD 내보내기"** — 현재 모델을 OTD 파일로 저장
- **"Excel 내보내기"** — 파형 데이터를 Excel로 저장

## 기술 스택

- **GUI**: Tkinter (Python 표준 내장)
- **시각화**: Matplotlib
- **수치 계산**: NumPy
- **파일 처리**: pandas, openpyxl

## 버전 히스토리

| 버전 | 날짜 | 내용 |
|------|------|------|
| v1.0.0 | 2026-04-21 | 초기 릴리즈 — 다중 모델, OTD/Excel 입출력, 타이밍 다이어그램 |

## 문의

dhooonk@lgdisplay.com

## 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.

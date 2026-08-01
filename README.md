# Seoul Bank Marketing Analysis

[English](README.en.md)

서울 영커리언스 캠프 DATA_B 과제로 진행한 은행 정기예금 마케팅 데이터 분석 저장소입니다.

1차 과제에서는 가입 가능성이 높은 고객군을 탐색했고, 2차 과제에서는 핵심 타겟 밖의 잠재고객, 고객별 실행 전략, A/B 테스트, 평가지표, 데이터 수집 계획과 머신러닝 확장까지 정리했습니다.

## 주차별 과제

| 구분 | 주제 | 문서 | 발표 자료 |
|---|---|---|---|
| 1차 과제 | 가입 가능성이 높은 고객 특성 분석 | [분석 보고서](docs/analysis_report.md) | [PPT](docs/presentation/DATA_B_김범수_1차과제.pptx) |
| 2차 과제 | 타겟 추가 설정과 각 고객별 전략 | [상세 정리](week2/README.md) | [PPT](week2/presentation/DATA_B_김범수_2차과제_최종본.pptx) · [발표 대본](week2/script/DATA_B_김범수_2차과제_발표대본.docx) |

## 핵심 결과

- 전체 데이터: 41,188행, 21개 컬럼
- 라벨: `y` (`yes`: 가입, `no`: 미가입)
- 전체 가입률: 11.27%
- 완전히 동일한 중복 행: 12건
- 이전 캠페인 성공 고객의 이번 가입률: 65.11%
- 65세 이상 가입률: 47.21%
- 학생 가입률: 31.43%
- 연락 횟수가 증가할수록 가입률이 낮아지는 패턴 확인
- 통화 시간(`duration`)은 강한 사후 신호지만 연락 전 타깃 선정에는 사용할 수 없는 누수 변수

중복되지 않도록 순차적으로 정의한 핵심 타깃은 다음과 같습니다.

1. 이전 캠페인 성공 고객
2. 1번을 제외한 65세 이상 고객
3. 1·2번을 제외한 학생 고객

원본 기준으로 세 그룹은 전체 고객의 약 6.46%이며, 그룹 내 가입률은 48.69%, 전체 평균 대비 Lift는 약 4.32배입니다. 이는 과거 데이터의 집중도를 나타내며 미래 성과를 보장하지 않습니다.

## 분석 관점

전체 피처를 먼저 탐색한 뒤 아래 관점으로 분류했습니다.

| 관점 | 주요 컬럼 | 질문 |
|---|---|---|
| 고객 특성 | `age`, `job`, `marital`, `education` | 어떤 생애주기의 고객이 반응하는가? |
| 금융 상태 | `default`, `housing`, `loan` | 부채·신용 상태에 따라 차이가 있는가? |
| 이번 캠페인 | `contact`, `month`, `day_of_week`, `campaign`, `duration` | 언제, 어떤 방식으로, 몇 번 연락할 것인가? |
| 과거 관계 | `pdays`, `previous`, `poutcome` | 과거 접점과 반응이 이번 가입에 연결되는가? |
| 경제 상황 | `emp.var.rate`, `cons.price.idx`, `cons.conf.idx`, `euribor3m`, `nr.employed` | 캠페인 시점의 경제 환경이 관련되는가? |

최종 발표에서는 가입률 차이뿐 아니라 다음 기준을 사용해 변수를 선별했습니다.

```text
변수의 활용 가치 = 예측력 + 사전 활용 가능성 + 실행 가능성
```

## 저장소 구조

```text
.
├── analysis/
│   └── bank_marketing_eda.py
├── docs/
│   ├── analysis_report.md
│   └── presentation/
│       └── DATA_B_김범수_1차과제.pptx
├── week2/
│   ├── README.md
│   ├── presentation/
│   │   └── DATA_B_김범수_2차과제_최종본.pptx
│   └── script/
│       ├── DATA_B_김범수_2차과제_발표대본.docx
│       └── DATA_B_김범수_2차과제_발표대본.txt
├── data/
│   └── README.md
├── outputs/                 # 분석 표 실행 시 생성
├── requirements.txt
└── README.md
```

## 실행 방법

Python 3.10 이상을 권장합니다.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python analysis/bank_marketing_eda.py --input data/bank-additional-full.csv
```

분석 결과는 `outputs/tables`에 CSV 표로 저장됩니다.

## 데이터 준비

원본 CSV는 저장소에 포함하지 않습니다. 캠프에서 제공한 `bank-additional-full.csv`를 `data/` 폴더에 넣어 실행하세요.

데이터는 UCI Bank Marketing 데이터셋을 기반으로 하며, 원 출처와 변수 설명은 [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/222/bank+marketing)에서 확인할 수 있습니다.

## 해석 시 주의점

- 이 데이터는 한국 고객 데이터가 아니므로 국내 시장에 그대로 일반화할 수 없습니다.
- 그룹별 가입률은 상관관계이며 인과관계를 증명하지 않습니다.
- `duration`은 통화 종료 후 생성되므로 사전 타깃 모델에서 제외해야 합니다.
- `pdays=999`는 실제 999일이 아니라 이전 접촉 없음에 해당하는 특수값입니다.
- `month`만으로는 연도와 시간 순서를 복원할 수 없어 정식 시계열분석이라고 보기 어렵습니다.
- `contact`, `month`, 거시경제지표는 캠페인 대상 선정과 시점이 섞인 교란 가능성이 있습니다.
- 65세 이상처럼 가입률이 높은 그룹도 표본 규모를 함께 확인해야 합니다.

## 발표 자료

[DATA_B_김범수_1차과제.pptx](docs/presentation/DATA_B_김범수_1차과제.pptx)

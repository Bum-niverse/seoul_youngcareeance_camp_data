from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TARGET = "y"
YES_VALUE = "yes"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="서울 영커리언스 은행 마케팅 데이터 EDA"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/bank-additional-full.csv"),
        help="분석할 CSV 경로",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs"),
        help="표와 그래프를 저장할 폴더",
    )
    return parser.parse_args()


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"데이터 파일을 찾을 수 없습니다: {path}\n"
            "캠프에서 제공한 CSV를 data/bank-additional-full.csv에 넣어주세요."
        )

    # 캠프 파일과 UCI 원본의 구분자가 다를 수 있어 자동 감지한다.
    frame = pd.read_csv(path, sep=None, engine="python")
    required = {"age", "job", "campaign", "poutcome", TARGET}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"필수 컬럼이 없습니다: {sorted(missing)}")
    return frame


def subscription_summary(frame: pd.DataFrame) -> pd.DataFrame:
    counts = frame[TARGET].value_counts().reindex(["no", "yes"], fill_value=0)
    result = counts.rename("count").to_frame()
    result["rate"] = result["count"] / len(frame)
    return result


def group_subscription(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    result = (
        frame.assign(is_yes=frame[TARGET].eq(YES_VALUE))
        .groupby(column, observed=False, dropna=False)["is_yes"]
        .agg(customer_count="size", yes_count="sum", yes_rate="mean")
        .sort_values(["yes_rate", "customer_count"], ascending=[False, False])
    )
    overall_rate = frame[TARGET].eq(YES_VALUE).mean()
    result["lift"] = result["yes_rate"] / overall_rate
    return result


def build_age_groups(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["age_group_10y"] = pd.cut(
        result["age"],
        bins=[-float("inf"), 24, 34, 44, 54, 64, float("inf")],
        labels=["<=24", "25-34", "35-44", "45-54", "55-64", "65+"],
    )
    result["age_group_5y"] = pd.cut(
        result["age"],
        bins=[
            -float("inf"),
            24,
            29,
            34,
            39,
            44,
            49,
            54,
            59,
            64,
            float("inf"),
        ],
        labels=[
            "<=24",
            "25-29",
            "30-34",
            "35-39",
            "40-44",
            "45-49",
            "50-54",
            "55-59",
            "60-64",
            "65+",
        ],
    )
    return result


def build_campaign_groups(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["campaign_group"] = pd.cut(
        result["campaign"],
        bins=[0, 1, 2, 3, 5, 10, float("inf")],
        labels=["1", "2", "3", "4-5", "6-10", "11+"],
        include_lowest=True,
    )
    return result


def target_segment_summary(frame: pd.DataFrame) -> pd.DataFrame:
    prior_success = frame["poutcome"].eq("success")
    senior_without_success = frame["age"].ge(65) & ~prior_success
    student_without_previous_targets = (
        frame["job"].eq("student")
        & ~prior_success
        & ~senior_without_success
    )

    segment = pd.Series(
        "other",
        index=frame.index,
        dtype="object",
        name="target_segment",
    )
    segment.loc[prior_success] = "1_prior_success"
    segment.loc[senior_without_success] = "2_age_65_plus"
    segment.loc[student_without_previous_targets] = "3_student"

    result = group_subscription(frame.assign(target_segment=segment), "target_segment")
    selected = segment.ne("other")
    selected_count = int(selected.sum())
    selected_yes = int(frame.loc[selected, TARGET].eq(YES_VALUE).sum())
    total_yes = int(frame[TARGET].eq(YES_VALUE).sum())
    overall_rate = frame[TARGET].eq(YES_VALUE).mean()
    selected_rate = selected_yes / selected_count

    result.attrs["combined"] = {
        "target_count": selected_count,
        "target_share": selected_count / len(frame),
        "target_yes_count": selected_yes,
        "target_yes_rate": selected_rate,
        "lift": selected_rate / overall_rate,
        "capture_rate": selected_yes / total_yes,
    }
    return result


def all_column_profile(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for column in frame.columns:
        series = frame[column]
        rows.append(
            {
                "column": column,
                "dtype": str(series.dtype),
                "missing_count": int(series.isna().sum()),
                "missing_rate": float(series.isna().mean()),
                "unique_count": int(series.nunique(dropna=False)),
                "unknown_count": (
                    int(series.eq("unknown").sum())
                    if series.dtype == "object"
                    else 0
                ),
            }
        )
    return pd.DataFrame(rows)


def save_table(table: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(path, encoding="utf-8-sig")


def run_analysis(frame: pd.DataFrame, output_dir: Path) -> None:
    tables = output_dir / "tables"

    duplicate_count = int(frame.duplicated().sum())
    clean = frame.drop_duplicates().copy()
    clean = build_age_groups(clean)
    clean = build_campaign_groups(clean)
    overall_rate = clean[TARGET].eq(YES_VALUE).mean()

    save_table(subscription_summary(frame), tables / "target_summary_raw.csv")
    save_table(subscription_summary(clean), tables / "target_summary_clean.csv")
    save_table(all_column_profile(frame), tables / "all_column_profile.csv")

    categorical_columns = clean.select_dtypes(
        include=["object", "string", "category"]
    ).columns
    for column in categorical_columns:
        if column == TARGET:
            continue
        save_table(
            group_subscription(clean, column),
            tables / "categorical" / f"{column}.csv",
        )

    numeric_summary = clean.select_dtypes(include="number").describe().T
    save_table(numeric_summary, tables / "numeric_summary.csv")

    age_10 = group_subscription(clean, "age_group_10y")
    age_5 = group_subscription(clean, "age_group_5y")
    campaign = group_subscription(clean, "campaign_group")
    poutcome = group_subscription(clean, "poutcome")
    job = group_subscription(clean, "job")

    save_table(age_10, tables / "age_group_10y.csv")
    save_table(age_5, tables / "age_group_5y.csv")
    save_table(campaign, tables / "campaign_group.csv")
    save_table(poutcome, tables / "poutcome.csv")
    save_table(job, tables / "job.csv")

    macro_columns = [
        "month",
        "emp.var.rate",
        "cons.price.idx",
        "cons.conf.idx",
        "euribor3m",
        "nr.employed",
    ]
    if set(macro_columns).issubset(clean.columns):
        macro_by_month = (
            clean.assign(is_yes=clean[TARGET].eq(YES_VALUE))
            .groupby("month", observed=False)
            .agg(
                customer_count=(TARGET, "size"),
                yes_rate=("is_yes", "mean"),
                emp_var_rate=("emp.var.rate", "mean"),
                consumer_price_index=("cons.price.idx", "mean"),
                consumer_confidence_index=("cons.conf.idx", "mean"),
                euribor_3m=("euribor3m", "mean"),
                employed=("nr.employed", "mean"),
            )
        )
        save_table(macro_by_month, tables / "macro_by_month.csv")

    segments = target_segment_summary(clean)
    save_table(segments, tables / "target_segments.csv")
    combined = pd.Series(segments.attrs["combined"], name="value").to_frame()
    save_table(combined, tables / "target_segments_combined.csv")

    print(f"원본 행 수: {len(frame):,}")
    print(f"완전 중복 행: {duplicate_count:,}")
    print(f"중복 제거 후 행 수: {len(clean):,}")
    print(f"중복 제거 후 전체 가입률: {overall_rate:.2%}")
    print(f"결과 저장 위치: {output_dir.resolve()}")


def main() -> None:
    args = parse_args()
    frame = load_data(args.input)
    run_analysis(frame, args.output)


if __name__ == "__main__":
    main()

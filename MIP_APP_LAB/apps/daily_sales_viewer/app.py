import base64
import os
from html import escape
from pathlib import Path
from typing import Optional

import altair as alt
import pandas as pd
import streamlit as st


LAB_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "assets" / "logo.jpg"
DOCUMENTS_DIR = LAB_ROOT.parent.parent
DEFAULT_DATA_DIR = LAB_ROOT / "sample_data" / "memorial_weekend_comparison"
ADVANCED_LOCAL_DATA_DIR = (
    DOCUMENTS_DIR
    / "New project 4"
    / "outputs"
    / "ad_hoc"
    / "2026-05-24_memorial_weekend_comparison"
    / "files"
)

REQUIRED_FILES = {
    "hourly": "hourly_sales_by_location.csv",
    "daily": "location_daily_summary.csv",
    "totals": "location_total_comparison.csv",
    "items": "top_items_by_location.csv",
}

TEXT_COLUMNS = {
    "holiday",
    "holiday_relative_day",
    "date",
    "day_of_week",
    "location",
    "status",
    "item_name",
    "notes",
}

YEAR_OPTIONS = ["Compare", "2025", "2026"]
LOCATION_OPTIONS = ["ALL", "FAL", "OGT", "KBK"]
METRIC_OPTIONS = ["Net Sales", "Orders", "Avg Order", "Total Before Tips"]
DAY_ORDER = ["Friday", "Saturday", "Sunday", "Monday"]
COMPARABLE_LOCATIONS = ["KBK", "OGT"]
ALL_2026_LOCATIONS = ["FAL", "KBK", "OGT"]
COMPANY_TOTAL_NOTE = (
    "FAL was not open during Memorial Weekend 2025. Comparable totals use KBK + OGT only. "
    "The including-new-location total shows current company growth after adding FAL."
)
REPORT_DATE_NOTE = (
    "This report compares Memorial Weekend Friday-Monday sales. "
    "2025 dates: Friday 2025-05-23 through Monday 2025-05-26. "
    "2026 dates: Friday 2026-05-22 through Monday 2026-05-25."
)


st.set_page_config(
    page_title="Memorial Weekend Comparison",
    page_icon=":bar_chart:",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 1.1rem;
        padding-bottom: 2rem;
    }

    h1 {
        font-size: clamp(1.45rem, 3vw, 2.2rem);
        line-height: 1.12;
        margin-bottom: 0.25rem;
    }

    h2, h3 {
        line-height: 1.2;
    }

    .dashboard-title {
        align-items: center;
        display: flex;
        flex-wrap: nowrap;
        gap: 0.8rem;
        justify-content: flex-start;
        margin: 0 0 0.2rem;
        text-align: left;
    }

    .dashboard-title h1 {
        flex: 0 1 auto;
        margin: 0;
        min-width: 0;
        text-align: left;
    }

    .dashboard-logo {
        flex: 0 0 auto;
        height: 54px;
        object-fit: contain;
        width: 54px;
    }

    div[data-testid="stTabs"] button {
        padding-left: 0.65rem;
        padding-right: 0.65rem;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.7rem;
        margin: 0.5rem 0 0.9rem;
    }

    .kpi-card {
        min-width: 0;
        border: 1px solid rgba(49, 51, 63, 0.14);
        border-radius: 8px;
        background: rgba(250, 250, 250, 0.9);
        padding: 0.8rem 0.85rem;
        box-shadow: 0 1px 2px rgba(49, 51, 63, 0.05);
    }

    .kpi-card.selected {
        border-color: rgba(29, 78, 216, 0.48);
        box-shadow: inset 0 0 0 1px rgba(29, 78, 216, 0.16);
    }

    .kpi-label {
        color: rgba(49, 51, 63, 0.72);
        font-size: 0.76rem;
        font-weight: 650;
        letter-spacing: 0;
        margin-bottom: 0.15rem;
    }

    .kpi-value {
        color: rgb(20, 24, 34);
        font-size: 1.35rem;
        font-weight: 760;
        line-height: 1.15;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .kpi-caption {
        color: rgba(49, 51, 63, 0.66);
        font-size: 0.72rem;
        line-height: 1.25;
        margin-top: 0.2rem;
        overflow-wrap: anywhere;
    }

    .note-panel {
        color: rgba(49, 51, 63, 0.82);
        font-size: 0.72rem;
        line-height: 1.25;
        padding: 0.2rem 0 0.1rem;
    }

    .tiny-data-note {
        margin: 0.15rem 0 0.45rem;
        color: rgba(49, 51, 63, 0.72);
        font-size: 0.72rem;
        line-height: 1.25;
    }

    .tiny-data-note summary {
        cursor: pointer;
        display: inline;
        color: rgba(49, 51, 63, 0.72);
        font-size: 0.72rem;
        font-weight: 600;
        list-style-position: inside;
    }

    .tiny-data-note div {
        max-width: 760px;
        padding-top: 0.15rem;
        color: rgba(49, 51, 63, 0.68);
    }

    .stAltairChart, [data-testid="stVegaLiteChart"] {
        width: 100%;
    }

    [data-testid="stDataFrame"] {
        font-size: 0.86rem;
    }

    @media (max-width: 780px) {
        .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
            padding-top: 0.75rem;
        }

        h1 {
            font-size: 1.35rem;
        }

        .dashboard-title {
            gap: 0.38rem;
        }

        .dashboard-title h1 {
            font-size: 1.2rem;
        }

        .dashboard-logo {
            height: 36px;
            width: 36px;
        }

        h2, h3 {
            font-size: 1.05rem;
        }

        div[data-testid="column"] {
            min-width: 100% !important;
            width: 100% !important;
            flex: 1 1 100% !important;
        }

        .kpi-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.5rem;
        }

        .kpi-card {
            padding: 0.62rem 0.68rem;
        }

        .kpi-value {
            font-size: 1.05rem;
        }

        .kpi-caption {
            font-size: 0.68rem;
        }

        div[data-testid="stTabs"] button {
            padding-left: 0.4rem;
            padding-right: 0.4rem;
            font-size: 0.84rem;
        }
    }

    @media (max-width: 430px) {
        .kpi-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def default_data_dir() -> Path:
    env_path = os.environ.get("MIP_MEMORIAL_DATA_DIR")
    return Path(env_path).expanduser() if env_path else DEFAULT_DATA_DIR


def render_dashboard_title() -> None:
    if not LOGO_PATH.exists():
        st.title("Memorial Weekend Comparison")
        return

    encoded_logo = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    logo_src = f"data:image/jpeg;base64,{encoded_logo}"
    st.markdown(
        f"""
        <div class="dashboard-title">
            <img class="dashboard-logo" src="{logo_src}" alt="Mornings in Paris logo">
            <h1>Memorial Weekend Comparison</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


def prepare_frame(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for column in df.columns:
        if column in TEXT_COLUMNS:
            continue

        converted = pd.to_numeric(df[column], errors="coerce")
        original_nonblank = df[column].notna().sum()
        converted_nonblank = converted.notna().sum()

        if original_nonblank == 0 or converted_nonblank >= original_nonblank * 0.9:
            df[column] = converted

    if "year" not in df.columns and "date" in df.columns:
        df["year"] = df["date"].dt.year

    if "location" in df.columns:
        df["location"] = df["location"].fillna("Unknown").astype(str)

    return df


@st.cache_data(show_spinner=False)
def load_exports(data_dir_text: str) -> tuple[dict[str, pd.DataFrame], list[str]]:
    data_dir = Path(data_dir_text).expanduser()
    frames: dict[str, pd.DataFrame] = {}
    missing: list[str] = []

    for key, filename in REQUIRED_FILES.items():
        path = data_dir / filename
        if not path.exists():
            missing.append(filename)
            continue
        frames[key] = prepare_frame(pd.read_csv(path))

    return frames, missing


def money(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"${value:,.2f}"


def compact_money(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    value = float(value)
    sign = "-" if value < 0 else ""
    absolute = abs(value)
    if absolute >= 1_000_000:
        return f"{sign}${absolute / 1_000_000:.1f}M"
    if absolute >= 1_000:
        return f"{sign}${absolute / 1_000:.1f}K"
    return f"{sign}${absolute:,.0f}"


def whole_number(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:,.0f}"


def compact_number(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    value = float(value)
    sign = "-" if value < 0 else ""
    absolute = abs(value)
    if absolute >= 1_000_000:
        return f"{sign}{absolute / 1_000_000:.1f}M"
    if absolute >= 1_000:
        return f"{sign}{absolute / 1_000:.1f}K"
    return f"{sign}{absolute:,.0f}"


def percent(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:,.1f}%"


def sum_column(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns or df.empty:
        return 0.0
    return float(df[column].fillna(0).sum())


def selected_years(year_mode: str) -> list[int]:
    if year_mode == "Compare":
        return [2025, 2026]
    return [int(year_mode)]


def filter_years(df: pd.DataFrame, years: list[int]) -> pd.DataFrame:
    if "year" not in df.columns:
        return df.copy()
    return df[df["year"].isin(years)].copy()


def filter_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    if location == "ALL" or "location" not in df.columns:
        return df.copy()
    return df[df["location"] == location].copy()


def chart_height(row_count: int, minimum: int = 220, row_height: int = 28, maximum: int = 360) -> int:
    return max(minimum, min(maximum, row_count * row_height))


def is_prior_year_not_open(row: pd.Series) -> bool:
    explicit_status = row.get("_prior_year_not_open", pd.NA)
    if pd.notna(explicit_status):
        return bool(explicit_status)

    for column in ("prior_year_status", "prior_year_data_status", "prior_year_location_status"):
        if column in row.index and str(row.get(column, "")).strip().lower() == "not_open":
            return True

    note = str(row.get("notes", "")).lower()
    if "not open" in note:
        return True

    net_2025 = row.get("net_sales_2025")
    net_2026 = row.get("net_sales_2026")
    return pd.isna(net_2025) and pd.notna(net_2026) and net_2026 > 0


def growth_display(row: pd.Series) -> str:
    custom_growth = row.get("_growth_label")
    if pd.notna(custom_growth):
        return str(custom_growth)
    if is_prior_year_not_open(row):
        return "New / Not open last year"
    return percent(row.get("percent_change"))


def build_company_total_rows(totals: pd.DataFrame) -> pd.DataFrame:
    comparable = totals[totals["location"].isin(COMPARABLE_LOCATIONS)]
    all_2026 = totals[totals["location"].isin(ALL_2026_LOCATIONS)]

    comparable_2025 = sum_column(comparable, "net_sales_2025")
    comparable_2026 = sum_column(comparable, "net_sales_2026")
    comparable_orders_2025 = sum_column(comparable, "orders_2025")
    comparable_orders_2026 = sum_column(comparable, "orders_2026")
    comparable_change = comparable_2026 - comparable_2025
    comparable_growth = (
        (comparable_change / comparable_2025) * 100 if comparable_2025 else float("nan")
    )

    all_2026_net = sum_column(all_2026, "net_sales_2026")
    all_2026_orders = sum_column(all_2026, "orders_2026")
    including_new_change = all_2026_net - comparable_2025
    including_new_order_change = all_2026_orders - comparable_orders_2025

    rows = [
        {
            "location": "Company Total - Comparable",
            "net_sales_2025": comparable_2025,
            "net_sales_2026": comparable_2026,
            "difference": comparable_change,
            "percent_change": comparable_growth,
            "orders_2025": comparable_orders_2025,
            "orders_2026": comparable_orders_2026,
            "order_difference": comparable_orders_2026 - comparable_orders_2025,
            "notes": COMPANY_TOTAL_NOTE,
            "_prior_year_not_open": False,
            "_growth_label": pd.NA,
        },
        {
            "location": "Company Total - Including New Location",
            "net_sales_2025": comparable_2025,
            "net_sales_2026": all_2026_net,
            "difference": including_new_change,
            "percent_change": pd.NA,
            "orders_2025": comparable_orders_2025,
            "orders_2026": all_2026_orders,
            "order_difference": including_new_order_change,
            "notes": COMPANY_TOTAL_NOTE,
            "_prior_year_not_open": False,
            "_growth_label": f"{percent(comparable_growth)} comparable + FAL new",
        },
    ]
    return pd.DataFrame(rows)


def comparison_table(totals: pd.DataFrame, location: str) -> pd.DataFrame:
    table = filter_location(totals, location).copy()
    table["_prior_year_not_open"] = table.apply(is_prior_year_not_open, axis=1)
    table["_growth_label"] = pd.NA
    columns = [
        "location",
        "net_sales_2025",
        "net_sales_2026",
        "difference",
        "percent_change",
        "orders_2025",
        "orders_2026",
        "order_difference",
        "notes",
        "_prior_year_not_open",
        "_growth_label",
    ]
    table = table[[column for column in columns if column in table.columns]]

    if location == "ALL":
        company_rows = build_company_total_rows(totals)
        table = pd.concat([company_rows, table.sort_values("location")], ignore_index=True)
        return table[columns]

    return table.sort_values("location")


def format_comparison_table(table: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in table.iterrows():
        if is_prior_year_not_open(row) and not str(row.get("location", "")).startswith("Company Total"):
            rows.append(
                {
                    "Location": row.get("location"),
                    "2025 Net": "Not open",
                    "2026 Net": compact_money(row.get("net_sales_2026")),
                    "Change": compact_money(row.get("net_sales_2026")),
                    "Growth": "New",
                    "2025 Orders": "New",
                    "2026 Orders": whole_number(row.get("orders_2026")),
                    "Order Change": whole_number(row.get("orders_2026")),
                }
            )
            continue

        rows.append(
            {
                "Location": row.get("location"),
                "2025 Net": compact_money(row.get("net_sales_2025")),
                "2026 Net": compact_money(row.get("net_sales_2026")),
                "Change": compact_money(row.get("difference")),
                "Growth": growth_display(row),
                "2025 Orders": whole_number(row.get("orders_2025")),
                "2026 Orders": whole_number(row.get("orders_2026")),
                "Order Change": whole_number(row.get("order_difference")),
            }
        )
    return pd.DataFrame(rows)


def sales_by_location_for_chart(totals: pd.DataFrame, location: str, years: list[int]) -> pd.DataFrame:
    table = filter_location(totals, location)
    rows = []

    for _, row in table.iterrows():
        for year in years:
            sales_column = f"net_sales_{year}"
            orders_column = f"orders_{year}"
            if sales_column not in table.columns:
                continue
            rows.append(
                {
                    "location": row["location"],
                    "year": str(year),
                    "net_sales": row.get(sales_column, 0),
                    "orders": row.get(orders_column, 0),
                }
            )

    return pd.DataFrame(rows)


def missing_2025_notes(totals: pd.DataFrame, location: str) -> pd.DataFrame:
    table = filter_location(totals, location).copy()
    if table.empty:
        return table

    notes = table["notes"].fillna("").str.lower() if "notes" in table.columns else ""
    missing_by_note = notes.str.contains("no 2025|missing 2025|no completed order|not open", regex=True)
    missing_by_value = (
        table.get("net_sales_2025", pd.Series(0, index=table.index)).fillna(0).eq(0)
        & table.get("net_sales_2026", pd.Series(0, index=table.index)).fillna(0).gt(0)
    )
    return table[missing_by_note | missing_by_value]


def format_hour(hour) -> str:
    if pd.isna(hour):
        return "No hour"
    hour = int(hour)
    suffix = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour}:00 {suffix}"


def render_kpi_cards(cards: list[dict[str, str]], selected_metric: str) -> None:
    columns = st.columns(4)
    for column, card in zip(columns, cards):
        with column:
            with st.container(border=True):
                st.metric(label=card["label"], value=card["value"], help=card["full"])
                st.caption(card["caption"])


def location_total_row(totals: pd.DataFrame, location: str) -> Optional[pd.Series]:
    matches = totals[totals["location"].eq(location)]
    if matches.empty:
        return None
    return matches.iloc[0]


def build_kpi_cards(
    daily: pd.DataFrame,
    totals: pd.DataFrame,
    year_mode: str,
    location: str,
) -> list[dict[str, str]]:
    if year_mode == "Compare" and location == "ALL":
        company_rows = build_company_total_rows(totals)
        comparable = company_rows[company_rows["location"].eq("Company Total - Comparable")].iloc[0]
        including_new = company_rows[
            company_rows["location"].eq("Company Total - Including New Location")
        ].iloc[0]

        return [
            {
                "label": "2026 Total incl. FAL",
                "value": compact_money(including_new["net_sales_2026"]),
                "caption": f"All locations · {money(including_new['net_sales_2026'])}",
                "full": money(including_new["net_sales_2026"]),
            },
            {
                "label": "2025 Comparable Total",
                "value": compact_money(comparable["net_sales_2025"]),
                "caption": f"Comparable: KBK + OGT · {money(comparable['net_sales_2025'])}",
                "full": money(comparable["net_sales_2025"]),
            },
            {
                "label": "Added / Change",
                "value": compact_money(including_new["difference"]),
                "caption": "2026 incl. FAL minus 2025 KBK + OGT",
                "full": money(including_new["difference"]),
            },
            {
                "label": "Comparable Growth %",
                "value": percent(comparable["percent_change"]),
                "caption": "Comparable: KBK + OGT",
                "full": percent(comparable["percent_change"]),
            },
        ]

    if year_mode == "Compare":
        row = location_total_row(totals, location)
        if row is None:
            return []

        if is_prior_year_not_open(row):
            return [
                {
                    "label": "2026 Net Sales",
                    "value": compact_money(row.get("net_sales_2026")),
                    "caption": f"Full: {money(row.get('net_sales_2026'))}",
                    "full": money(row.get("net_sales_2026")),
                },
                {
                    "label": "2025",
                    "value": "Not open",
                    "caption": "No prior-year baseline",
                    "full": "Not open during Memorial Weekend 2025",
                },
                {
                    "label": "YoY Status",
                    "value": "New",
                    "caption": "New / Not open last year",
                    "full": "New / Not open last year",
                },
                {
                    "label": "2026 Orders",
                    "value": compact_number(row.get("orders_2026")),
                    "caption": f"Full: {whole_number(row.get('orders_2026'))}",
                    "full": whole_number(row.get("orders_2026")),
                },
            ]

        return [
            {
                "label": "2026 Net Sales",
                "value": compact_money(row.get("net_sales_2026")),
                "caption": f"Full: {money(row.get('net_sales_2026'))}",
                "full": money(row.get("net_sales_2026")),
            },
            {
                "label": "2025 Net Sales",
                "value": compact_money(row.get("net_sales_2025")),
                "caption": f"Full: {money(row.get('net_sales_2025'))}",
                "full": money(row.get("net_sales_2025")),
            },
            {
                "label": "Change",
                "value": compact_money(row.get("difference")),
                "caption": f"Full: {money(row.get('difference'))}",
                "full": money(row.get("difference")),
            },
            {
                "label": "Growth %",
                "value": percent(row.get("percent_change")),
                "caption": "Vs Memorial Weekend 2025",
                "full": percent(row.get("percent_change")),
            },
        ]

    net_sales = sum_column(daily, "estimated_net_sales")
    orders = sum_column(daily, "order_count")
    before_tips = sum_column(daily, "estimated_total_before_tips")
    average_sale = net_sales / orders if orders else 0.0

    return [
        {
            "label": "Net Sales",
            "value": compact_money(net_sales),
            "caption": f"Full: {money(net_sales)}",
            "full": money(net_sales),
        },
        {
            "label": "Orders",
            "value": compact_number(orders),
            "caption": f"Full: {whole_number(orders)}",
            "full": whole_number(orders),
        },
        {
            "label": "Avg Order",
            "value": compact_money(average_sale),
            "caption": f"Full: {money(average_sale)}",
            "full": money(average_sale),
        },
        {
            "label": "Total Before Tips",
            "value": compact_money(before_tips),
            "caption": f"Full: {money(before_tips)}",
            "full": money(before_tips),
        },
    ]


def metric_value_from_row(row: pd.Series, metric: str) -> float:
    if metric == "Orders":
        return row.get("order_count", 0)
    if metric == "Avg Order":
        orders = row.get("order_count", 0)
        return row.get("estimated_net_sales", 0) / orders if orders else 0
    if metric == "Total Before Tips":
        return row.get("estimated_total_before_tips", 0)
    return row.get("estimated_net_sales", 0)


def metric_axis(metric: str) -> alt.Axis:
    if metric == "Orders":
        return alt.Axis(format=",.0f")
    return alt.Axis(format="$,.0f")


def metric_tooltip(metric: str) -> alt.Tooltip:
    if metric == "Orders":
        return alt.Tooltip("metric_value:Q", title=metric, format=",.0f")
    return alt.Tooltip("metric_value:Q", title=metric, format="$,.2f")


def build_daily_metric(daily: pd.DataFrame, metric: str, location: str) -> pd.DataFrame:
    if daily.empty:
        return daily.copy()

    group_columns = ["year", "holiday_relative_day"]
    grouped = daily.groupby(group_columns, as_index=False).agg(
        estimated_net_sales=("estimated_net_sales", "sum"),
        order_count=("order_count", "sum"),
        estimated_total_before_tips=("estimated_total_before_tips", "sum"),
    )
    grouped["day_order"] = grouped["holiday_relative_day"].apply(
        lambda day: DAY_ORDER.index(day) if day in DAY_ORDER else len(DAY_ORDER)
    )
    grouped["location"] = "ALL" if location == "ALL" else location
    grouped["metric_value"] = grouped.apply(lambda row: metric_value_from_row(row, metric), axis=1)
    return grouped.sort_values(["year", "day_order"])


def build_hourly_metric(hourly: pd.DataFrame, metric: str, location: str) -> tuple[pd.DataFrame, str]:
    if hourly.empty:
        return hourly.copy(), ""

    grouped = (
        hourly.dropna(subset=["hour"])
        .groupby(["year", "location", "hour"], as_index=False)
        .agg(
            net_sales=("net_sales", "sum"),
            order_count=("order_count", "sum"),
            item_quantity=("item_quantity", "sum"),
        )
    )

    if location == "ALL":
        grouped = grouped.groupby(["year", "hour"], as_index=False).agg(
            net_sales=("net_sales", "sum"),
            order_count=("order_count", "sum"),
            item_quantity=("item_quantity", "sum"),
        )
        grouped["location"] = "ALL"

    if metric == "Orders":
        grouped["metric_value"] = grouped["order_count"]
        label = "Orders"
    elif metric == "Avg Order":
        grouped["metric_value"] = grouped.apply(
            lambda row: row["net_sales"] / row["order_count"] if row["order_count"] else 0,
            axis=1,
        )
        label = "Avg Order"
    elif metric == "Total Before Tips":
        grouped["metric_value"] = grouped["net_sales"]
        label = "Net Sales"
    else:
        grouped["metric_value"] = grouped["net_sales"]
        label = "Net Sales"

    grouped["hour_label"] = grouped["hour"].apply(format_hour)
    return grouped.sort_values(["year", "hour"]), label


def format_top_items_table(df: pd.DataFrame) -> pd.DataFrame:
    table = df[["year", "location", "item_name", "quantity", "net_sales"]].copy()
    table["year"] = table["year"].astype("Int64").astype(str)
    table["quantity"] = table["quantity"].apply(whole_number)
    table["net_sales"] = table["net_sales"].apply(money)
    return table.rename(
        columns={
            "year": "Year",
            "location": "Location",
            "item_name": "Item",
            "quantity": "Qty",
            "net_sales": "Net Sales",
        }
    )


def format_hourly_table(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    table = df[["year", "location", "hour_label", "metric_value"]].copy()
    table["year"] = table["year"].astype("Int64").astype(str)
    if metric == "Orders":
        table["metric_value"] = table["metric_value"].apply(whole_number)
    else:
        table["metric_value"] = table["metric_value"].apply(money)
    return table.rename(
        columns={
            "year": "Year",
            "location": "Location",
            "hour_label": "Hour",
            "metric_value": metric,
        }
    )


def format_daily_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    table = df.copy()
    table["avg_order"] = table.apply(
        lambda row: row["estimated_net_sales"] / row["order_count"] if row.get("order_count", 0) else 0,
        axis=1,
    )
    columns = [
        "year",
        "holiday_relative_day",
        "date",
        "location",
        "status",
        "estimated_net_sales",
        "order_count",
        "avg_order",
        "estimated_total_before_tips",
    ]
    table = table[[column for column in columns if column in table.columns]]
    if "date" in table.columns:
        table["date"] = table["date"].dt.strftime("%Y-%m-%d")
    for column in ["estimated_net_sales", "avg_order", "estimated_total_before_tips"]:
        if column in table.columns:
            table[column] = table[column].apply(money)
    if "order_count" in table.columns:
        table["order_count"] = table["order_count"].apply(whole_number)
    return table.rename(
        columns={
            "year": "Year",
            "holiday_relative_day": "Day",
            "date": "Date",
            "location": "Location",
            "status": "Status",
            "estimated_net_sales": "Net Sales",
            "order_count": "Orders",
            "avg_order": "Avg Order",
            "estimated_total_before_tips": "Total Before Tips",
        }
    )


render_dashboard_title()
st.caption("Mobile-friendly local dashboard using only the Memorial Weekend comparison CSV files.")

with st.expander("What this report includes", expanded=False):
    st.caption(
        f"{REPORT_DATE_NOTE} "
        "Comparable year-over-year totals use KBK + OGT only because FAL was not open during Memorial Weekend 2025. "
        "2026 all-location totals may include FAL where labeled."
    )

with st.sidebar:
    st.header("Data Source")
    data_dir_text = st.text_input("CSV folder", value=str(default_data_dir()))
    st.caption(
        "Cloud/demo mode uses sample_data/memorial_weekend_comparison/. "
        f"For local advanced mode, point this to {ADVANCED_LOCAL_DATA_DIR}."
    )
    st.caption("Only CSV files are read. No Square API calls or tokens are used.")

frames, missing_files = load_exports(data_dir_text)

if missing_files:
    st.error("The dashboard cannot find these required CSV files:")
    st.write(missing_files)
    st.stop()

hourly = frames["hourly"]
daily = frames["daily"]
totals = frames["totals"]
items = frames["items"]

filter_cols = st.columns(4)
with filter_cols[0]:
    year_mode = st.selectbox("Year mode", YEAR_OPTIONS, index=0)
with filter_cols[1]:
    location_choice = st.selectbox("Location", LOCATION_OPTIONS, index=0)
with filter_cols[2]:
    metric_choice = st.selectbox("Metric", METRIC_OPTIONS, index=0)
with filter_cols[3]:
    top_item_count = st.radio(
        "Top items",
        [10, 20],
        index=0,
        horizontal=True,
        format_func=lambda value: f"Top {value}",
    )

years = selected_years(year_mode)
daily_filtered = filter_location(filter_years(daily, years), location_choice)
items_filtered = filter_location(filter_years(items, years), location_choice)
hourly_filtered = filter_location(filter_years(hourly, years), location_choice)
comparison = comparison_table(totals, location_choice)

render_kpi_cards(build_kpi_cards(daily_filtered, totals, year_mode, location_choice), metric_choice)

if year_mode == "Compare" and location_choice == "ALL":
    st.caption(
        "Comparable totals exclude FAL because FAL was not open during Memorial Weekend 2025. "
        "The 2026 total and Added / Change cards show company growth after adding FAL."
    )

missing_notes = missing_2025_notes(totals, location_choice)
note_lines = [f"<div>{escape(REPORT_DATE_NOTE)}</div>"]
if location_choice == "ALL":
    note_lines.append(f"<div>{escape(COMPANY_TOTAL_NOTE)}</div>")
if not missing_notes.empty:
    for _, row in missing_notes.iterrows():
        note = row.get("notes", "2025 data is missing or incomplete.")
        note_lines.append(f"<div>{escape(str(note))}</div>")

if note_lines:
    st.markdown(
        f"""
        <details class="tiny-data-note">
            <summary>⚠️ Data notes</summary>
            {''.join(note_lines)}
        </details>
        """,
        unsafe_allow_html=True,
    )

overview_tab, items_tab, hourly_tab, daily_tab = st.tabs(
    ["Comparison", "Top Items", "Hourly", "Daily Detail"]
)

with overview_tab:
    st.subheader("Memorial Weekend Comparison")
    st.dataframe(format_comparison_table(comparison), width="stretch", hide_index=True)

    st.subheader("Net Sales by Location")
    chart_data = sales_by_location_for_chart(totals, location_choice, years)

    if chart_data.empty:
        st.info("No net sales rows match the selected filters.")
    else:
        sales_chart = (
            alt.Chart(chart_data)
            .mark_bar(size=28)
            .encode(
                x=alt.X("location:N", title="Location"),
                y=alt.Y("net_sales:Q", title="Net sales", axis=alt.Axis(format="$,.0f")),
                color=alt.Color("year:N", title="Year"),
                xOffset=alt.XOffset("year:N"),
                tooltip=[
                    alt.Tooltip("location:N", title="Location"),
                    alt.Tooltip("year:N", title="Year"),
                    alt.Tooltip("net_sales:Q", title="Net sales", format="$,.2f"),
                    alt.Tooltip("orders:Q", title="Orders", format=",.0f"),
                ],
            )
            .properties(height=300)
        )
        st.altair_chart(sales_chart, use_container_width=True)

with items_tab:
    st.subheader("Top Items by Location and Year")

    if items_filtered.empty:
        st.info("No item rows match the selected filters.")
    else:
        display_items = items_filtered.copy()
        display_items = display_items[display_items["item_name"].ne("(no item data)")]
        display_items = display_items.sort_values(
            ["year", "location", "rank_by_net_sales", "net_sales"],
            ascending=[True, True, True, False],
        )
        display_items = (
            display_items.groupby(["year", "location"], as_index=False, group_keys=False)
            .head(top_item_count)
            .copy()
        )

        if display_items.empty:
            st.info("No top-item detail is available for the selected filters.")
        else:
            display_items["item_label"] = display_items["item_name"].apply(
                lambda item: item if len(str(item)) <= 28 else f"{str(item)[:25]}..."
            )
            display_items["group"] = (
                display_items["location"].astype(str) + " / " + display_items["year"].astype("Int64").astype(str)
            )
            item_height = 210 if top_item_count == 10 else 300
            item_chart = (
                alt.Chart(display_items)
                .mark_bar(size=14)
                .encode(
                    x=alt.X("net_sales:Q", title="Net sales", axis=alt.Axis(format="$,.0f")),
                    y=alt.Y("item_label:N", title=None, sort="-x"),
                    color=alt.Color("year:N", title="Year"),
                    facet=alt.Facet("group:N", columns=1, title=None),
                    tooltip=[
                        alt.Tooltip("location:N", title="Location"),
                        alt.Tooltip("year:O", title="Year"),
                        alt.Tooltip("item_name:N", title="Item"),
                        alt.Tooltip("quantity:Q", title="Quantity", format=",.0f"),
                        alt.Tooltip("net_sales:Q", title="Net sales", format="$,.2f"),
                    ],
                )
                .resolve_scale(y="independent")
                .properties(height=item_height)
            )
            st.altair_chart(item_chart, use_container_width=True)
            st.dataframe(format_top_items_table(display_items), width="stretch", hide_index=True)

with hourly_tab:
    st.subheader("Hourly Sales Comparison by Year")

    if hourly_filtered.empty:
        st.info("No hourly rows match the selected filters.")
    else:
        visible_hourly, hourly_metric_label = build_hourly_metric(
            hourly_filtered,
            metric_choice,
            location_choice,
        )

        if metric_choice == "Total Before Tips":
            st.caption("Hourly CSVs do not include total-before-tips. This chart uses hourly net sales.")

        if visible_hourly.empty:
            st.info("No hourly detail is available for the selected filters.")
        else:
            hourly_chart = (
                alt.Chart(visible_hourly)
                .mark_line(point=True)
                .encode(
                    x=alt.X(
                        "hour:O",
                        title="Hour",
                        sort=sorted(visible_hourly["hour"].dropna().unique().tolist()),
                    ),
                    y=alt.Y(
                        "metric_value:Q",
                        title=hourly_metric_label,
                        axis=metric_axis(hourly_metric_label),
                    ),
                    color=alt.Color("year:N", title="Year"),
                    tooltip=[
                        alt.Tooltip("year:O", title="Year"),
                        alt.Tooltip("location:N", title="Location"),
                        alt.Tooltip("hour_label:N", title="Hour"),
                        metric_tooltip(hourly_metric_label),
                    ],
                )
                .properties(height=300)
            )
            st.altair_chart(hourly_chart, use_container_width=True)
            st.dataframe(format_hourly_table(visible_hourly, hourly_metric_label), width="stretch", hide_index=True)

with daily_tab:
    st.subheader(f"{metric_choice} by Day")
    daily_metric = build_daily_metric(daily_filtered, metric_choice, location_choice)

    if daily_metric.empty:
        st.info("No daily rows match the selected filters.")
    else:
        daily_chart = (
            alt.Chart(daily_metric)
            .mark_line(point=True)
            .encode(
                x=alt.X(
                    "holiday_relative_day:N",
                    title="Day",
                    sort=DAY_ORDER,
                ),
                y=alt.Y(
                    "metric_value:Q",
                    title=metric_choice,
                    axis=metric_axis(metric_choice),
                ),
                color=alt.Color("year:N", title="Year"),
                tooltip=[
                    alt.Tooltip("year:O", title="Year"),
                    alt.Tooltip("holiday_relative_day:N", title="Day"),
                    metric_tooltip(metric_choice),
                ],
            )
            .properties(height=260)
        )
        st.altair_chart(daily_chart, use_container_width=True)

    st.subheader("Daily Detail")
    st.dataframe(format_daily_table(daily_filtered), width="stretch", hide_index=True)

    with st.expander("Show full CSV columns", expanded=False):
        raw_daily = daily_filtered.copy()
        if "date" in raw_daily.columns:
            raw_daily["date"] = raw_daily["date"].dt.strftime("%Y-%m-%d")
        st.dataframe(raw_daily, width="stretch", hide_index=True)

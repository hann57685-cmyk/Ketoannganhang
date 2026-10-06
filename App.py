import streamlit as st
from datetime import date, timedelta
import calendar


# =========================================================
# CẤU HÌNH TRANG
# =========================================================

st.set_page_config(
    page_title="Công cụ tính tiền gửi tiết kiệm",
    page_icon="💰",
    layout="wide"
)

st.title("💰 CÔNG CỤ TÍNH TIỀN GỬI TIẾT KIỆM")
st.caption("Quy ước: 1 năm = 365 ngày | Ngày gửi được tính lãi | Ngày rút không tính lãi")


# =========================================================
# HÀM ĐỊNH DẠNG TIỀN
# =========================================================

def format_money(value):
    return f"{value:,.0f} VNĐ"


# =========================================================
# HÀM TÍNH SỐ NGÀY TÍNH LÃI
# =========================================================

def calculate_interest_days(start_date, end_date):
    """
    Tính số ngày từ ngày gửi đến trước ngày rút.
    
    Ví dụ:
    Gửi 01/01, rút 02/01
    => tính lãi ngày 01/01
    => số ngày = 1
    """
    return (end_date - start_date).days


# =========================================================
# HÀM CHIA KHOẢNG THỜI GIAN THEO TỪNG THÁNG
# =========================================================

def get_month_periods(start_date, end_date):
    """
    Tạo các khoảng tháng trong thời gian gửi.

    Tính từ start_date đến trước end_date.
    """

    periods = []

    current = start_date

    while current < end_date:

        # Ngày cuối cùng của tháng hiện tại
        last_day = calendar.monthrange(
            current.year,
            current.month
        )[1]

        month_end = date(
            current.year,
            current.month,
            last_day
        )

        # Ngày kết thúc khoảng tính lãi của tháng
        # Không bao gồm end_date
        next_start = month_end + timedelta(days=1)

        period_end = min(next_start, end_date)

        days = (period_end - current).days

        if days > 0:
            periods.append({
                "year": current.year,
                "month": current.month,
                "start": current,
                "end": period_end - timedelta(days=1),
                "days": days
            })

        current = next_start

    return periods


# =========================================================
# HÀM TÍNH LÃI ĐƠN THEO TỪNG THÁNG
# =========================================================

def calculate_simple_monthly_interest(
    principal,
    annual_rate,
    start_date,
    end_date
):
    """
    Lãi đơn:

    Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365

    Lãi từng tháng được tính theo số ngày thực tế.
    """

    monthly_data = []

    periods = get_month_periods(start_date, end_date)

    total_interest = 0

    for period in periods:

        interest = (
            principal
            * annual_rate
            * period["days"]
            / 365
        )

        total_interest += interest

        monthly_data.append({
            "Tháng": f"{period['month']:02d}/{period['year']}",
            "Từ ngày": period["start"].strftime("%d/%m/%Y"),
            "Đến ngày": period["end"].strftime("%d/%m/%Y"),
            "Số ngày": period["days"],
            "Tiền lãi": interest
        })

    return monthly_data, total_interest


# =========================================================
# HÀM TÍNH LÃI KÉP
# =========================================================

def calculate_compound_interest(
    principal,
    annual_rate,
    start_date,
    end_date
):
    """
    Lãi kép theo ngày.

    Lãi suất ngày = lãi suất năm / 365

    Giá trị cuối kỳ:

    A = P × (1 + r/365)^n

    Trong đó:
        P = tiền gốc
        r = lãi suất năm
        n = số ngày
    """

    periods = get_month_periods(start_date, end_date)

    balance = principal
    monthly_data = []

    total_interest = 0

    for period in periods:

        beginning_balance = balance

        # Lãi kép theo số ngày thực tế
        ending_balance = (
            beginning_balance
            * (1 + annual_rate / 365) ** period["days"]
        )

        interest = ending_balance - beginning_balance

        balance = ending_balance

        total_interest += interest

        monthly_data.append({
            "Tháng": f"{period['month']:02d}/{period['year']}",
            "Từ ngày": period["start"].strftime("%d/%m/%Y"),
            "Đến ngày": period["end"].strftime("%d/%m/%Y"),
            "Số ngày": period["days"],
            "Số dư đầu kỳ": beginning_balance,
            "Tiền lãi": interest,
            "Số dư cuối kỳ": ending_balance
        })

    return monthly_data, total_interest, balance


# =========================================================
# HÀM TÍNH NGÀY ĐÁO HẠN THEO KỲ HẠN
# =========================================================

def calculate_maturity_date(start_date, term_months):

    """
    Tính ngày đáo hạn dựa trên số tháng.

    Ví dụ:
    01/01 + 12 tháng = 01/01 năm sau
    """

    month = start_date.month - 1 + term_months
    year = start_date.year + month // 12
    month = month % 12 + 1

    day = min(
        start_date.day,
        calendar.monthrange(year, month)[1]
    )

    return date(year, month, day)


# =========================================================
# NHẬP DỮ LIỆU
# =========================================================

st.subheader("📌 Thông tin tiền gửi")

col1, col2 = st.columns(2)

with col1:

    principal = st.number_input(
        "💵 Số tiền gửi (VNĐ)",
        min_value=0.0,
        value=100_000_000.0,
        step=1_000_000.0,
        format="%.0f"
    )

    term_months = st.number_input(
        "📅 Kỳ hạn (tháng)",
        min_value=1,
        max_value=120,
        value=12,
        step=1
    )

    annual_rate_percent = st.number_input(
        "📈 Lãi suất (%/năm)",
        min_value=0.0,
        max_value=100.0,
        value=6.0,
        step=0.01
    )

with col2:

    payment_method = st.selectbox(
        "💳 Hình thức nhận lãi",
        [
            "Cuối kỳ",
            "Hàng tháng",
            "Đầu kỳ"
        ]
    )

    interest_type = st.selectbox(
        "📊 Phương pháp tính lãi",
        [
            "Lãi đơn",
            "Lãi kép"
        ]
    )

    start_date = st.date_input(
        "📅 Ngày khách hàng gửi tiền",
        value=date.today()
    )

    withdrawal_date = st.date_input(
        "📅 Ngày khách hàng rút tiền",
        value=calculate_maturity_date(
            date.today(),
            term_months
        )
    )


# =========================================================
# KIỂM TRA LÃI KÉP
# =========================================================

if interest_type == "Lãi kép" and payment_method != "Cuối kỳ":

    st.warning(
        "⚠️ Lãi kép chỉ được áp dụng khi hình thức nhận lãi là Cuối kỳ. "
        "Hệ thống sẽ tự chuyển sang Lãi đơn."
    )

    actual_interest_type = "Lãi đơn"

else:
    actual_interest_type = interest_type


# =========================================================
# TÍNH TOÁN
# =========================================================

if st.button("🧮 TÍNH TIỀN LÃI", use_container_width=True):

    # Kiểm tra dữ liệu

    if principal <= 0:

        st.error("❌ Số tiền gửi phải lớn hơn 0.")

        st.stop()

    if withdrawal_date <= start_date:

        st.error(
            "❌ Ngày rút tiền phải lớn hơn ngày gửi tiền."
        )

        st.stop()

    # Lãi suất dạng thập phân
    annual_rate = annual_rate_percent / 100

    # Số ngày tính lãi
    interest_days = calculate_interest_days(
        start_date,
        withdrawal_date
    )

    # =====================================================
    # LÃI ĐƠN
    # =====================================================

    if actual_interest_type == "Lãi đơn":

        monthly_data, total_interest = (
            calculate_simple_monthly_interest(
                principal,
                annual_rate,
                start_date,
                withdrawal_date
            )
        )

        maturity_amount = principal + total_interest

    # =====================================================
    # LÃI KÉP
    # =====================================================

    else:

        (
            monthly_data,
            total_interest,
            maturity_amount
        ) = calculate_compound_interest(
            principal,
            annual_rate,
            start_date,
            withdrawal_date
        )


    # =====================================================
    # XỬ LÝ HÌNH THỨC NHẬN LÃI
    # =====================================================

    if payment_method == "Cuối kỳ":

        interest_paid_upfront = 0
        interest_paid_monthly = 0

        final_received = maturity_amount

    elif payment_method == "Hàng tháng":

        # Hàng tháng sử dụng lãi đơn.
        # Lãi được trả từng tháng,
        # tiền gốc được nhận khi rút.

        interest_paid_upfront = 0
        interest_paid_monthly = total_interest

        final_received = principal

    else:
        # Đầu kỳ:
        # Toàn bộ tiền lãi được trả ngay khi gửi.
        # Khi rút, khách hàng nhận lại tiền gốc.

        interest_paid_upfront = total_interest
        interest_paid_monthly = 0

        final_received = principal


    # =====================================================
    # HIỂN THỊ KẾT QUẢ
    # =====================================================

    st.divider()

    st.subheader("📊 KẾT QUẢ TÍNH TOÁN")

    # -----------------------------------------------------
    # Thông tin tổng quan
    # -----------------------------------------------------

    result_col1, result_col2, result_col3, result_col4 = st.columns(4)

    with result_col1:
        st.metric(
            "💵 Tiền gốc",
            format_money(principal)
        )

    with result_col2:
        st.metric(
            "📅 Số ngày tính lãi",
            f"{interest_days} ngày"
        )

    with result_col3:
        st.metric(
            "📈 Tổng tiền lãi",
            format_money(total_interest)
        )

    with result_col4:

        if payment_method == "Cuối kỳ":

            display_final = maturity_amount

        else:

            display_final = final_received

        st.metric(
            "💰 Nhận khi rút",
            format_money(display_final)
        )


    # =====================================================
    # THÔNG TIN CHI TIẾT
    # =====================================================

    st.subheader("📋 Chi tiết khoản tiền gửi")

    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:

        st.write(
            f"**Ngày gửi:** "
            f"{start_date.strftime('%d/%m/%Y')}"
        )

        st.write(
            f"**Ngày rút:** "
            f"{withdrawal_date.strftime('%d/%m/%Y')}"
        )

        st.write(
            f"**Số ngày tính lãi:** "
            f"{interest_days} ngày"
        )

        st.write(
            f"**Lãi suất:** "
            f"{annual_rate_percent:.2f}%/năm"
        )

    with detail_col2:

        st.write(
            f"**Kỳ hạn:** "
            f"{term_months} tháng"
        )

        st.write(
            f"**Hình thức nhận lãi:** "
            f"{payment_method}"
        )

        st.write(
            f"**Phương pháp:** "
            f"{actual_interest_type}"
        )

        st.write(
            "**Quy ước:** 365 ngày/năm"
        )


    # =====================================================
    # TIỀN LÃI HÀNG THÁNG
    # =====================================================

    st.subheader("📅 Tiền lãi hàng tháng")

    if actual_interest_type == "Lãi đơn":

        # Thêm số thứ tự
        for index, row in enumerate(monthly_data, start=1):
            row["STT"] = index

        # Đưa STT lên đầu
        for row in monthly_data:
            row["STT"] = row.pop("STT")

        # Tạo bản sao để hiển thị đẹp
        display_data = []

        for row in monthly_data:

            display_data.append({
                "STT": row["STT"],
                "Tháng": row["Tháng"],
                "Từ ngày": row["Từ ngày"],
                "Đến ngày": row["Đến ngày"],
                "Số ngày": row["Số ngày"],
                "Tiền lãi": format_money(row["Tiền lãi"])
            })

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        display_data = []

        for index, row in enumerate(monthly_data, start=1):

            display_data.append({
                "STT": index,
                "Tháng": row["Tháng"],
                "Từ ngày": row["Từ ngày"],
                "Đến ngày": row["Đến ngày"],
                "Số ngày": row["Số ngày"],
                "Số dư đầu kỳ": format_money(
                    row["Số dư đầu kỳ"]
                ),
                "Tiền lãi": format_money(
                    row["Tiền lãi"]
                ),
                "Số dư cuối kỳ": format_money(
                    row["Số dư cuối kỳ"]
                )
            })

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )


    # =====================================================
    # TỔNG KẾT
    # =====================================================

    st.divider()

    st.subheader("💰 Tổng kết khoản tiền gửi")

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:

        st.write(
            f"**Tiền gốc:** "
            f"{format_money(principal)}"
        )

        st.write(
            f"**Tổng tiền lãi:** "
            f"{format_money(total_interest)}"
        )

        st.write(
            f"**Tổng giá trị gốc + lãi:** "
            f"{format_money(maturity_amount)}"
        )

    with summary_col2:

        if payment_method == "Cuối kỳ":

            st.success(
                f"💵 **Ngày rút tiền, khách hàng nhận:** "
                f"{format_money(maturity_amount)}"
            )

        elif payment_method == "Hàng tháng":

            st.info(
                f"📅 **Tiền lãi đã nhận hàng tháng:** "
                f"{format_money(total_interest)}"
            )

            st.success(
                f"💵 **Ngày rút tiền, khách hàng nhận lại tiền gốc:** "
                f"{format_money(principal)}"
            )

            st.write(
                f"**Tổng tiền khách hàng nhận trong toàn bộ kỳ:** "
                f"{format_money(principal + total_interest)}"
            )

        else:

            st.info(
                f"📅 **Tiền lãi nhận đầu kỳ:** "
                f"{format_money(total_interest)}"
            )

            st.success(
                f"💵 **Ngày rút tiền, khách hàng nhận lại tiền gốc:** "
                f"{format_money(principal)}"
            )

            st.write(
                f"**Tổng tiền khách hàng nhận trong toàn bộ kỳ:** "
                f"{format_money(principal + total_interest)}"
            )


# =========================================================
# GHI CHÚ
# =========================================================

with st.expander("ℹ️ Quy tắc tính lãi"):

    st.markdown("""
### 1. Lãi đơn

Công thức:

**Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365**

Trong đó:

- Ngày gửi được tính lãi.
- Ngày rút không được tính lãi.
- Nếu gửi từ 01/01 đến 02/01 thì số ngày tính lãi là **1 ngày**.

### 2. Lãi kép

Lãi kép chỉ áp dụng cho **hình thức nhận lãi cuối kỳ**.

Công thức được sử dụng:

**A = P × (1 + r / 365)^n**

Trong đó:

- `P`: tiền gốc
- `r`: lãi suất năm
- `n`: số ngày thực gửi
- `A`: số tiền gốc + lãi cuối kỳ

### 3. Nhận lãi hàng tháng

Tiền lãi được tính riêng theo từng tháng dựa trên **số ngày thực tế của tháng đó**.

### 4. Nhận lãi đầu kỳ

Toàn bộ tiền lãi của kỳ gửi được trả ngay khi khách hàng gửi tiền.

Đến ngày rút tiền, khách hàng nhận lại tiền gốc.

### 5. Nhận lãi cuối kỳ

Đến ngày rút tiền, khách hàng nhận:

**Tiền gốc + tổng tiền lãi**
""")

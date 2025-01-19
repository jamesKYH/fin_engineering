import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from main import get_combined_sampled_data
from fpdf import FPDF
import base64
import os
from io import BytesIO
import plotly.io as pio
from fpdf.enums import XPos, YPos




# 페이지 설정
st.set_page_config(page_title="창업 보고서 생성", layout="wide")
st.title("📊 창업 보고서 생성 도구")
st.markdown("---")

if "region_url" not in st.session_state:
    st.warning("지역을 먼저 선택하세요. 좌측 사이드바 main에서 지역을 선택해 주세요.")
    st.stop()  # 이후 코드를 실행하지 않음

region_url = st.session_state["region_url"]
sampled_df = get_combined_sampled_data(region_url)

if not sampled_df.empty:
    pass
else:
    st.error("데이터를 불러올 수 없습니다.")
df = sampled_df.copy()

# 날짜 변환
df['ta_ymd'] = pd.to_datetime(df['ta_ymd'], format='%Y%m%d')




# 업종 선택 섹션
st.sidebar.header("📂 업종 선택")
st.sidebar.markdown("원하는 업종 대분류와 소분류를 선택하세요.")
selected_category_1 = st.sidebar.selectbox("대분류 업종", df["card_tpbuz_nm_1"].unique())

# 대분류에 따른 소분류 선택
subcategories = df[df["card_tpbuz_nm_1"] == selected_category_1]["card_tpbuz_nm_2"].unique()
selected_category_2 = st.sidebar.selectbox("소분류 업종", subcategories)

# 관련 데이터 필터링
filtered_df = df[(df["card_tpbuz_nm_1"] == selected_category_1) & (df["card_tpbuz_nm_2"] == selected_category_2)]

# 보고서 생성 섹션
st.write(f"## 📄 {selected_category_1} > {selected_category_2} 업종 창업 보고서")
st.markdown("---")





if not filtered_df.empty:
    # 주요 인사이트 대시보드
    st.subheader("🌟 주요 인사이트")
    # 최고 매출 시간대와 요일 정보를 매핑
    hour_mapping = {
        1: "00:00 ~ 06:59", 2: "07:00 ~ 08:59", 3: "09:00 ~ 10:59",
        4: "11:00 ~ 12:59", 5: "13:00 ~ 14:59", 6: "15:00 ~ 16:59",
        7: "17:00 ~ 18:59", 8: "19:00 ~ 20:59", 9: "21:00 ~ 22:59",
        10: "23:00 ~ 23:59"
    }

    day_mapping = {
        1: "월요일", 2: "화요일", 3: "수요일",
        4: "목요일", 5: "금요일", 6: "토요일", 7: "일요일"
    }

    # 최고 매출 시간대 및 요일
    peak_hour = filtered_df.groupby("hour")["amt"].sum().idxmax()
    peak_day = filtered_df.groupby("day")["amt"].sum().idxmax()

    # 매핑 적용
    peak_hour_label = hour_mapping.get(peak_hour, "정보 없음")
    peak_day_label = day_mapping.get(peak_day, "정보 없음")

    total_sales = filtered_df["amt"].sum()
    avg_sales = filtered_df["amt"].mean()
    peak_hour = filtered_df.groupby("hour")["amt"].sum().idxmax()
    peak_day = filtered_df.groupby("day")["amt"].sum().idxmax()

    # 주요 인사이트 출력
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="총 매출 (원)", value=f"{total_sales:,.0f}")
    with col2:
        st.metric(label="평균 매출 (원)", value=f"{avg_sales:,.0f}")
    with col3:
        st.metric(label="최고 매출 시간대", value=f"{peak_hour_label}")
    with col4:
        st.metric(label="최고 매출 요일", value=f"{peak_day_label}")


    st.markdown("---")

    # 시간대별 매출 강조 차트
    st.subheader("⏰ 시간대별 매출 분석")
    hour_sales = filtered_df.groupby("hour")["amt"].sum().reset_index()
    peak_hour_value = hour_sales[hour_sales["hour"] == peak_hour]["amt"].values[0]

    fig = px.bar(hour_sales, x="hour", y="amt", title="시간대별 매출", labels={"amt": "매출 (원)", "hour": "시간대"})
    fig.add_trace(
        go.Scatter(
            x=[peak_hour], y=[peak_hour_value],
            mode="markers+text",
            text=["최고 매출 시간대"],
            textposition="top center",
            marker=dict(color="red", size=12)
        )
    )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()
    # 요일별 매출 분석
    st.subheader("📅 요일별 매출 분석")

    # Ensure 'day' column is properly mapped
    day_mapping = {
        1: "월요일", 2: "화요일", 3: "수요일", 4: "목요일",
        5: "금요일", 6: "토요일", 7: "일요일"
    }

    filtered_df["day_name"] = filtered_df["day"].map(day_mapping)
    day_sales = filtered_df.groupby("day_name")["amt"].sum().reset_index()

    # Handle empty or mismatched data
    if not day_sales.empty:
        peak_day_name = day_mapping.get(peak_day, "N/A")
        peak_day_value = day_sales.loc[day_sales["day_name"] == peak_day_name, "amt"].values
        peak_day_value = peak_day_value[0] if len(peak_day_value) > 0 else 0

        # Create bar chart
        fig2 = px.bar(
            day_sales,
            x="day_name",
            y="amt",
            title="요일별 매출",
            labels={"amt": "매출 (원)", "day_name": "요일"},
        )

        if peak_day_value > 0:
            fig2.add_trace(
                go.Scatter(
                    x=[peak_day_name],
                    y=[peak_day_value],
                    mode="markers+text",
                    text=["최고 매출 요일"],
                    textposition="top center",
                    marker=dict(color="red", size=12),
                )
            )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("요일별 매출 데이터가 없습니다.")


    st.divider()
    # 요일 및 시간대 교차 분석
    st.subheader("📊 요일 및 시간대 교차 분석")

    # Group data for heatmap
    cross_analysis = filtered_df.groupby(["day", "hour"])["amt"].sum().reset_index()
    cross_analysis["day_name"] = cross_analysis["day"].map(day_mapping)

    if not cross_analysis.empty:
        heatmap = px.density_heatmap(
            cross_analysis,
            x="hour",
            y="day_name",
            z="amt",
            title="요일 및 시간대별 매출 히트맵",
            labels={"hour": "시간대", "day_name": "요일", "amt": "매출 (원)"},
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(heatmap, use_container_width=True)
    else:
        st.warning("요일 및 시간대 교차 데이터가 없습니다.")
    st.divider()
    # 장기 소비 트렌드 분석
    st.subheader("📅 장기 소비 트렌드 분석")
    monthly_sales = filtered_df.groupby(filtered_df['ta_ymd'].dt.to_period('M'))["amt"].sum().reset_index()
    monthly_sales['ta_ymd'] = monthly_sales['ta_ymd'].astype(str)

    line_chart = px.line(
        monthly_sales, x="ta_ymd", y="amt",
        title="월별 매출 트렌드",
        labels={"ta_ymd": "월", "amt": "매출 (원)"},
        markers=True
    )
    st.plotly_chart(line_chart, use_container_width=True)

    # 성수기/비수기 강조
    avg_monthly_sales = monthly_sales["amt"].mean()
    monthly_sales["seasonality"] = monthly_sales["amt"].apply(
        lambda x: "성수기" if x > avg_monthly_sales else "비수기"
    )

    seasonality_chart = px.bar(
        monthly_sales, x="ta_ymd", y="amt", color="seasonality",
        title="성수기와 비수기 분석",
        labels={"ta_ymd": "월", "amt": "매출 (원)", "seasonality": "구분"},
        color_discrete_map={"성수기": "blue", "비수기": "gray"}
    )
    st.plotly_chart(seasonality_chart, use_container_width=True)

    # 안전한 매핑 처리
    peak_day_name = day_mapping.get(str(peak_day).zfill(2), "알 수 없음")  # 기본값을 '알 수 없음'으로 설정
    st.divider()
    # 마케팅 전략 제안
    st.subheader("📈 마케팅 전략 제안")
    st.divider()
    st.write("### 캠페인 아이디어")

    # 안전한 매핑 처리
    peak_day_name = day_mapping.get(str(peak_day).zfill(2), "알 수 없음")  # 기본값을 '알 수 없음'으로 설정

    # 마케팅 전략 제안 작성
    st.markdown(f"- **특정 시간대 할인**: {peak_hour}시대에 맞춘 할인 캠페인 진행.")
    st.markdown(f"- **특정 요일 회원 이벤트**: {peak_day_name}에 회원 전용 이벤트 개최.")
    st.markdown("- **성수기 집중 프로모션**: 성수기에 맞춰 광고와 프로모션 예산을 집중 배치.")
    st.divider()
    st.write("### 상품 및 서비스 개선 방향")
    st.markdown("""
        - 주요 고객층(연령대와 성별)에 맞는 상품 구성을 강화합니다.\n
        - 예를 들어, 젊은 연령대(20-30대)가 주요 고객층이라면 트렌드 상품을 추가하거나, 
        중장년층(40-50대)이 많다면 안정성과 실용성을 강조한 서비스를 제공합니다.
    """)
    st.info(
        "장기 트렌드와 성수기 데이터를 활용하여, 특정 시점에 맞춘 전략을 수립하고 매출을 극대화하세요."
    )
else:
    st.error("선택된 업종에 대한 데이터가 없습니다. 다른 업종을 선택해 보세요.")

def generate_pdf(title, insights, charts):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 폰트 경로 지정 (fonts 디렉토리에 저장된 경우)
    font_path = os.path.abspath("fonts/NotoSans-Regular.ttf")
    pdf.add_font("NotoSans", "", font_path, uni=True)
    pdf.set_font("NotoSans", size=12)

    # 제목 추가
    pdf.set_font("NotoSans", size=16, style="B")
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)

    # 주요 인사이트 추가
    pdf.set_font("NotoSans", size=12)
    pdf.multi_cell(0, 10, "주요 인사이트:")
    for insight in insights:
        pdf.multi_cell(0, 10, f" - {insight}")
    pdf.ln(10)

    # 차트 이미지 추가
    for chart_path in charts:
        pdf.add_page()
        pdf.image(chart_path, x=10, y=30, w=180)

    return pdf.output(dest="S").encode("utf-8")

# # PDF 다운로드 링크 생성 함수
# def download_pdf_link(pdf_content, filename="report.pdf"):
#     b64 = base64.b64encode(pdf_content).decode()
#     href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">📄 PDF 다운로드</a>'
#     return href

# # PDF 생성 버튼과 다운로드 링크
# st.subheader("📄 보고서 다운로드")
# st.markdown("작성된 보고서를 PDF로 다운로드하세요.")

# # 차트 저장
# chart_files = []
# for i, chart in enumerate([fig, fig2, heatmap, line_chart, seasonality_chart]):
#     chart_path = f"chart_{i}.png"
#     pio.write_image(chart, chart_path)
#     chart_files.append(chart_path)

# # PDF 생성
# pdf_title = f"{selected_category_1} > {selected_category_2} 업종 창업 보고서"
# insight_texts = [
#     f"총 매출: {total_sales:,.0f} 원",
#     f"평균 매출: {avg_sales:,.0f} 원",
#     f"최고 매출 시간대: {peak_hour}시대",
#     f"최고 매출 요일: {peak_day}요일",
#     "성수기/비수기 분석 및 장기 소비 트렌드 포함"
# ]
# pdf_content = generate_pdf(pdf_title, insight_texts, chart_files)

# # PDF 다운로드 링크 표시
# st.markdown(download_pdf_link(pdf_content), unsafe_allow_html=True)

# # 정리: 생성된 차트 이미지 삭제
# for file in chart_files:
#     os.remove(file)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from main import get_combined_sampled_data  # 메인 코드에서 함수 가져오기
# 페이지 설정 (스크립트의 첫 번째 명령어로 이동)
st.set_page_config(page_title="업종 대분류 및 소분류 분석", layout="wide")
# 페이지 제목


st.title("📊 업종 분석 도구")
st.markdown(
    """
    선택한 업종의 대분류 및 소분류에 대한 다양한 데이터를 확인하고 분석할 수 있습니다.
    데이터를 시각적으로 이해하기 쉽게 정리하였습니다.
    """
)







if "region_url" not in st.session_state:
    st.warning("지역을 먼저 선택하세요. 좌측 사이드바 main에서 지역을 선택해 주세요.")
    st.stop()  # 이후 코드를 실행하지 않음
# 캐시된 데이터 가져오기
region_url = st.session_state["region_url"]
sampled_df = get_combined_sampled_data(region_url)
if not sampled_df.empty:
    pass
else:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()
df = sampled_df.copy()



if not sampled_df.empty:
    pass
else:
    st.error("데이터를 불러올 수 없습니다.")
    st.stop()
    
    
df = sampled_df



# 대분류 관련 정보
st.subheader("업종대분류 선택")
# 대분류 관련 데이터 처리 및 시각화
unique_main_categories = df["card_tpbuz_nm_1"].dropna().unique()
selected_main = st.selectbox("**비교하고 싶은 업종 대분류를 선택하세요**", sorted(unique_main_categories))

# 소분류 관련 정보
st.subheader("업종소분류 선택")
# 1. 해당 대분류에 속하는 소분류 목록 추출 및 선택 (최대 3개)
available_subcategories = df[df["card_tpbuz_nm_1"] == selected_main]["card_tpbuz_nm_2"].dropna().unique()
selected_subcategories = st.multiselect(
    f"**🔍 {selected_main}에 속하는 업종 소분류를 선택하세요 (최대 3개)**",
    options=sorted(available_subcategories),
    default=[sorted(available_subcategories)[0]] if len(available_subcategories) > 0 else None,
    max_selections=3
)
# 최소 1개 이상 선택 확인
if not selected_subcategories:
    st.warning("적어도 하나의 업종 소분류를 선택해야 합니다.")
    st.stop()
# 선택한 업종 소분류로 데이터 필터링
filtered_df = df[df["card_tpbuz_nm_2"].isin(selected_subcategories) & (df["card_tpbuz_nm_1"] == selected_main)].copy()
st.divider()
# 데이터 전처리: 날짜 처리
filtered_df['ta_ymd'] = pd.to_datetime(filtered_df['ta_ymd'], format='%Y%m%d', errors='coerce')
filtered_df['year_month'] = filtered_df['ta_ymd'].dt.to_period('M').astype(str)
# 1. 월별 총 매출 금액 추이 비교
st.markdown("### 📈 월별 매출 금액 추이")
st.write("월별 매출 데이터를 통해 특정 업종 소분류의 성수기와 비수기를 파악할 수 있습니다.")
monthly_sales = (
    filtered_df.groupby(['year_month', 'card_tpbuz_nm_2'])['amt']
    .sum()
    .reset_index()
)
fig1 = px.line(
    monthly_sales, x='year_month', y='amt', color='card_tpbuz_nm_2',
    title="월별 매출 금액 추이",
    labels={'year_month': '년-월', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'}
)
st.plotly_chart(fig1, use_container_width=True)
st.divider()
# 2. 성별 및 연령대 관련 그래프
st.markdown("### 👫 성별 & 연령대 분석")
st.write("소비자의 성별 및 연령대를 기준으로 매출 데이터를 비교하고 주요 소비자 그룹을 파악하세요.")
# 성별 매출 비율
st.markdown("#### 성별 매출 비율")
gender_sales = (
    filtered_df.groupby(['sex', 'card_tpbuz_nm_2'])['amt']
    .sum()
    .reset_index()
)
fig2 = px.pie(
    gender_sales, names='sex', values='amt', color='sex',
    facet_col='card_tpbuz_nm_2',
    title="성별 매출 비율",
    color_discrete_map={'M': 'blue', 'F': 'pink'}
)
st.plotly_chart(fig2, use_container_width=True)
# 연령대별 매출 비교 - 파이 차트
st.markdown("#### 연령대별 매출 비율")
age_mapping = {
    1: '10대 이하', 2: '10대', 3: '20대', 4: '30대', 5: '40대',
    6: '50대', 7: '60대 이상'
}
if 'age' in filtered_df.columns:
    filtered_df['age_group'] = filtered_df['age'].map(age_mapping)
    age_sales = (
        filtered_df.groupby(['age_group', 'card_tpbuz_nm_2'])['amt']
        .sum()
        .reset_index()
    )
    fig3 = px.pie(
        age_sales,
        names='age_group',
        values='amt',
        color='age_group',
        title="연령대별 매출 비율",
        facet_col='card_tpbuz_nm_2',
        labels={'age_group': '연령대', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'},
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.write("데이터프레임에 'age' 열이 존재하지 않습니다.")
st.divider()
# 3. 시간대 및 요일별 소비 패턴 분석
st.markdown("### ⏰ 시간대 및 요일별 소비 분석")
st.write("시간대와 요일 데이터를 활용해 매출이 집중되는 시점을 파악하고, 이를 기반으로 프로모션 전략을 수립하세요.")
# 시간대별 매출 비교
st.markdown("#### 시간대별 매출 비교")
hourly_data = (
    filtered_df.groupby(['hour', 'card_tpbuz_nm_2'])['amt']
    .sum()
    .reset_index()
)
fig4 = px.bar(
    hourly_data, x='hour', y='amt', color='card_tpbuz_nm_2',
    title="시간대별 매출 비교",
    labels={'hour': '시간대', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'}
)
st.plotly_chart(fig4, use_container_width=True)
# 요일별 매출 비교
st.markdown("#### 요일별 매출 비교")
day_labels = {
    1: '월', 2: '화', 3: '수', 4: '목', 5: '금', 6: '토', 7: '일'
}
filtered_df['weekday'] = filtered_df['ta_ymd'].dt.dayofweek + 1
filtered_df['weekday'] = filtered_df['weekday'].map(day_labels)
weekday_sales = (
    filtered_df.groupby(['weekday', 'card_tpbuz_nm_2'])['amt']
    .sum()
    .reset_index()
)
weekday_order = ['월', '화', '수', '목', '금', '토', '일']
weekday_sales['weekday'] = pd.Categorical(weekday_sales['weekday'], categories=weekday_order, ordered=True)
weekday_sales = weekday_sales.sort_values('weekday')
fig5 = px.bar(
    weekday_sales, x='weekday', y='amt', color='weekday',
    title="요일별 매출 비교",
    labels={'weekday': '요일', 'amt': '매출 금액', 'card_tpbuz_nm_2': '업종 소분류'},
    facet_col='card_tpbuz_nm_2'
)
st.plotly_chart(fig5, use_container_width=True)
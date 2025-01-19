import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO 
import pandas as pd
import os
import plotly.express as px
from openai_utils import fetch_region_info
from dotenv import load_dotenv
import ssl
import threading
# SSL 인증서 검증 비활성화
ssl._create_default_https_context = ssl._create_unverified_context

# 페이지 설정
st.set_page_config(page_title="창업 정보 플랫폼", layout="wide", page_icon="🏢")

# 헤더 섹션
st.title("🏢 창업을 꿈꾸는 당신을 위한 정보 플랫폼")
st.divider()

# 소개
st.header("창업을 준비하고 계신가요?")
st.write(
    "본 홈페이지는 예비 창업자들이 자신만의 비즈니스를 계획하고 실행하는 데 필요한 데이터와 인사이트를 제공합니다."
)

# 주요 기능 섹션
st.subheader("🌟 제공 기능")

# 컬럼 레이아웃으로 나누어 가독성 향상
col1, col2 = st.columns(2)

with col1:
    st.markdown("### **1. 업종 분석**")
    st.write(
        """
        주요 업종에 대한 전반적인 데이터를 제공합니다. \n\n
        - **대분류 정보 제공**: 업종별 매출, 소비자 트렌드, 시간대별 매출 등.
        - **소분류 정보 제공**: 연령대별 소비 패턴 등 상세 분석 제공.\n\n
        """
    )
    st.info("📊 차트와 그래프를 통해 직관적으로 정보를 확인하세요!")

with col2:
    st.markdown("### **2. 맞춤형 시각화 도구**")
    st.write(
        """
        입력하신 데이터와 조건을 기반으로 업종 및 지역별 데이터를 시각화할 수 있습니다.
        - **시간 단위 분석**: 일별, 주별, 월별 데이터를 활용한 예측.
        - **트렌드 비교**: 다양한 카테고리를 한눈에 비교.
        """
    )
    st.success("🖼️ 데이터를 커스터마이즈하여 비즈니스 성과를 예측하세요!")

# 추가 기능 섹션
st.markdown("---")







# 지역 선택 기능 추가
st.sidebar.header("지역 선택")





# 한글 지역명과 URL에 사용될 영문명을 매핑한 딕셔너리
region_mapping = {
    "포천시": "pochun",
#     "수원시": "suwon",
#     '광명시' : 'kwangmyeong',
# '부천시':'bucheon',

# '시흥시' : 'siheung',
# '안산시' : 'ansan',
# '용인시' : 'yongin',
# '포천시' : 'pochun',
# '하남시' : 'hanam',
# '화성시' : 'hwasung'
}


selected_region = st.sidebar.selectbox("창업 예정 지역을 선택하세요", list(region_mapping.keys()))

# 선택된 지역의 영문명을 가져오기
region_url = region_mapping[selected_region]

st.session_state["region_url"] = region_url 




# 파일 읽기 함수 (캐싱)
@st.cache_data
def load_csv_file(file_path):
    """CSV 파일을 읽어오는 함수"""
    try:
        df = pd.read_csv(file_path, encoding="utf-8")
        return df
    except Exception as e:
        st.write("에러 발생:")
        return None

# 데이터 병합 및 샘플링 함수 (캐싱)
@st.cache_data
def get_combined_sampled_data(region):
    """2023년 데이터를 병합하고 샘플링"""
    # 파일 경로 템플릿
    base_url = f'https://woori-fisa-bucket.s3.ap-northeast-2.amazonaws.com/fisa04-card/tbsh_gyeonggi_day_2023{{}}_{region}.csv'

    combined_df = pd.DataFrame()

    # 202301부터 202312까지 반복 처리
    for month in range(1, 13):
        month_str = f"{month:02d}"  # 월을 두 자리로 포맷팅
        file_path = base_url.format(month_str)

        df = load_csv_file(file_path)
        if df is not None:
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # 데이터 샘플링
    if not combined_df.empty:
        sample_ratio = 0.01  # 샘플링 비율 (1%)
        sampled_df = combined_df.sample(frac=sample_ratio, random_state=42)
        return sampled_df
    else:
        return pd.DataFrame()  # 빈 데이터프레임 반환

def clear_cache_on_region_change(selected_region):
    """
    지역이 변경되었는지 확인하고, 변경되었으면 캐시를 초기화
    """
    if "previous_region" not in st.session_state:
        st.session_state["previous_region"] = selected_region

    # 지역이 변경된 경우
    if st.session_state["previous_region"] != selected_region:
        st.cache_data.clear()  # 캐시 초기화
        st.session_state["previous_region"] = selected_region

# 메인 함수
def main():

    st.subheader("📊 지역별 데이터 로드")
    st.write(f"선택된 지역: {selected_region}")
    
    clear_cache_on_region_change(selected_region)
     # 특색 정보 표시 컨테이너
    info_container = st.empty()

    # 특색 정보를 갱신하는 쓰레드 시뮬레이션
    data_loaded = False  # 데이터 로드 상태 플래그
    import time
    def update_region_info():
        """
        3초마다 특색 정보를 갱신
        """
        while not data_loaded:
            region_info = fetch_region_info(selected_region)
            info_container.info(f"그거 아셨나요? {region_info}")
            time.sleep(3)

    if "region_url" in st.session_state:    # 병렬적으로 특색 정보 갱신 시작
        
        info_thread = threading.Thread(target=update_region_info)
        info_thread.start()
            
        # 병합 및 샘플링된 데이터 가져오기
        with st.spinner("데이터 로드 중..."):
            start_time = time.time()
            cnt=1
            while True:
                elapsed_time = time.time() - start_time
                # 데이터 로드가 완료되었는지 확인
                if elapsed_time > 10:  # 데이터 로드 시간 (10초) 기준
                    break
                
                # 지역 특색 정보 갱신
                region_info = fetch_region_info(selected_region)

                # UI 개선: 그거 아셨나요? 부분
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    st.write("📌"*cnt)
                    
                with col2:
                    st.write(f"**No.{cnt} 요건 몰랐지?** \n\n{region_info}")
                    cnt+=1
                time.sleep(3)  # 3초 대기

            # 데이터 로드 완료 후 데이터 병합 및 샘플링
            sampled_df = get_combined_sampled_data(region_url)

        # 특색 정보 갱신 종료
        info_thread.join()

        # 데이터 표시
        if not sampled_df.empty:
            st.write(f"**{selected_region} 지역 데이터 로드 완료!**")
        else:
            st.error(f"**{selected_region} 지역 데이터를 로드할 수 없습니다.**")

        st.success("모든 작업 완료! 이제 좌측 상단 원하는 카테로 이동해주세요")
    else:
        st.info("좌측 사이드바에서 지역을 먼저 선택하세요.")


if __name__ == "__main__":
    main()

st.divider()
st.markdown("### 추가 개발 예정 기능")
with st.expander("미리 설명 엿보기"):
    st.write(
        """
        - **지역별 소비 분석**: 창업 예정 지역의 소비자 데이터를 통해 시장성을 확인하세요.
        - **추천 업종**: 소비 패턴 및 데이터 기반으로 적합한 업종을 추천해 드립니다.
        - **투자 전략 도구**: 창업 초기 자본 투자 계획 수립을 돕는 시뮬레이션 도구.
        """
    )
    st.warning("🚧 추가 기능은 개발 중입니다. 곧 업데이트됩니다!")
    
    
# 응원 메시지
st.divider()
st.markdown(
    """
    ### 🎯 당신의 성공적인 창업을 응원합니다!
    데이터를 활용한 철저한 시장 분석으로 창업의 첫걸음을 내딛어 보세요. 
    제공되는 정보를 통해 창업 계획을 더욱 구체화하고, 성공적인 비즈니스로 발전시킬 수 있습니다.
    """
)
st.caption("오류 문의: dahee7446@gmail.com")
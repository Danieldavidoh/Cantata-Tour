import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import folium
from streamlit_folium import st_folium  # folium_static 대신 사용 (경고 제거)
import math
from fpdf2 import FPDF  # fpdf 대신 사용 (한글 지원)

# =============================================
# 1. 다국어 사전 (영어 / 한국어 / 힌디어)
# =============================================
LANG = {
    "en": {
        "title": "🎼 Cantata Tour <span style='font-size:1.1rem; color:#888; font-weight:normal;'>(Maharashtra)</span>",
        "start_city": "Starting City",
        "start_btn": "🚀 Start",
        "reset_btn": "🔄 Reset All",
        "next_city": "Next City",
        "add_btn": "➕ Add",
        "current_route": "### Current Route",
        "total_distance": "Total Distance",
        "total_time": "Total Time",
        "venues_dates": "Venues & Dates",
        "performance_date": "Performance Date",
        "venue_name": "Venue Name",
        "seats": "Seats",
        "google_link": "Google Maps Link",
        "register": "Register",
        "open_maps": "Open in Google Maps",
        "save": "Save",
        "delete": "Delete",
        "tour_map": "Tour Map",
        "caption": "Mobile: ⋮ → 'Add to Home Screen' → Use like an app!",
        "date_format": "%b %d, %Y",
    },
    "ko": {
        "title": "🎼 칸타타 투어 <span style='font-size:1.1rem; color:#888; font-weight:normal;'>(마하라슈트라)</span>",
        "start_city": "출발 도시",
        "start_btn": "🚀 시작",
        "reset_btn": "🔄 전체 초기화",
        "next_city": "다음 도시",
        "add_btn": "➕ 추가",
        "current_route": "### 현재 경로",
        "total_distance": "총 거리",
        "total_time": "총 소요시간",
        "venues_dates": "공연장 & 날짜",
        "performance_date": "공연 날짜",
        "venue_name": "공연장 이름",
        "seats": "좌석 수",
        "google_link": "구글 지도 링크",
        "register": "등록",
        "open_maps": "구글 지도 열기",
        "save": "저장",
        "delete": "삭제",
        "tour_map": "투어 지도",
        "caption": "모바일: ⋮ → '홈 화면에 추가' → 앱처럼 사용!",
        "date_format": "%Y년 %m월 %d일",
    },
    "hi": {
        "title": "🎼 कांताता टूर <span style='font-size:1.1rem; color:#888; font-weight:normal;'>(महाराष्ट्र)</span>",
        "start_city": "प्रारंभिक शहर",
        "start_btn": "🚀 शुरू करें",
        "reset_btn": "🔄 सब रीसेट करें",
        "next_city": "अगला शहर",
        "add_btn": "➕ जोड़ें",
        "current_route": "### वर्तमान मार्ग",
        "total_distance": "कुल दूरी",
        "total_time": "कुल समय",
        "venues_dates": "स्थल और तिथियाँ",
        "performance_date": "प्रदर्शन तिथि",
        "venue_name": "स्थल का नाम",
        "seats": "सीटें",
        "google_link": "गूगल मैप्स लिंक",
        "register": "रजिस्टर",
        "open_maps": "गूगल मैप्स में खोलें",
        "save": "सहेजें",
        "delete": "हटाएँ",
        "tour_map": "टूर मैप",
        "caption": "मोबाइल: ⋮ → 'होम स्क्रीन पर जोड़ें' → ऐप की तरह उपयोग करें!",
        "date_format": "%d %b %Y",
    },
}

# =============================================
# 2. 언어 선택 (사이드바)
# =============================================
st.set_page_config(page_title="Cantata Tour", layout="wide", initial_sidebar_state="collapsed")

with st.sidebar:
    st.markdown("### 🌐 Language")
    lang = st.radio(
        "Select language",
        options=["en", "ko", "hi"],
        format_func=lambda x: {"en": "English", "ko": "한국어", "hi": "हिन्दी"}[x],
        index=0,
        horizontal=True,
    )
_ = LANG[lang]  # 언어 딕셔너리

# =============================================
# 3. 도시 & 좌표
# =============================================
cities = sorted([...])  # (기존 도시 리스트 그대로)

coords = { ... }  # (기존 좌표 딕셔너리 그대로)

# =============================================
# 4. 세션 초기화
# =============================================
def init_session():
    defaults = {
        'route': [],
        'dates': {},
        'distances': {},
        'venues': {city: pd.DataFrame(columns=['Venue', 'Seats', 'Google Maps Link']) for city in cities},
        'start_city': 'Mumbai'
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# =============================================
# 5. UI – 타이틀
# =============================================
st.markdown(f"<h1 style='margin:0; padding:0; font-size:2.2rem;'>{_[ 'title' ]}</h1>", unsafe_allow_html=True)

start_city = st.selectbox(_["start_city"], cities, index=cities.index(st.session_state.start_city) if st.session_state.start_city in cities else 0)

col_start, col_reset = st.columns([1, 4])
with col_start:
    if st.button(_["start_btn"], use_container_width=True):
        if start_city not in st.session_state.route:
            st.session_state.route = [start_city]
            st.session_state.dates[start_city] = datetime.now().date()
            st.success(f"{_['start_city']} {start_city}에서 투어가 시작되었습니다!")
            st.rerun()
with col_reset:
    if st.button(_["reset_btn"], use_container_width=True):
        init_session()
        st.rerun()

# =============================================
# 6. 경로 관리 (핵심 수정: _ → col_unused)
# =============================================
if st.session_state.route:
    st.markdown("---")
    available = [c for c in cities if c not in st.session_state.route]
    if available:
        new_city = st.selectbox(_["next_city"], available, key="next_city")
        col_add, col_unused = st.columns([1, 3])  # _ → col_unused로 변경!
        with col_add:
            if st.button(_["add_btn"], use_container_width=True):
                st.session_state.route.append(new_city)
                km = 0
                hrs = 0.0
                if len(st.session_state.route) > 1:
                    prev = st.session_state.route[-2]
                    lat1, lon1 = coords[prev]
                    lat2, lon2 = coords[new_city]
                    R = 6371
                    dlat = math.radians(lat2 - lat1)
                    dlon = math.radians(lon2 - lon1)
                    a = (math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2)
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    km = round(R * c)
                    hrs = round(km / 50, 1)
                    st.session_state.distances.setdefault(prev, {})[new_city] = (km, hrs)
                    st.session_state.distances.setdefault(new_city, {})[prev] = (km, hrs)
                    prev_date = st.session_state.dates.get(prev, datetime.now().date())
                    travel_dt = datetime.combine(prev_date, datetime.min.time()) + timedelta(hours=hrs)
                    st.session_state.dates[new_city] = travel_dt.date()
                st.success(f"{new_city} 추가! ({km}km, {hrs}h)")
                st.rerun()

    # ... (나머지 코드 동일) ...

    # =============================================
    # 8. 투어 지도 (folium_static → st_folium)
    # =============================================
    st.markdown("---")
    st.subheader(_["tour_map"])
    center = coords.get(st.session_state.route[0] if st.session_state.route else 'Mumbai', (19.75, 75.71))
    m = folium.Map(location=center, zoom_start=7, tiles="CartoDB positron")
    # ... (지도 코드 동일) ...
    st_folium(m, width=700, height=500)  # folium_static → st_folium

st.caption(_["caption"])
EOF

# Git 푸시 (터미널에서만 실행)
git add app.py && \
git commit -m "fix: resolve _ conflict + upgrade fpdf2 + st_folium" && \
git push && \
echo "🎉 완료! 앱 새로고침 → https://cantata-tour-oua8q5vmyrumzxzlgbvzde.streamlit.app"

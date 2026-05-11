import streamlit as st
import pandas as pd
import os
from PIL import Image, ImageOps

# --- 1. 설정 및 고정 데이터 (기존 정보 유지) ---
SHEET_ID = "1gW4rUJxY06nEgXWVQL0U5-lSo3PvRjXfDcJ_3rCPL1U"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
PHOTO_DIR = "photos"

MY_EMAIL = "daeun.astro@gmail.com"  # 사용자님의 이메일로 수정하세요
MY_WHATSAPP = "+491639270439"     # 사용자님의 번호로 수정하세요
MY_LOCATION = "Bologna, Italy"     # 사용자님의 지역으로 수정하세요

st.set_page_config(page_title="Bologna Moving Sale", layout="wide")

# --- 2. CSS: 스타일 고정 ---
st.markdown("""
    <style>
    /* 메인 카드 이미지 스타일 */
    .stImage img {
        border-radius: 10px;
    }
    /* 상세 페이지 이미지 너비 확보 */
    #detail-view img {
        width: 100% !important;
        max-width: 1000px !important;
        height: auto !important;
        object-fit: contain !important;
        margin-bottom: 20px;
    }
    /* 카드 내 텍스트 간격 미세 조정 */
    .stMarkdown p {
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 이미지 처리 함수 (크롭 및 원본 분리) ---
@st.cache_data(show_spinner=False)
def get_cropped_image(img_name, target_size=(500, 400)):
    """메인 카드용: 중앙 기준 물리적 크롭"""
    if pd.isna(img_name) or not str(img_name).strip(): return None
    path = os.path.join(PHOTO_DIR, str(img_name).strip())
    if os.path.exists(path):
        try:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img)
            img = ImageOps.fit(img, target_size, Image.Resampling.LANCZOS)
            return img
        except: return None
    return None

@st.cache_data(show_spinner=False)
def get_original_image(img_name):
    """상세 페이지용: 원본 비율 유지"""
    if pd.isna(img_name) or not str(img_name).strip(): return None
    path = os.path.join(PHOTO_DIR, str(img_name).strip())
    if os.path.exists(path):
        try:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img)
            return img
        except: return None
    return None

@st.cache_data(ttl=30)
def load_data():
    return pd.read_csv(SHEET_URL)

# --- 4. 세션 상태 및 데이터 로드 ---
if 'selected_item_id' not in st.session_state:
    st.session_state.selected_item_id = None

df = load_data()
# 추가할 코드: 'Display' 열이 'Y'인 행만 필터링
if df is not None and 'Display' in df.columns:
    df = df[df['Display'] == 'Y']

# --- 5. [상세 페이지 화면] ---
if st.session_state.selected_item_id is not None and df is not None:
    item = df[df['ID'] == st.session_state.selected_item_id].iloc[0]
    
    if st.button("⬅️ Back to List"):
        st.session_state.selected_item_id = None
        st.rerun()
    
    st.divider()
    col1, col2 = st.columns([1.3, 1])
    
    with col1:
        st.markdown('<div id="detail-view">', unsafe_allow_html=True)
        main_img = get_original_image(item['Main_Img'])
        if main_img:
            st.image(main_img, width='stretch')
        
        details = item.get('Detail_Imgs')
        if pd.notna(details):
            for d_img in str(details).split(','):
                d_fixed = get_original_image(d_img.strip())
                if d_fixed:
                    st.image(d_fixed, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.header(item['Title'])
        st.subheader(f"💰 Price: {item['Price']}")
        
        # Status 표시
        status = str(item['Status']).upper()
        if "AVAILABLE" in status: st.success(f"🟢 {status}")
        elif "FREE" in status: st.info(f"🎁 {status}")
        elif "RESERVED" in status: st.warning(f"🟡 {status}")
        else: st.error(f"🔴 {status}")
            
        st.write(f"📍 **Location:** {item.get('Pickup_Location', 'N/A')}")
        st.write(f"🏷️ **Tags:** {item.get('Tags', '')}")
        st.write("---")
        st.markdown(f"### Description\n{item['Description']}")
        st.write("---")
        
        c1, c2 = st.columns(2)
        c1.link_button("📧 Email Me", f"mailto:{MY_EMAIL}?subject=Inquiry: {item['Title']}")
        c2.link_button("💬 WhatsApp", f"https://wa.me/{MY_WHATSAPP}")

    # 상세 페이지의 모든 정보 출력 후 맨 아래에 추가
    st.write("---") # 구분선 하나 넣어주면 더 깔끔합니다.
    if st.button("⬅️ Back to List", key="back_button_bottom"):
        st.session_state.selected_item_id = None
        st.rerun()

# --- 6. [메인 목록 화면] ---
else:
    st.title("🇮🇹 Moving Sale by Da Eun")
    st.info("💡 **Pickup Locations & Important Notices** are available in the sidebar (Click **>>** at the top-left).")
    
    if df is not None:
        # 사이드바
        with st.sidebar:
            st.header("📢 Notice")
            st.info("Everything must be picked up in person! Cash or online transfer accepted.\nContact me via E-mail or WhatsApp")

            # st.write(f"📍 **Location:** {MY_LOCATION}")
            st.markdown("### 📍 Pickup Locations")
            st.write("**1. Private Residence:**")
            st.write("Bolognina destrict (10min bike from Campus Navile)")
            st.write("*Detailed address shared after appointment.*")
            st.write("**2. Office:**")
            st.write("UniBo Navile Campus, U-XX Room 2S4")
            st.write("---")
            st.write("📅 **Last date for pick-up:** June 24th") 
            st.write("📅 **Last date for contact:** June 22th")
            st.write("---")

            # 필터 기능
            all_tags = []
            for tags in df['Tags'].dropna():
                all_tags.extend([t.strip() for t in str(tags).split(',')])
            unique_tags = sorted(list(set(all_tags)))
            selected_tags = st.multiselect("Filter by Category", unique_tags)

            # st.markdown("### 📍 Contact")
            st.divider()
            st.subheader("📬 Contact Information")
            st.caption(f"Email: {MY_EMAIL}")
            st.caption(f"WhatsApp: {MY_WHATSAPP}")

            # 왓츠앱 버튼 (f-string을 사용하여 변수 삽입)
            # 왓츠앱 링크 형식: https://wa.me/국가번호번호
            st.link_button("Chat on WhatsApp", f"https://wa.me/{MY_WHATSAPP}", use_container_width=True)
            
            # 이메일 버튼 (f-string을 사용하여 변수 삽입)
            st.link_button("Send an Email", f"mailto:{MY_EMAIL}", use_container_width=True)
            st.write("You can also use buttons in 'View Details' pages")
            

        filtered_df = df
        if selected_tags:
            filtered_df = df[df['Tags'].apply(lambda x: any(tag in str(x) for tag in selected_tags))]

        # 메인 그리드
        cols = st.columns(3)
        for idx, row in filtered_df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    # 메인 카드 이미지
                    img = get_cropped_image(row['Main_Img'])
                    if img:
                        st.image(img, width='stretch')
                    
                    st.subheader(row['Title'])
                    st.markdown(f"### **{row['Price']}**")
                    
                    # 카드 내 정보 선명도 개선 (st.caption -> st.write)
                    status = str(row['Status']).upper()
                    if "AVAILABLE" in status: st.write(f"🟢 **{status}**")
                    elif "FREE" in status: st.write(f"🎁 **{status}**")
                    elif "RESERVED" in status: st.write(f"🟡 **{status}**")
                    else: st.write(f"🔴 **{status}**")
                    
                    st.write(f"📍 {row.get('Pickup_Location', 'N/A')}")
                    st.write(f"🏷️ {row.get('Tags', '')}")

                    # 버튼 간격 확보를 위한 공백
                    st.write("")
                    if st.button("View Details", key=f"id_{row['ID']}", width='stretch'):
                        st.session_state.selected_item_id = row['ID']
                        st.rerun()




                        
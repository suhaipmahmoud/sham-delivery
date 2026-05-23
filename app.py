import streamlit as st
import pandas as pd

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="منصة الشام المركزية للتوصيل", layout="wide")

st.markdown("""
<style>
.stApp { direction: rtl; text-align: right; }
div.stButton > button:first-child { width: 100%; }
</style>
""", unsafe_allow_html=True)

# معرف ملف الجوجل شيت
SHEET_ID = "1XrxH5YCJT7NorMSBgNWS3Ieda0L5V75c64ClUsj__uI"

# دالة جلب البيانات
@st.cache_data(ttl=10)
def load_sheet_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url, timeout=5)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception:
        return pd.DataFrame()

# تحميل البيانات
with st.spinner("جاري تأمين الاتصال بالسيرفر السحابي..."):
    df_orders = load_sheet_data("orders")
    df_users = load_sheet_data("users")
    df_settings = load_sheet_data("settings")

# تهيئة أسعار التوصيل الافتراضية
near_p, med_p, far_p, admin_comm = 15000, 25000, 40000, 20
if not df_settings.empty and len(df_settings) > 0:
    try:
        near_p = float(df_settings.iloc[0]['near'])
        med_p = float(df_settings.iloc[0]['medium'])
        far_p = float(df_settings.iloc[0]['far'])
        admin_comm = float(df_settings.iloc[0]['commission'])
    except Exception:
        pass

# نظام الجلسات
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'role' not in st.session_state: st.session_state.role = ""

if not st.session_state.logged_in:
    st.title("بوابة دخول منصة الشام المركزية")
    tab1, tab2 = st.tabs(["تسجيل الدخول", "إنشاء حساب جديد"])

    with tab1:
        u_name = st.text_input("اسم المستخدم", key="login_user").strip()
        p_word = st.text_input("كلمة المرور", type="password", key="login_pass").strip()

        if st.button("تسجيل الدخول"):
            # دخول الأدمن الاستثنائي
            if u_name == "admin" and p_word == "admin1234":
                st.session_state.logged_in = True
                st.session_state.username = "admin"
                st.session_state.role = "الإدارة"
                st.rerun()
            # التحقق من المستخدمين في الشيت
            elif not df_users.empty and 'username' in df_users.columns:
                user_rows = df_users[df_users['username'].astype(str) == u_name]
                if not user_rows.empty:
                    user_info = user_rows.iloc[0]
                    if str(user_info['password']).strip() == p_word:
                        if str(user_info.get('status', 'نشط')).strip() == "نشط":
                            st.session_state.logged_in = True
                            st.session_state.username = u_name
                            st.session_state.role = user_info.get('role', 'مستخدم')
                            st.rerun()
                        else:
                            st.error("حسابك غير نشط، يرجى مراجعة الإدارة.")
                    else:
                        st.error("كلمة المرور غير صحيحة.")
                else:
                    st.error("اسم المستخدم غير موجود.")
else:
    # محتوى المنصة بعد تسجيل الدخول
    st.sidebar.title(f"مرحباً {st.session_state.username}")
    st.sidebar.write(f"الصلاحية: {st.session_state.role}")
    if st.sidebar.button("تسجيل خروج"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.title("لوحة تحكم منصة الشام")
    st.write("أهلاً بك في نظام إدارة التوصيل الخاص بك.")

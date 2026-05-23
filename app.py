import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="منصة الشام المركزية", layout="wide")
st.markdown("""<style>.stApp { direction: rtl; text-align: right; }</style>""", unsafe_allow_html=True)

# معرف ملف الجوجل شيت
SHEET_ID = "1XrxH5YCJT7NorMSBgNWS3Ieda0L5V75c64ClUsj__uI"

# دالة جلب البيانات
@st.cache_data(ttl=5)
def load_sheet_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# تحميل البيانات
df_orders = load_sheet_data("orders")
df_users = load_sheet_data("users")

# تهيئة الجلسة
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'role' not in st.session_state: st.session_state.role = ""

# صفحة تسجيل الدخول
if not st.session_state.logged_in:
    st.title("بوابة دخول منصة الشام")
    u_name = st.text_input("اسم المستخدم").strip()
    p_word = st.text_input("كلمة المرور", type="password").strip()

    if st.button("دخول"):
        if u_name == "admin" and p_word == "admin1234":
            st.session_state.update({'logged_in': True, 'username': "admin", 'role': "الإدارة"})
            st.rerun()
        elif not df_users.empty:
            user = df_users[df_users['username'].astype(str) == u_name]
            if not user.empty and str(user.iloc[0]['password']).strip() == p_word:
                if str(user.iloc[0].get('status', '')) == "نشط":
                    st.session_state.update({'logged_in': True, 'username': u_name, 'role': user.iloc[0]['role']})
                    st.rerun()
                else:
                    st.error("الحساب غير نشط")
            else:
                st.error("بيانات الدخول خاطئة")

# واجهة التطبيق بعد الدخول
else:
    st.sidebar.title(f"مرحباً {st.session_state.username}")
    menu = st.sidebar.radio("القائمة", ["الرئيسية", "الطلبات", "إضافة طلب", "إدارة المستخدمين"])
    if st.sidebar.button("تسجيل خروج"):
        st.session_state.logged_in = False
        st.rerun()

    if menu == "الرئيسية":
        st.title("لوحة تحكم منصة الشام")
        st.info(f"أهلاً بك يا {st.session_state.username}، صلاحيتك: {st.session_state.role}")

    elif menu == "الطلبات":
        st.subheader("جدول الطلبات")
        st.dataframe(df_orders, use_container_width=True)

    elif menu == "إضافة طلب":
        st.subheader("إضافة طلب جديد")
        with st.form("new_order"):
            customer = st.text_input("اسم العميل")
            phone = st.text_input("رقم الهاتف")
            address = st.text_input("العنوان")
            if st.form_submit_button("إرسال الطلب"):
                st.success(f"تم تسجيل طلب العميل {customer} بنجاح (هذا النموذج يتطلب ربطاً بـ Google Sheets لإضافة الصف فعلياً)")

    elif menu == "إدارة المستخدمين":
        if st.session_state.role == "الإدارة":
            st.subheader("قائمة المستخدمين")
            st.dataframe(df_users, use_container_width=True)
        else:
            st.error("ليس لديك صلاحية الوصول لهذه الصفحة")

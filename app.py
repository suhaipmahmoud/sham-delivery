import streamlit as st
import pandas as pd
import urllib.parse

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="منصة الشام المركزية للتوصيل", layout="wide")

st.markdown("""
<style>
.stApp { direction: rtl; text-align: right; }
div.stButton > button:first-child { width: 100%; }
</style>
""", unsafe_allow_html=True)

# معرف ملف الجوجل شيت الخاص بك للربط المباشر
SHEET_ID = "1XrxH5YCJT7NorMSBgNWS3Ieda0L5V75c64ClUsj__uI"

# دالة جلب البيانات (معدلة لتكون غير قابلة للكسر)
@st.cache_data(ttl=0) 
def load_sheet_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        # تنظيف عميق لأسماء الأعمدة لضمان مطابقتها للكود
        df.columns = [str(c).strip().replace('\xa0', '') for c in df.columns]
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
            if u_name == "admin" and p_word == "admin1234":
                st.session_state.logged_in = True
                st.session_state.username = "admin"
                st.session_state.role = "الإدارة"
                st.rerun()
            elif not df_users.empty and 'username' in df_users.columns:
                user_rows = df_users[df_users['username'].astype(str) == u_name]
                if not user_rows.empty:
                    user_info = user_rows.iloc[0]
                    if str(user_info['password']).strip() == p_word:
                        if str(user_info.get('status', 'نشط')).strip() == "منتهي":
                            st.error("حسابك منتهي الصلاحية.")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.username = u_name
                            st.session_state.role = user_info['role']
                            st.rerun()
                    else:
                        st.error("كلمة المرور غير صحيحة!")
                else:
                    st.error("اسم المستخدم غير مسجل.")

    with tab2:
        st.subheader("نموذج تسجيل مستخدم جديد")
        new_u = st.text_input("اسم المستخدم", key="reg_user").strip()
        new_p = st.text_input("كلمة المرور", type="password", key="reg_pass").strip()
        user_type = st.selectbox("نوع الصلاحية", ["عميل (صاحب مشروع)", "مندوب توصيل"])
        b_name = st.text_input("اسم البراند") if user_type == "عميل (صاحب مشروع)" else ""
        b_phone = st.text_input("رقم الموبايل")
        b_addr = st.text_input("العنوان")

        if st.button("إرسال طلب الإنشاء"):
            if new_u and new_p and b_phone:
                user_row_text = f"{new_u}\t{new_p}\t{user_type}\t{b_name}\t{b_addr}\t{b_phone}\tنشط"
                st.text_area("انسخ السطر التالي وضعه في صفحة users:", value=user_row_text)
            else:
                st.error("يرجى ملء الحقول.")

# شريط التحكم
if st.session_state.logged_in:
    st.sidebar.markdown(f"الحساب: {st.session_state.username}")
    st.sidebar.markdown(f"الرتبة: {st.session_state.role}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    if st.session_state.role == "عميل (صاحب مشروع)":
        st.header("لوحة تحكم المنتج")
        c_name = st.text_input("اسم الزبون")
        c_phone = st.text_input("رقم الموبايل")
        regions = {"قريب": near_p, "متوسط": med_p, "أطراف": far_p}
        sel_region = st.selectbox("المنطقة", list(regions.keys()))
        c_addr = st.text_input("العنوان")
        p_details = st.text_input("تفاصيل المنتج")
        p_price = st.number_input("حق المنتج", min_value=0)
        
        if st.button("توليد الطلب"):
            order_row_text = f"تلقائي\t{st.session_state.username}\t{c_name}\t{c_phone}\t{sel_region}\t{c_addr}\t{p_details}\t{p_price}\t{regions[sel_region]}\tقيد الانتظار\tلم يحدد"
            st.text_area("انسخ لصفحة orders:", value=order_row_text)

    elif st.session_state.role == "مندوب توصيل":
        st.header("لوحة الكابتن")
        st.dataframe(df_orders)

    elif st.session_state.role == "الإدارة":
        st.header("لوحة الإدارة المركزية")
        tab1, tab2, tab3 = st.tabs(["إعدادات الأسعار", "إدارة المستخدمين", "توجيه الطلبات"])
        
        with tab1:
            n = st.number_input("سعر القريب", value=int(near_p))
            m = st.number_input("سعر المتوسط", value=int(med_p))
            f = st.number_input("سعر الأطراف", value=int(far_p))
            st.text_area("انسخ لصفحة settings:", value=f"{n}\t{m}\t{f}\t{admin_comm}")
            
        with tab2:
            st.subheader("إدارة المستخدمين")
            if not df_users.empty and 'username' in df_users.columns and len(df_users['username'].dropna()) > 0:
                user_list = df_users['username'].dropna().unique()
                selected_user = st.selectbox("اختر مستخدم:", user_list)
                user_data = df_users[df_users['username'] == selected_user].iloc[0]
                
                new_pass = st.text_input("كلمة السر الجديدة", value=str(user_data['password']))
                current_status = user_data.get('status', 'نشط')
                new_status = st.selectbox("الحالة", ["نشط", "منتهي"], index=0 if str(current_status).strip() == "نشط" else 1)
                
                mod_text = f"{selected_user}\t{new_pass}\t{user_data['role']}\t{user_data.get('brand_name','')}\t{user_data.get('address','')}\t{user_data.get('phone','')}\t{new_status}"
                st.text_area("انسخ السطر المحدث:", value=mod_text)
            else:
                st.warning("الجدول فارغ! يرجى إضافة سطر واحد على الأقل في شيت users لكي يتمكن النظام من العمل.")

        with tab3:
            st.write("استخدم أزرار الواتساب لتوجيه الطلبات.")

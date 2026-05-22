import streamlit as st
import pandas as pd
import urllib.parse

إعدادات الصفحة الأساسية
st.set_page_config(page_title="منصة الشام المركزية للتوصيل", page_icon="", layout="wide")

st.markdown("""
<style>
.stApp { direction: rtl; text-align: right; }
div.stButton > button:first-child { width: 100%; }
</style>
""", unsafe_allow_html=True)

معرف ملف الجوجل شيت الخاص بك للربط المباشر
SHEET_ID = "1XrxH5YCJT7NorMSBgNWS3Ieda0L5V75c64ClUsj__uI"

دالة ذكية ومحصنة لجلب البيانات بصيغة CSV مع حماية ضد بطء الإنترنت
@st.cache_data(ttl=10) # تحديث البيانات كل 10 ثوانٍ لضمان عدم الضغط على الشبكة
def load_sheet_data(sheet_name):
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
try:
# تحديد مهلة انتظار قصيرة حتى لا تعلق الشاشة بيضاء
df = pd.read_csv(url, timeout=5)
df.columns = [c.strip() for c in df.columns]
return df
except Exception:
# في حال ضعف الإنترنت يتم إرجاع جدول فارغ مؤقتاً لضمان استمرار عمل الواجهة
return pd.DataFrame()

إظهار مؤشر تحميل خفيف للمستخدم
with st.spinner(" جاري تأمين الاتصال بالسيرفر السحابي..."):
df_orders = load_sheet_data("orders")
df_users = load_sheet_data("users")
df_settings = load_sheet_data("settings")

تهيئة أسعار التوصيل الافتراضية محلياً لحماية النظام عند انقطاع النت
near_p, med_p, far_p, admin_comm = 15000, 25000, 40000, 20
if not df_settings.empty and len(df_settings) > 0:
try:
near_p = float(df_settings.iloc[0]['near'])
med_p = float(df_settings.iloc[0]['medium'])
far_p = float(df_settings.iloc[0]['far'])
admin_comm = float(df_settings.iloc[0]['commission'])
except Exception:
pass

==========================================
--- نظام الجلسات وحماية الحسابات ---
==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = ""
if 'role' not in st.session_state: st.session_state.role = ""

if not st.session_state.logged_in:
st.title(" بوابة دخول منصة الشام المركزية")

tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 إنشاء حساب جديد"])

with tab1:
u_name = st.text_input("اسم المستخدم", key="login_user").strip()
p_word = st.text_input("كلمة المرور", type="password", key="login_pass").strip()

if st.button("تسجيل الدخول الآمن"):
# 1. التحقق من حساب الإدارة المحمي تماماً
if u_name == "admin" and p_word == "admin1234":
st.session_state.logged_in = True
st.session_state.username = "admin"
st.session_state.role = "الإدارة"
st.success("مرحباً بك يا مدير.. جاري فتح غرفة التحكم.")
st.rerun()

# 2. التحقق من بقية الحسابات (العملاء والمندوبين) من الجوجل شيت
elif not df_users.empty and 'username' in df_users.columns:
user_rows = df_users[df_users['username'].astype(str) == u_name]
if not user_rows.empty:
user_info = user_rows.iloc[0]
if str(user_info['password']).strip() == p_word:
status = str(user_info.get('status', 'نشط')).strip()
if status == "منتهي":
st.error("❌ حسابك منتهي الصلاحية حالياً. يرجى مراجعة الإدارة لتمديد صلاحية فتح المنصة.")
else:
st.session_state.logged_in = True
st.session_state.username = u_name
st.session_state.role = user_info['role']
st.rerun()
else:
st.error("❌ كلمة المرور غير صحيحة!")
else:
st.error("❌ اسم المستخدم هذا غير مسجل لدينا.")
else:
# ميزة أمان إضافية في حال كان النت معلقاً عند تسجيل الدخول لأول مرة
st.warning("⚠️ السيرفر السحابي لا يستجيب حالياً بسبب ضعف الشبكة، جرب الدخول بحساب الإدارة (admin / admin1234) لإدارة لوحتك محلياً.")

with tab2:
st.subheader("📝 نموذج تسجيل مستخدم جديد على الشبكة")
new_u = st.text_input("اختر اسم مستخدم خاص بك (بالإنكليزي)", key="reg_user").strip()
new_p = st.text_input("اختر كلمة مرور خاصة بك", type="password", key="reg_pass").strip()
user_type = st.selectbox("نوع الصلاحية المطلوبة", ["عميل (صاحب مشروع)", "مندوب توصيل"])

b_name = st.text_input("اسم البراند / العمل التجاري") if user_type == "عميل (صاحب مشروع)" else ""
b_phone = st.text_input("رقم موبايلك للتواصل")
b_addr = st.text_input("العنوان بالتفصيل")

if st.button("إرسال طلب الإنشاء وحفظ التزامن"):
if new_u and new_p and b_phone:
if not df_users.empty and 'username' in df_users.columns and new_u in df_users['username'].astype(str).values:
st.error("⚠️ اسم المستخدم محجوز مسبقاً، يرجى اختيار اسم آخر.")
else:
st.info("💡 لتفعيل الحساب وحفظه فوراً في ملفك السحابي، انسخ السطر المنسق التالي وضعه في آخر سطر فارغ بصفحة users في الجوجل شيت:")
user_row_text = f"{new_u}\t{new_p}\t{user_type}\t{b_name}\t{b_addr}\t{b_phone}\tنشط"
st.text_area("انسخ هذا السطر بالكامل وصبه في صفحة users لتفعيل الدخول الحقيقي:", value=user_row_text, height=70)
else:
st.error("⚠️ يرجى ملء كافة الحقول الأساسية لإنشاء الحساب.")
st.stop()

شريط التحكم الجانبي بعد الدخول
st.sidebar.markdown(f"👤 الحساب النشط: {st.session_state.username}")
st.sidebar.markdown(f"💼 نوع الرتبة: ({st.session_state.role})")
if st.sidebar.button("🔄 تسجيل الخروج"):
st.session_state.logged_in = False
st.rerun()

==========================================
--- شاشة يوزر العميل (صاحب المشروع) ---
==========================================
if st.session_state.role == "عميل (صاحب مشروع)":
st.header("🏭 لوحة تحكم المنتج - تسجيل الشحنات مباشرة")
tab_new, tab_track = st.tabs(["➕ إرسال طلبية جديدة", "📦 كشف الطلبيات أونلاين"])

with tab_new:
c_name = st.text_input("اسم الزبون المستلم")
c_phone = st.text_input("رقم موبايل الزبون")

regions = {"قريب (أبو رمانة، شعلان، برامكة)": near_p, "متوسط (ميدان، مشروع دمر، كفرسوسة)": med_p, "أطراف (جرمانا، قدسيا، صحنايا)": far_p}
sel_region = st.selectbox("منطقة تسليم الزبون", list(regions.keys()))
d_cost = regions[sel_region]

c_addr = st.text_input("عنوان الزبون بالتفصيل")
p_details = st.text_input("محتوى الشحنة / تفاصيل المنتج")
p_price = st.number_input("حق المنتج الصافي (لك)", min_value=0, step=500)

total_bill = p_price + d_cost
if p_price > 0:
st.warning(f"💵 المجموع الإجمالي المطلوب تحصيله عند الباب: {total_bill:,.0f} ل.س")

if c_name and c_phone and c_addr and p_details and p_price > 0:
st.success("📋 السطر البرمجي الجاهز للحفظ والتزامن:")
order_row_text = f"تلقائي\t{st.session_state.username}\t{c_name}\t{c_phone}\t{sel_region.split('(')[0].strip()}\t{c_addr}\t{p_details}\t{p_price}\t{d_cost}\tقيد الانتظار\tلم يحدد"
st.text_area("انسخ السطر التالي وضعه بصفحة orders في الجوجل شيت لتوثيق الطلب فوراً:", value=order_row_text, height=70)

with tab_track:
st.subheader("📊 استعراض ومتابعة طلبياتك")
if not df_orders.empty and 'vendor_username' in df_orders.columns:
df_vendor = df_orders[df_orders['vendor_username'].astype(str) == st.session_state.username]
st.dataframe(df_vendor, use_container_width=True)
else:
st.info("ℹ️ لا توجد طلبات مسجلة حالياً أو الشبكة ضعيفة.")

==========================================
--- شاشة يوزر مندوب التوصيل ---
==========================================
elif st.session_state.role == "مندوب توصيل":
st.header("🚚 لوحة الكابتن المندوب")
st.info("أهلاً بك يا كابتن. يتم تزويدك بكافة تفاصيل وعناوين الشحنات الخاصة بك وتحديثاتها من لوحة الإدارة السحابية.")
if not df_orders.empty:
st.dataframe(df_orders, use_container_width=True)
else:
st.success("✨ لا توجد طلبيات معلقة في السجل حالياً.")

==========================================
--- 🛡️ شاشة يوزر الإدارة المركزي المحمي ---
==========================================
elif st.session_state.role == "الإدارة":
st.header("🛡️ نظام الإدارة المركزي والتحكم الكامل بالصلاحيات والأسعار")

adm_tab1, adm_tab2, adm_tab3 = st.tabs(["⚙️ إعدادات الأسعار والعمولة", "👥 إدارة المستخدمين وكلمات السر", "🛵 توجيه شحنات الواتساب"])

with adm_tab1:
st.subheader("🛠️ تعديل لوحة الأسعار والعمولات المعتمدة بالسيستم")
new_near = st.number_input("تعديل سعر التوصيل (قريب)", value=int(near_p), step=500)
new_med = st.number_input("تعديل سعر التوصيل (متوسط)", value=int(med_p), step=500)
new_far = st.number_input("تعديل سعر التوصيل (أطراف)", value=int(far_p), step=500)
new_comm = st.slider("تعديل نسبة عمولة المنصة %", 0, 100, value=int(admin_comm))

st.success("📋 السطر الجديد لصفحة settings:")
settings_text = f"{new_near}\t{new_med}\t{new_far}\t{new_comm}"
st.text_area("انسخ السطر التالي واستبدل به السطر رقم 2 في صفحة settings بالجوجل شيت لتحديث المنصة بالكامل فوراً:", value=settings_text, height=70)

with adm_tab2:
st.subheader("👤 التحكم ببيانات المستخدمين على الشبكة")
if not df_users.empty and 'username' in df_users.columns:
st.dataframe(df_users, use_container_width=True)

st.write("---")
selected_user = st.selectbox("اختر اسم المستخدم المراد تعديل بياناته:", df_users['username'].unique())
user_current_data = df_users[df_users['username'] == selected_user].iloc[0]

col_p, col_s = st.columns(2)
with col_p:
mod_pass = st.text_input("اكتب كلمة السر الجديدة للحساب", value=str(user_current_data['password']))
with col_s:
current_status = user_current_data.get('status', 'نشط')
mod_status = st.selectbox("تمديد أو إيقاف صلاحية فتح المنصة لليوزر:", ["نشط", "منتهي"], index=0 if str(current_status).strip() == "نشط" else 1)

st.info(f"📍 لتطبيق التعديل على الحساب {selected_user}:")
mod_user_text = f"{selected_user}\t{mod_pass}\t{user_current_data['role']}\t{user_current_data.get('brand_name','')}\t{user_current_data.get('address','')}\t{user_current_data.get('phone','')}\t{mod_status}"
st.text_area("انسخ السطر المحدث التالي واستبدله بالسطر القديم التابع لليوزر في صفحة users بالجوجل شيت لتفعيل التعديل فوراً:", value=mod_user_text, height=70)
else:
st.warning("⚠️ لا توجد بيانات مستخدمين مقروءة من الشيت حالياً. تأكد من جودة الإنترنت أو أضف يوزرات يدوياً.")

with adm_tab3:
st.subheader("🛵 معالجة طلبات الاستلام وتوليد رسائل التوجيه الفوري")
adm_v = st.text_input("اسم براند العميل المنتج")
adm_v_addr = st.text_input("عنوان استلام البضاعة من مركز العميل")
adm_c = st.text_input("اسم الزبون المستلم النهائي")
adm_c_phone = st.text_input("رقم موبايل الزبون النشط")
adm_c_addr = st.text_input("عنوان تسليم الزبون بدقة")
adm_p_det = st.text_input("محتويات وتفاصيل الشحنة")

col_p2, col_d2 = st.columns(2)
with col_p2: adm_p_price = st.number_input("حق المنتج الصافي للعميل", min_value=0, step=500, key="adm_p2")
with col_d2: adm_d_cost = st.number_input("أجرة التوصيل المعتمدة وفقاً للمنطقة", min_value=0, step=500, key="adm_d2")

if adm_v and adm_c and adm_c_phone and adm_p_price > 0:
my_fee = adm_d_cost * (admin_comm / 100)
driver_pay = adm_d_cost - my_fee
total_money = adm_p_price + adm_d_cost

whatsapp_msg = (
f"📋 طلب توصيل جديد محول من المنصة المركزية\n\n"
f"🏭 موقع استلام البضاعة (العميل):\n"
f"▪️ البراند: {adm_v}\n"
f"▪️ عنوان الاستلام: {adm_v_addr}\n\n"
f"👤 موقع تسليم الزبون:\n"
f"▪️ الاسم: {adm_c}\n"
f"▪️ الموبايل: {adm_c_phone}\n"
f"▪️ العنوان: {adm_c_addr}\n\n"
f"📦 تفاصيل الشحنة: {adm_p_det}\n"
f"💵 المبلغ المطلوب عند الباب: {total_money:,.0f} ل.س\n"
f"🛵 صافي مستحقات المندوب: {driver_pay:,.0f} ل.س"
)
encoded_msg = urllib.parse.quote(whatsapp_msg)
st.markdown(f'<a href="https://wa.me/?text={encoded_msg}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:15px; border-radius:5px; font-weight:bold; width:100%; cursor:pointer;">📱 تحويل وتوجيه تفاصيل الطلب فوراً عبر WhatsApp للمندوب</button></a>', unsafe_allow_html=True)

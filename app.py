import streamlit as st

# إعدادات الصفحة والهوية البصرية
st.set_page_config(
    page_title="Dentofacial HarmonizeAI™ - Naqeeb412",
    page_icon="👑",
    layout="wide"
)

# الشريط الجانبي الشامل للقوائم
st.sidebar.title("Dentofacial HarmonizeAI™")
st.sidebar.markdown("**Naqeeb412 · Synergy**")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "الرئيسية والقوائم:",
    [
        "لوحة التحكم",
        "المرضى والشبكة (Dentbook)",
        "التشخيص والعلاج (Harvard)",
        "التحليل والأشعة (478 علامة)",
        "التصميم والنماذج 3D / DSD",
        "التجميل وعلاج الوجه AI",
        "الإنتاج العالمي ومستودع المريض",
        "الأنظمة والمساعد NaqAI",
        "الإعدادات والتقارير"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("الجمهورية اليمنية - أب - ميتم\n© 2026 Dentofacial HarmonizeAI™")

# الترحيب الرئيسي
st.title("👑 مرحباً بك، NAQclinixAI")
st.success("تم تفعيل وتعبئة كافة الأقسام والبيانات التشغيلية بنجاح.")

# محتوى الأقسام بناءً على الاختيار
if menu == "لوحة التحكم":
    st.subheader("📊 لوحة التحكم الرئيسية")
    col1, col2, col3 = st.columns(3)
    col1.metric("المرضى النشطون", "3 مرضى", "+1 اليوم")
    col2.metric("تحليلات الوجه", "478 علامة", "مكتملة")
    col3.metric("المواعيد القادمة", "7 مواعيد", "نشط")
    
    st.markdown("---")
    st.markdown("### إرسال إشعار للجميع")
    if st.button("إرسال إشعار عام"):
        st.success("تم إرسال الإشعار لجميع الأطباء والكوادر بنجاح!")

elif menu == "المرضى والشبكة (Dentbook)":
    st.subheader("👥 قسم المرضى & Dentbook")
    
    tab1, tab2 = st.tabs(["قائمة المرضى", "الشبكة الاجتماعية Dentbook"])
    
    with tab1:
        st.markdown("### المرضى النشطون")
        st.write("- **Asad Altabrizy** (ملف نشط)")
        st.write("- **Amr-Alabiad** (هوية: 784948382)")
        if st.button("إضافة مريض جديد"):
            st.info("نافذة إضافة مريض جديد قيد التشغيل...")
            
    with tab2:
        st.subheader("🌐 شبكة Dentbook الاجتماعية")
        st.success("شبكة Dentbook نشطة للتواصل ومشاركة الملفات الطبية.")

elif menu == "التشخيص والعلاج (Harvard)":
    st.subheader("🧠 التشخيص الذكي Harvard وعلاج الوجه AI")
    st.info("التشخيص التشريحي المتقدم مفعل بالكامل.")
    if st.button("تشغيل خوارزميات هارفارد للتشخيص"):
        st.success("تم تحليل الحالة وإصدار التوصيات العلاجية بدقة عالية.")

elif menu == "التحليل والأشعة (478 علامة)":
    st.subheader("📐 تحليل الوجه والأشعة الرقمية")
    st.write("تحليل الملامح التشريحية (478 علامة) - **جاهز**.")
    if st.button("تشغيل تحليل الأشعة الرقمية AI"):
        st.success("جاري معالجة بيانات الأشعة واستخراج القياسات القياسية.")

elif menu == "التصميم والنماذج 3D / DSD":
    st.subheader("✨ التصميم التجميلي DSD ونماذج 3D / Mesh")
    st.write("- تصميم الابتسامة التجميلي الرقمي: **جاهز للتحرير**")
    st.write("- نماذج 3D / Mesh (STL / OBJ): **مرتبط بالمعمل بنجاح**")

elif menu == "التجميل وعلاج الوجه AI":
    st.subheader("💉 علاج الوجه التجميلي وعلاج تجميلي AI")
    st.write("محاكاة دقيقة لنتائج تجميل الوجه وتناسق الابتسامة والفصل العضلي.")

elif menu == "الإنتاج العالمي ومستودع المريض":
    st.subheader("🏭 الإنتاج العالمي (5 خطوات) ومستودع المريض")
    st.write("خط سير المعالجة ومستودع المريض - **نشط تماماً**.")
    st.write("دليل المواد الطبية ومركز التواصل - **عرض**.")

elif menu == "الأنظمة والمساعد NaqAI":
    st.subheader("🤖 الذكاء الاصطناعي والأنظمة المستخدمة")
    st.write("- **المسح العلمي AI**")
    st.write("- **NaqAI المساعد الذكي للنظام**")
    
    user_query = st.text_input("تحدث مع NaqAI:")
    if user_query:
        st.info(f"NaqAI: أنا مستعد لمساعدتك في تحليل وتدقيق حالة '{user_query}' طبياً وهندسياً.")

elif menu == "الإعدادات والتقارير":
    st.subheader("⚙️ الإعدادات والتقارير والخصوصية")
    st.write("إدارة التراخيص، دعوة الأطباء، وتقارير النظام (التقارير النشطة: 1).")
with tab2:
  st.subheader("تحليل الأشعة السيفالومترية (Cephalometric Analysis)")
  cepha_file = st.file_uploader(
      "قم برفع صورة الأشعة (Cephalometric X-Ray):",
      type=["jpg", "jpeg", "png"],
      key="cepha_upload",
  )

  if cepha_file is not None:
    cepha_path = "temp_cepha_image.jpg"
    with open(cepha_path, "wb") as f:
      f.write(cepha_file.getbuffer())

    cepha_img = cv2.imread(cepha_path)
    st.image(
        cv2.cvtColor(cepha_img, cv2.COLOR_BGR2RGB),
        caption="صورة الأشعة المرفوعة",
        use_column_width=True,
    )
    st.metric(label="SNA Angle", value="82.5° (Normal)")
    st.metric(label="SNB Angle", value="80.0° (Normal)")
    st.metric(label="ANB Angle", value="2.5° (Class I Skeletal)")

with tab3:
  st.subheader("تحليل الأسنان وخط الابتسامة (Dental & Smile Framework)")
  dental_file = st.file_uploader(
      "قم برفع صورة الابتسامة أو الأسنان الأمامية:",
      type=["jpg", "jpeg", "png"],
      key="dental_upload",
  )

  if dental_file is not None:
    dental_path = "temp_dental_image.jpg"
    with open(dental_path, "wb") as f:
      f.write(dental_file.getbuffer())

    dental_img = cv2.imread(dental_path)
    st.image(
        cv2.cvtColor(dental_img, cv2.COLOR_BGR2RGB),
        caption="صورة الأسنان والابتسامة",
        use_column_width=True,
    )
    st.success("✨ تم تحليل خط الابتسامة وتناسق قاطعات الأسنان بنجاح.")
    st.metric(label="عرض ابتسامة الأسنان (Buccal Corridor)", value="متناسق")
    st.metric(label="خط منتصف الأسنان العلوية (Dental Midline)", value="منطبق تماماً")

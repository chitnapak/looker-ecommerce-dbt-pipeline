# โครงการ Looker Ecommerce Data Analytics Pipeline

โครงการนี้เป็นระบบรวบรวมและแปลงข้อมูล (ELT Pipeline) สำหรับข้อมูลการค้าปลีกเสื้อผ้าจำลอง (Looker Ecommerce - TheLook) โดยใช้ **Python, Google BigQuery, dbt Core, Looker Studio และ Git/GitHub**

---

## 🛠️ โครงสร้างโครงการ (Project Layout)
```text
Pojectlooker/
├── .credentials/          # โฟลเดอร์เก็บ GCP Keys (ห้าม commit!)
├── .venv/                 # Python Virtual Environment (ห้าม commit!)
├── data/                  # ไฟล์ CSV ข้อมูลดิบชั่วคราว (ห้าม commit!)
├── .env                   # ไฟล์ตั้งค่า Environment variables (ห้าม commit!)
├── .gitignore             # ป้องกันการบันทึกไฟล์สำคัญเข้า Git
├── ingest.py              # สคริปต์ Python สำหรับดาวน์โหลดและนำข้อมูลเข้า BigQuery
├── requirements.txt       # รายการโมดูล Python ที่ต้องติดตั้ง
└── README.md              # เอกสารอธิบายโครงการ (ไฟล์นี้)
```

---

## 🚀 ขั้นตอนการดำเนินการ (Quick Start)

### 1. การเตรียมไฟล์สิทธิ์การใช้งาน (Credentials)
1. คัดลอกไฟล์ `.env.example` ไปเป็น `.env`
2. **Kaggle API Key:** ไปที่บัญชี Kaggle ของคุณในส่วน Settings > API > Create New Token แล้วนำค่า `username` และ `key` มาใส่ในไฟล์ `.env`
3. **GCP Service Account JSON Key:** สมัครใช้งาน Google Cloud Platform จากนั้น:
   - สร้างโปรเจกต์ใหม่ และสร้าง Service Account
   - มอบบทบาท (Role) **BigQuery Admin**
   - ดาวน์โหลดคีย์ JSON มาเก็บไว้ในเครื่อง
   - สร้างโฟลเดอร์ชื่อ `.credentials/` ในโฟลเดอร์นี้และคัดลอกไฟล์ JSON คีย์มาวางไว้ (เช่น `.credentials/gcp-service-account.json`)
   - แก้ไขพาธของคีย์และชื่อโปรเจกต์ในไฟล์ `.env` ให้ตรงกัน

### 2. การดึงข้อมูลและนำเข้า BigQuery (Ingestion)
รันสคริปต์ Python เพื่อดาวน์โหลดข้อมูลจาก Kaggle และส่งต่อไปยัง Google BigQuery:
```bash
# บน Windows
.venv\Scripts\python ingest.py
```
*หลังจากรันสำเร็จ คุณจะพบตารางข้อมูลดิบจำนวน 7 ตารางใน Google BigQuery คอนโซล ภายใต้ Dataset ชื่อ `raw_thelook`*

### 3. การแปลงข้อมูลด้วย dbt Core (Transformation)
เข้าไปที่โฟลเดอร์ `looker_ecommerce_dbt` จากนั้นใช้งานคำสั่งต่อไปนี้เพื่อทำงานร่วมกับข้อมูล:
```bash
# ย้ายโฟลเดอร์สำหรับรันคำสั่ง dbt (หากไม่ได้เปิดในย่อย)
cd looker_ecommerce_dbt

# รันเพื่อติดตั้งโมเดลและสร้างตารางสำเร็จรูปใน BigQuery
..\.venv\Scripts\dbt run --profiles-dir .

# ทดสอบคุณภาพและความถูกต้องของข้อมูล (Data Tests)
..\.venv\Scripts\dbt test --profiles-dir .

# จัดทำเอกสารและแผนผังความสัมพันธ์ (Interactive Lineage Graph)
..\.venv\Scripts\dbt docs generate --profiles-dir .
```
*ระบบจะสร้างตารางประมวลผลปลายทาง (Marts Layer) ภายใต้ Dataset ชื่อ `dbt_dev` บน BigQuery โดยมีตารางมิติและข้อเท็จจริง ได้แก่ `dim_users`, `dim_products`, `fct_order_items` และตารางสรุปผลประสิทธิภาพสูง `fct_daily_sales`*

---

## 🔒 ความปลอดภัยของข้อมูลลับ (Security note)
ไฟล์และโฟลเดอร์ดังต่อไปนี้จะ**ไม่ถูกอัปโหลด**ขึ้นสู่ GitHub เพื่อป้องกันปัญหาระบบความปลอดภัยตามมาตรฐาน `.gitignore` ที่ตั้งไว้:
- โฟลเดอร์ `.venv/`
- ไฟล์สกุล `.json` ทั้งหมด (รวมถึง GCP keys)
- ไฟล์ `.env`
- โฟลเดอร์ `data/` และไฟล์ `.csv` ขนาดใหญ่

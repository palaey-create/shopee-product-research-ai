# Shopee Product Research AI Auto (เริ่มต้นฟรี)

ระบบสร้างรายงาน HTML จัดอันดับสินค้า Shopee + สัญญาณ TikTok และเผยแพร่เป็นเว็บไซต์ที่เปิดได้ทั้ง Windows/iPad โดยใช้ GitHub Actions ตามเวลาไทย 07:00 น.

## ข้อเท็จจริงสำคัญ
- ไม่สร้างยอดขาย/วิว/คอมมิชชันปลอม ช่องที่ไม่มีข้อมูลจะเว้นว่าง
- ระบบไม่ scrape Shopee/TikTok และไม่ bypass login/anti-bot. ต้องนำเข้าข้อมูลจากรายงานที่บัญชีคุณดาวน์โหลดได้ หรือแหล่งข้อมูล/API ที่ได้รับอนุญาต
- การตั้งเวลาไม่ได้ทำให้ Shopee/TikTok ส่งข้อมูลสดให้เอง รายงานเปลี่ยนเมื่อมีข้อมูลใหม่ใน data/
- TikTok Creative Center แสดงเทรนด์/แฮชแท็ก/ตัวอย่างโฆษณา ไม่ได้เปิดยอดขาย Affiliate ของทุกคลิป
- ค่าคอมมิชชันให้กรอกจากรายงาน/หน้าบัญชี Affiliate ที่เชื่อถือได้เท่านั้น

## ติดตั้ง
1. สร้าง repository ใหม่ที่ https://github.com/new ชื่อ `shopee-product-research-ai` เลือก Public เพื่อใช้ GitHub Pages ฟรีได้ง่าย ห้ามใส่ข้อมูลส่วนตัว/รหัสผ่าน/รายงานลับใน repo สาธารณะ
2. แตก ZIP นี้ แล้วอัปโหลดไฟล์ทั้งหมดไปยัง repository โดยคงโครงสร้างโฟลเดอร์
3. Settings → Pages → Build and deployment → Source เลือก `GitHub Actions`
4. Actions → เปิดใช้งาน workflows หากมีปุ่ม Enable workflows
5. Actions → `Daily Product Research` → Run workflow เพื่อทดสอบ
6. หลังสำเร็จ เปิด Settings → Pages เพื่อดู URL รายงาน ใช้ URL เดียวกันได้ทั้ง Windows/iPad
7. ระบบตั้งเวลา `07:00 Asia/Bangkok` ไว้แล้ว อาจมีความล่าช้าเล็กน้อย

## นำเข้าข้อมูล
### Shopee
- เข้า https://affiliate.shopee.co.th/ และดาวน์โหลดรายงาน CSV/XLSX หากบัญชีมีตัวเลือก
- ถ้าเป็น XLSX ให้บันทึกเป็น CSV UTF-8 และจัดคอลัมน์ให้ตรงกับ `data/products.csv`:
`product_name,product_url,category,price_thb,displayed_sales,rating,review_count,commission_rate_pct,commission_source,source_checked_at,video_ease_1_to_5,competition_1_to_5,trust_1_to_5,notes`
- ใส่เฉพาะยอดขายที่แสดง/รายงานจริง พร้อมแหล่งข้อมูลและวันที่ตรวจ
### TikTok
- ตรวจเทรนด์ใน https://ads.tiktok.com/business/creativecenter/ หรือ TikTok Shop Creator Center / Inspiration Center ที่บัญชีเข้าถึงได้
- เพิ่มแถวใน `data/tiktok_trends.csv`:
`keyword,trend_score_1_to_5,views,posts,source_url,checked_at,notes`
- คะแนนเทรนด์ 1–5 เป็นการประเมินจากหลักฐานที่คุณดูได้ ไม่ใช่ API อัตโนมัติ
### ลิงก์ที่ต้องการตรวจ
เพิ่มลง `data/links_to_review.csv`. ถ้ามีเพียง URL ระบบจะเก็บลิงก์ไว้ แต่จะไม่สร้างราคา/ยอดขายที่เข้าถึงไม่ได้

## คะแนน 0–100
เป็น heuristic จากข้อมูลจริงเท่าที่มี ไม่ใช่การทำนายยอดขาย. ข้อมูลน้อยกว่า 4 ปัจจัยจะแสดง `ข้อมูลไม่ครบ`. 75–100 ทดลองทำคลิป, 55–74 เก็บข้อมูลเพิ่ม, ต่ำกว่า 55 พักไว้ก่อน.
## ข้อจำกัด
รุ่นนี้สร้างรายงานอัตโนมัติทุกวัน แต่ยังไม่ค้นหาสินค้าทั่ว Shopee/TikTok สดด้วยตัวเอง เพราะต้องมี API/แหล่งข้อมูลที่ได้รับอนุญาตก่อน. GitHub Pages เป็นรายงานอ่านอย่างเดียว. หากได้ API ที่อนุญาตแล้ว ค่อยเพิ่ม adapter และเก็บ credentials ใน GitHub Actions Secrets.

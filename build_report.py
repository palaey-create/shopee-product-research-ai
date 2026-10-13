import csv, html, os, json
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs")
os.makedirs(OUT, exist_ok=True)
now = datetime.now(ZoneInfo("Asia/Bangkok"))

def read_csv(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def val(row, key):
    s = (row.get(key) or "").strip()
    if not s: return None
    try: return float(s.replace(",", "").replace("%", ""))
    except ValueError: return None

def esc(x): return html.escape(str(x or ""))
products, trends, links = read_csv("products.csv"), read_csv("tiktok_trends.csv"), read_csv("links_to_review.csv")
commission_rows = read_csv("commission_rates.csv")
commission_map = {}

for cr in commission_rows:
    u = (cr.get("product_url") or "").strip()
    n = (cr.get("product_name") or "").strip().casefold()
    rate = val(cr, "commission_rate_pct")

    if rate is not None:
        if u:
            commission_map["url:" + u] = cr
        if n:
            commission_map["name:" + n] = cr
trend_map = {}
for t in trends:
    key=(t.get("keyword") or "").strip().lower()
    if key and val(t,"trend_score_1_to_5") is not None: trend_map[key]=t

ranked=[]
for p in products:
    name=(p.get("product_name") or "").strip()
    url=(p.get("product_url") or "").strip()
    if not name and not url: continue
    name=name or "สินค้า (ยังไม่มีชื่อ)"
    category=(p.get("category") or "").strip()
    sales,rating,reviews=val(p,"displayed_sales"),val(p,"rating"),val(p,"review_count")
    commission_row = (
    commission_map.get("url:" + url)
    or commission_map.get("name:" + name.casefold())
)

commission = val(p, "commission_rate_pct")

if commission is None and commission_row:
    commission = val(commission_row, "commission_rate_pct")

price = val(p, "price_thb")
ease,competition,trust=val(p,"video_ease_1_to_5"),val(p,"competition_1_to_5"),val(p,"trust_1_to_5")
matched=next((t for k,t in trend_map.items() if k in name.lower() or (category and k in category.lower())),None)
trend_score=val(matched or {},"trend_score_1_to_5") if matched else None
    parts=[]
    if sales is not None: parts.append((min(5,max(0,sales/400))/5*15,15))
    if rating is not None: parts.append((min(5,max(0,rating))/5*10,10))
    if commission is not None: parts.append((min(5,max(0,commission/2))/5*20,20))
    if trend_score is not None: parts.append((min(5,max(0,trend_score))/5*25,25))
    if ease is not None: parts.append((min(5,max(0,ease))/5*15,15))
    if competition is not None: parts.append(((6-min(5,max(1,competition)))/5*10,10))
    if trust is not None: parts.append((min(5,max(0,trust))/5*5,5))
    weight=sum(w for _,w in parts)
    score=round(sum(v for v,_ in parts)/weight*100) if weight else None
    comm_baht=round(price*commission/100,2) if price is not None and commission is not None else None
    if score is None: rec="ข้อมูลไม่พอจัดอันดับ"
    elif len(parts)<4: rec="ข้อมูลไม่ครบ — ตรวจเพิ่ม"
    elif score>=75: rec="ควรพิจารณาทดลองทำคลิป"
    elif score>=55: rec="เก็บข้อมูลเพิ่ม"
    else: rec="พักไว้ก่อน"
    ranked.append(dict(name=name,url=url,category=category,price=price,sales=sales,rating=rating,reviews=reviews,
        commission=commission,comm_baht=comm_baht,trend=trend_score,score=score,rec=rec,known=len(parts),
        checked=p.get("source_checked_at",""),notes=p.get("notes","")))
ranked.sort(key=lambda x:(x["score"] is not None,x["score"] or -1,x["known"]),reverse=True)
ranked=ranked[:100]
def fmt(x,suffix=""): return "ไม่มีข้อมูล" if x is None else esc(x)+suffix
rows=[]
for i,p in enumerate(ranked,1):
    link=f'<a href="{esc(p["url"])}" target="_blank" rel="noopener">เปิดสินค้า</a>' if p["url"].startswith(("https://","http://")) else "ไม่มีลิงก์"
    rows.append(f'<tr><td>{i}</td><td>{esc(p["name"])}</td><td>{esc(p["category"])}</td><td>{fmt(p["price"]," บาท")}</td><td>{fmt(p["sales"])}</td><td>{fmt(p["rating"])}</td><td>{fmt(p["reviews"])}</td><td>{fmt(p["commission"],"%")}</td><td>{fmt(p["comm_baht"]," บาท")}</td><td>{fmt(p["trend"],"/5")}</td><td><b>{fmt(p["score"],"/100")}</b><small>{p["known"]}/7 ปัจจัยมีข้อมูล</small></td><td>{esc(p["rec"])}</td><td>{link}</td></tr>')
trend_rows=[]
for t in trends:
    u=(t.get("source_url") or "").strip()
    l=f'<a href="{esc(u)}" target="_blank" rel="noopener">เปิดแหล่งข้อมูล</a>' if u.startswith(("https://","http://")) else "ไม่มีลิงก์"
    trend_rows.append(f'<tr><td>{esc(t.get("keyword"))}</td><td>{fmt(val(t,"trend_score_1_to_5"),"/5")}</td><td>{fmt(val(t,"views"))}</td><td>{fmt(val(t,"posts"))}</td><td>{l}</td><td>{esc(t.get("checked_at"))}</td></tr>')
link_rows=[]
for r in links:
    u=(r.get("url") or "").strip()
    l=f'<a href="{esc(u)}" target="_blank" rel="noopener">{esc(u)}</a>' if u.startswith(("http://","https://")) else esc(u)
    link_rows.append(f'<tr><td>{l}</td><td>{esc(r.get("source"))}</td><td>{esc(r.get("added_at"))}</td><td>{esc(r.get("notes"))}</td></tr>')
def table(head,body,empty):
    return '<p class="empty">'+empty+'</p>' if not body else '<div class="scroll"><table><thead><tr>'+''.join('<th>'+h+'</th>' for h in head)+'</tr></thead><tbody>'+''.join(body)+'</tbody></table></div>'
page=f"""<!doctype html><html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#e94f37"><title>Shopee Product Research AI</title>
<style>
:root{{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;color:#222;background:#f5f6f8}}body{{margin:0}}header{{background:#e94f37;color:#fff;padding:22px max(16px,calc((100vw - 1250px)/2))}}main{{max-width:1250px;margin:22px auto;padding:0 14px}}h1{{font-size:clamp(23px,4vw,34px);margin:0 0 5px}}h2{{margin-top:28px}}.cards{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:16px 0}}.card{{background:#fff;padding:16px;border-radius:13px;box-shadow:0 2px 10px #0000000a}}.big{{font-size:26px;font-weight:750}}.notice{{background:#fff6dc;border:1px solid #f0d98d;border-radius:10px;padding:13px;line-height:1.55}}.scroll{{overflow:auto;background:#fff;border-radius:12px;margin-top:12px}}table{{border-collapse:collapse;width:100%;min-width:1000px;font-size:14px}}th,td{{padding:10px;border-bottom:1px solid #e9e9e9;text-align:left;vertical-align:top}}th{{background:#272727;color:white}}td small{{display:block;color:#777}}a{{color:#d64024}}.empty{{background:#fff;padding:18px;border-radius:10px;color:#555}}input{{padding:10px;border:1px solid #ccc;border-radius:8px;width:min(100%,360px);font:inherit}}footer{{color:#666;font-size:13px;margin:28px 0}}@media(max-width:650px){{.cards{{grid-template-columns:1fr}}header{{padding:18px}}}}
</style></head><body><header><h1>🛍️ Shopee Product Research AI</h1><div>รายงานจัดอันดับสินค้า · Shopee + TikTok · เวลาไทย {now.strftime("%d/%m/%Y %H:%M")}</div></header><main>
<div class="notice"><b>ความซื่อสัตย์ของข้อมูล:</b> ใช้เฉพาะข้อมูลที่ใส่ใน CSV ไม่มีการสร้างยอดขาย วิว หรือค่าคอมมิชชัน ช่องที่ไม่มีข้อมูลจะแสดง “ไม่มีข้อมูล” คะแนนเป็นตัวช่วยคัดกรอง ไม่ใช่การรับประกันยอดขาย</div>
<div class="cards"><div class="card">สินค้าที่มีในรายงาน<div class="big">{len(ranked)}</div></div><div class="card">สินค้าที่มีคะแนน<div class="big">{sum(1 for p in ranked if p["score"] is not None)}</div></div><div class="card">ลิงก์รอตรวจสอบ<div class="big">{len(links)}</div></div></div>
<h2>อันดับสินค้า (สูงสุด 100 รายการ)</h2><input id="filter" placeholder="ค้นหาชื่อสินค้า/หมวดหมู่..." oninput="filterRows()">
{table(["อันดับ","สินค้า","หมวดหมู่","ราคา","ยอดขายที่แสดง","คะแนนรีวิว","จำนวนรีวิว","คอมมิชชัน","คอมฯ โดยประมาณ/ออเดอร์","TikTok Trend","คะแนนโอกาส","คำแนะนำ","ลิงก์"],rows,"ยังไม่มีข้อมูลสินค้า ให้เพิ่มข้อมูลจริงใน data/products.csv แล้วรัน workflow")}
<h2>สัญญาณ TikTok ที่บันทึกไว้</h2>{table(["คำค้น/เทรนด์","คะแนนเทรนด์","วิว","โพสต์","แหล่งข้อมูล","วันที่ตรวจ"],trend_rows,"ยังไม่มีข้อมูลเทรนด์ ให้บันทึกข้อมูลจริงใน data/tiktok_trends.csv")}
<h2>ลิงก์ที่รอตรวจสอบ</h2>{table(["ลิงก์","แหล่งที่มา","วันที่เพิ่ม","หมายเหตุ"],link_rows,"ยังไม่มีลิงก์รอตรวจสอบ")}
<h2>วิธีคิดคะแนน</h2><p>ยอดขายที่มีหลักฐาน 15%, รีวิว 10%, คอมมิชชัน 20%, TikTok trend 25%, ความง่ายในการทำคลิป 15%, คู่แข่ง 10%, ความน่าเชื่อถือ 5%. ระบบปรับน้ำหนักตามข้อมูลที่มี และแสดงจำนวนปัจจัยที่ใช้จริง</p><p>ค่าคอมฯ โดยประมาณ = ราคา × อัตราคอมมิชชัน ÷ 100 ไม่ใช่ยอดจ่ายจริง</p>
<footer>สร้างเมื่อ {now.isoformat(timespec="minutes")} · <a href="https://ads.tiktok.com/business/creativecenter/" target="_blank">TikTok Creative Center</a> · <a href="https://affiliate.shopee.co.th/" target="_blank">Shopee Affiliate Portal</a></footer></main>
<script>function filterRows(){{let q=document.getElementById('filter').value.toLowerCase();document.querySelectorAll('table tbody tr').forEach(r=>r.style.display=r.innerText.toLowerCase().includes(q)?'':'none')}}</script></body></html>"""
with open(os.path.join(OUT,"index.html"),"w",encoding="utf-8") as f: f.write(page)
with open(os.path.join(OUT,"report.json"),"w",encoding="utf-8") as f: json.dump({"generated_at":now.isoformat(),"products":ranked,"trends":trends,"links_to_review":links},f,ensure_ascii=False,indent=2)
print(f"Generated report with {len(ranked)} products, {len(trends)} trends, {len(links)} links. No missing values fabricated.")

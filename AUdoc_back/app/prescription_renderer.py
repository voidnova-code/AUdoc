from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap

C_BG        = (255, 255, 255)
C_HEADER_BG = (29, 92, 53)
C_HEADER_FG = (255, 255, 255)
C_ACCENT    = (29, 92, 53)
C_BORDER    = (220, 232, 224)
C_TEXT_MAIN = (30,  40,  35)
C_TEXT_MUT  = (100, 120, 110)
C_RX_BG     = (240, 248, 243)
C_MED_BADGE = (212, 237, 218)
C_MED_TEXT  = (21,  87,  50)
C_FOOTER_BG = (245, 250, 247)
C_LINE      = (200, 220, 210)
W, PAD = 860, 44

_FONTS: dict = {}


def _load_font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def _f(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    key = (size, bold)
    if key not in _FONTS:
        _FONTS[key] = _load_font(size, bold)
    return _FONTS[key]


def render_prescription(record) -> bytes:
    """
    Generate a prescription PNG for the given MedicalHistory record.
    Returns raw PNG bytes (no disk I/O).
    Speed opts: module-level font cache, compress_level=1.
    """
    meds = list(record.prescribedmedicine_set.select_related("medicine").all())
    med_block_h = max(len(meds), 1) * 84 + 20
    H = 330 + med_block_h + 160

    img  = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    y = 0

    # ── Header ────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 88], fill=C_HEADER_BG)
    draw.text((PAD, 16), "AUdoc", font=_f(32, True), fill=C_HEADER_FG)
    draw.text((PAD, 54), "Assam University Silchar  \u2022  Student Health Center",
              font=_f(13), fill=(180, 220, 200))
    issue_date = record.appointment_date or record.created_at.date()
    rx_no  = f"RX-{issue_date.year}-{record.id:04d}"
    date_s = issue_date.strftime("Issued %d %b %Y")
    draw.text((W - PAD, 22), rx_no,  font=_f(12), fill=(180, 220, 200), anchor="rt")
    draw.text((W - PAD, 40), date_s, font=_f(12), fill=(180, 220, 200), anchor="rt")
    y = 88
    draw.rectangle([0, y, W, y + 3], fill=(45, 130, 80))
    y += 26

    # ── Patient / Doctor row ──────────────────────────────────────────────
    col_r = W // 2 + 10
    draw.text((PAD,   y), "PATIENT",          font=_f(10), fill=C_TEXT_MUT)
    draw.text((col_r, y), "ATTENDING DOCTOR", font=_f(10), fill=C_TEXT_MUT)
    y += 18
    draw.text((PAD,   y), str(record.student_id or "N/A"),   font=_f(20, True), fill=C_TEXT_MAIN)
    draw.text((col_r, y), str(record.doctor_name or "N/A"),  font=_f(20, True), fill=C_TEXT_MAIN)
    y += 28
    draw.text((PAD,   y), "Assam University Student", font=_f(12), fill=C_TEXT_MUT)
    draw.text((col_r, y), "AUdoc Health Center",      font=_f(12), fill=C_TEXT_MUT)
    y += 38
    draw.rectangle([PAD, y, W - PAD, y + 1], fill=C_BORDER)
    y += 22

    # ── Diagnosis ─────────────────────────────────────────────────────────
    draw.text((PAD, y), "DIAGNOSIS", font=_f(10), fill=C_TEXT_MUT)
    y += 18
    draw.text((PAD, y), str(record.illness), font=_f(18, True), fill=C_ACCENT)
    y += 28
    for line in textwrap.wrap(str(record.symptoms or ""), width=95)[:3]:
        draw.text((PAD, y), line, font=_f(13), fill=C_TEXT_MUT)
        y += 18
    y += 14
    draw.rectangle([PAD, y, W - PAD, y + 1], fill=C_BORDER)
    y += 22

    # ── Medicines ─────────────────────────────────────────────────────────
    draw.text((PAD, y), "Rx  MEDICINES PRESCRIBED", font=_f(11, True), fill=C_TEXT_MUT)
    y += 24
    food_map = {"BEFORE": "Before Food", "AFTER": "After Food",
                "WITH": "With Food", "ANYTIME": "Anytime"}
    if meds:
        for idx, pm in enumerate(meds, 1):
            med_name = pm.medicine.name if pm.medicine else "Unknown"
            dosage   = pm.dosage or ""
            food     = food_map.get(pm.food_timing, pm.food_timing)
            times    = [t for t, flag in [
                ("Morning",   pm.take_morning),
                ("Afternoon", pm.take_afternoon),
                ("Evening",   pm.take_evening),
                ("Night",     pm.take_night),
            ] if flag]
            times_str = ", ".join(times) if times else "As directed"
            c1, c2 = y, y + 70
            draw.rounded_rectangle([PAD, c1, W - PAD, c2],
                                   radius=8, fill=C_RX_BG, outline=C_BORDER)
            bx, by = PAD + 18, (c1 + c2) // 2
            draw.ellipse([bx - 14, by - 14, bx + 14, by + 14], fill=C_ACCENT)
            draw.text((bx, by), str(idx), font=_f(12, True), fill=C_HEADER_FG, anchor="mm")
            tx = bx + 30
            draw.text((tx, c1 + 12), med_name, font=_f(16, True), fill=C_TEXT_MAIN)
            bx2, badge_y = tx, c1 + 38
            for lbl in filter(None, [dosage, times_str, food,
                                     f"{pm.duration_days} days",
                                     f"Qty: {pm.quantity}"]):
                tw = int(draw.textlength(lbl, font=_f(11))) + 16
                draw.rounded_rectangle([bx2, badge_y, bx2 + tw, badge_y + 20],
                                       radius=6, fill=C_MED_BADGE)
                draw.text((bx2 + 8, badge_y + 2), lbl, font=_f(11), fill=C_MED_TEXT)
                bx2 += tw + 8
            y = c2 + 10
    else:
        draw.text((PAD, y), "No medicines prescribed.", font=_f(13), fill=C_TEXT_MUT)
        y += 24
    y += 18
    draw.rectangle([PAD, y, W - PAD, y + 1], fill=C_BORDER)
    y += 20

    # ── General advice ────────────────────────────────────────────────────
    advice = (
        "General advice: Complete the full course as prescribed. "
        "Stay hydrated and rest. Contact the health center if "
        "symptoms worsen or persist beyond 3 days."
    )
    for line in textwrap.wrap(advice, width=105):
        draw.text((PAD, y), line, font=_f(12), fill=C_TEXT_MUT)
        y += 18
    y += 24

    # ── Signature ─────────────────────────────────────────────────────────
    doc_name = str(record.doctor_name or "Attending Doctor")
    draw.text((W - PAD, y), doc_name, font=_f(15, True),
              fill=C_TEXT_MAIN, anchor="rt")
    y += 22
    draw.text((W - PAD, y), "General Physician  \u2022  AUdoc Health Center",
              font=_f(11), fill=C_TEXT_MUT, anchor="rt")
    draw.line([W - PAD - 220, y + 20, W - PAD, y + 20], fill=C_LINE, width=1)
    y += 40

    # ── Footer ────────────────────────────────────────────────────────────
    draw.rectangle([0, y, W, H], fill=C_FOOTER_BG)
    draw.rectangle([0, y, W, y + 1], fill=C_BORDER)
    draw.text((PAD, y + 14), f"Scan/verify at https://audoc.me/rx/{rx_no}",
              font=_f(10), fill=C_TEXT_MUT)
    draw.text((PAD, y + 30),
              "Digitally generated by AUdoc \u2014 valid without a physical signature. "
              "Please retain for your records.",
              font=_f(10), fill=(160, 180, 170))

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=False, compress_level=1)
    buf.seek(0)
    return buf.read()

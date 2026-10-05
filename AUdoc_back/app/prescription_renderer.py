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

# ── Compact canvas (fits a typical doctor portal panel without scrolling) ──
W, PAD = 620, 28

_FONTS: dict = {}


def _load_font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/arialbd.ttf"  if bold else "C:/Windows/Fonts/arial.ttf",
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
    Generate a compact prescription PNG for the given MedicalHistory record.
    Designed to fit a doctor portal preview panel without scrolling.
    Returns raw PNG bytes (no disk I/O). compress_level=1 for speed.
    """
    meds = list(record.prescribedmedicine_set.select_related("medicine").all())
    # Each medicine card is 50 px tall; header+info+diag = ~230, footer = ~110
    med_block_h = max(len(meds), 1) * 56 + 14
    referred_block_h = 40 if getattr(record, 'is_referred', False) and getattr(record, 'referred_to', '') else 0
    H = 230 + med_block_h + 110 + referred_block_h

    img  = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    y = 0

    # ── Header ────────────────────────────────────────────────────────────
    draw.rectangle([0, 0, W, 60], fill=C_HEADER_BG)
    draw.text((PAD, 10), "AUdoc", font=_f(22, True), fill=C_HEADER_FG)
    draw.text((PAD, 36), "Assam University Silchar  \u2022  Student Health Center",
              font=_f(9), fill=(180, 220, 200))
    issue_date = record.appointment_date or record.created_at.date()
    rx_no  = f"RX-{issue_date.year}-{record.id:04d}"
    date_s = issue_date.strftime("Issued %d %b %Y")
    draw.text((W - PAD, 14), rx_no,  font=_f(9), fill=(180, 220, 200), anchor="rt")
    draw.text((W - PAD, 28), date_s, font=_f(9), fill=(180, 220, 200), anchor="rt")
    y = 60
    draw.rectangle([0, y, W, y + 2], fill=(45, 130, 80))
    y += 14

    # ── Patient / Doctor row ──────────────────────────────────────────────
    col_r = W // 2 + 8
    draw.text((PAD,   y), "PATIENT",          font=_f(7), fill=C_TEXT_MUT)
    draw.text((col_r, y), "ATTENDING DOCTOR", font=_f(7), fill=C_TEXT_MUT)
    y += 12
    draw.text((PAD,   y), str(record.student_id or "N/A"),  font=_f(14, True), fill=C_TEXT_MAIN)
    # Use attending_doctor FK name if available, otherwise fall back to doctor_name string
    attending_name = (
        record.attending_doctor.name
        if getattr(record, 'attending_doctor_id', None) and record.attending_doctor
        else str(record.doctor_name or "N/A")
    )
    draw.text((col_r, y), attending_name, font=_f(14, True), fill=C_TEXT_MAIN)
    y += 18
    draw.text((PAD,   y), "Assam University Student", font=_f(8), fill=C_TEXT_MUT)
    draw.text((col_r, y), "AUdoc Health Center",      font=_f(8), fill=C_TEXT_MUT)
    y += 22
    draw.rectangle([PAD, y, W - PAD, y + 1], fill=C_BORDER)
    y += 12

    # ── Diagnosis ─────────────────────────────────────────────────────────
    draw.text((PAD, y), "DIAGNOSIS", font=_f(7), fill=C_TEXT_MUT)
    y += 12
    draw.text((PAD, y), str(record.illness), font=_f(13, True), fill=C_ACCENT)
    y += 18
    for line in textwrap.wrap(str(record.symptoms or ""), width=80)[:2]:
        draw.text((PAD, y), line, font=_f(9), fill=C_TEXT_MUT)
        y += 13
    y += 8
    draw.rectangle([PAD, y, W - PAD, y + 1], fill=C_BORDER)
    y += 12

    # ── Medicines ─────────────────────────────────────────────────────────
    draw.text((PAD, y), "Rx  MEDICINES PRESCRIBED", font=_f(8, True), fill=C_TEXT_MUT)
    y += 14
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
            c1, c2 = y, y + 50
            draw.rounded_rectangle([PAD, c1, W - PAD, c2],
                                   radius=6, fill=C_RX_BG, outline=C_BORDER)
            bx, by = PAD + 13, (c1 + c2) // 2
            draw.ellipse([bx - 10, by - 10, bx + 10, by + 10], fill=C_ACCENT)
            draw.text((bx, by), str(idx), font=_f(9, True), fill=C_HEADER_FG, anchor="mm")
            tx = bx + 22
            draw.text((tx, c1 + 8), med_name, font=_f(11, True), fill=C_TEXT_MAIN)
            bx2, badge_y = tx, c1 + 28
            for lbl in filter(None, [dosage, times_str, food,
                                     f"{pm.duration_days} days",
                                     f"Qty: {pm.quantity}"]):
                tw = int(draw.textlength(lbl, font=_f(8))) + 12
                draw.rounded_rectangle([bx2, badge_y, bx2 + tw, badge_y + 15],
                                       radius=4, fill=C_MED_BADGE)
                draw.text((bx2 + 6, badge_y + 2), lbl, font=_f(8), fill=C_MED_TEXT)
                bx2 += tw + 6
            y = c2 + 7
    else:
        draw.text((PAD, y), "No medicines prescribed.", font=_f(9), fill=C_TEXT_MUT)
        y += 16
    y += 10
    draw.rectangle([PAD, y, W - PAD, y + 1], fill=C_BORDER)
    y += 10

    # ── General advice ────────────────────────────────────────────────────
    advice = (
        "General advice: Complete the full course as prescribed. "
        "Stay hydrated and rest. Contact the health center if "
        "symptoms worsen or persist beyond 3 days."
    )
    for line in textwrap.wrap(advice, width=90)[:2]:
        draw.text((PAD, y), line, font=_f(8), fill=C_TEXT_MUT)
        y += 12
    y += 10

    # ── Signature ─────────────────────────────────────────────────────────
    doc_name = attending_name
    draw.text((W - PAD, y), doc_name, font=_f(11, True),
              fill=C_TEXT_MAIN, anchor="rt")
    y += 14
    draw.text((W - PAD, y), "General Physician  \u2022  AUdoc Health Center",
              font=_f(8), fill=C_TEXT_MUT, anchor="rt")
    draw.line([W - PAD - 160, y + 14, W - PAD, y + 14], fill=C_LINE, width=1)
    y += 26

    # ── Referral note (if referred) ───────────────────────────────────────
    if getattr(record, 'is_referred', False) and getattr(record, 'referred_to', ''):
        C_REF_BG  = (255, 243, 205)
        C_REF_BDR = (255, 193,  7)
        C_REF_TXT = (133,  77,  14)
        draw.rounded_rectangle([PAD, y, W - PAD, y + 34], radius=6,
                               fill=C_REF_BG, outline=C_REF_BDR)
        draw.text((PAD + 10, y + 6),  "REFERRED TO:",
                  font=_f(8, True), fill=C_REF_TXT)
        ref_text = str(record.referred_to)[:80]
        draw.text((PAD + 10, y + 18), ref_text, font=_f(9), fill=C_REF_TXT)
        y += 42

    # ── Footer ────────────────────────────────────────────────────────────
    draw.rectangle([0, y, W, H], fill=C_FOOTER_BG)
    draw.rectangle([0, y, W, y + 1], fill=C_BORDER)
    draw.text((PAD, y + 8),  f"Scan/verify at https://audoc.me/rx/{rx_no}",
              font=_f(7), fill=C_TEXT_MUT)
    draw.text((PAD, y + 20),
              "Digitally generated by AUdoc \u2014 valid without a physical signature.",
              font=_f(7), fill=(160, 180, 170))

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=False, compress_level=1)
    buf.seek(0)
    return buf.read()

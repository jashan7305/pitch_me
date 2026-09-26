from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.util import Inches, Pt

from models.pitch import PitchContent, PitchSlide


# ---------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------

NAVY = RGBColor(20, 32, 48)
BLUE = RGBColor(35, 92, 160)
LIGHT_BLUE = RGBColor(232, 241, 250)
WHITE = RGBColor(255, 255, 255)
LIGHT_GREY = RGBColor(245, 247, 249)
MID_GREY = RGBColor(105, 115, 125)
DARK_GREY = RGBColor(45, 52, 60)
BORDER = RGBColor(220, 225, 230)
GREEN = RGBColor(35, 125, 85)

# Colors used specifically on navy backgrounds — named once so every dark
# slide draws from the same palette instead of repeating raw RGB literals.
CARD_NAVY = RGBColor(30, 46, 65)
ACCENT_ON_DARK = RGBColor(120, 180, 235)    # "MARSH" wordmark on navy
EYEBROW_ON_DARK = RGBColor(150, 185, 215)    # small eyebrow labels on navy
MUTED_ON_DARK = RGBColor(190, 205, 220)       # body/description text on navy
FOOTER_ON_DARK = RGBColor(150, 170, 190)      # footer strip on navy

FONT = "Aptos"

# ---------------------------------------------------------------------
# Layout tokens — every slide type reads from the same numbers, so
# margins, type scale and spacing stay identical across the whole deck.
# ---------------------------------------------------------------------

SLIDE_WIDTH_IN = 13.333
SLIDE_HEIGHT_IN = 7.5

MARGIN = 0.65
CONTENT_WIDTH = SLIDE_WIDTH_IN - (2 * MARGIN)  # 12.033"
CARD_PAD = 0.3                                   # inner padding shared by every card

KICKER_SIZE = 11    # small "MARSH" wordmark, every slide
TITLE_SIZE = 30       # main slide title, every slide
SUBTITLE_SIZE = 15   # descriptive line under a title, every slide
FOOTER_SIZE = 9        # footer strip, every slide


# ---------------------------------------------------------------------
# Text fitting
# ---------------------------------------------------------------------
#
# python-pptx has no real text-measurement API — it doesn't know how many
# lines a string will wrap to in a given box. Left unhandled, that's what
# caused the overflow bug: font size was previously chosen from bullet
# *count* alone, so 4 long bullets (which wrap to 2-3 lines each) overflowed
# just as easily as 5 short ones did.
#
# This estimates wrapped line count from character count and picks the
# largest font size (from a supplied ladder, largest first) whose estimated
# total height fits the box. It's an approximation, calibrated loosely for
# Aptos/Calibri-style proportional fonts — not a substitute for keeping
# generated text reasonably concise, but it means the font actually
# responds to how much text there is, not just how many bullets.

_CHARS_PER_INCH_AT_10PT = 15.5  # empirical average glyph density for this font at 10pt


def fit_font_size(
    texts: list[str],
    box_width_in: float,
    box_height_in: float,
    sizes: list[int],
    *,
    space_after_pt: float = 12,
) -> int:
    """Largest size in `sizes` (descending) whose estimated wrapped height fits the box."""
    for size in sizes:
        chars_per_line = max(1, int(_CHARS_PER_INCH_AT_10PT * (10 / size) * box_width_in))
        total_lines = sum(max(1, -(-len(t) // chars_per_line)) for t in texts)  # ceil division
        line_height_in = (size * 1.25) / 72
        spacing_in = (space_after_pt / 72) * len(texts)
        if (total_lines * line_height_in + spacing_in) <= box_height_in:
            return size
    return sizes[-1]  # smallest size as a floor, even if still tight


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def add_text(
    slide,
    text: str,
    left: float,
    top: float,
    width: float,
    height: float,
    *,
    font_size: int = 20,
    bold: bool = False,
    color=DARK_GREY,
    alignment=PP_ALIGN.LEFT,
    font_name: str = FONT,
):
    box = slide.shapes.add_textbox(
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )

    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.vertical_anchor = MSO_ANCHOR.TOP
    frame.auto_size = MSO_AUTO_SIZE.NONE  # we size text ourselves; don't let the app re-guess

    paragraph = frame.paragraphs[0]
    paragraph.alignment = alignment

    run = paragraph.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color

    return box


def add_bullets(
    slide,
    points: list[str],
    left: float,
    top: float,
    width: float,
    height: float,
    *,
    font_size: int = 20,
    color=DARK_GREY,
):
    box = slide.shapes.add_textbox(
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )

    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.NONE
    frame.margin_left = Inches(0.05)
    frame.margin_right = Inches(0.05)
    frame.margin_top = Inches(0.02)
    frame.margin_bottom = Inches(0.02)

    for i, point in enumerate(points):
        paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()

        paragraph.text = f"•  {point}"
        paragraph.font.name = FONT
        paragraph.font.size = Pt(font_size)
        paragraph.font.color.rgb = color
        paragraph.level = 0
        paragraph.space_after = Pt(12)

    return box


def add_card(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    *,
    fill=WHITE,
    corner_radius: float = 0.06,
):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left),
        Inches(top),
        Inches(width),
        Inches(height),
    )

    shape.fill.solid()
    shape.fill.fore_color.rgb = fill

    shape.line.color.rgb = BORDER
    shape.line.width = Pt(0.75)

    shape.shadow.inherit = False
    shape.adjustments[0] = corner_radius

    return shape


def add_header(
    slide,
    title: str,
    subtitle: str | None = None,
):
    add_text(
        slide,
        "MARSH",
        MARGIN,
        0.38,
        1.2,
        0.3,
        font_size=KICKER_SIZE,
        bold=True,
        color=BLUE,
    )

    add_text(
        slide,
        title,
        MARGIN,
        0.78,
        CONTENT_WIDTH,
        0.65,
        font_size=TITLE_SIZE,
        bold=True,
        color=NAVY,
    )

    if subtitle:
        add_text(
            slide,
            subtitle,
            MARGIN,
            1.42,
            CONTENT_WIDTH,
            0.45,
            font_size=SUBTITLE_SIZE,
            color=MID_GREY,
        )

    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(MARGIN),
        Inches(1.95),
        Inches(1.0),
        Inches(0.055),
    )

    line.fill.solid()
    line.fill.fore_color.rgb = BLUE
    line.line.fill.background()
    line.shadow.inherit = False


def add_footer(slide, slide_number: int, *, dark: bool = False):
    add_text(
        slide,
        f"MARSH  |  CLIENT ADVISORY  |  {slide_number}",
        MARGIN,
        7.05,
        CONTENT_WIDTH,
        0.25,
        font_size=FOOTER_SIZE,
        color=FOOTER_ON_DARK if dark else MID_GREY,
    )


def add_claim_cards(
    slide,
    claims,
    left: float,
    top: float,
    width: float,
    height: float,
):
    """Render claims as readable cards rather than one giant paragraph."""

    if not claims:
        return

    count = min(len(claims), 4)
    card_width = (width - (count - 1) * 0.15) / count

    for i, claim in enumerate(claims[:count]):
        x = left + i * (card_width + 0.15)

        add_card(slide, x, top, card_width, height, fill=LIGHT_GREY)

        add_text(
            slide,
            claim.claim_type.replace("_", " ").title(),
            x + CARD_PAD,
            top + 0.15,
            card_width - (2 * CARD_PAD),
            0.3,
            font_size=10,
            bold=True,
            color=BLUE,
        )

        body_height = height - 0.65
        body_size = fit_font_size([claim.claim], card_width - (2 * CARD_PAD), body_height, sizes=[13, 12, 11, 10])

        add_text(
            slide,
            claim.claim,
            x + CARD_PAD,
            top + 0.52,
            card_width - (2 * CARD_PAD),
            body_height,
            font_size=body_size,
            color=DARK_GREY,
        )


# ---------------------------------------------------------------------
# Slide layouts
# ---------------------------------------------------------------------

def create_standard_slide(
    prs: Presentation,
    pitch_slide: PitchSlide,
):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    add_header(slide, pitch_slide.title, pitch_slide.subtitle)

    main_col_width = 7.2
    gap = 0.3
    support_col_width = CONTENT_WIDTH - gap - main_col_width
    support_x = MARGIN + main_col_width + gap

    # Main content card — extended down to just above the footer, so
    # font-fitting has real headroom before it needs to shrink.
    card_top = 2.25
    card_height = 4.5
    add_card(slide, MARGIN, card_top, main_col_width, card_height, fill=WHITE)

    add_text(
        slide,
        "KEY POINTS",
        MARGIN + CARD_PAD,
        card_top + 0.3,
        2.0,
        0.3,
        font_size=10,
        bold=True,
        color=BLUE,
    )

    points = pitch_slide.key_points[:5]
    bullets_width = main_col_width - (2 * CARD_PAD)
    bullets_top = card_top + 0.75
    bullets_height = card_height - 0.75 - CARD_PAD

    font_size = fit_font_size(points, bullets_width, bullets_height, sizes=[21, 19, 17, 15, 13])

    add_bullets(
        slide,
        points,
        MARGIN + CARD_PAD,
        bullets_top,
        bullets_width,
        bullets_height,
        font_size=font_size,
    )

    # Supporting claim cards — sized so the column's total height matches
    # the main card's, keeping both columns' bottom edges aligned.
    if pitch_slide.claims:
        add_text(
            slide,
            "SUPPORTING CONTEXT",
            support_x,
            2.55,
            support_col_width,
            0.3,
            font_size=10,
            bold=True,
            color=BLUE,
        )

        claims = pitch_slide.claims[:2]
        claims_top = 2.95
        claims_bottom = card_top + card_height
        row_gap = 0.2
        card_height_r = (claims_bottom - claims_top - row_gap) / 2

        for i, claim in enumerate(claims):
            y = claims_top + i * (card_height_r + row_gap)

            add_card(slide, support_x, y, support_col_width, card_height_r, fill=LIGHT_GREY)

            add_text(
                slide,
                claim.claim_type.replace("_", " ").title(),
                support_x + CARD_PAD,
                y + 0.2,
                support_col_width - (2 * CARD_PAD),
                0.25,
                font_size=10,
                bold=True,
                color=BLUE,
            )

            body_top = y + 0.52
            body_height = (y + card_height_r) - body_top - 0.1
            body_width = support_col_width - (2 * CARD_PAD)
            body_size = fit_font_size([claim.claim], body_width, body_height, sizes=[13, 12, 11, 10])

            add_text(
                slide,
                claim.claim,
                support_x + CARD_PAD,
                body_top,
                body_width,
                body_height,
                font_size=body_size,
                color=DARK_GREY,
            )

    add_footer(slide, len(prs.slides))

    return slide


def create_recommendation_slide(
    prs: Presentation,
    pitch_slide: PitchSlide,
    company_name: str,
    policy_provider: str,
):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = NAVY

    add_text(
        slide,
        "MARSH",
        MARGIN,
        0.55,
        1.5,
        0.3,
        font_size=KICKER_SIZE,
        bold=True,
        color=ACCENT_ON_DARK,
    )

    add_text(
        slide,
        "RECOMMENDATION",
        MARGIN,
        1.15,
        3.5,
        0.35,
        font_size=KICKER_SIZE,
        bold=True,
        color=EYEBROW_ON_DARK,
    )

    add_text(
        slide,
        pitch_slide.title,
        MARGIN,
        1.6,
        CONTENT_WIDTH,
        0.75,
        font_size=TITLE_SIZE,
        bold=True,
        color=WHITE,
    )

    add_card(slide, MARGIN, 2.65, CONTENT_WIDTH, 2.45, fill=WHITE)

    inner_left = MARGIN + CARD_PAD
    inner_width = CONTENT_WIDTH - (2 * CARD_PAD)

    add_text(
        slide,
        policy_provider,
        inner_left,
        3.0,
        inner_width,
        0.45,
        font_size=14,
        bold=True,
        color=BLUE,
    )

    recommendation = pitch_slide.key_points[0] if pitch_slide.key_points else ""
    rec_size = fit_font_size([recommendation], inner_width, 1.1, sizes=[25, 22, 19, 16])

    add_text(
        slide,
        recommendation,
        inner_left,
        3.55,
        inner_width,
        1.1,
        font_size=rec_size,
        bold=True,
        color=NAVY,
    )

    if len(pitch_slide.key_points) > 1:
        rationale = pitch_slide.key_points[1:4]
        rationale_size = fit_font_size(rationale, inner_width, 1.0, sizes=[16, 14, 12])

        add_bullets(
            slide,
            rationale,
            inner_left,
            5.45,
            inner_width,
            1.0,
            font_size=rationale_size,
            color=MUTED_ON_DARK,
        )

    add_footer(slide, len(prs.slides), dark=True)

    return slide


# ---------------------------------------------------------------------
# Static Marsh slide
# ---------------------------------------------------------------------

def create_why_marsh_slide(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = NAVY

    add_text(
        slide,
        "MARSH",
        MARGIN,
        0.55,
        1.5,
        0.3,
        font_size=KICKER_SIZE,
        bold=True,
        color=ACCENT_ON_DARK,
    )

    add_text(
        slide,
        "Why choose Marsh?",
        MARGIN,
        1.15,
        CONTENT_WIDTH,
        0.7,
        font_size=TITLE_SIZE,
        bold=True,
        color=WHITE,
    )

    add_text(
        slide,
        "Turning insurance decisions into informed risk-management conversations.",
        MARGIN,
        1.95,
        CONTENT_WIDTH - 1.2,
        0.5,
        font_size=SUBTITLE_SIZE,
        color=MUTED_ON_DARK,
    )

    reasons = [
        (
            "01",
            "We are committed partners",
            "Our diverse and relevant perspectives support our clients’ complex and emerging needs. By understanding our clients’ unique needs, we tailor solutions that pave the way for their ultimate success.",
        ),
        (
            "02",
            "We apply unique expertise",
            "Marsh leverages its industry capabilities, best-in-class digital and technical expertise, and advisory services to deliver comprehensive risk solutions that bend the risk curve and empower clients with data-driven, actionable insights.",
        ),
        (
            "03",
            "Data Driven",
            "We combine industry knowledge and data-driven insights, enabling clients to create new opportunities.",
        ),
        (
            "04",
            "We deliver actionable solutions",
            "By partnering with Marsh, clients gain the ability to navigate complex challenges, enhance their resilience, and drive sustainable business growth, supported by enterprise-wide solutions and differentiated advice in the areas of Risk, Strategy and People.",
        ),
    ]

    # Cards made taller than before (1.5" -> 1.8") specifically because the
    # longer descriptions (02, 04) didn't fit in the old height at any
    # reasonable font size — this is what actually overflowed in the deck
    # you generated. Font-fitting below is the safety net on top of that.
    card_gap = 0.45
    card_width = (CONTENT_WIDTH - card_gap) / 2
    card_height = 1.8
    row_gap = 0.2
    row1_y = 2.85
    row2_y = row1_y + card_height + row_gap
    col1_x = MARGIN
    col2_x = MARGIN + card_width + card_gap

    positions = [
        (col1_x, row1_y),
        (col2_x, row1_y),
        (col1_x, row2_y),
        (col2_x, row2_y),
    ]

    for (number, title, description), (x, y) in zip(reasons, positions):
        add_card(slide, x, y, card_width, card_height, fill=CARD_NAVY)

        add_text(
            slide,
            number,
            x + CARD_PAD - 0.05,
            y + 0.2,
            0.5,
            0.3,
            font_size=KICKER_SIZE,
            bold=True,
            color=ACCENT_ON_DARK,
        )

        title_left = x + 0.85
        title_width = card_width - 0.85 - CARD_PAD

        add_text(
            slide,
            title,
            title_left,
            y + 0.2,
            title_width,
            0.35,
            font_size=16,
            bold=True,
            color=WHITE,
        )

        desc_top = y + 0.65
        desc_height = (y + card_height) - desc_top - 0.15
        desc_size = fit_font_size([description], title_width, desc_height, sizes=[11, 10, 9])

        add_text(
            slide,
            description,
            title_left,
            desc_top,
            title_width,
            desc_height,
            font_size=desc_size,
            color=MUTED_ON_DARK,
        )

    add_footer(slide, len(prs.slides), dark=True)

    return slide


# ---------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------

def generate_pptx(
    pitch: PitchContent,
    output_path: str | Path,
) -> Path:

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prs = Presentation()

    prs.slide_width = Inches(SLIDE_WIDTH_IN)
    prs.slide_height = Inches(SLIDE_HEIGHT_IN)

    for pitch_slide in pitch.slides:
        is_recommendation = (
            pitch_slide.slide_number == len(pitch.slides)
            and (
                "recommend" in pitch_slide.title.lower()
                or pitch_slide.title.lower() == "recommendation"
            )
        )

        if is_recommendation:
            create_recommendation_slide(
                prs,
                pitch_slide,
                pitch.company_name,
                pitch.policy_provider,
            )
        else:
            create_standard_slide(prs, pitch_slide)

    create_why_marsh_slide(prs)

    prs.save(output_path)

    return output_path
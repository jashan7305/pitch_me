from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
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
    frame.margin_left = Inches(0.05)
    frame.margin_right = Inches(0.05)
    frame.margin_top = Inches(0.02)
    frame.margin_bottom = Inches(0.02)

    for i, point in enumerate(points):
        paragraph = frame.paragraphs[0] if i == 0 else frame.add_paragraph()

        # Real PowerPoint bullet character, set once (avoids re-writing the
        # run after formatting, which previously happened twice for no reason).
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

    # Every card in the deck shares the same flat look and corner radius,
    # rather than inheriting PowerPoint's default theme shadow inconsistently.
    shape.shadow.inherit = False
    shape.adjustments[0] = corner_radius

    return shape


def add_header(
    slide,
    title: str,
    subtitle: str | None = None,
):
    # Small Marsh label
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

    # Main title
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

    # Accent line
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
    """
    Shared by every slide type (standard, recommendation, and the static
    Why-Marsh slide) so the format, position and page count are identical
    throughout the deck. `dark=True` swaps in a lighter grey for navy slides.
    """
    add_text(
        slide,
        f"PitchMe  |  CLIENT ADVISORY  |  {slide_number}",
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
    """
    Render claims as readable cards rather than one giant paragraph.
    """

    if not claims:
        return

    count = min(len(claims), 4)

    card_width = (width - (count - 1) * 0.15) / count

    for i, claim in enumerate(claims[:count]):
        x = left + i * (card_width + 0.15)

        add_card(
            slide,
            x,
            top,
            card_width,
            height,
            fill=LIGHT_GREY,
        )

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

        add_text(
            slide,
            claim.claim,
            x + CARD_PAD,
            top + 0.52,
            card_width - (2 * CARD_PAD),
            height - 0.65,
            font_size=13,
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

    add_header(
        slide,
        pitch_slide.title,
        pitch_slide.subtitle,
    )

    # Two-column body: main content card + supporting-claims column.
    # Widths are derived from CONTENT_WIDTH so both columns' outer edges
    # sit at the same margin as everything else on the slide.
    main_col_width = 7.2
    gap = 0.3
    support_col_width = CONTENT_WIDTH - gap - main_col_width
    support_x = MARGIN + main_col_width + gap

    # Main content card
    add_card(
        slide,
        MARGIN,
        2.25,
        main_col_width,
        3.85,
        fill=WHITE,
    )

    add_text(
        slide,
        "KEY POINTS",
        MARGIN + CARD_PAD,
        2.55,
        2.0,
        0.3,
        font_size=10,
        bold=True,
        color=BLUE,
    )

    # Keep bullets readable.
    points = pitch_slide.key_points[:5]

    font_size = 21

    if len(points) >= 5:
        font_size = 18

    add_bullets(
        slide,
        points,
        MARGIN + CARD_PAD,
        3.0,
        main_col_width - (2 * CARD_PAD),
        2.75,
        font_size=font_size,
    )

    # Supporting claim cards
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

        card_height = 1.65

        for i, claim in enumerate(claims):
            y = 2.95 + i * 1.85

            add_card(
                slide,
                support_x,
                y,
                support_col_width,
                card_height,
                fill=LIGHT_GREY,
            )

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

            add_text(
                slide,
                claim.claim,
                support_x + CARD_PAD,
                y + 0.52,
                support_col_width - (2 * CARD_PAD),
                0.95,
                font_size=13,
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

    # Background
    background = slide.background
    fill = background.fill
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

    # Recommendation card — goes through the shared add_card() helper so it
    # gets the same corner radius / flat-shadow treatment as every other
    # card in the deck (previously built as a one-off shape here).
    add_card(
        slide,
        MARGIN,
        2.65,
        CONTENT_WIDTH,
        2.45,
        fill=WHITE,
    )

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

    add_text(
        slide,
        recommendation,
        inner_left,
        3.55,
        inner_width,
        1.1,
        font_size=25,
        bold=True,
        color=NAVY,
    )

    # Rationale — sits below the white card, directly on the navy
    # background, so it needs a light color, not the bullet default of
    # dark grey (which would be unreadable against navy).
    if len(pitch_slide.key_points) > 1:
        add_bullets(
            slide,
            pitch_slide.key_points[1:4],
            inner_left,
            5.45,
            inner_width,
            1.0,
            font_size=16,
            color=MUTED_ON_DARK,
        )

    add_footer(slide, len(prs.slides), dark=True)

    return slide


# ---------------------------------------------------------------------
# Static Marsh slide
# ---------------------------------------------------------------------

def create_why_marsh_slide(prs: Presentation):
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Dark background
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

    # Two-column grid sized from CONTENT_WIDTH so its right edge lines up
    # with the same margin as every other slide, instead of falling short.
    card_gap = 0.45
    card_width = (CONTENT_WIDTH - card_gap) / 2
    card_height = 1.5
    row1_y = 2.9
    row2_y = 4.75
    col1_x = MARGIN
    col2_x = MARGIN + card_width + card_gap

    positions = [
        (col1_x, row1_y),
        (col2_x, row1_y),
        (col1_x, row2_y),
        (col2_x, row2_y),
    ]

    for (number, title, description), (x, y) in zip(reasons, positions):
        add_card(
            slide,
            x,
            y,
            card_width,
            card_height,
            fill=CARD_NAVY,
        )

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

        add_text(
            slide,
            description,
            title_left,
            y + 0.65,
            title_width,
            0.65,
            font_size=11,
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

    # Widescreen 16:9
    prs.slide_width = Inches(SLIDE_WIDTH_IN)
    prs.slide_height = Inches(SLIDE_HEIGHT_IN)

    # -------------------------------------------------------------
    # Generated slides
    # -------------------------------------------------------------

    for pitch_slide in pitch.slides:

        # Treat the final generated slide as the recommendation
        # when it contains recommendation language.
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
            create_standard_slide(
                prs,
                pitch_slide,
            )

    # -------------------------------------------------------------
    # Always append static Marsh slide
    # -------------------------------------------------------------

    create_why_marsh_slide(prs)

    prs.save(output_path)

    return output_path
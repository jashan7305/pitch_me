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

FONT = "Aptos"


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

        paragraph.text = point
        paragraph.font.name = FONT
        paragraph.font.size = Pt(font_size)
        paragraph.font.color.rgb = DARK_GREY
        paragraph.level = 0
        paragraph.space_after = Pt(12)

        # Real PowerPoint bullet
        paragraph.text = f"•  {point}"

    return box


def add_card(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    *,
    fill=WHITE,
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
    shape.line.width = Pt(1)

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
        0.65,
        0.38,
        1.2,
        0.3,
        font_size=11,
        bold=True,
        color=BLUE,
    )

    # Main title
    add_text(
        slide,
        title,
        0.65,
        0.78,
        11.8,
        0.65,
        font_size=28,
        bold=True,
        color=NAVY,
    )

    if subtitle:
        add_text(
            slide,
            subtitle,
            0.65,
            1.42,
            11.8,
            0.45,
            font_size=15,
            color=MID_GREY,
        )

    # Accent line
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(0.65),
        Inches(1.95),
        Inches(1.0),
        Inches(0.055),
    )

    line.fill.solid()
    line.fill.fore_color.rgb = BLUE
    line.line.fill.background()


def add_footer(slide, slide_number: int):
    add_text(
        slide,
        f"MARSH  |  CLIENT ADVISORY  |  {slide_number}",
        0.65,
        7.05,
        12.0,
        0.25,
        font_size=9,
        color=MID_GREY,
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
            x + 0.15,
            top + 0.15,
            card_width - 0.3,
            0.3,
            font_size=10,
            bold=True,
            color=BLUE,
        )

        add_text(
            slide,
            claim.claim,
            x + 0.15,
            top + 0.52,
            card_width - 0.3,
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

    # Main content card
    add_card(
        slide,
        0.65,
        2.25,
        7.15,
        3.85,
        fill=WHITE,
    )

    add_text(
        slide,
        "KEY POINTS",
        0.95,
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
        0.95,
        3.0,
        6.45,
        2.75,
        font_size=font_size,
    )

    # Supporting claim cards
    if pitch_slide.claims:
        add_text(
            slide,
            "SUPPORTING CONTEXT",
            8.15,
            2.55,
            3.5,
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
                8.15,
                y,
                4.45,
                card_height,
                fill=LIGHT_GREY,
            )

            add_text(
                slide,
                claim.claim_type.replace("_", " ").title(),
                8.4,
                y + 0.2,
                3.9,
                0.25,
                font_size=10,
                bold=True,
                color=BLUE,
            )

            add_text(
                slide,
                claim.claim,
                8.4,
                y + 0.52,
                3.9,
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
        0.75,
        0.55,
        1.5,
        0.3,
        font_size=12,
        bold=True,
        color=RGBColor(120, 180, 235),
    )

    add_text(
        slide,
        "RECOMMENDATION",
        0.75,
        1.15,
        3.5,
        0.35,
        font_size=11,
        bold=True,
        color=RGBColor(150, 185, 215),
    )

    add_text(
        slide,
        pitch_slide.title,
        0.75,
        1.6,
        11.4,
        0.75,
        font_size=32,
        bold=True,
        color=WHITE,
    )

    # Recommendation card
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.75),
        Inches(2.65),
        Inches(11.85),
        Inches(2.45),
    )

    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.fill.background()

    add_text(
        slide,
        policy_provider,
        1.1,
        3.0,
        10.8,
        0.45,
        font_size=14,
        bold=True,
        color=BLUE,
    )

    recommendation = pitch_slide.key_points[0] if pitch_slide.key_points else ""

    add_text(
        slide,
        recommendation,
        1.1,
        3.55,
        10.8,
        1.1,
        font_size=25,
        bold=True,
        color=NAVY,
    )

    # Rationale
    if len(pitch_slide.key_points) > 1:
        add_bullets(
            slide,
            pitch_slide.key_points[1:4],
            1.1,
            5.45,
            10.8,
            1.0,
            font_size=16,
        )

    add_text(
        slide,
        f"{company_name}  •  Prepared by Marsh",
        0.75,
        7.05,
        11.8,
        0.25,
        font_size=9,
        color=RGBColor(160, 175, 190),
    )

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
        0.75,
        0.55,
        1.5,
        0.3,
        font_size=12,
        bold=True,
        color=RGBColor(120, 180, 235),
    )

    add_text(
        slide,
        "Why choose Marsh?",
        0.75,
        1.15,
        11.5,
        0.7,
        font_size=34,
        bold=True,
        color=WHITE,
    )

    add_text(
        slide,
        "Turning insurance decisions into informed risk-management conversations.",
        0.75,
        1.95,
        10.8,
        0.5,
        font_size=17,
        color=RGBColor(190, 205, 220),
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

    positions = [
        (0.75, 2.9),
        (6.65, 2.9),
        (0.75, 4.75),
        (6.65, 4.75),
    ]

    for (number, title, description), (x, y) in zip(reasons, positions):
        add_card(
            slide,
            x,
            y,
            5.45,
            1.5,
            fill=RGBColor(30, 46, 65),
        )

        add_text(
            slide,
            number,
            x + 0.25,
            y + 0.2,
            0.5,
            0.3,
            font_size=11,
            bold=True,
            color=RGBColor(120, 180, 235),
        )

        add_text(
            slide,
            title,
            x + 0.85,
            y + 0.2,
            4.25,
            0.35,
            font_size=16,
            bold=True,
            color=WHITE,
        )

        add_text(
            slide,
            description,
            x + 0.85,
            y + 0.65,
            4.25,
            0.65,
            font_size=11,
            color=RGBColor(190, 205, 220),
        )

    add_text(
        slide,
        "MARSH  |  CLIENT ADVISORY",
        0.75,
        7.05,
        11.8,
        0.25,
        font_size=9,
        color=RGBColor(145, 165, 185),
    )

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
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

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
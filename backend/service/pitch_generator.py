from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt

from models.pitch import PitchContent


def _add_title(
    slide,
    title: str,
    subtitle: str | None = None,
) -> None:
    """Add a slide title and optional subtitle."""

    title_box = slide.shapes.add_textbox(
        Inches(0.6),
        Inches(0.45),
        Inches(12.1),
        Inches(0.7),
    )

    frame = title_box.text_frame
    frame.clear()

    paragraph = frame.paragraphs[0]
    paragraph.text = title
    paragraph.font.size = Pt(28)
    paragraph.font.bold = True

    if subtitle:
        subtitle_box = slide.shapes.add_textbox(
            Inches(0.65),
            Inches(1.15),
            Inches(11.8),
            Inches(0.45),
        )

        frame = subtitle_box.text_frame
        frame.clear()

        paragraph = frame.paragraphs[0]
        paragraph.text = subtitle
        paragraph.font.size = Pt(14)


def _add_bullets(
    slide,
    points: list[str],
    *,
    top: float = 1.7,
) -> None:
    """Add presentation points to a slide."""

    box = slide.shapes.add_textbox(
        Inches(0.8),
        Inches(top),
        Inches(11.4),
        Inches(4.8),
    )

    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True

    for index, point in enumerate(points):
        paragraph = (
            frame.paragraphs[0]
            if index == 0
            else frame.add_paragraph()
        )

        paragraph.text = point
        paragraph.font.size = Pt(18)
        paragraph.space_after = Pt(12)


def _add_claims(
    slide,
    claims,
    *,
    top: float = 4.9,
) -> None:
    """
    Add claim text to the slide.

    Claims are rendered exactly as generated.
    No audit result is consulted here.
    """

    if not claims:
        return

    box = slide.shapes.add_textbox(
        Inches(0.8),
        Inches(top),
        Inches(11.4),
        Inches(1.5),
    )

    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True

    for index, claim in enumerate(claims):
        paragraph = (
            frame.paragraphs[0]
            if index == 0
            else frame.add_paragraph()
        )

        paragraph.text = claim.claim
        paragraph.font.size = Pt(12)
        paragraph.space_after = Pt(6)


def generate_pptx(
    pitch: PitchContent,
    output_path: str | Path,
) -> Path:
    """
    Generate a PowerPoint directly from PitchContent.

    The audit system is intentionally not involved here.
    The PPTX represents exactly what the pitch agent generated.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    presentation = Presentation()

    # 16:9 widescreen
    presentation.slide_width = Inches(13.333)
    presentation.slide_height = Inches(7.5)

    blank_layout = presentation.slide_layouts[6]

    for pitch_slide in pitch.slides:
        slide = presentation.slides.add_slide(
            blank_layout
        )

        _add_title(
            slide,
            pitch_slide.title,
            pitch_slide.subtitle,
        )

        _add_bullets(
            slide,
            pitch_slide.key_points,
        )

        _add_claims(
            slide,
            pitch_slide.claims,
        )

    # Recommendation slide
    recommendation_slide = presentation.slides.add_slide(
        blank_layout
    )

    _add_title(
        recommendation_slide,
        "Recommendation",
        pitch.company_name,
    )

    _add_bullets(
        recommendation_slide,
        [
            pitch.recommendation,
            pitch.recommendation_rationale,
        ],
        top=1.8,
    )

    presentation.save(
        str(output_path)
    )

    return output_path
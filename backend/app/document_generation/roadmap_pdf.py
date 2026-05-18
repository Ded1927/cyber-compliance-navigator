"""PDF generation for anonymous roadmap export."""

from io import BytesIO
from typing import Any

from fpdf import FPDF

PDF_MIME_TYPE = "application/pdf"

# Paths to Unicode TTF fonts shipped with the container image.
# We register DejaVuSans so that Cyrillic text renders correctly.
_FONT_REGISTERED = False


def _register_fonts(pdf: FPDF) -> None:
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return

    try:
        pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
        pdf.add_font(
            "DejaVu", "B", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", uni=True
        )
        _FONT_REGISTERED = True
    except RuntimeError:
        # If DejaVu is not installed, fall back to Helvetica (no Cyrillic).
        pass


class RoadmapPdfGenerator:
    """Generates a one-page-per-task PDF for an anonymous roadmap."""

    def generate(self, tasks: list[dict[str, Any]], org_type_label: str) -> BytesIO:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=25)
        _register_fonts(pdf)

        font_family = "DejaVu" if _FONT_REGISTERED else "Helvetica"

        # --- Title page ---
        pdf.add_page()
        pdf.set_font(font_family, "B", 22)
        pdf.cell(0, 20, "Дорожня карта кіберкомплаєнсу", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(4)

        pdf.set_font(font_family, "", 12)
        pdf.cell(0, 10, f"Тип організації: {org_type_label}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.cell(0, 10, f"Кількість кроків: {len(tasks)}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(6)

        pdf.set_draw_color(215, 222, 230)
        pdf.line(20, pdf.get_y(), pdf.w - 20, pdf.get_y())
        pdf.ln(8)

        pdf.set_font(font_family, "", 10)
        pdf.multi_cell(
            0,
            6,
            "Цей документ згенеровано сервісом CyberLaw Navigator на основі "
            "відповідей опитувальника. Для збереження прогресу та доступу до "
            "повного функціоналу зареєструйтесь у системі.",
            align="C",
        )

        # --- Task pages ---
        for task in tasks:
            pdf.add_page()
            self._render_task(pdf, task, font_family)

        output = BytesIO()
        pdf.output(output)
        output.seek(0)
        return output

    def _render_task(self, pdf: FPDF, task: dict[str, Any], font: str) -> None:
        index = task.get("index", "")
        title = task.get("title", "")
        description = task.get("description", "")
        guidance = task.get("guidance") or ""
        references = task.get("references") or ""
        legal_basis = task.get("legal_basis", "")
        deadline_days = task.get("deadline_days", "")

        # Header bar
        pdf.set_fill_color(18, 53, 91)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font(font, "B", 14)
        pdf.cell(0, 12, f"  Крок {index}. {title}", new_x="LMARGIN", new_y="NEXT", fill=True)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

        # Meta line
        pdf.set_font(font, "", 10)
        pdf.set_text_color(82, 97, 111)
        pdf.cell(0, 7, f"Правова основа: {legal_basis}   •   Строк виконання: {deadline_days} днів", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

        # Description
        self._section(pdf, font, "Опис", description)

        # Guidance
        if guidance:
            self._section(pdf, font, "Підказки для виконання", guidance)

        # References
        if references:
            self._section(pdf, font, "Референси", references)

    def _section(self, pdf: FPDF, font: str, heading: str, body: str) -> None:
        pdf.set_font(font, "B", 11)
        pdf.cell(0, 8, heading, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font(font, "", 10)
        pdf.multi_cell(0, 6, body)
        pdf.ln(3)

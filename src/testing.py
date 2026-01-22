from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors


class GameReportTemplate():
    def __init__(self, output_name):
        self.output_name = output_name

    def _make_table(self, data, col_widths, row_height=18):
        """Create a table that won't collapse when cells are empty."""
        # Ensure blanks have at least a space so row heights don't collapse
        safe = []
        for r in data:
            safe.append([(" " if (c is None or str(c) == "") else c) for c in r])

        t = Table(
            safe,
            colWidths=col_widths,
            rowHeights=[row_height] * len(safe),
        )
        t.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.75, colors.black),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return t


    def build_game_report_template(self, output_path=None):
        if output_path is None:
            output_path = self.output_name

        doc = SimpleDocTemplate(
            output_path,
            pagesize=LETTER,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="TitleStyle",
                fontSize=16,
                leading=20,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
                spaceAfter=16,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SectionHeader",
                fontSize=12,
                leading=14,
                fontName="Helvetica-Bold",
                spaceBefore=14,
                spaceAfter=8,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Placeholder",
                fontSize=10,
                leading=13,
                spaceAfter=12,
            )
        )

        elements = []

        # -------------------------------------------------
        # PAGE 1: INTENSITY
        # -------------------------------------------------
        elements.append(Paragraph("Game Report – Intensity Band Metrics", styles["TitleStyle"]))

        elements.append(Paragraph("Intensity Note:", styles["SectionHeader"]))
        elements.append(Paragraph("[ Narrative text placeholder – intensity summary ]", styles["Placeholder"]))

        elements.append(Paragraph("Highlighted Players – Intensity Bands", styles["SectionHeader"]))
        elements.append(Paragraph("[ Narrative text placeholder – highlighted players ]", styles["Placeholder"]))

        intensity_table_data = [
            ["PLAYER_NAME", "Total Supra Max Efforts", "Supra Max %", "Very High Intensity %"],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
        ]
        intensity_table = self._make_table(
            intensity_table_data,
            col_widths=[170, 140, 90, 120],
            row_height=18,
        )
        elements.append(Spacer(1, 12))
        elements.append(intensity_table)
        elements.append(Spacer(1, 18))

        elements.append(Paragraph("Load Note:", styles["SectionHeader"]))
        elements.append(Paragraph("[ Narrative text placeholder – load and freshness notes ]", styles["Placeholder"]))

        elements.append(PageBreak())

        # -------------------------------------------------
        # PAGE 2: LOAD METRICS
        # -------------------------------------------------
        elements.append(Paragraph("Game Report – Load Metrics", styles["TitleStyle"]))

        load_table_data = [
            ["NAME", "DTL", "CTL", "Freshness (7 Day)", "Freshness (3 Day)", "Game Only DTL"],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
            ["", "", "", "", "", ""],
        ]
        load_table = self._make_table(
            load_table_data,
            col_widths=[140, 70, 70, 90, 90, 90],
            row_height=18,
        )
        elements.append(load_table)
        elements.append(Spacer(1, 18))

        elements.append(Paragraph("Highlighted Players by Freshness", styles["SectionHeader"]))
        elements.append(Paragraph("[ Narrative text placeholder – freshness highlights ]", styles["Placeholder"]))

        elements.append(PageBreak())

        # -------------------------------------------------
        # PAGE 3: PERIOD DISTRIBUTION
        # -------------------------------------------------
        elements.append(Paragraph("Intensity Band Distribution by Period", styles["TitleStyle"]))

        period_table_data = [
            ["PLAYER_NAME", "Period 1", "Period 2", "Period 3"],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
            ["", "", "", ""],
        ]
        period_table = self._make_table(
            period_table_data,
            col_widths=[180, 110, 110, 110],
            row_height=18,
        )
        elements.append(period_table)
        elements.append(Spacer(1, 16))

        elements.append(Paragraph("[ Narrative text placeholder – period distribution analysis ]", styles["Placeholder"]))

        doc.build(elements)


if __name__ == "__main__":
    report = GameReportTemplate("testing.pdf")
    report.build_game_report_template()
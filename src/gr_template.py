from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    FrameBreak,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Preformatted,
    NextPageTemplate,
    Paragraph
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
import pandas as pd

# sets game date & other team's name
opp = "Detroit Red Wings"
gd = "1/7/05"

# page size and styles
styles = getSampleStyleSheet()


class GameReportTemplate:
    def __init__(
        self,
        report_name,
        sm_narrative,
        lm_narrative,
        df_go_dtl,
        df_freshness,
        df_team_sm,
        df_relative_sm,
        intensity_note,
        load_note
    ):
        self.report_name = report_name
        self.sm_narrative = sm_narrative
        self.lm_narrative = lm_narrative
        self.df_go_dtl = df_go_dtl
        self.df_freshness = df_freshness
        self.df_team_sm = df_team_sm
        self.df_relative_sm = df_relative_sm
        self.intensity_note = intensity_note
        self.load_note = load_note

    # make sure headers fit in tables
    def wrap_table_header(self, data):
        header_style = ParagraphStyle(
            "table_header",
            fontName="Times-Bold",
            fontSize=8,
            leading=9,
            alignment=1,  # center
        )
        data = data.copy()
        data[0] = [Paragraph(str(h), header_style) for h in data[0]]
        return data

    # header / template layer: KEEP ONLY NON-TEXT DRAWING HERE (e.g., images/lines)
    def metrics_table(self, canvas, doc):
        canvas.saveState()

        canvas.drawImage(
            "../assets/achieve.png",
            doc.leftMargin - inch / 2,
            inch * 9.75,
            width=inch * 1.75,
            mask="auto",
            preserveAspectRatio=True,
        )
        canvas.drawImage(
            "../assets/sabres.png",
            inch * 2.1,
            inch * 2.075,
            width=inch * 0.5,
            mask="auto",
            preserveAspectRatio=True,
        )
        canvas.setFont("Times-Roman", 14)
        canvas.drawCentredString(inch * 7, inch * 10.905, f"Game Report - {gd}")

        canvas.restoreState()

    # fill table with df data
    def df_to_table_data(self, df: pd.DataFrame):
        df = df.fillna("")
        return [list(df.columns)] + df.astype(str).values.tolist()

    def _base_table_style(self):
        return TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )

    def go(self):
        leftMargin = 0.75 * inch
        rightMargin = 0.75 * inch
        bottomMargin = 0.75 * inch
        topMargin = 1.5 * inch  # header space for images/etc

        doc = BaseDocTemplate(
            f"{self.report_name}.pdf",
            pagesize=defaultPageSize,
            leftMargin=leftMargin,
            rightMargin=rightMargin,
            bottomMargin=bottomMargin,
            topMargin=topMargin,
        )

        # --------------------
        # Styles
        # --------------------
        title_style = ParagraphStyle(
            "story_title",
            parent=styles["Title"],
            fontName="Times-Bold",
            fontSize=20,
            leading=24,
            alignment=1,
            spaceAfter=6,
        )

        label_style = ParagraphStyle(
            "col_label",
            parent=styles["BodyText"],
            fontName="Times-Roman",
            fontSize=12,
            leading=14,
            alignment=0,
            spaceAfter=6,
        )

        note_style = ParagraphStyle(
            "note_style",
            parent=styles["BodyText"],
            fontName="Times-Roman",
            fontSize=9,
            leading=11,
            alignment=0,
            spaceBefore=4,
            spaceAfter=0,
        )

        narrative_style = ParagraphStyle(
            "narrative",
            parent=styles["BodyText"],
            fontName="Times-Roman",
            fontSize=10,
            leading=12,
            alignment=0,
        )

        # --------------------
        # Frames
        # --------------------
        gutter = 0.2 * inch
        usable_w = doc.width
        col_w = (usable_w - gutter) / 2

        y0 = doc.bottomMargin
        h = doc.height

        # Title band for the 2-col page
        title_h = 0.9 * inch
        vgap = 0.1 * inch

        # Bottom band for Intensity Note on 2-col page
        intensity_h = 1.6 * inch

        # Bottom band for Load Note on SM narrative pages
        load_h = 1.35 * inch

        # --- 2-col page frames ---
        title_frame = Frame(
            doc.leftMargin,
            y0 + (h - title_h),
            doc.width,
            title_h,
            id="title",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        col_h = h - title_h - vgap - intensity_h

        left_frame = Frame(
            doc.leftMargin,
            y0 + intensity_h,
            col_w,
            col_h,
            id="left",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        right_frame = Frame(
            doc.leftMargin + col_w + gutter,
            y0 + intensity_h,
            col_w,
            col_h,
            id="right",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        intensity_frame = Frame(
            doc.leftMargin,
            y0,
            doc.width,
            intensity_h,
            id="intensity",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        # --- 1-col narrative (plain) ---
        onecol_frame = Frame(
            doc.leftMargin,
            y0,
            doc.width,
            h,
            id="onecol",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        # --- 1-col narrative with bottom load note band ---
        onecol_main_frame = Frame(
            doc.leftMargin,
            y0 + load_h,
            doc.width,
            h - load_h,
            id="onecol_main",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        onecol_load_frame = Frame(
            doc.leftMargin,
            y0,
            doc.width,
            load_h,
            id="onecol_load",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        # --------------------
        # Page templates
        # --------------------
        two_col_tpl = PageTemplate(
            id="TwoCol",
            frames=[title_frame, left_frame, right_frame, intensity_frame],
            onPage=self.metrics_table,
        )

        one_col_tpl = PageTemplate(
            id="OneCol",
            frames=[onecol_frame],
            onPage=self.metrics_table,
        )

        # SM narrative pages (main + bottom Load Note band)
        one_col_load_tpl = PageTemplate(
            id="OneColLoad",
            frames=[onecol_main_frame, onecol_load_frame],
            onPage=self.metrics_table,
        )

        doc.addPageTemplates([two_col_tpl, one_col_tpl, one_col_load_tpl])

        # --------------------
        # Build tables
        # --------------------
        sm_team_df = self.df_team_sm.drop(columns=["Total Very High Intensity Efforts"], errors="ignore")
        sm_team_data = self.wrap_table_header(self.df_to_table_data(sm_team_df))

        left_colWidths = [col_w * 0.65, col_w * 0.35]
        sm_team_tbl = Table(sm_team_data, colWidths=left_colWidths, repeatRows=1, splitByRow=1)
        sm_team_tbl.setStyle(self._base_table_style())

        sm_relative_data = self.wrap_table_header(self.df_to_table_data(self.df_relative_sm.head(19)))
        right_colWidths = [col_w * 0.52, col_w * 0.24, col_w * 0.24]
        sm_relative_tbl = Table(sm_relative_data, colWidths=right_colWidths, repeatRows=1, splitByRow=1)
        sm_relative_tbl.setStyle(self._base_table_style())

        # --------------------
        # Story
        # --------------------
        story = []

        # --- 2-col page ---
        story.append(Paragraph(f"Buffalo Sabres vs {opp}", title_style))
        story.append(Spacer(1, 6))

        # Left col
        story.append(Paragraph("Player SupraMax Efforts as<br/>Percentage of Team Total", label_style))
        story.append(sm_team_tbl)

        # Right col
        story.append(FrameBreak())
        story.append(Paragraph("Player SupraMax/VHI Efforts<br/>Relative to Personal Player Average", label_style))
        story.append(sm_relative_tbl)

        # Bottom intensity note band
        story.append(FrameBreak())
        story.append(Paragraph(f"<b>Intensity Note:</b> {self.intensity_note}", note_style))

        # --- SM narrative pages: OneColLoad (main narrative + bottom load note band) ---
        story.append(NextPageTemplate("OneColLoad"))
        story.append(PageBreak())

        # Narrative in main frame; can flow to multiple pages (still OneColLoad)
        story.append(Paragraph(self.sm_narrative, narrative_style))

        # When SM narrative is done, move into the bottom band on THAT page template
        story.append(FrameBreak())
        story.append(Paragraph(f"<b>Load Note:</b> {self.load_note}", note_style))

        # --- LM narrative pages: plain one column (no load note band) ---
        '''
        story.append(NextPageTemplate("OneCol"))
        story.append(PageBreak())
        story.append(Paragraph(self.lm_narrative, narrative_style))
        '''

        doc.build(story)
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
    NextPageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import pandas as pd

# sets game date & other team's name
opp = "Detroit Red Wings"
gd = "1/7/05"

# page size and styles
PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
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
    ):
        self.report_name = report_name
        self.sm_narrative = sm_narrative
        self.lm_narrative = lm_narrative
        self.df_go_dtl = df_go_dtl
        self.df_freshness = df_freshness
        self.df_team_sm = df_team_sm
        self.df_relative_sm = df_relative_sm

    #  make sure headers fit in tables
    def wrap_table_header(self, data):
        header_style = ParagraphStyle(
            "table_header",
            fontName="Times-Bold",
            fontSize=8,  # smaller than body
            leading=9,
            alignment=1  # center
        )

        data = data.copy()
        data[0] = [Paragraph(str(h), header_style) for h in data[0]]
        return data

    #  header / template layer
    def intensity_band_metrics(self, canvas, doc):
        canvas.saveState()

        # title
        canvas.setFont("Times-Bold", 24)
        canvas.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 120, f"Buffalo Sabres vs {opp}")

        # header line
        canvas.setFont("Times-Roman", 14)
        canvas.drawCentredString(inch * 6.5, inch * 10.905, f"Game Report - {gd}")

        # images
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
            inch * 2.35,
            inch * 2.075,
            width=inch * 0.5,
            mask="auto",
            preserveAspectRatio=True,
        )

        # separation lines
        line_y = inch * 9
        '''
        canvas.setLineWidth(2)
        canvas.line(doc.leftMargin, line_y, doc.pagesize[0] - doc.rightMargin, line_y)

        line_x = (doc.leftMargin + (doc.pagesize[0] - doc.rightMargin)) / 2
        canvas.line(line_x, inch * 9, line_x, inch * 3)
        '''

        # labels
        canvas.setFont("Times-Roman", 12)
        canvas.drawString(inch * 1.05, line_y - inch / 4, "Player SupraMax Efforts as")
        canvas.drawString(inch * 1.05, line_y - inch / 2.25, "Percentage of Team Total")
        canvas.drawString(inch * 4.25, line_y - inch / 4, "Player SupraMax/VHI Efforts")
        canvas.drawString(inch * 4.25, line_y - inch / 2.25, "Relative to Personal Player Average")

        canvas.restoreState()

    #  fill table with df data
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
        # Reserve header area with topMargin (so tables start below it)
        leftMargin = 0.75 * inch
        rightMargin = 0.75 * inch
        bottomMargin = 0.75 * inch
        topMargin = 3.2 * inch  # header space

        doc = BaseDocTemplate(
            f"{self.report_name}.pdf",
            pagesize=defaultPageSize,
            leftMargin=leftMargin,
            rightMargin=rightMargin,
            bottomMargin=bottomMargin,
            topMargin=topMargin,
        )

        # Two side-by-side frames (splittable across pages!)
        gutter = 0.2 * inch
        usable_w = doc.width
        col_w = (usable_w - gutter) / 2
        y0 = doc.bottomMargin
        h = doc.height

        left_frame = Frame(
            doc.leftMargin,
            y0,
            col_w,
            h,
            id="left",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        right_frame = Frame(
            doc.leftMargin + col_w + gutter,
            y0,
            col_w,
            h,
            id="right",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        template = PageTemplate(id="TwoCol", frames=[left_frame, right_frame], onPage=self.intensity_band_metrics)
        doc.addPageTemplates([template])

        # ---- Build the two tables
        sm_team_df = self.df_team_sm.drop(columns=["Total Very High Intensity Efforts"], errors="ignore")
        sm_team_data = self.df_to_table_data(sm_team_df)
        sm_team_data = self.wrap_table_header(sm_team_data)

        # Size columns to the frame width (left table has 2 cols)
        left_colWidths = [col_w * 0.65, col_w * 0.35]
        sm_team_tbl = Table(sm_team_data, colWidths=left_colWidths, repeatRows=1, splitByRow=1)
        sm_team_tbl.setStyle(self._base_table_style())

        sm_relative_data = self.df_to_table_data(self.df_relative_sm.head(19))
        sm_relative_data = self.wrap_table_header(sm_relative_data)

        # Right table has 3 cols (name wider)
        right_colWidths = [col_w * 0.52, col_w * 0.24, col_w * 0.24]
        sm_relative_tbl = Table(sm_relative_data, colWidths=right_colWidths, repeatRows=1, splitByRow=1)
        sm_relative_tbl.setStyle(self._base_table_style())

        # ---- story: left table goes into left frame, then framebreak, then right frame
        story = []
        story.append(sm_team_tbl)
        story.append(FrameBreak())
        story.append(sm_relative_tbl)
        story.append(Spacer(1, 12))

        #  NEW PAGE FOR NARRATIVES **TESTING**
        story.append(PageBreak())
        story.append(Preformatted(self.sm_narrative, styles["BodyText"]))
        story.append(PageBreak())
        story.append(Preformatted(self.lm_narrative, styles["BodyText"]))

        doc.build(story)
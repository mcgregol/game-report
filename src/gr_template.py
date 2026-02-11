from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
import pandas as pd

#  sets game date & other team's name
opp = 'Detroit Red Wings'
gd = '1/7/05'

#  set page size and style to defaults
PAGE_HEIGHT = defaultPageSize[1]; PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()

class GameReportTemplate:
    def __init__(self, report_name, sm_narrative, lm_narrative, df_go_dtl, df_freshness, df_team_sm, df_relative_sm):
        self.report_name = report_name
        self.sm_narrative = sm_narrative
        self.lm_narrative = lm_narrative
        self.df_go_dtl = df_go_dtl
        self.df_freshness = df_freshness
        self.df_team_sm = df_team_sm
        self.df_relative_sm = df_relative_sm

    #  intensity band static template
    def intensity_band_metrics(self, canvas, doc):
        canvas.saveState()

        #  add title
        canvas.setFont('Times-Bold', 24)
        canvas.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT-120, f'Buffalo Sabres vs {opp}')

        #  add headers
        canvas.setFont('Times-Roman', 14)
        canvas.drawCentredString(inch * 6.5, inch * 10.905, f'Game Report - {gd}')
        canvas.drawImage('../assets/achieve.png',
                         doc.leftMargin-inch/2, inch*9.75,
                         width=inch*1.75,
                         mask='auto',
                         preserveAspectRatio=True
                         )
        canvas.drawImage('../assets/sabres.png',
                         inch*2.35, inch*2.075,
                         width=inch*0.5,
                         mask='auto',
                         preserveAspectRatio=True)

        #  add separation lines
        line_y = inch*9
        canvas.setLineWidth(2)
        canvas.line(doc.leftMargin,
                    line_y,
                    doc.pagesize[0]-doc.rightMargin,
                    line_y
                    )
        line_x = (doc.leftMargin+(doc.pagesize[0]-doc.rightMargin))/2
        canvas.line(line_x, inch*9, line_x, inch*3)

        #  add table labels
        canvas.drawString(inch*1.05,
                          line_y-inch/4,
                          "Player SupraMax Efforts as")
        canvas.drawString(inch*1.05,
                          line_y-inch/2.25,
                          "Percentage of Team Total")
        canvas.drawString(inch*4.25,
                          line_y-inch/4,
                          "Player SupraMax/VHI Efforts")
        canvas.drawString(inch*4.25,
                          line_y-inch/2.25,
                          "Relative to Personal Player Average")

        canvas.restoreState()

    #  load metrics static template
    def load_metrics(self, canvas, doc):
        canvas.saveState()

        canvas.restoreState()

    #  create function to convert df to list
    def df_to_table_data(self, df: pd.DataFrame):
        #  replace NaN
        df = df.fillna("")

        header = list(df.columns)
        rows = df.astype(str).values.tolist()

        return [header] + rows

    def go(self):
        doc = SimpleDocTemplate(f'{self.report_name}.pdf')
        Story = []

        #  supramax team table
        sm_team_data = self.df_to_table_data(self.df_team_sm.drop(columns=['Total Very High Intensity Efforts'], errors='ignore'))
        sm_team_tbl = Table(sm_team_data, hAlign='LEFT', repeatRows=1)
        sm_team_tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ]))

        #  supramax relative table
        sm_relative_data = self.df_to_table_data(self.df_relative_sm)
        sm_relative_tbl = Table(sm_relative_data, hAlign='RIGHT', repeatRows=1)
        sm_relative_tbl.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ]))

        #  add to story
        # ---- width available for content
        available_width = doc.width
        half = available_width / 2

        # resize both tables so they fit their half
        sm_team_tbl._argW = [half / len(sm_team_data[0])] * len(sm_team_data[0])
        sm_relative_tbl._argW = [half / len(sm_relative_data[0])] * len(sm_relative_data[0])

        # ---- container table (2 columns, 1 row)
        pair_tbl = Table(
            [[sm_team_tbl, sm_relative_tbl]],
            colWidths=[half, half]
        )

        pair_tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

        Story.append(Spacer(1, inch * 2.2))
        Story.append(pair_tbl)

        doc.build(Story, onFirstPage=self.intensity_band_metrics, onLaterPages=self.load_metrics)

if __name__ == "__main__":
    t = GameReportTemplate('yassss','','','','','','')
    t.go()
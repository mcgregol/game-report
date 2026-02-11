from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

#  sets game date & other team's name
opp = 'Detroit Red Wings'
gd = '1/7/05'

#  set page size and style to defaults
PAGE_HEIGHT = defaultPageSize[1]; PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()

class GameReportTemplate:
    def __init__(self, sm_narrative, lm_narrative, df_go_dtl, df_freshness, df_team_sm, df_relative_sm):
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
        canvas.line(line_x, inch*9, line_x, inch*4)

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
        canvas.setFont('Times-Roman', 9)
        canvas.restoreState()

    def go(self):
        doc = SimpleDocTemplate("testing.pdf")
        Story = [Spacer(1,2*inch)]
        style = styles['Normal']

        doc.build(Story, onFirstPage=self.intensity_band_metrics, onLaterPages=self.load_metrics)

if __name__ == "__main__":
    t = GameReportTemplate('','','','','','')
    t.go()
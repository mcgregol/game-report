from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
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

    def intensity_band_metrics(self, canvas, doc):
        canvas.saveState()

        canvas.setFont('Times-Bold', 24)
        canvas.drawCentredString(PAGE_WIDTH/2, PAGE_HEIGHT-120, f'Buffalo Sabres vs {opp}')

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

        canvas.setFont('Times-Roman', 12)
        canvas.drawCentredString(inch*6.5, inch*10.905, f'Game Report - {gd}')

        canvas.restoreState()

    def load_metrics(self, canvas, doc):
        canvas.saveState()
        canvas.setFont('Times-Roman', 9)
        canvas.restoreState()

    def go(self):
        doc = SimpleDocTemplate("testing.pdf")
        Story = [Spacer(1,2*inch)]
        style = styles['Normal']
        for i in range(100):
            bogustext = ("This is Paragraph number %s. " % i) * 20
            p = Paragraph(bogustext, style)
            Story.append(p)
            Story.append(Spacer(1, 0.2 * inch))
        doc.build(Story, onFirstPage=self.intensity_band_metrics, onLaterPages=self.load_metrics)

if __name__ == "__main__":
    t = GameReportTemplate('','','','','','')
    t.go()
class GameReportTemplate:
    def __init__(self, sm_narrative, lm_narrative, df_go_dtl, df_freshness, df_team_sm, df_relative_sm):
        self.sm_narrative = sm_narrative
        self.lm_narrative = lm_narrative
        self.df_go_dtl = df_go_dtl
        self.df_freshness = df_freshness
        self.df_team_sm = df_team_sm
        self.df_relative_sm = df_relative_sm
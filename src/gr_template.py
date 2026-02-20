from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    FrameBreak,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    NextPageTemplate,
    Paragraph
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
import pandas as pd

# sets game date & other team's name
opp = "Detroit Red Wings"
gd = "1/7/05"

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
        df_ib_period,
        intensity_note,
        load_note,
        ib_period_note
    ):
        self.report_name = report_name
        self.sm_narrative = sm_narrative
        self.lm_narrative = lm_narrative
        self.df_go_dtl = df_go_dtl
        self.df_freshness = df_freshness
        self.df_team_sm = df_team_sm
        self.df_relative_sm = df_relative_sm
        self.df_ib_period = df_ib_period
        self.intensity_note = intensity_note
        self.load_note = load_note
        self.ib_period_note = ib_period_note

    def _normalize_ib_period_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        period_ib.xlsx comes in with a 'header row' sitting in row 0:
          ['Date of DTE','PLAYER_NAME','Avg Supra Max Efforts', ...]
        and columns like ['Unnamed: 0','Unnamed: 1','Period1','Period2','Period3'].

        This function:
          - uses row 0 to rename columns properly
          - drops that row
          - converts fractions (0.8882) -> percent (88.82)
          - returns clean df with columns:
            Date of DTE, PLAYER_NAME, Period1 Avg Supra Max Efforts, ...
        """
        if df is None or df.empty:
            return pd.DataFrame()

        out = df.copy()

        # Detect the "row 0 contains headers" pattern
        if (
                "Period1" in out.columns
                and len(out) > 0
                and str(out.iloc[0].get("Period1", "")).strip().lower().startswith("avg supra")
        ):
            # build new column names from row0
            colmap = {}
            colmap[out.columns[0]] = str(out.iloc[0, 0]).strip()  # Date of DTE
            colmap[out.columns[1]] = str(out.iloc[0, 1]).strip()  # PLAYER_NAME

            for c in out.columns[2:]:
                # c is Period1/2/3; row0 cell is "Avg Supra Max Efforts"
                colmap[c] = f"{c} {str(out.loc[out.index[0], c]).strip()}"

            out = out.rename(columns=colmap).iloc[1:].reset_index(drop=True)

        return out

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

    def _lm_list_table_style(self):
        """
        Load-metrics list style:
        - no grid
        - no bold
        - slightly tighter font/padding so it fits cleanly
        """
        return TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("LEADING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 1),
                ("RIGHTPADDING", (0, 0), (-1, -1), 1),
                ("TOPPADDING", (0, 0), (-1, -1), 0.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )

    def load_metrics_decor(self, canvas, doc, divider_x):
        """Draw shared header elements + the vertical divider on the Load Metrics page."""
        self.metrics_table(canvas, doc)
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#1F6F8B"))
        canvas.setLineWidth(1.25)

        # Vertical divider between Freshness and Game Only DTL
        y0 = doc.bottomMargin + 0.15 * inch
        y1 = doc.pagesize[1] - doc.topMargin - 1.05 * inch
        canvas.line(divider_x, y0, divider_x, y1)

        canvas.restoreState()

    @staticmethod
    def _format_numeric(series: pd.Series, decimals: int = 2) -> pd.Series:
        vals = pd.to_numeric(series, errors="coerce").round(decimals)
        return vals.apply(lambda x: "" if pd.isna(x) else f"{x:.{decimals}f}")

    def _ensure_cols(self, df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
        """
        Ensure every expected column exists (prevents row-length mismatches in ReportLab tables).
        """
        out = df.copy()
        for c in cols:
            if c not in out.columns:
                out[c] = ""
        return out[cols]

    def go(self):
        leftMargin = 0.75 * inch
        rightMargin = 0.75 * inch
        bottomMargin = 0.75 * inch
        topMargin = 1.5 * inch  # header space for images/etc

        doc = BaseDocTemplate(
            f"../docs/{self.report_name}.pdf",
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

        lm_title_style = ParagraphStyle(
            "lm_title",
            parent=styles["BodyText"],
            fontName="Times-Bold",
            fontSize=14,
            leading=16,
            spaceAfter=4,
            spaceBefore=0,
        )
        lm_section_style = ParagraphStyle(
            "lm_section",
            parent=styles["BodyText"],
            fontName="Times-Bold",
            fontSize=10,
            leading=12,
            spaceAfter=4,
            spaceBefore=0,
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

        # Title band for the Load Metrics page
        lm_title_h = 0.7 * inch

        # Load Metrics page layout (Freshness gets more room)
        lm_gutter = 0.28 * inch
        lm_left_w = doc.width * 0.64
        lm_right_w = doc.width - lm_left_w - lm_gutter

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

        # --- Load Metrics page frames ---
        lm_title_frame = Frame(
            doc.leftMargin,
            y0 + (h - lm_title_h),
            doc.width,
            lm_title_h,
            id="lm_title",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        lm_left_frame = Frame(
            doc.leftMargin,
            y0,
            lm_left_w,
            h - lm_title_h,
            id="lm_left",
            showBoundary=0,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )

        lm_right_frame = Frame(
            doc.leftMargin + lm_left_w + lm_gutter,
            y0,
            lm_right_w,
            h - lm_title_h,
            id="lm_right",
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

        divider_x = doc.leftMargin + lm_left_w + (lm_gutter / 2)
        load_metrics_tpl = PageTemplate(
            id="LoadMetrics",
            frames=[lm_title_frame, lm_left_frame, lm_right_frame],
            onPage=lambda c, d: self.load_metrics_decor(c, d, divider_x),
        )

        one_col_load_tpl = PageTemplate(
            id="OneColLoad",
            frames=[onecol_main_frame, onecol_load_frame],
            onPage=self.metrics_table,
        )

        doc.addPageTemplates([two_col_tpl, load_metrics_tpl, one_col_tpl, one_col_load_tpl])

        # --------------------
        # Build tables for page 1
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
        # Build Load Metrics tables (final polish)
        #   - ensure consistent column counts (fixes misaligned rows)
        #   - plain header row (NOT bold)
        #   - balanced widths; name col wide enough for long names
        # --------------------
        # Freshness table
        desired_freshness_cols = ["PLAYER_NAME", "DTL", "CTL", "Freshness (7 day)", "Freshness (3 day)"]
        freshness_df = self._ensure_cols(self.df_freshness.copy(), desired_freshness_cols).fillna("")

        # Rename headers
        freshness_df = freshness_df.rename(columns={"Freshness (7 day)": "(7day)", "Freshness (3 day)": "(3day)"})
        # Format numeric columns (safe even if blank strings)
        for c in ["DTL", "CTL", "(7day)", "(3day)"]:
            if c in freshness_df.columns:
                freshness_df[c] = self._format_numeric(freshness_df[c], decimals=2)

        # Plain header row (blank name header)
        fr_headers = list(freshness_df.columns)
        fr_header_row = ["" if h == "PLAYER_NAME" else str(h) for h in fr_headers]
        fr_rows = [fr_header_row] + freshness_df.astype(str).values.tolist()

        # Column widths:
        # - Give name column more room so long names don't crush numeric columns
        # - Keep numeric columns evenly sized so they align cleanly
        fr_n = len(fr_headers)
        if fr_n <= 1:
            fr_col_widths = [lm_left_w]
        else:
            fr_name_w = lm_left_w * 0.50
            fr_rest_w = lm_left_w - fr_name_w
            fr_col_widths = [fr_name_w] + [fr_rest_w / (fr_n - 1)] * (fr_n - 1)

        freshness_tbl = Table(fr_rows, colWidths=fr_col_widths, repeatRows=0, splitByRow=1)
        freshness_tbl.setStyle(self._lm_list_table_style())
        # Align numeric columns centered; keep names left
        if fr_n > 1:
            freshness_tbl.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (1, 0), (-1, 0), "CENTER"),   # header labels
                        ("ALIGN", (1, 1), (-1, -1), "CENTER"), # numeric body
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),    # names
                    ]
                )
            )

        # --- Conditional formatting for (3day) to match the screenshot rules ---
        # Rules (priority order):
        # 1) <= -60 : red
        # 2) -30 to -20 : light
        # 3) -59.9 to 40 : orange (covers most values; placed last so it won't override #2)

        if "(3day)" in freshness_df.columns and "Freshness (3 day)" in self.df_freshness.columns:
            three_day_col_idx = list(freshness_df.columns).index("(3day)")
            three_vals = pd.to_numeric(self.df_freshness["Freshness (3 day)"], errors="coerce")

            red = colors.HexColor("#E53935")
            orange = colors.HexColor("#FB8C00")
            light = colors.HexColor("#F6C77A")  # light tan/orange

            # +1 offset due to header row in fr_rows
            for i, v in enumerate(three_vals, start=1):
                if pd.isna(v):
                    continue

                # 1) <= -60
                if v <= -60:
                    freshness_tbl.setStyle(
                        TableStyle([("BACKGROUND", (three_day_col_idx, i), (three_day_col_idx, i), red)])
                    )

                # 2) Between -30 and -20 (inclusive)
                elif -30 <= v <= -20:
                    freshness_tbl.setStyle(
                        TableStyle([("BACKGROUND", (three_day_col_idx, i), (three_day_col_idx, i), light)])
                    )

                # 3) Between -59.9 and 40 (inclusive)
                elif -59.9 <= v <= 40:
                    freshness_tbl.setStyle(
                        TableStyle([("BACKGROUND", (three_day_col_idx, i), (three_day_col_idx, i), orange)])
                    )

        # Game Only DTL table (keep it simple: PLAYER_NAME + Avg DTL)
        go_df = self.df_go_dtl.copy()
        desired_go_cols = ["PLAYER_NAME", "Avg DTL"]
        go_df = self._ensure_cols(go_df, desired_go_cols).fillna("")

        if "Avg DTL" in go_df.columns:
            go_df["Avg DTL"] = self._format_numeric(go_df["Avg DTL"], decimals=2)

        go_headers = list(go_df.columns)
        go_header_row = ["" if h == "PLAYER_NAME" else str(h) for h in go_headers]
        go_rows = [go_header_row] + go_df.astype(str).values.tolist()

        go_n = len(go_headers)
        if go_n <= 1:
            go_col_widths = [lm_right_w]
        else:
            go_name_w = lm_right_w * 0.78
            go_rest_w = lm_right_w - go_name_w
            go_col_widths = [go_name_w] + [go_rest_w / (go_n - 1)] * (go_n - 1)

        go_tbl = Table(go_rows, colWidths=go_col_widths, repeatRows=0, splitByRow=1)
        go_tbl.setStyle(self._lm_list_table_style())
        if go_n > 1:
            go_tbl.setStyle(
                TableStyle(
                    [
                        ("ALIGN", (1, 0), (-1, 0), "CENTER"),
                        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                        ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ]
                )
            )

        # --------------------
        # Story (Load Metrics LAST)
        # --------------------
        story = []

        # --- Page 1 (2-col) ---
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

        # --- SM narrative pages (OneColLoad) ---
        story.append(NextPageTemplate("OneColLoad"))
        story.append(PageBreak())
        story.append(Paragraph(self.sm_narrative, narrative_style))

        # Bottom load note band (last frame on that template)
        story.append(FrameBreak())
        story.append(Paragraph(f"<b>Load Note:</b> {self.load_note}", note_style))

        # --- Load Metrics page (LAST) ---
        story.append(NextPageTemplate("LoadMetrics"))
        story.append(PageBreak())

        story.append(Paragraph("- Load Metrics", lm_title_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.25,
                lineCap="round",
                color=colors.HexColor("#1F6F8B"),
                spaceBefore=2,
                spaceAfter=8,
            )
        )

        # Left column
        story.append(Paragraph("Freshness", lm_section_style))
        story.append(freshness_tbl)

        # Right column
        story.append(FrameBreak())
        story.append(Paragraph("Game Only DTL", lm_section_style))
        story.append(go_tbl)

        # LM narratives
        story.append(NextPageTemplate("OneCol"))
        story.append(PageBreak())
        story.append(Paragraph(self.lm_narrative, narrative_style))

        # --------------------
        # Period IB Table (New Page)
        # --------------------
        story.append(NextPageTemplate("OneCol"))
        story.append(PageBreak())

        story.append(Paragraph("- Intensity Band Distribution by Period", lm_title_style))
        story.append(
            HRFlowable(
                width="100%",
                thickness=1.25,
                lineCap="round",
                color=colors.HexColor("#1F6F8B"),
                spaceBefore=2,
                spaceAfter=8,
            )
        )

        period_df = self._normalize_ib_period_df(self.df_ib_period).fillna("")
        period_df = period_df.drop(columns=["Date of DTE"], errors="ignore")

        # Identify “Avg Supra Max” columns (after normalization they will match)
        color_cols = [c for c in period_df.columns if "Avg Supra Max" in str(c)]

        def _pct_num(v):
            """Return numeric percent (e.g. 0.8882 -> 88.82, 88.82 -> 88.82)."""
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return None
            s = str(v).strip()
            if s == "":
                return None
            if s.endswith("%"):
                s = s[:-1].strip()
            num = pd.to_numeric(s, errors="coerce")
            if pd.isna(num):
                return None
            if abs(num) <= 2:  # fraction
                num *= 100
            return float(num)

        def _pct_str(v):
            n = _pct_num(v)
            return "" if n is None else f"{n:.2f}%"

        # Build display df (with % strings)
        display_df = period_df.copy()
        for c in color_cols:
            display_df[c] = display_df[c].apply(_pct_str)

        # Wrap headers like snapshot: "Period2<br/>Avg Supra Max<br/>Efforts"
        wrapped_headers = []
        for c in display_df.columns:
            cc = str(c)
            if cc.startswith("Period") and "Avg Supra Max" in cc:
                p = cc.split(" ", 1)[0]  # Period2
                wrapped_headers.append(f"{p}<br/>Avg Supra Max<br/>Efforts")
            else:
                wrapped_headers.append(cc)

        period_data = [wrapped_headers] + display_df.astype(str).values.tolist()
        period_data = self.wrap_table_header(period_data)

        # --- Column widths (fixed, names first) ---
        ncols = len(display_df.columns)
        name_w = doc.width * 0.28  # tweak 0.26–0.32 if you want
        per_w = (doc.width - name_w) / (ncols - 1)
        col_widths = [name_w] + [per_w] * (ncols - 1)

        period_tbl = Table(period_data, colWidths=col_widths, repeatRows=1, splitByRow=1)
        period_tbl.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("ALIGN", (1, 0), (-1, 0), "CENTER"),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        # Conditional formatting rules (per your screenshot)
        red = colors.HexColor("#E53935")  # > 100
        orange = colors.HexColor("#FB8C00")  # 80–100
        yellow = colors.HexColor("#FBC02D")  # 60–80
        green = colors.HexColor("#5CB85C")  # < 60

        for c in color_cols:
            col_idx = list(period_df.columns).index(c)
            for r in range(len(period_df)):
                v = _pct_num(period_df.iloc[r][c])
                if v is None:
                    continue

                if v > 100:
                    bg = red
                elif 80 <= v <= 100:
                    bg = orange
                elif 60 <= v < 80:
                    bg = yellow
                else:
                    bg = green

                period_tbl.setStyle(TableStyle([("BACKGROUND", (col_idx, r + 1), (col_idx, r + 1), bg)]))

        story.append(period_tbl)

        #  Intensity band by period note
        story.append(Spacer(1, inch/2))
        story.append(Paragraph(f"<b>Intensity Band Distribution by Period:</b> {self.ib_period_note}", note_style))

        doc.build(story)
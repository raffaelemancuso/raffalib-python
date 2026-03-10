import docx
from docx import Document
from docx.shared import Pt, RGBColor, Mm
from docx.oxml.ns import qn
from docx.enum.text import WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.enum.section import WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from dataclasses import dataclass
from pathlib import Path


class DocxFile:
    def __init__(
        self,
        page_height: float = 210,
        page_width: float = 297,
        landscape: bool = False,
        left_margin: float = 25.4,
        right_margin: float = 25.4,
        top_margin: float = 25.4,
        bottom_margin: float = 25.4,
        heading_text: str | None = None,
        heading_font_name: str = "Aptos",
        heading_font_size: int = 12,
        heading_bold: bool = True,
        heading_italic: bool = False,
        heading_underline: bool = False,
        heading_color: [int, int, int] = (0x00, 0x00, 0x00),
        heading_space_before: int = 0,
        heading_space_after: int = 6,
    ):

        # create new document
        self.doc = Document()

        # Page layout
        section = self.doc.sections[0]
        if landscape:
            self.page_height = page_height
            self.page_width = page_width
            section.orientation = WD_ORIENT.LANDSCAPE
        else:
            self.page_height = page_width
            self.page_width = page_height
            section.orientation = WD_ORIENT.PORTRAIT
            
        section.page_height = Mm(self.page_height)
        section.page_width = Mm(self.page_width)
            
        # Page margins
        section.left_margin = Mm(left_margin)
        section.right_margin = Mm(right_margin)
        section.top_margin = Mm(top_margin)
        section.bottom_margin = Mm(bottom_margin)
        section.header_distance = Mm(12.7)
        section.footer_distance = Mm(12.7)

        # Add section heading
        if heading_text:
            # Add heading
            self.doc.add_heading(heading_text)

            # Set style of the header
            style = self.doc.styles["Heading 1"]

            font = style.font

            font.name = heading_font_name
            # Setting the style of the header requires this additional workaround
            # see: https://stackoverflow.com/a/60922725/1719931
            rFonts = style.element.rPr.rFonts
            rFonts.set(qn("w:asciiTheme"), heading_font_name)

            font.size = Pt(heading_font_size)
            font.bold = heading_bold
            font.italic = heading_italic
            font.underline = heading_underline

            font.color.rgb = RGBColor(*heading_color)

            paragraph_format = style.paragraph_format
            paragraph_format.space_before = Pt(heading_space_before)
            paragraph_format.space_after = Pt(heading_space_after)
            paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    
        self.table = None

    def add_table(
        self,
        n_rows,
        n_cols,
        table_autofit: bool = True,
        table_style: str = "Table Grid",
        table_font_name: str = "Aptos",
        table_font_size: int = 12,
        table_header_font_name: str = "Aptos",
        table_header_font_size: int = 12,
        table_header_font_bold: bool = True,
    ):

        # Create table
        self.table_autofit = table_autofit
        self.table = self.doc.add_table(n_rows, n_cols)

        # Set table style
        # See: https://github.com/python-openxml/python-docx/issues/9
        self.table.style = table_style

        # Create style for table header (first row)
        style = self.doc.styles.add_style("CellHeader", WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = self.doc.styles["Normal"]
        font = style.font
        font.name = table_header_font_name
        font.size = Pt(table_header_font_size)
        font.bold = table_header_font_bold

        # Create style for table cells (second row onwards)
        style = self.doc.styles.add_style("CellText", WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = self.doc.styles["Normal"]
        font = style.font
        font.name = table_font_name
        font.size = Pt(table_font_size)

    # Additional workaround to make autofit actually work
    # See: https://github.com/python-openxml/python-docx/issues/209#issuecomment-566128709
    def _table_autofit_hotfix(self):
        for column in self.table.columns:
            for cell in column.cells:
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                tcW = tcPr.get_or_add_tcW()
                tcW.type = "auto"

    def save(self, outfp: Path):
        
        if self.table:
            # Hotfix for table autofit
            if self.table_autofit:
                self._table_autofit_hotfix()

            # Set table text style for header (row 0)
            for cell in self.table.rows[0].cells:
                for paragraph in cell.paragraphs:
                    paragraph.style = "CellHeader"

            # Set table text style for data cells (rows >= 1)
            for row in self.table.rows[1:]:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        paragraph.style = "CellText"  # assuming style named "Cell Text"

        # save the doc
        self.doc.save(outfp)

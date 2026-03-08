import docx
from docx import Document
from docx.shared import Pt, RGBColor, Mm
from docx.oxml.ns import qn
from docx.enum.text import WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.enum.section import WD_ORIENT
from dataclasses import dataclass

@dataclass
class DocxOptions:
    page_height = 210
    page_width = 297
    landscape = False
    left_margin = 25.4
    right_margin = 25.4
    top_margin = 25.4
    bottom_margin = 25.4
    heading_text:str|None = None
    heading_font_name:str = "Aptos"
    heading_font_size = 12
    heading_bold = True
    heading_italic = False
    heading_underline = False
    heading_color = (0x00, 0x00, 0x00)
    heading_space_before = 0
    heading_space_after = 6
    
def prepare_docx(options:DocxOptions):
    
    # create new document
    doc = Document()
    
    # Page layout
    section = doc.sections[0]
    if options.landscape:
        section.page_height = Mm(options.page_height)
        section.page_width = Mm(options.page_width)
        section.orientation = WD_ORIENT.LANDSCAPE

    else:
        section.page_height = Mm(options.page_width)
        section.page_width = Mm(options.page_height)
        section.orientation = WD_ORIENT.PORTRAIT
    
    section.left_margin = Mm(options.left_margin)
    section.right_margin = Mm(options.right_margin)
    section.top_margin = Mm(options.top_margin)
    section.bottom_margin = Mm(options.bottom_margin)
    section.header_distance = Mm(12.7)
    section.footer_distance = Mm(12.7)

    # Add section heading
    if options.heading_text:
        
        # Add heading
        doc.add_heading(options.heading_text)

        # Set style of the header
        style = doc.styles["Heading 1"]

        font = style.font

        font.name = options.heading_font_name
        # Setting the style of the header requires this additional workaround
        # see: https://stackoverflow.com/a/60922725/1719931
        rFonts = style.element.rPr.rFonts
        rFonts.set(qn("w:asciiTheme"), options.heading_font_name)

        font.size = Pt(options.heading_font_size)
        font.bold = options.heading_bold
        font.italic = options.heading_italic
        font.underline = options.heading_underline

        font.color.rgb = RGBColor(*options.heading_color)

        paragraph_format = style.paragraph_format
        paragraph_format.space_before = Pt(options.heading_space_before)
        paragraph_format.space_after = Pt(options.heading_space_after)
    paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    
    return doc
     
# Additional workaround to make autofit actually work
# See: https://github.com/python-openxml/python-docx/issues/209#issuecomment-566128709
def set_autofit(doc: Document) -> Document:
    """
    Hotfix for autofit.
    """
    for t_idx, table in enumerate(doc.tables):
        doc.tables[t_idx].autofit = True
        doc.tables[t_idx].allow_autofit = True
        doc.tables[t_idx]._tblPr.xpath("./w:tblW")[0].attrib[
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type"
        ] = "auto"
        for row_idx, r_val in enumerate(doc.tables[t_idx].rows):
            for cell_idx, c_val in enumerate(
                doc.tables[t_idx].rows[row_idx].cells
            ):
                doc.tables[t_idx].rows[row_idx].cells[
                    cell_idx
                ]._tc.tcPr.tcW.type = "auto"
                doc.tables[t_idx].rows[row_idx].cells[
                    cell_idx
                ]._tc.tcPr.tcW.w = 0
    return doc
"""Build the two books from editable Markdown; no network access is needed."""
from pathlib import Path
import re,html,textwrap
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,Table,TableStyle,Flowable,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
FONT=Path('/usr/share/fonts/truetype/dejavu')
# Override FONT_DIR on systems whose DejaVu fonts are installed elsewhere.
import os
FONT=Path(os.environ.get('FONT_DIR',str(FONT)))
for name,file in [('BookSerif','DejaVuSerif.ttf'),('BookSerifBold','DejaVuSerif-Bold.ttf'),('BookSans','DejaVuSans.ttf'),('BookSansBold','DejaVuSans-Bold.ttf'),('BookMono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT/file)))
pdfmetrics.registerFontFamily('BookSerif',normal='BookSerif',bold='BookSerifBold',italic='BookSerif',boldItalic='BookSerifBold')
pdfmetrics.registerFontFamily('BookSans',normal='BookSans',bold='BookSansBold',italic='BookSans',boldItalic='BookSansBold')
INK=colors.HexColor('#142B3A');TEAL=colors.HexColor('#147C80');PALE=colors.HexColor('#F0F5F5');GRAY=colors.HexColor('#51606B')
W,H=576,720; M=48; CONTENT=W-2*M
styles={
 'body':ParagraphStyle('body',fontName='BookSerif',fontSize=10.2,leading=15.4,textColor=INK,spaceAfter=9),
 'h1':ParagraphStyle('h1',fontName='BookSansBold',fontSize=23,leading=28,textColor=INK,spaceAfter=18),
 'h2':ParagraphStyle('h2',fontName='BookSansBold',fontSize=13,leading=18,textColor=TEAL,spaceBefore=12,spaceAfter=8,keepWithNext=True),
 'small':ParagraphStyle('small',fontName='BookSans',fontSize=8.1,leading=12,textColor=GRAY,spaceAfter=7),
 'cell':ParagraphStyle('cell',fontName='BookSans',fontSize=8.1,leading=11.5,textColor=INK),
 'cellhead':ParagraphStyle('cellhead',fontName='BookSansBold',fontSize=8.1,leading=11.5,textColor=colors.white),
 'toc':ParagraphStyle('toc',fontName='BookSans',fontSize=9.1,leading=12.5,spaceBefore=0,leftIndent=0,firstLineIndent=0,textColor=INK),
}
def inline(s):
    s=html.escape(s)
    s=re.sub(r'`([^`]+)`',lambda m:'<font name="BookMono" size="8.7">'+m.group(1)+'</font>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    return s

class Code(Flowable):
    def __init__(self,source,lines=None):
        super().__init__(); self.source=source
        self.lines=[] if lines is None else lines
        if lines is None:
            for line in source.splitlines():
                indent=len(line)-len(line.lstrip())
                wrapped=textwrap.wrap(line,width=99,replace_whitespace=False,drop_whitespace=False,subsequent_indent=' '*(min(indent,12)+2)+'↪ ',break_long_words=True,break_on_hyphens=False) or ['']
                self.lines.extend(wrapped)
        self.height=len(self.lines)*10.3+20
    def wrap(self,availW,availH):self.width=availW;return availW,self.height
    def split(self,availW,availH):
        if self.height<=550:return []
        n=int((availH-20)/10.3)
        if n<3:return []
        if n>=len(self.lines):return [self]
        return [Code(self.source,self.lines[:n]),Code(self.source,self.lines[n:])]
    def draw(self):
        c=self.canv;c.setFillColor(PALE);c.roundRect(0,0,self.width,self.height,5,fill=1,stroke=0)
        c.setStrokeColor(TEAL);c.setLineWidth(2);c.line(0,5,0,self.height-5)
        c.setFillColor(INK);c.setFont('BookMono',7.45)
        for i,line in enumerate(self.lines):c.drawString(10,self.height-15-i*10.3,line)

class ModelDiagram(Flowable):
    def wrap(self,availW,availH):self.width=availW;self.height=172;return availW,self.height
    def draw(self):
        c=self.canv
        def box(x,y,title,detail):
            c.setFillColor(PALE);c.setStrokeColor(TEAL);c.roundRect(x,y,132,48,5,fill=1,stroke=1)
            c.setFillColor(INK);c.setFont('BookSansBold',9);c.drawCentredString(x+66,y+29,title)
            c.setFont('BookSans',7.3);c.drawCentredString(x+66,y+14,detail)
        def arrow(x1,y1,x2,y2,label,lx,ly):
            c.setStrokeColor(TEAL);c.setLineWidth(1.2);c.line(x1,y1,x2,y2)
            if y1==y2:c.line(x2-5,y2+3,x2,y2);c.line(x2-5,y2-3,x2,y2)
            else:c.line(x2-3,y2+5,x2,y2);c.line(x2+3,y2+5,x2,y2)
            c.setFillColor(GRAY);c.setFont('BookSans',7);c.drawCentredString(lx,ly,label)
        box(0,110,'Encounter record','Information content')
        box(174,110,'Hospital encounter','Process')
        box(348,110,'Patient','Person / object')
        box(0,20,'Code concept','Recorded terminology')
        arrow(132,134,174,134,'documents',153,143)
        arrow(306,134,348,134,'hasPatient',327,143)
        arrow(66,110,66,68,'primaryCode',105,87)
        c.setFillColor(GRAY);c.setFont('BookSans',7.4)
        c.drawString(174,48,'The record describes an event.')
        c.drawString(174,34,'Its code is not the person or a disease episode.')

class Book(BaseDocTemplate):
    def __init__(self,path,title,subtitle):
        super().__init__(str(path),pagesize=(W,H),leftMargin=M,rightMargin=M,topMargin=57,bottomMargin=57,
            title=title,author='Joe Hoeller',subject=subtitle,allowSplitting=True)
        self.booktitle=title;self.chapter='Title page';self._chapter_index=0
        frame=Frame(M,57,CONTENT,H-114,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='book',frames=[frame],onPage=self.header,onPageEnd=self.footer))
    def beforeDocument(self):self.chapter='Title page';self._chapter_index=0
    def header(self,c,doc):
        if doc.page>1:
            c.saveState();c.setFillColor(GRAY);c.setFont('BookSans',7.5)
            c.drawString(M,H-30,self.booktitle.upper())
            c.setStrokeColor(colors.HexColor('#D6E2E5'));c.line(M,H-39,W-M,H-39);c.restoreState()
    def footer(self,c,doc):
        c.saveState();c.setStrokeColor(colors.HexColor('#D6E2E5'));c.line(M,43,W-M,43)
        text='© 2026 Joe Hoeller, AI Systems & Enterprise Knowledge Engineer | '+self.chapter
        size=7.1
        while pdfmetrics.stringWidth(text,'BookSans',size)>CONTENT-25:size-=0.1
        c.setFont('BookSans',size);c.setFillColor(GRAY);c.drawString(M,29,text)
        c.setFont('BookSans',8);c.drawRightString(W-M,29,str(doc.page));c.restoreState()
    def afterFlowable(self,flow):
        if hasattr(flow,'chapter_title'):
            self.chapter=flow.chapter_title
            key=flow.bookmark
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(self.chapter,key,0,False)
            self.notify('TOCEntry',(0,self.chapter,self.page,key))
        elif hasattr(flow,'running_title'):self.chapter=flow.running_title

def blocks(markdown):
    lines=markdown.splitlines(); result=[];i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line=='[MODEL_DIAGRAM]':result.extend([ModelDiagram(),Spacer(1,10)]);i+=1;continue
        if line.startswith('```'):
            source=[];i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):source.append(lines[i]);i+=1
            result.extend([Code('\n'.join(source)),Spacer(1,10)]);i+=1;continue
        if line.startswith('## '):result.append(Paragraph(inline(line[3:]),styles['h2']));i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.match(r'^:?-+:?$',c.replace(' ','')) for c in cells):rows.append(cells)
                i+=1
            n=max(len(x) for x in rows)
            widths=[CONTENT/n]*n
            if n==3:widths=[CONTENT*.27,CONTENT*.32,CONTENT*.41]
            if n==4:widths=[CONTENT*.24,CONTENT*.20,CONTENT*.26,CONTENT*.30]
            data=[[Paragraph(inline(c),styles['cellhead'] if ri==0 else styles['cell']) for c in row] for ri,row in enumerate(rows)]
            table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),INK),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),('LINEBELOW',(0,0),(-1,-1),0.3,colors.HexColor('#D3E0E3'))]))
            if table.wrap(CONTENT,1000)[1]<=330:
                group=[table]
                if result and isinstance(result[-1],Paragraph) and result[-1].style.name=='h2':group.insert(0,result.pop())
                result.append(KeepTogether(group))
            else:result.append(table)
            result.append(Spacer(1,12));continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].strip().startswith(('## ','```','|')):
            paragraph.append(lines[i].strip());i+=1
        result.append(Paragraph(inline(' '.join(paragraph)),styles['body']))
    return result

def load_chapters(path):
    chapters=[]; current=None; fenced=False; seen_title=False
    for line in path.read_text().splitlines():
        if line.startswith('```'):fenced=not fenced
        if line.startswith('# ') and not fenced:
            if not seen_title:seen_title=True;continue
            current={'title':line[2:].strip(),'lines':[]};chapters.append(current)
        elif current is not None:current['lines'].append(line)
    return [{'title':x['title'],'body':'\n'.join(x['lines'])} for x in chapters]

def build(filename,source,title,subtitle,label):
    chapters=load_chapters(ROOT/'book'/source);doc=Book(ROOT/filename,title,subtitle)
    story=[Spacer(1,38),Paragraph('OPEN KNOWLEDGE ENGINEERING · 2026 EDITION',styles['small']),Spacer(1,19),
      Paragraph(title,ParagraphStyle('cover',fontName='BookSansBold',fontSize=37,leading=44,textColor=INK)),Spacer(1,22),
      Paragraph(subtitle,ParagraphStyle('sub',fontName='BookSerif',fontSize=20,leading=29,textColor=TEAL)),Spacer(1,36),
      Paragraph(label,styles['body']),Spacer(1,30),Paragraph('Joe Hoeller<br/>AI Systems &amp; Enterprise Knowledge Engineer',styles['body']),
      Spacer(1,30),Paragraph('Healthcare learning edition<br/>Real source data · SKOS alignment · BFO · OWL DL<br/>Enterprise products, evidence and adoption',styles['small']),PageBreak()]
    h=Paragraph('Contents',styles['h1']);h.running_title='Contents';story.append(h)
    story.append(Paragraph('Chapter titles and page numbers are linked. The outline panel provides another route through the book.',styles['small']))
    toc=TableOfContents();toc.levelStyles=[styles['toc']];story.append(toc)
    for index,ch in enumerate(chapters,1):
        story.append(PageBreak());story.append(Paragraph(f'CHAPTER {index:02d}',styles['small']))
        h=Paragraph(inline(ch['title']),styles['h1']);h.chapter_title=ch['title'];h.bookmark=f'chapter-{index}'
        story.append(h);story.extend(blocks(ch['body']))
    doc.multiBuild(story)
    print(filename,'chapters',len(chapters))

if __name__=='__main__':
    build('Enterprise_Ontology_Engineering_Primer_Tutorial.pdf','Enterprise_Ontology_Engineering_Primer.md',
          'Enterprise Ontology Engineering','From source records to governed reasoning',
          'A practical book for designing meaning, aligning taxonomies and operating an enterprise knowledge product.')
    build('Enterprise_Ontology_Engineering_Lab_Workbook.pdf','Enterprise_Ontology_Engineering_Lab_Workbook.md',
          'Enterprise Ontology Lab Workbook','Build, query, reason and explain',
          'Twenty-five notebook walkthroughs with learner exercises, separate solutions and a complete healthcare capstone.')

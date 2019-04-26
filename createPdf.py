#!/usr/bin/env python3
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table
from reportlab.lib.styles import getSampleStyleSheet
from redminelib import Redmine


# issuesTab = [11433, 11466, 11508]
# numberOfIssues = len(issuesTab)

# # def createPDF(issuesTab)
# data = [numberOfissues+1][4]

# for issue in issuesTab:

 
doc = SimpleDocTemplate("ClientName.pdf", pagesize=letter)
# container for the 'Flowable' objects
elements = []
 
styleSheet = getSampleStyleSheet()
 
I = Image('logo.png')
I.drawHeight = 1.25*inch*I.drawHeight / I.drawWidth
I.drawWidth = 1.25*inch

P0 = Paragraph('''
               <b>A pa<font color=red>r</font>a<i>graph</i></b>
               <super><font color=yellow>1</font></super>''',
               styleSheet["BodyText"])

P = Paragraph('''
    <para align=center spaceb=3>The <b>ReportLab Left
    <font color=red>Logo</font></b>
    Image</para>''',
    styleSheet["BodyText"])

data= [['Issue', 'Title and description', 'Priority', 'Linked tickets'],
       ['00', [P,P0], '01',  '04'],
       ['10', [P,P0], '11',  '14'],
       ['20', [P,P0], '21',  '24']]
 
t=Table(data,style=[('GRID',(1,1),(-2,-2),1,colors.green),
                    ('BOX',(0,0),(1,-1),2,colors.red),
                    ('LINEABOVE',(1,2),(-2,2),1,colors.blue),
                    ('LINEBEFORE',(2,1),(2,-2),1,colors.pink),
                    ('BACKGROUND', (0, 0), (3, 0), colors.grey),
                    ('BOX',(0,0),(-1,-1),2,colors.black),
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    ('VALIGN',(3,0),(3,0),'BOTTOM'),
                    ('ALIGN',(3,1),(3,1),'CENTER'),
                    ('ALIGN',(3,2),(3,2),'LEFT'),
])
t._argW[3]=1.5*inch
 
elements.append(t)
# write the document to disk
doc.build(elements)
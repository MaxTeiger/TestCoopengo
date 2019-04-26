# Sample platypus document
# From the FAQ at reportlab.org/oss/rl-toolkit/faq/#1.1

import os
import urllib2
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

issuesTab = [11433, 11466, 11508]

Title = "Report for [CLIENT_NAME]"
pageinfo = "platypus example"

REDMINE_URL = 'https://support.coopengo.com'
REDMINE_TOKEN = os.environ['REDMINE_TOKEN']

# retrieve the logo from the current  folder or from internet
filename = './logo.png'
def getCoopengoLogo():
    # """ Get a python logo image for this example """
    if not os.path.exists(filename):
        response = urllib2.urlopen('https://media.licdn.com/dms/image/C4E0BAQG0YKYFxxoO-w/company-logo_200_200/0?e=2159024400&v=beta&t=6xHe9hFM2bM2jd3vYN4BhZ4QQRcXcodMnwR6TSiZcl0')
        f = open(filename, 'w')
        f.write(response.read())
        f.close()

# Define a template for the first page of the PDF 
def myFirstPage(canvas, doc):

    getCoopengoLogo()

    canvas.drawImage(filename, PAGE_WIDTH-100, PAGE_HEIGHT - 100, width=100, height=100) # Who needs consistency?
    canvas.saveState()
    canvas.setFont('Helvetica',16)
    canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-108, Title)
    canvas.setFont('Times-Roman',9)
    canvas.drawString(inch, 0.75 * inch,"First Page / %s" % pageinfo)
    canvas.restoreState()

# Define a template for the later pages of the PDF
def myLaterPages(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, 0.75 * inch,"Page %d %s" % (doc.page, pageinfo))
    canvas.restoreState()

# This function must return at least two tables, one for bugs and one for features
def returnTables():
    return 1

def go():
    doc = SimpleDocTemplate("ClientReport.pdf")
    Story = [Spacer(1,2*inch)]
    style = styles["Normal"]

    bogustext = "1. Fonctionnalites\n\n"

    p = Paragraph(bogustext, style)
    Story.append(p)
    Story.append(Spacer(1,0.2*inch))


    # Create a function that returns two tables from issues 

    data= [['Issue', 'Title and description', 'Priority', 'Linked tickets'],
       ['00', 'Test', '01',  '04'],
       ['10', '[P,P0]', '11',  '14'],
       ['20', '[P,P0]', '21',  '24']]
 
    t=Table(data,style=[
                    ('BACKGROUND', (0, 0), (3, 0), colors.grey),
                    ('GRID',(0,0),(-1,-1),0.5,colors.black),
                    ('VALIGN',(3,0),(3,0),'BOTTOM'),
                    ('ALIGN',(0,0),(3,0),'CENTER'),
                    ('ALIGN',(1,1),(-1,-1),'LEFT'),
    ])
    
    t._argW[1]=PAGE_WIDTH/1.5

    Story.append(t)

    bogustext = "2. Anomalies\n\n"
    Story.append(Spacer(1,0.4*inch))


    p = Paragraph(bogustext, style)
    Story.append(p)
    Story.append(Spacer(1,0.2*inch))
    Story.append(t)
    Story.append(Spacer(1,0.4*inch))

    p = Paragraph("3. Installation", style)
    Story.append(p)

    p

    doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)
    
if __name__ == "__main__":
    go()

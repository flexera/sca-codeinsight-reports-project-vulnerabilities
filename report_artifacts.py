'''
Copyright 2020 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Fri Aug 07 2020
File : report_artifacts.py
'''

import logging
import os
from datetime import datetime
import base64

logger = logging.getLogger(__name__)

#--------------------------------------------------------------------------------#
def create_report_artifacts(reportData):
    logger.info("Entering create_report_artifacts")

    # Dict to hold the complete list of reports
    reports = {}

    htmlFile = generate_html_report(reportData)
    
    reports["viewable"] = htmlFile
    reports["allFormats"] = [htmlFile]

    logger.info("Exiting create_report_artifacts")
    
    return reports 


#------------------------------------------------------------------#
def generate_html_report(reportData):
    logger.info("    Entering generate_html_report")


    reportName = reportData["reportName"]
    projectName  = reportData["projectName"]
    projectID  = reportData["projectID"]
    baseURL  = reportData["baseURL"]
    vulnerabilityData = reportData["vulnerabilityData"]
    
    scriptDirectory = os.path.dirname(os.path.realpath(__file__))
    cssFile =  os.path.join(scriptDirectory, "html-assets/css/revenera_common.css")
    logoImageFile =  os.path.join(scriptDirectory, "html-assets/images/logo_reversed.svg")
    iconFile =  os.path.join(scriptDirectory, "html-assets/images/favicon-revenera.ico")
    statusApprovedIcon = os.path.join(scriptDirectory, "html-assets/images/status_approved_selected.png")
    statusRejectedIcon = os.path.join(scriptDirectory, "html-assets/images/status_rejected_selected.png")
    statusDraftIcon = os.path.join(scriptDirectory, "html-assets/images/status_draft_ready_selected.png")

    logger.debug("cssFile: %s" %cssFile)
    logger.debug("imageFile: %s" %logoImageFile)
    logger.debug("iconFile: %s" %iconFile)
    logger.debug("statusApprovedIcon: %s" %statusApprovedIcon)
    logger.debug("statusRejectedIcon: %s" %statusRejectedIcon)
    logger.debug("statusDraftIcon: %s" %statusDraftIcon)


    #########################################################
    #  Encode the image files
    encodedLogoImage = encodeImage(logoImageFile)
    encodedfaviconImage = encodeImage(iconFile)
    encodedStatusApprovedIcon = encodeImage(statusApprovedIcon)
    encodedStatusRejectedIcon = encodeImage(statusRejectedIcon)
    encodedStatusDraftIcon = encodeImage(statusDraftIcon)

    # Grab the current date/time for report date stamp
    now = datetime.now().strftime("%B %d, %Y at %H:%M:%S")

    htmlFile = reportName + ".html"
    logger.debug("htmlFile: %s" %htmlFile)

    #---------------------------------------------------------------------------------------------------
    # Create a simple HTML file to display
    #---------------------------------------------------------------------------------------------------
    try:
        html_ptr = open(htmlFile,"w")
    except:
        logger.error("Failed to open htmlfile %s:" %htmlFile)
        raise

    html_ptr.write("<html>\n") 
    html_ptr.write("    <head>\n")

    html_ptr.write("        <!-- Required meta tags --> \n")
    html_ptr.write("        <meta charset='utf-8'>  \n")
    html_ptr.write("        <meta name='viewport' content='width=device-width, initial-scale=1, shrink-to-fit=no'> \n")

    html_ptr.write(''' 
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.1/css/bootstrap.min.css" integrity="sha384-VCmXjywReHh4PwowAiWNagnWcLhlEJLA5buUprzK8rxFgeH0kww/aWY76TfkUoSX" crossorigin="anonymous">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/dataTables.bootstrap4.min.css">
    ''')


    html_ptr.write("        <style>\n")

    # Add the contents of the css file to the head block
    try:
        f_ptr = open(cssFile)
        logger.debug("Adding css file details")
        for line in f_ptr:
            html_ptr.write("            %s" %line)
        f_ptr.close()
    except:
        logger.error("Unable to open %s" %cssFile)
        print("Unable to open %s" %cssFile)

    html_ptr.write("        </style>\n")  

    html_ptr.write("    	<link rel='icon' type='image/png' href='data:image/png;base64, {}'>\n".format(encodedfaviconImage.decode('utf-8')))
    html_ptr.write("        <title>%s</title>\n" %(reportName.upper()))
    html_ptr.write("    </head>\n") 

    html_ptr.write("<body>\n")
    html_ptr.write("<div class=\"container-fluid\">\n")

    #---------------------------------------------------------------------------------------------------
    # Report Header
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN HEADER -->\n")
    html_ptr.write("<div class='header'>\n")
    html_ptr.write("  <div class='logo'>\n")
    html_ptr.write("    <img src='data:image/svg+xml;base64,{}' style='width: 400px;'>\n".format(encodedLogoImage.decode('utf-8')))
    html_ptr.write("  </div>\n")
    html_ptr.write("<div class='report-title'>%s</div>\n" %reportName)
    html_ptr.write("</div>\n")
    html_ptr.write("<!-- END HEADER -->\n")

    #---------------------------------------------------------------------------------------------------
    # Body of Report
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN BODY -->\n")  

    html_ptr.write("<table id='inventoryData' class='table table-hover table-sm row-border' style='width:90%'>\n")

    html_ptr.write("    <thead>\n")
    html_ptr.write("        <tr>\n")
    html_ptr.write("            <th colspan='7' class='text-center'><h4>%s</h4></th>\n" %projectName) 
    html_ptr.write("        </tr>\n") 
    html_ptr.write("        <tr>\n") 
    html_ptr.write("            <th style='width: 15%' class='text-center'>VULNERABILITY</th>\n") 
    html_ptr.write("            <th style='width: 20%' class='text-center'>COMPONENT</th>\n") 
    html_ptr.write("            <th style='width: 5%' class='text-center'>SCORE</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>SEVERITY</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>SOURCE</th>\n")
    html_ptr.write("            <th style='width: 50%' class='text-center'>DESCRIPTION</th>\n") 
    html_ptr.write("        </tr>\n")
    html_ptr.write("    </thead>\n")  
    html_ptr.write("    <tbody>\n")  

    for inventoryID in reportData["vulnerabilityData"]:

        componentName = reportData["vulnerabilityData"][inventoryID]["componentName"]
        componentVersionName = reportData["vulnerabilityData"][inventoryID]["componentVersionName"]

        inventoryItemLink = reportData["baseURL"] + '''/codeinsight/FNCI#myprojectdetails/?id=''' + reportData["projectID"] + '''&tab=projectInventory&pinv=''' + str(inventoryID)

        for vulnerabilityName in reportData["vulnerabilityData"][inventoryID]["vulnerabilities"]:

            vulnerabilityDescription = reportData["vulnerabilityData"][inventoryID]["vulnerabilities"][vulnerabilityName][0]
            vulnerabilitySource = reportData["vulnerabilityData"][inventoryID]["vulnerabilities"][vulnerabilityName][1]
            vulnerabilityUrl = reportData["vulnerabilityData"][inventoryID]["vulnerabilities"][vulnerabilityName][2]
            vulnerabilityCvssV2Score = reportData["vulnerabilityData"][inventoryID]["vulnerabilities"][vulnerabilityName][3]
            vulnerabilityCvssV2Severity = reportData["vulnerabilityData"][inventoryID]["vulnerabilities"][vulnerabilityName][4]
            vulnerabilityCvssV3Score = reportData["vulnerabilityData"][inventoryID]["vulnerabilities"][vulnerabilityName][5]

            if vulnerabilityCvssV3Score == "N/A":
                vulnerabilityCvssV3Score = "-"
            
            vulnerabilityCvssV3Severity = reportData["vulnerabilityData"][inventoryID]["vulnerabilities"][vulnerabilityName][6]

            html_ptr.write("<td style=\"vertical-align:middle\"><a href=\"%s\" target=\"_blank\">%s</a></td>\n" %(vulnerabilityUrl, vulnerabilityName))
            html_ptr.write("<td style=\"vertical-align:middle\"><a href=\"%s\" target=\"_blank\">%s - %s</a></td>\n" %(inventoryItemLink, componentName, componentVersionName))
            html_ptr.write("<td style=\"vertical-align:middle\" data-order=\"%s\"> <span class=\"btn btn-%s\">%s</span></td>\n" %(vulnerabilityCvssV3Score, vulnerabilityCvssV3Severity.lower(), vulnerabilityCvssV3Score))
            html_ptr.write("<td style=\"vertical-align:middle\">%s</td>\n" %vulnerabilityCvssV3Severity)

            
            html_ptr.write("<td style=\"vertical-align:middle\">%s</td>\n" %vulnerabilitySource)
            html_ptr.write("<td style=\"vertical-align:middle\">%s </div> </td>\n" %vulnerabilityDescription)

            html_ptr.write("</tr>\n")


    html_ptr.write("    </tbody>\n")


    html_ptr.write("</table>\n")  

    html_ptr.write("<!-- END BODY -->\n")  

    #---------------------------------------------------------------------------------------------------
    # Report Footer
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN FOOTER -->\n")
    html_ptr.write("<div class='report-footer'>\n")
    html_ptr.write("  <div style='float:left'>&copy; 2020 Flexera</div>\n")
    html_ptr.write("  <div style='float:right'>Generated on %s</div>\n" %now)
    html_ptr.write("</div>\n")
    html_ptr.write("<!-- END FOOTER -->\n")   

    html_ptr.write("</div>\n")

    #---------------------------------------------------------------------------------------------------
    # Add javascript 
    #---------------------------------------------------------------------------------------------------

    html_ptr.write('''

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>  
    <script src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script> 
    ''')


    html_ptr.write('''
        <script>
            var table = $('#inventoryData').DataTable({"order": [[ 2, "desc" ]]});

            $(document).ready(function() {
                table;
            } );

        </script>


        ''')


    html_ptr.write("</body>\n") 
    html_ptr.write("</html>\n") 
    html_ptr.close() 

    logger.info("    Exiting generate_html_report")
    return htmlFile


####################################################################
def encodeImage(imageFile):

    #############################################
    # Create base64 variable for branding image
    try:
        with open(imageFile,"rb") as image:
            logger.debug("Encoding image: %s" %imageFile)
            encodedImage = base64.b64encode(image.read())
            return encodedImage
    except:
        logger.error("Unable to open %s" %imageFile)
        raise
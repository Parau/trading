@echo off

rem alterei o arquivo para rodar direto o client portal

set config_file=root\conf.yaml
echo "config file: %config_file%"
for /F %%i in ("%config_file%") do set config_path=%%~dpi
echo "config path :%config_path%"

set RUNTIME_PATH="%config_path%;dist\ibgroup.web.core.iblink.router.clientportal.gw.jar;build\lib\runtime\*"

echo "running %verticle% "
echo "runtime path : %RUNTIME_PATH%"

java -server -Dvertx.disableDnsResolver=true -Djava.net.preferIPv4Stack=true -Dvertx.logger-delegate-factory-class-name=io.vertx.core.logging.SLF4JLogDelegateFactory -Dnologback.statusListenerClass=ch.qos.logback.core.status.OnConsoleStatusListener -Dnolog4j.debug=true -Dnolog4j2.debug=true -classpath %RUNTIME_PATH% ibgroup.web.core.clientportal.gw.GatewayStart
rem optional arguments
rem -conf conf.beta.yaml --nossl


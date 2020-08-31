$serialnumber = "0323610cc6f699f24b1374395ae932950ea6"

# Use the new Certificate into Veeam Cloud Connect
asnp VeeamPSSnapin

Connect-VBRServer -Server localhost

$certificate = Get-VBRCloudGatewayCertificate -FromStore | Where {$_.SerialNumber -eq $serialnumber}

Add-VBRCloudGatewayCertificate -Certificate $certificate

Disconnect-VBRServer
Return
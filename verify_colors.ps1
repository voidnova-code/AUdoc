$dir = 'AUdoc_back\app\templates\app'
$files = @('home.html','appointment.html','blood_bank.html','donation.html','blood_donors_list.html','donor_response_confirm.html')
foreach ($f in $files) {
  $path = Join-Path $dir $f
  $c = Get-Content $path -Raw
  $hasBs = if ($c -match '--bs-primary') { 'YES' } else { 'NO !!!' }
  $remaining = ([regex]::Matches($c, '#1a5c96|#134a7a|#c8ddef|#9ab3c8|#e3eef8|#0d2d4a|#1e4a6e')).Count
  Write-Host "[$f] bs-primary=$hasBs  remaining-old-blues=$remaining"
}

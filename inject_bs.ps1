$dir = 'AUdoc_back\app\templates\app'
$files = @('home.html','appointment.html','blood_bank.html','donation.html','blood_donors_list.html','donor_response_confirm.html')

$bsBs    = '      --bs-primary:          #4a7c59;'
$bsRgb   = '      --bs-primary-rgb:      74, 124, 89;'
$bsLink  = '      --bs-link-color:       #4a7c59;'
$bsHover = '      --bs-link-hover-color: #2e5c3a;'
$bsBlock = "$bsBs`n$bsRgb`n$bsLink`n$bsHover"

foreach ($f in $files) {
  $path = Join-Path $dir $f
  $content = Get-Content $path -Raw -Encoding UTF8

  if ($content -notmatch '--bs-primary') {
    # Find end of :root block: last CSS variable before the closing }
    # Replace --green-light or --green or --red or --accent line followed by closing }
    $patterns = @(
      '(--green-light:[^\n]+\n)(    \})',
      '(--green:[^\n]+\n)(    \})',
      '(--red:[^\n]+\n)(    \})',
      '(--accent:[^\n]+\n)(    \})'
    )
    foreach ($pat in $patterns) {
      if ($content -match $pat) {
        $content = $content -replace $pat, "`$1$bsBlock`n`$2"
        break
      }
    }
  }

  Set-Content $path $content -Encoding UTF8 -NoNewline
  $ok = if ($content -match '--bs-primary') { 'OK' } else { 'FAILED' }
  Write-Host "[$f] bs-override=$ok"
}

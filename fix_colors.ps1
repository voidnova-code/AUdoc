$dir = 'AUdoc_back\app\templates\app'
$files = @('home.html','appointment.html','blood_bank.html','donation.html','blood_donors_list.html','donor_response_confirm.html')

$bsBlock = "      --bs-primary:          #4a7c59;`n      --bs-primary-rgb:      74, 124, 89;`n      --bs-link-color:       #4a7c59;`n      --bs-link-hover-color: #2e5c3a;"

# Simple string substitutions (pairs)
$subs = @(
  @('#cde2f5',         '#d4edda'),
  @('background:#eff8ff;border:1.5px solid #bfdbfe', 'background:#eef7f1;border:1.5px solid #b7dfc0'),
  @('background: #0d2a1a;', 'background: #0d2418;')
)

foreach ($f in $files) {
  $path = Join-Path $dir $f
  $content = Get-Content $path -Raw -Encoding UTF8

  # Inject Bootstrap overrides right before the :root closing brace
  # Match a line with a CSS variable ending in ; followed by optional whitespace + }
  # Use a pattern that works for all different last-variable names
  if ($content -notmatch '--bs-primary') {
    $content = $content -replace '(--(?:green-light|green|red|accent):[^\n]+;\n)(\s{4}\})', "`$1$bsBlock`n`$2"
    # Fallback for files where last var is --accent (appointment, blood_donors_list)
    if ($content -notmatch '--bs-primary') {
      $content = $content -replace '(--accent:[^\n]+;\n)(\s{4}\})', "`$1$bsBlock`n`$2"
    }
  }

  # Apply remaining color fixes
  foreach ($pair in $subs) {
    $content = $content.Replace($pair[0], $pair[1])
  }

  Set-Content $path $content -Encoding UTF8 -NoNewline
  Write-Host "Done: $f"
}

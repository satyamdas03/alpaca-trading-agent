# Launch a multi-pane Windows Terminal workspace for RESEARCH_HERMES.
# Three panes: project root | aqra (code/tests) | specs (paper/theory).
#
# Usage from PowerShell:
#   .\launch_workspace.ps1
# Or from Git Bash / cmd:
#   powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\point\projects\RESEARCH_HERMES\launch_workspace.ps1"

$root = "C:\Users\point\projects\RESEARCH_HERMES"
$aqra = "$root\aqra"
$specs = "$root\docs\superpowers\specs"

$args = @(
    '-d', $root,
    ';', 'split-pane', '-V', '-d', $aqra,
    ';', 'split-pane', '-H', '-d', $specs
)

Start-Process -FilePath 'wt.exe' -ArgumentList $args -WindowStyle Hidden
Write-Output "Windows Terminal workspace launched: root | aqra | specs"

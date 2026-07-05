@echo off
:: Launch a multi-pane Windows Terminal workspace for RESEARCH_HERMES.
:: Three panes: project root | aqra | specs.
::
:: Usage: double-click this file, or run from any shell:
::   cmd /c "C:\Users\point\projects\RESEARCH_HERMES\launch_workspace.cmd"

set "PSCMD=Start-Process -FilePath \"wt.exe\" -ArgumentList \"-d `"\"C:\Users\point\projects\RESEARCH_HERMES`\"`" ; split-pane -V -d `"\"C:\Users\point\projects\RESEARCH_HERMES\aqra`\"`" ; split-pane -H -d `"\"C:\Users\point\projects\RESEARCH_HERMES\docs\superpowers\specs`\"`\"" -WindowStyle Hidden"

powershell -NoProfile -Command "%PSCMD%"

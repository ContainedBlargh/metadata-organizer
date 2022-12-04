# Define a parameter for the path to the file
param(
   [string]$filePath
)

# Read the content of the file into a variable
$content = Get-Content -Path $filePath

# Use a regular expression to replace multiple newline characters with exactly three newline characters
$replacedContent = $content -replace '(\r?\n){2,}', "`r`n`r`n`r`n"

# Save the replaced content back to the file
$replacedContent | Set-Content -Path $filePath

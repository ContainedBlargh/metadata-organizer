# Define a parameter for the path to the file
param(
	[string]$filePath
)

 # Read the content of the file into a variable
 $content = Get-Content -Path $filePath

 # Filter the content to remove all lines starting with `:::`
 $filteredContent = $content | Where-Object { $_ -notmatch '^:::' } Where-Object { $_ -notmatch '^\[\[!\[.*'']]]' }

 # Save the filtered content back to the file
$filteredContent | Set-Content -Path $filePath

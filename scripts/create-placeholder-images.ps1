# Create placeholder images for OpenGraph and Twitter

# Define paths
$ogImagePath = "web/public/images/og-image.jpg"
$twitterImagePath = "web/public/images/twitter-image.jpg"

# Create a simple HTML file with the text content
$htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 1200px;
            height: 630px;
            background-color: #0f172a;
            color: white;
            font-family: Arial, sans-serif;
        }
        .container {
            text-align: center;
            max-width: 80%;
        }
        h1 {
            font-size: 48px;
            margin-bottom: 20px;
        }
        p {
            font-size: 24px;
            margin-bottom: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI ERP SaaS Platform</h1>
        <p>AI-Powered Invoice Automation | Save 60% vs Competitors</p>
    </div>
</body>
</html>
"@

# Save the HTML file
$htmlPath = "temp-image.html"
$htmlContent | Out-File -FilePath $htmlPath -Encoding utf8

Write-Host "HTML file created. Please manually convert this to images using a browser or image editor."
Write-Host "HTML file: $htmlPath"
Write-Host "Required image paths:"
Write-Host "- OpenGraph: $ogImagePath (1200x630px)"
Write-Host "- Twitter: $twitterImagePath (1200x630px)"































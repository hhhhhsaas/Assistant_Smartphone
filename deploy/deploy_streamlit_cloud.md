# 🚀 Deploy to Streamlit Cloud

## Prerequisites
1. GitHub account
2. Streamlit Cloud account (free at share.streamlit.io)

## Step 1: Push to GitHub

```bash
# Initialize git
git init

# Create .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore

# Add files
git add .
git commit -m "Initial commit: Phone Advisor System"

# Create repo on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/phone-advisor.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repo
4. Settings:
   - Repository: YOUR_USERNAME/phone-advisor
   - Branch: main
   - Main file path: app.py
5. Click "Deploy"

## Step 3: Environment Variables (if needed)

In Streamlit Cloud dashboard:
1. Go to App settings
2. Secrets section
3. Add any API keys or secrets

## Step 4: Custom Domain (Optional)

1. In App settings
2. Go to "Custom subdomain"
3. Choose your subdomain: yourapp.streamlit.app

## Monitoring

- Check logs in Streamlit Cloud dashboard
- Monitor usage metrics
- Set up alerts for errors

## Update Deployment

```bash
# Make changes locally
git add .
git commit -m "Update: description"
git push

# Streamlit Cloud auto-deploys from GitHub
```

## Troubleshooting

### Large Files
If you have large data files:
1. Use Git LFS
2. Or load data from external source (S3, Google Drive)

### Memory Issues
- Streamlit Cloud free tier: 1GB RAM
- Optimize data loading with caching
- Use `@st.cache_resource` for heavy objects

### Performance
- Enable fast refresh: `--server.fastRefresh false`
- Minimize data transfers
- Use session state efficiently

## Alternative: Deploy with GitHub Pages + Streamlit Sharing

1. Create `index.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=https://yourapp.streamlit.app">
</head>
<body>
    <p>Redirecting to Phone Advisor...</p>
</body>
</html>
```

2. Enable GitHub Pages
3. Share: https://YOUR_USERNAME.github.io/phone-advisor
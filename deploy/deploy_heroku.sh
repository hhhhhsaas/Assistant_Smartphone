#!/bin/bash

# Deploy to Heroku Script
echo "🚀 Deploying Phone Advisor to Heroku"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not installed. Please install from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if logged in
heroku auth:whoami &> /dev/null
if [ $? -ne 0 ]; then
    echo "📝 Please login to Heroku:"
    heroku login
fi

# Create Heroku app
APP_NAME="phone-advisor-$(date +%s)"
echo "📱 Creating app: $APP_NAME"
heroku create $APP_NAME

# Create setup.sh for Streamlit config
cat > setup.sh << 'EOF'
mkdir -p ~/.streamlit/

cat > ~/.streamlit/config.toml << 'EOL'
[server]
headless = true
port = $PORT
enableCORS = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
EOL
EOF

# Create Procfile
cat > Procfile << 'EOF'
web: sh setup.sh && streamlit run app.py
EOF

# Create runtime.txt
echo "python-3.9.16" > runtime.txt

# Update requirements.txt for Heroku
cat > requirements_heroku.txt << 'EOF'
streamlit==1.32.0
pandas==2.2.0
numpy==1.26.3
scikit-learn==1.4.1
plotly==5.19.0
altair==5.2.0
openpyxl==3.1.2
python-dotenv==1.0.0
EOF

# Initialize git if needed
if [ ! -d .git ]; then
    git init
fi

# Add Heroku remote
git remote add heroku https://git.heroku.com/$APP_NAME.git

# Commit changes
git add .
git commit -m "Deploy to Heroku"

# Deploy
echo "🚀 Deploying to Heroku..."
git push heroku main

# Scale dynos
heroku ps:scale web=1

# Open app
echo "✅ Deployment complete!"
echo "📱 App URL: https://$APP_NAME.herokuapp.com"
heroku open

# Show logs
echo "📋 Showing logs (Ctrl+C to exit):"
heroku logs --tail
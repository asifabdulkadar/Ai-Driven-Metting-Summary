# Deployment Guide for AI-Driven Meeting Summarizer

## 🚀 Streamlit Cloud Deployment

### Prerequisites
1. **MongoDB Atlas Account**: Sign up at [mongodb.com/atlas](https://mongodb.com/atlas)
2. **GitHub Repository**: Push your code to GitHub
3. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

### Step 1: Set Up MongoDB Atlas

1. **Create a Cluster**:
   - Go to MongoDB Atlas
   - Click "Create Cluster"
   - Choose the free tier (M0)
   - Select a region close to your users

2. **Create Database User**:
   - Go to "Database Access"
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Create a username and password (save these!)

3. **Configure Network Access**:
   - Go to "Network Access"
   - Click "Add IP Address"
   - Choose "Allow Access from Anywhere" (0.0.0.0/0)
   - This allows Streamlit Cloud to connect

4. **Get Connection String**:
   - Go to "Clusters" → "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password

### Step 2: Deploy to Streamlit Cloud

1. **Push Code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Streamlit Cloud deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Set main file path to `app.py`
   - Click "Deploy"

3. **Configure Secrets**:
   - In your Streamlit Cloud app settings
   - Go to "Secrets" tab
   - Add the following:
   ```toml
   [mongo]
   uri = "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/meeting_summarizer?retryWrites=true&w=majority"
   ```

### Step 3: Test Deployment

1. **Check Logs**: Look for MongoDB connection messages
2. **Test Upload**: Try uploading a sample file
3. **Verify Database**: Check if data is being saved

## 🌐 GitHub Pages Deployment (Static Website)

### Step 1: Prepare Static Files

The `index.html` file is already created and ready for GitHub Pages.

### Step 2: Deploy to GitHub Pages

1. **Push HTML File**:
   ```bash
   git add index.html
   git commit -m "Add GitHub Pages website"
   git push origin main
   ```

2. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Click "Settings"
   - Scroll to "Pages" section
   - Select "Deploy from a branch"
   - Choose "main" branch
   - Select "/ (root)" folder
   - Click "Save"

3. **Access Your Site**:
   - Your site will be available at: `https://yourusername.github.io/repository-name`
   - It may take a few minutes to deploy

## 🔧 Troubleshooting

### MongoDB Connection Issues

1. **Check Connection String**:
   ```bash
   # Test locally
   python -c "from pymongo import MongoClient; client = MongoClient('your-connection-string'); print(client.admin.command('ping'))"
   ```

2. **Verify Network Access**:
   - Ensure MongoDB Atlas allows 0.0.0.0/0
   - Check if your IP is whitelisted

3. **Check Secrets Configuration**:
   - Verify the secrets are properly formatted
   - Make sure there are no extra spaces or characters

### Streamlit Cloud Issues

1. **Dependency Problems**:
   - Check `requirements.txt` for version conflicts
   - Ensure `runtime.txt` specifies Python 3.11

2. **Import Errors**:
   - Verify all imports are correct
   - Check if all dependencies are listed

3. **Timeout Issues**:
   - Increase timeout values in database connection
   - Check if external services are accessible

### GitHub Pages Issues

1. **404 Errors**:
   - Ensure `index.html` is in the root directory
   - Check if the file is properly committed

2. **Styling Issues**:
   - Verify CDN links are accessible
   - Check browser console for errors

## 📋 Deployment Checklist

### For Streamlit Cloud:
- [ ] MongoDB Atlas cluster created
- [ ] Database user created
- [ ] Network access configured (0.0.0.0/0)
- [ ] Connection string obtained
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud app created
- [ ] Secrets configured
- [ ] App deployed successfully
- [ ] Database connection tested

### For GitHub Pages:
- [ ] `index.html` file created
- [ ] Code pushed to GitHub
- [ ] GitHub Pages enabled
- [ ] Site accessible via URL
- [ ] All features working

## 🎯 Next Steps

1. **Monitor Performance**: Check Streamlit Cloud logs regularly
2. **Update Dependencies**: Keep packages up to date
3. **Backup Data**: Regular MongoDB Atlas backups
4. **Scale Up**: Upgrade MongoDB Atlas tier as needed
5. **Custom Domain**: Configure custom domain for GitHub Pages

## 📞 Support

If you encounter issues:
1. Check the logs in Streamlit Cloud
2. Verify MongoDB Atlas connection
3. Test locally first
4. Check GitHub Pages deployment status

Remember: The static GitHub Pages version is a demo/portfolio site, while the Streamlit Cloud version is the full application with AI processing capabilities.

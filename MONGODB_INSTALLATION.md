# MongoDB Installation Guide

This guide provides step-by-step instructions for installing MongoDB on different operating systems.

## 🪟 Windows Installation

### Method 1: MongoDB Community Server (Recommended)

#### Step 1: Download MongoDB
1. Go to [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Select:
   - **Version**: Latest stable version (e.g., 7.0.x)
   - **Platform**: Windows
   - **Package**: MSI
3. Click "Download"

#### Step 2: Install MongoDB
1. Run the downloaded `.msi` file
2. Follow the installation wizard:
   - **Setup Type**: Choose "Complete"
   - **Service Configuration**: 
     - Check "Install MongoDB as a Service"
     - Service Name: MongoDB
     - Run Service as: Network Service User
   - **Install MongoDB Compass**: Check this box (optional GUI tool)
3. Click "Install"

#### Step 3: Verify Installation
1. Open Command Prompt as Administrator
2. Navigate to MongoDB bin directory:
   ```cmd
   cd "C:\Program Files\MongoDB\Server\7.0\bin"
   ```
3. Start MongoDB:
   ```cmd
   mongod
   ```
4. Open another Command Prompt and test connection:
   ```cmd
   mongo
   ```

#### Step 4: Configure MongoDB as Windows Service
1. Open Services (services.msc)
2. Find "MongoDB" service
3. Right-click → Properties
4. Set Startup Type to "Automatic"
5. Start the service

### Method 2: Using Chocolatey (Package Manager)

```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install MongoDB
choco install mongodb

# Start MongoDB service
net start MongoDB
```

## 🍎 macOS Installation

### Method 1: Using Homebrew (Recommended)

#### Step 1: Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install MongoDB
```bash
# Add MongoDB tap
brew tap mongodb/brew

# Install MongoDB Community Edition
brew install mongodb-community

# Start MongoDB service
brew services start mongodb/brew/mongodb-community
```

#### Step 3: Verify Installation
```bash
# Check if MongoDB is running
brew services list | grep mongodb

# Test connection
mongosh
```

### Method 2: Manual Installation

#### Step 1: Download MongoDB
1. Go to [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Select macOS and download the `.tgz` file

#### Step 2: Extract and Install
```bash
# Extract the archive
tar -zxvf mongodb-macos-x86_64-7.0.x.tgz

# Move to /usr/local
sudo mv mongodb-macos-x86_64-7.0.x /usr/local/mongodb

# Add to PATH
echo 'export PATH="/usr/local/mongodb/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Create data directory
sudo mkdir -p /usr/local/var/mongodb
sudo mkdir -p /usr/local/var/log/mongodb

# Set permissions
sudo chown $(whoami) /usr/local/var/mongodb
sudo chown $(whoami) /usr/local/var/log/mongodb
```

#### Step 3: Start MongoDB
```bash
# Start MongoDB
mongod --dbpath /usr/local/var/mongodb --logpath /usr/local/var/log/mongodb/mongo.log --fork
```

## 🐧 Linux Installation

### Ubuntu/Debian

#### Step 1: Import MongoDB Public Key
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
```

#### Step 2: Add MongoDB Repository
```bash
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

#### Step 3: Update Package Database
```bash
sudo apt-get update
```

#### Step 4: Install MongoDB
```bash
sudo apt-get install -y mongodb-org
```

#### Step 5: Start MongoDB Service
```bash
# Start MongoDB
sudo systemctl start mongod

# Enable MongoDB to start on boot
sudo systemctl enable mongod

# Check status
sudo systemctl status mongod
```

### CentOS/RHEL/Fedora

#### Step 1: Create MongoDB Repository File
```bash
sudo vi /etc/yum.repos.d/mongodb-org-7.0.repo
```

Add the following content:
```ini
[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-7.0.asc
```

#### Step 2: Install MongoDB
```bash
sudo yum install -y mongodb-org
```

#### Step 3: Start MongoDB Service
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

## 🐳 Docker Installation (All Platforms)

### Step 1: Install Docker
- **Windows**: Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
- **macOS**: Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
- **Linux**: Follow [Docker installation guide](https://docs.docker.com/engine/install/)

### Step 2: Run MongoDB Container
```bash
# Run MongoDB with Docker
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:7.0

# Or with persistent data
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0
```

### Step 3: Connect to MongoDB
```bash
# Connect to MongoDB container
docker exec -it mongodb mongosh
```

## ☁️ MongoDB Atlas (Cloud - Recommended for Production)

### Step 1: Create Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Click "Try Free"
3. Create an account

### Step 2: Create Cluster
1. Choose "Build a Database"
2. Select "FREE" tier
3. Choose cloud provider and region
4. Click "Create Cluster"

### Step 3: Configure Database Access
1. Go to "Database Access"
2. Click "Add New Database User"
3. Create username and password
4. Set permissions to "Read and write to any database"

### Step 4: Configure Network Access
1. Go to "Network Access"
2. Click "Add IP Address"
3. Add your current IP or "0.0.0.0/0" for all IPs

### Step 5: Get Connection String
1. Go to "Clusters"
2. Click "Connect"
3. Choose "Connect your application"
4. Copy the connection string

## 🔧 Configuration for Meeting Summarizer

### Local MongoDB Setup
1. **Create database**:
   ```javascript
   use meeting_summarizer
   ```

2. **Create collections**:
   ```javascript
   db.createCollection("transcripts")
   db.createCollection("summaries")
   db.createCollection("tasks")
   ```

3. **Update .env file**:
   ```env
   MONGODB_URI=mongodb://localhost:27017/
   DATABASE_NAME=meeting_summarizer
   ```

### MongoDB Atlas Setup
1. **Update .env file** with Atlas connection string:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   DATABASE_NAME=meeting_summarizer
   ```

## 🧪 Testing MongoDB Connection

### Using MongoDB Shell
```bash
# Connect to MongoDB
mongosh

# Test basic operations
use meeting_summarizer
db.test.insertOne({message: "Hello MongoDB!"})
db.test.find()
```

### Using Python (for Meeting Summarizer)
```python
from pymongo import MongoClient

# Test connection
client = MongoClient("mongodb://localhost:27017/")
db = client.meeting_summarizer

# Test operations
result = db.test.insert_one({"test": "connection"})
print("MongoDB connection successful!")
```

## 🚨 Troubleshooting

### Common Issues

1. **MongoDB won't start**:
   - Check if port 27017 is available
   - Ensure data directory has proper permissions
   - Check MongoDB logs for errors

2. **Connection refused**:
   - Verify MongoDB service is running
   - Check firewall settings
   - Ensure correct connection string

3. **Authentication failed**:
   - Check username/password
   - Verify database permissions
   - Ensure correct authentication database

### Useful Commands

```bash
# Check MongoDB status
sudo systemctl status mongod

# View MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log

# Restart MongoDB
sudo systemctl restart mongod

# Stop MongoDB
sudo systemctl stop mongod
```

## 📚 Next Steps

After installing MongoDB:

1. **Run the setup script**:
   ```bash
   python setup.py
   ```

2. **Test the system**:
   ```bash
   python test_system.py
   ```

3. **Start the application**:
   ```bash
   streamlit run app.py
   ```

Your MongoDB installation is now ready for the AI-Driven Meeting Summarizer! 🎉

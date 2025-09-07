# AI-Driven Meeting Summarizer

A comprehensive solution for meeting transcription, summarization, and task management using Python, Streamlit, Ollama, and MongoDB.

## 🚀 Features

- **Multi-format Support**: Upload text transcripts (.txt, .json), audio files (.wav, .mp3), or video files (.mp4, .mkv)
- **AI-Powered Processing**: Convert audio/video to text using Whisper or SpeechRecognition
- **Smart Summarization**: Generate meeting summaries using Ollama gemma:2b model
- **Action Item Extraction**: Automatically extract tasks with assignees and suggested deadlines
- **Task Management**: Store and manage tasks in MongoDB with APScheduler for reminders
- **Interactive Dashboard**: Beautiful Streamlit interface with sidebar navigation
- **Export Options**: Download summaries and tasks as CSV or PDF files
- **Real-time Scheduling**: Automatic task scheduling with deadline reminders

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB (local installation or cloud service)
- Ollama installed and running
- FFmpeg (for video processing)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-meeting-summarizer.git
cd ai-meeting-summarizer
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Ollama and Pull the Model
```bash
# Install Ollama from https://ollama.ai
# Then pull the gemma:2b model
ollama pull gemma:2b
```

### 4. Install FFmpeg (for video processing)
- **Windows**: Download from https://ffmpeg.org/download.html
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 5. Set Up MongoDB
- **Local**: Install MongoDB and start the service
- **Cloud**: Use MongoDB Atlas or another cloud service

### 6. Configure Environment Variables
Create a `.env` file in the project root:
```env
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=meeting_summarizer
OLLAMA_BASE_URL=http://localhost:11434
```

## 🚀 Quick Start

1. **Start MongoDB** (if running locally):
   ```bash
   mongod
   ```

2. **Start Ollama**:
   ```bash
   ollama serve
   ```

3. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

4. **Access the Dashboard**:
   Open your browser and navigate to `http://localhost:8501`

## 📖 Usage

### Upload a Meeting File
1. Navigate to the Home page
2. Upload a text, audio, or video file
3. Click "Process Meeting"
4. Wait for AI processing to complete

### View Results
1. Review the generated summary
2. Check extracted action items
3. Manage tasks in the Dashboard
4. Export results as needed

### Export Options
- **CSV Export**: Download summaries and tasks as CSV files
- **PDF Export**: Generate professional PDF reports
- **Complete Reports**: Export summary + tasks in one file

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Upload   │───▶│  AI Processing  │───▶│   Dashboard     │
│  (Text/Audio/   │    │  (Whisper +     │    │  (Summary +     │
│   Video)        │    │   Gemma:2b)     │    │   Tasks)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Transcript     │    │   MongoDB       │    │   Export        │
│  Storage        │    │   Database      │    │   System        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Technical Details

### Core Components

- **app.py**: Main Streamlit application
- **ollama_nlp.py**: AI processing with Ollama
- **transcript_loader.py**: File processing and transcription
- **task_manager.py**: Task management and scheduling
- **db.py**: MongoDB operations
- **exports.py**: Export functionality

### AI Models Used

- **Whisper**: Speech-to-text conversion
- **Gemma:2b**: Meeting summarization and task extraction
- **Custom NLP**: Action item parsing and formatting

### Database Schema

- **transcripts**: Raw meeting transcripts
- **summaries**: AI-generated summaries
- **tasks**: Extracted action items with scheduling

## 📊 Features in Detail

### Multi-format Support
- **Text Files**: Direct processing of .txt and .json files
- **Audio Files**: Support for .wav, .mp3 formats
- **Video Files**: Support for .mp4, .mkv formats with FFmpeg

### AI Processing Pipeline
1. **Transcription**: Convert audio/video to text using Whisper
2. **Summarization**: Generate intelligent summaries using Gemma:2b
3. **Task Extraction**: Identify action items with assignees and deadlines
4. **Scheduling**: Automatically schedule task reminders

### Task Management
- **Automatic Creation**: Tasks created from AI-extracted action items
- **Smart Scheduling**: APScheduler integration for reminders
- **Status Tracking**: Monitor task completion and deadlines
- **Priority Management**: High/medium/low priority classification

### Export System
- **CSV Format**: Structured data for analysis
- **PDF Format**: Professional reports for sharing
- **Customizable**: Filter by date, status, or meeting
- **Batch Export**: Export multiple meetings at once

## 🔒 Security & Privacy

- **Local Processing**: All AI processing happens locally
- **Data Encryption**: Secure storage of sensitive data
- **No Cloud Dependency**: Complete offline functionality
- **Privacy Compliance**: GDPR-ready data handling

## 🚀 Performance

- **Real-time Processing**: Immediate feedback during processing
- **Scalable Architecture**: Handles multiple concurrent users
- **Memory Optimization**: Efficient resource utilization
- **Caching**: Smart caching for improved performance

## 🧪 Testing

Run the test suite:
```bash
python test_system.py
```

## 📈 Monitoring

The application includes comprehensive logging:
- Processing status updates
- Error tracking and reporting
- Performance metrics
- User activity logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local AI model hosting
- [Whisper](https://github.com/openai/whisper) for speech recognition
- [Streamlit](https://streamlit.io/) for the web interface
- [MongoDB](https://www.mongodb.com/) for data storage

## 📞 Support

For support, email [your-email@example.com] or create an issue in this repository.

## 🔮 Roadmap

- [ ] Multi-language support
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] API integration
- [ ] Voice commands
- [ ] Predictive analytics

---

**Made with ❤️ for better meeting productivity**

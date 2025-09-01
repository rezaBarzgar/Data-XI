# ⚽ FPL Captain Recommender

An AI-powered Fantasy Premier League captain recommendation system built with Streamlit and LangChain.

## 🎯 Features

- **Smart Captain Recommendations**: Get 3 ranked captain choices with detailed reasoning
- **Rich Data Analysis**: Player stats, form analysis, fixture difficulty, and ownership data
- **Interactive Visualizations**: Charts showing team performance and player metrics
- **Real-time FPL Data**: Fetches latest data from the official FPL API
- **Multiple LLM Support**: Choose from various OpenAI models

## 🚀 How to Use

1. **Get Your Team ID**: 
   - Visit [Fantasy Premier League](https://fantasy.premierleague.com/)
   - Go to your team page
   - Copy the number from the URL: `fantasy.premierleague.com/entry/[YOUR_ID]/`

2. **Set Up API Key**:
   - Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
   - Enter it in the sidebar or set as environment variable

3. **Get Recommendations**:
   - Enter your team ID
   - Click "Initialize Recommender"
   - Click "Get Captain Recommendations"
   - Analyze the results and make your choice!

## 🛠️ Technical Details

- **Data Source**: Official Fantasy Premier League API
- **AI Model**: OpenAI GPT (configurable)
- **Framework**: Streamlit for web interface
- **Visualization**: Plotly for interactive charts
- **Language**: Python 3.8+

## 📊 What Data is Analyzed?

- Player form and recent performance
- Fixture difficulty ratings
- Historical head-to-head records
- Injury and availability status
- Ownership percentages and differentials
- Team context and motivation factors

## 🔒 Privacy & Security

- No personal data is stored
- API keys are handled securely
- All data fetched in real-time from public APIs

## 🤝 Contributing

This project was built for educational purposes in LLM engineering and Fantasy Premier League analysis.

## 📄 License

MIT License - feel free to fork and modify!

---
Built with ❤️ using Streamlit, LangChain, and the FPL API
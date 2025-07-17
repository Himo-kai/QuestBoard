# 🧭 QuestBoard

**QuestBoard** is a gamified terminal-based job board that aggregates and curates gig listings—turning freelance hunting into an RPG-inspired experience. It pulls quests from **Craigslist** (Las Vegas), **Reddit** (`r/donedirtcheap`), and **user submissions** based on smart keyword matching, skill tagging, and difficulty estimation.

## 🏗️ Architecture Overview

```
+----------------+     +------------------+     +-------------------+
|  Data Sources  | --> |  Quest Fetcher   | --> |   Quest Board     |
|  - Reddit      |     |  - Scrapers      |     |  - Web Interface  |
|  - Craigslist  |     |  - API Clients   |     |  - API Endpoints  |
|  - User Input  |     |  - Data Cleaners |     |  - Admin Panel    |
+----------------+     +------------------+     +-------------------+
                                    |                     |
                                    v                     v
+------------------+     +------------------+     +-------------------+
|  NLP Engine      | <-- |  Difficulty     |     |  Database         |
|  - TF-IDF        |     |  Calculator     |     |  - SQLite/Postgres|
|  - Embeddings    |     |  - Scoring      |     |  - Caching        |
|  - Keywords      |     |  - Tagging      |     +-------------------+
+------------------+     +------------------+
```

### Core Components
- **Quest Fetcher**: Handles data collection from various sources
- **NLP Engine**: Processes text for difficulty scoring and tagging
- **Web Interface**: User and admin interfaces for interacting with quests
- **Database**: Stores quests, users, and application data

## New Features

### Guild Hall Administration
- **Moderator Interface**: Approve or reject user-submitted quests
- **Quest Moderation**: Ensure quality and relevance of all quests
- **User Management**: Track user submissions and activity

### User Quest Submissions
- **Submit Quests**: Users can now submit their own quests
- **Auto-Moderation**: Quests are held for review before going live
- **User Profiles**: Track your submitted quests and approval status

### Guild Card System
- **User Stats**: Track your questing history and achievements
- **Rank Progression**: Earn ranks based on your questing activity
- **Performance Metrics**: View your average difficulty and completion rate

### Map-Based Region Selector
- **Regional Filtering**: Find quests in specific locations
- **Visual Interface**: Intuitive map-based navigation
- **Location-Based Recommendations**: Get quests relevant to your area

### Enhanced Difficulty Engine
- **NLP-Powered**: Advanced natural language processing for better difficulty assessment
- **Content Analysis**: Considers both title and description for accurate ratings
- **Adaptive Learning**: Improves over time based on user feedback

---

## Table of Contents
- [Features](#-new-features)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Database Schema](#-database-schema)
- [Development](#-development)
- [License](#-license)

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- SQLite (comes with Python)
- Reddit API credentials (required for Reddit integration)
- Google Chrome (for Craigslist scraping)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/questboard.git
   cd questboard
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### First-Time Setup

1. Run the setup wizard to configure Reddit API credentials:
   ```bash
   python env_wizard.py
   ```

2. Initialize the database:
   ```bash
   flask db upgrade
   flask init-db
   ```

### Running the App

```bash
# Run the app (runs setup wizard if needed)
python app.py

# View available quests in your browser
http://localhost:5000

# Access the Guild Hall admin interface
http://localhost:5000/guildhall/review
```

## API Endpoints

### Quest Management
- `POST /submit` - Submit a new quest
- `GET /quests` - List all approved quests
- `GET /quests/region/<region>` - Get quests by region
- `GET /guildcard/<user_id>` - Get user stats and guild card

### Guild Hall (Admin)
- `GET /guildhall/review` - View pending quests
- `POST /guildhall/review` - Approve/Reject quests
  - Parameters: `quest_id`, `action` (approve/reject)

## Database Schema

### Quests Table
- `id` - Unique identifier
- `title` - Quest title
- `description` - Detailed description
- `difficulty` - Estimated difficulty (0-10)
- `source` - Source of the quest (Reddit/Craigslist/User)
- `created_at` - When the quest was created
- `last_seen` - Last time the quest was updated
- `gear_required` - Required equipment/tools
- `approved` - Approval status (NULL=pending, 1=approved, 0=rejected)
- `region` - Geographic region
- `submitted_by` - User who submitted the quest

### Bookmark Table
- `id` - Bookmark ID
- `quest_id` - Reference to quest
- `user_id` - User who bookmarked
- `created_at` - When it was bookmarked
- `notes` - User notes

## 🛠️ Development

### Running Migrations
```bash
python run_migrations.py
```

### Testing
```bash
pytest tests/
```

### Environment Variables
Create a `.env` file with the following variables:
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Usage Examples

### Basic Usage

```bash
# Run the app (runs setup wizard if needed)
python app.py

# View available quests in your browser
http://localhost:5000
```

### Docker Usage

```bash
# Build Docker image
docker build -t questboard .

# Run Docker container
docker run -p 5000:5000 questboard

# Access the app
http://localhost:5000
```

### Environment Variables

The app uses the following environment variables:

```
# Reddit API credentials (set via setup wizard)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=QuestBoard/1.0

# Database settings
DATABASE_PATH=questboard.db
```

#### Setting Up Reddit API Credentials

1. Visit Reddit's App Preferences: https://www.reddit.com/prefs/apps
2. Click "create another app"
3. Choose "script" application type
4. Set redirect URI to: `http://localhost:8080`
5. Copy your client ID and secret
6. Run the setup wizard:
```bash
python env_wizard.py
```

The wizard will guide you through the setup process and create the `.env` file for you.

---

## Features

- **Gear Suggestion Engine** — Tells you what tools you’ll need based on job descriptions.
- **Difficulty Ratings** — Ranks jobs with a 1–5 star scale based on complexity.
- **Smart Relevance Filter** — Uses `sentence-transformers` to detect relevant gigs even if your key interests aren't mentioned directly.
- **Auto-Extracted Compensation** — Parses pay rates from listings, when available.
- **Reddit Integration** — Pulls tasks from community forums like `r/donedirtcheap`.
- **First-Time API Wizard** — Helps users generate Reddit API keys via guided CLI prompts.
- **Gamified Interface** — Makes job hunting feel like quest selection from a fantasy board.

---

## Requirements

- Python 3.9+
- Reddit API Credentials (see Setup)
- Linux/macOS/Windows (Docker-friendly)

Install dependencies with:

```
pip install -r requirements.txt
```

## Getting Started

# Clone the repo
```
git clone https://github.com/yourusername/QuestBoard.git

cd QuestBoard
```

# Optional: manual Setup Reddit credentials via wizard
```
python env_wizard.py
```

# Launch the board! -
 *This auto-runs the setup wizard if credentials arent found in the .env file*
 ```
python app.py
```

# First-Time Reddit Setup
*This is covered in the set up wizard which guides you through setting up Reddit's API.*

Reddit’s API requires authentication.

   *Visit: https://www.reddit.com/prefs/apps

   *Click "create another app"

   *Choose "script", fill in http://localhost:8080 as the redirect URL

   *Copy the client_id and secret

   *Run the wizard:
```
python env_wizard.py
```
Paste your credentials when prompted, and you're ready to quest!

---

Smart Matching Logic

Feature	Description

Gear Suggestions	Pulls gear names from a curated keyword list (editable via gear_keywords.py)

AI Matching	Uses sentence-transformers to detect jobs relevant to "AI", "tech", etc., even if not explicitly stated

Filtering	Automatically excludes irrelevant gigs (e.g., "study", "girls", "women") unless tagged tech-relevant
Compensation	Rewards are parsed from listing content; posts with "TBD" or "$0" are excluded unless high-priority

## Project Structure

📁 QuestBoard/
├── app.py               # Main application logic
├── gear_keywords.py     # Gear keyword engine
├── reddit_source.py     # Reddit quest pulling logic
├── env_wizard.py        # CLI wizard for Reddit API setup
├── utils.py             # Shared formatting, filters, and helper methods
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker support

 Roadmap

GUI / TUI mode via textual or urwid

Accept / Abandon / Complete quest tracking

Save/load quest logs

Add more Reddit communities (customizable)

    Export to Markdown or PDF for offline browsing

 Contributing

Not currently open for contributions, but you're welcome to fork and build your own QuestBoard.

## 🧪 Example Quest

```
[🛠] Quest: "Fix busted faucet for old vet"
Location: North Las Vegas
Reward: $20 + warm gratitude
Difficulty: 3.2 ★☆☆
Tags: [plumbing, compassion, solo]

[📝] Description: 
Looking for someone to fix a leaky kitchen faucet for an elderly veteran. 
Basic tools required. Will provide coffee and cookies!

[⚔️] Requirements:
- Basic plumbing skills
- Own tools
- Valid driver's license
- Good with pets (has a friendly old dog)
```

## 🔍 NLP & Difficulty Scoring

QuestBoard uses a combination of techniques to analyze and score quests:

1. **Text Processing**
   - TF-IDF vectorization for keyword importance
   - Sentence embeddings for semantic understanding
   - Custom regex patterns for key information extraction

2. **Difficulty Factors**
   - Text complexity analysis
   - Required skills and tools
   - Historical completion data
   - User ratings and feedback

3. **Gear Suggestions**
   - Matches quest requirements with recommended tools/equipment
   - Considers both explicit and implicit requirements
   - Suggests alternatives when available

## 📚 API Reference

### Core Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/quests` | GET | List all quests | None |
| `/api/quests/<id>` | GET | Get quest details | None |
| `/api/quests/submit` | POST | Submit new quest | User |
| `/api/quests/<id>/bookmark` | POST | Bookmark a quest | User |
| `/admin/quests/pending` | GET | List pending quests | Admin |
| `/admin/quests/<id>/moderate` | POST | Approve/reject quest | Admin |

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Test coverage report:
```bash
coverage run -m pytest
coverage report -m
```

Current test coverage: [Add coverage badge here]

## 📜 License

QuestBoard is licensed under the Mozilla Public License 2.0 (MPL-2.0). This means you can use, modify, and distribute the software under the terms of this license. The full license text is available in the [LICENSE](LICENSE) file.

Key points:
- You can use this software for any purpose, commercial or non-commercial
- You must make any modifications to the source code available under the same license
- You must include the original copyright notice and license file

For the full license terms, please see [LICENSE](LICENSE) or visit [https://mozilla.org/MPL/2.0/](https://mozilla.org/MPL/2.0/)


 Contact

Made with mild annoyance by [Himokai]
Twitter / GitHub / Smoke Signals: @himokai

    "The world’s full of quests, you just need the right lens to see them." — -someone on Reddit probably...

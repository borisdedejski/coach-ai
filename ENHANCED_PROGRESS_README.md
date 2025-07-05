# Enhanced Progress Analysis - AI Coach

## Overview

The AI Coach now features enhanced progress analysis with deeper personalization, including mood pattern detection, trend analysis, and trigger identification.

## Key Features

### 1. Mood Trends by Day of Week
- Analyzes mood patterns for each day of the week
- Identifies which days typically have better/worse moods
- Example: "You seem to feel more anxious on Mondays"

### 2. Mood Changes Over Time (Sliding Window)
- Uses a 7-day sliding window to detect mood trends
- Identifies if mood is improving, declining, or stable
- Example: "Your mood has steadily improved over the past week"

### 3. Trigger Detection
- Keyword-based analysis to identify common themes
- Detects patterns in work stress, relationships, health, finances, etc.
- Example: "Work stress seems to come up frequently in your entries"

### 4. Overall Mood Direction & Stability
- Calculates overall emotional trajectory
- Measures mood stability (very stable, moderately stable, volatile)
- Provides actionable insights about emotional patterns

## Technical Implementation

### Core Functions

#### `analyze_mood_by_day_of_week(entries)`
- Groups entries by day of the week
- Calculates average sentiment scores per day
- Identifies most common moods for each day

#### `analyze_mood_trends(entries, window_size=7)`
- Uses sliding window approach for trend detection
- Compares first and last averages to determine direction
- Thresholds: >0.1 for improving, <-0.1 for declining

#### `detect_triggers(entries)`
- Keyword matching for common emotional triggers
- Categories: work_stress, relationship, health, financial, social, personal_goals
- Returns frequency counts and most frequent themes

#### `calculate_overall_mood_direction(entries)`
- Compares first third vs last third of entries
- Calculates variance for stability assessment
- Provides detailed direction and stability metrics

### API Endpoints

#### Enhanced Progress Analysis
```
GET /v1/progress/{user_id}/enhanced
```

**Response:**
```json
{
  "summary": "Your mood has been improving over the past week...",
  "score": 0.75,
  "patterns": {
    "day_patterns": {
      "Monday": {
        "avg_sentiment": -0.2,
        "most_common_mood": "anxious",
        "entry_count": 3
      }
    },
    "trend_analysis": {
      "trend": "analyzed",
      "direction": "improving",
      "change_magnitude": 0.15
    },
    "trigger_analysis": {
      "detected_triggers": {"work_stress": 5},
      "most_frequent": ["work_stress"],
      "total_entries_analyzed": 20
    },
    "mood_direction": {
      "direction": "slightly_improving",
      "stability": "moderately_stable",
      "overall_change": 0.08,
      "variance": 0.12
    }
  }
}
```

## Usage

### Chainlit Interface

1. **Automatic Analysis**: After each mood-related entry, the system automatically shows enhanced progress analysis
2. **Manual Trigger**: Type `/progress` or `show progress` to see detailed analysis anytime
3. **Real-time Insights**: View patterns, trends, and triggers in a formatted display

### Example Interaction

```
User: "I'm feeling stressed about work today"
Bot: [Provides mood analysis and reflection question]
Bot: [Shows enhanced progress analysis with patterns]

User: "/progress"
Bot: [Shows detailed progress analysis with all patterns]
```

## Configuration

### Analysis Parameters

- **Entry Limit**: 20 entries for comprehensive analysis
- **Sliding Window**: 7 days for trend detection
- **Day Pattern Threshold**: Minimum 2 entries per day for analysis
- **Trend Thresholds**: ±0.1 for direction changes
- **Stability Thresholds**: 
  - Very stable: variance < 0.1
  - Moderately stable: variance < 0.25
  - Volatile: variance ≥ 0.25

### Trigger Keywords

The system monitors these categories:
- **Work Stress**: work, job, boss, deadline, meeting, office, colleague
- **Relationships**: partner, boyfriend, girlfriend, husband, wife, friend, family
- **Health**: sick, pain, doctor, medicine, sleep, exercise, diet
- **Financial**: money, bills, expenses, budget, debt, salary
- **Social**: party, social, lonely, people, crowd, conversation
- **Personal Goals**: goal, achievement, success, failure, progress, plan

## Testing

Run the test script to verify functionality:

```bash
python test_enhanced_progress.py
```

This will:
1. Create test journal entries with various moods and themes
2. Test the enhanced progress analysis endpoint
3. Display the analysis results

## Future Enhancements

1. **Advanced NLP**: Replace keyword matching with more sophisticated text analysis
2. **Seasonal Patterns**: Detect mood changes across months/seasons
3. **Correlation Analysis**: Identify relationships between different triggers
4. **Predictive Insights**: Forecast mood trends based on historical patterns
5. **Personalized Recommendations**: Suggest coping strategies based on detected patterns 
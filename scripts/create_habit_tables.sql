-- Habit & Activity Tracking System Setup
-- PostgreSQL SQL Script
-- Run this script to create all habit tracking tables and initialize default habits

-- Create habits table
CREATE TABLE IF NOT EXISTS habits (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    target_value FLOAT,
    unit VARCHAR(50),
    mental_health_benefit TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create user_habits table
CREATE TABLE IF NOT EXISTS user_habits (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    habit_id INTEGER NOT NULL REFERENCES habits(id),
    is_active BOOLEAN DEFAULT TRUE,
    target_value FLOAT,
    reminder_time VARCHAR(10), -- Format: "HH:MM"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create activity_logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    habit_id INTEGER NOT NULL REFERENCES habits(id),
    activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    value FLOAT,
    completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    mood_before VARCHAR(100),
    mood_after VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create habit_streaks table
CREATE TABLE IF NOT EXISTS habit_streaks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    habit_id INTEGER NOT NULL REFERENCES habits(id),
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_completed_date TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    daily_checkin_enabled BOOLEAN DEFAULT TRUE,
    habit_reminders_enabled BOOLEAN DEFAULT TRUE,
    progress_notifications_enabled BOOLEAN DEFAULT TRUE,
    preferred_checkin_time VARCHAR(10) DEFAULT '09:00', -- Format: "HH:MM"
    timezone VARCHAR(50) DEFAULT 'UTC',
    notification_frequency VARCHAR(20) DEFAULT 'daily',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_habits_user_id ON user_habits(user_id);
CREATE INDEX IF NOT EXISTS idx_user_habits_habit_id ON user_habits(habit_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_habit_id ON activity_logs(habit_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_activity_date ON activity_logs(activity_date);
CREATE INDEX IF NOT EXISTS idx_habit_streaks_user_id ON habit_streaks(user_id);
CREATE INDEX IF NOT EXISTS idx_habit_streaks_habit_id ON habit_streaks(habit_id);

-- Insert default habits
INSERT INTO habits (name, category, description, frequency, target_value, unit, mental_health_benefit) VALUES
('Sleep Quality', 'sleep', 'Track your sleep duration and quality', 'daily', 8.0, 'hours', 'Good sleep improves mood, reduces anxiety, and enhances cognitive function.'),
('Exercise', 'exercise', 'Physical activity for mental health', 'daily', 30.0, 'minutes', 'Exercise releases endorphins, reduces stress, and improves overall mood.'),
('Meditation', 'mindfulness', 'Mindfulness and meditation practice', 'daily', 10.0, 'minutes', 'Meditation reduces stress, improves focus, and promotes emotional balance.'),
('Social Connection', 'social', 'Meaningful social interactions', 'daily', 1.0, 'times', 'Social connections reduce loneliness and provide emotional support.'),
('Gratitude Practice', 'mindfulness', 'Daily gratitude journaling', 'daily', 3.0, 'items', 'Gratitude practice increases positive emotions and life satisfaction.'),
('Screen Time Management', 'digital_wellness', 'Limit excessive screen time', 'daily', 4.0, 'hours', 'Reducing screen time improves sleep quality and reduces anxiety.'),
('Healthy Eating', 'nutrition', 'Balanced meals and hydration', 'daily', 3.0, 'meals', 'Proper nutrition supports brain function and stabilizes mood.'),
('Creative Activity', 'creativity', 'Engage in creative pursuits', 'weekly', 1.0, 'times', 'Creative activities reduce stress and provide emotional expression.')
ON CONFLICT (name) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_user_habits_updated_at 
    BEFORE UPDATE ON user_habits 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_habit_streaks_updated_at 
    BEFORE UPDATE ON habit_streaks 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at 
    BEFORE UPDATE ON user_preferences 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Verify the setup
SELECT 'Tables created successfully!' as status;

-- Show table counts
SELECT 'habits' as table_name, COUNT(*) as record_count FROM habits
UNION ALL
SELECT 'user_habits' as table_name, COUNT(*) as record_count FROM user_habits
UNION ALL
SELECT 'activity_logs' as table_name, COUNT(*) as record_count FROM activity_logs
UNION ALL
SELECT 'habit_streaks' as table_name, COUNT(*) as record_count FROM habit_streaks
UNION ALL
SELECT 'user_preferences' as table_name, COUNT(*) as record_count FROM user_preferences;

-- Show available habits
SELECT id, name, category, target_value, unit FROM habits WHERE is_active = TRUE ORDER BY category, name; 
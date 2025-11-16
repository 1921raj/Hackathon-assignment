# Competitor Monitor

A Django web application that continuously monitors competitor activities across publicly available channels and organizes insights so marketers can react faster.

## Features

- **Automatic Monitoring**: Pulls competitor updates automatically from websites
- **Smart Classification**: Classifies updates (pricing, campaign, release, partnership, feature, news)
- **Trend Detection**: Detects trends and repeated patterns across competitor activities
- **High-Impact Notifications**: Notifies users of important competitor actions
- **Insights Dashboard**: Comprehensive dashboard for decision-making

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

## Usage

1. Access the admin panel at `/admin/` to manage competitors and settings
2. Add competitors through the web interface at `/competitors/add/`
3. Configure monitoring settings for each competitor
4. Run monitoring manually from the dashboard or set up automated tasks
5. View updates, trends, and notifications through the dashboard

## Project Structure

- `competitor_monitor/`: Main Django project settings
- `monitor/`: Main application with models, views, and services
- `templates/`: HTML templates for the web interface
- `static/`: Static files (CSS, JavaScript, images)

## Models

- **Competitor**: Represents companies being monitored
- **CompetitorUpdate**: Individual updates from competitors
- **Trend**: Detected trends and patterns
- **Notification**: User notifications for high-impact updates
- **MonitoringConfig**: Configuration for monitoring each competitor

## Services

- **CompetitorMonitor**: Handles web scraping and update detection
- **TrendAnalyzer**: Analyzes patterns and detects trends

## License

This project is for demonstration purposes.




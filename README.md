# Klaviyo Vertical Expansion Demo

**Live Demo**: https://klaviyo.github.io/liang_pk-agent-demo/

## Overview

This demo showcases how Klaviyo's infrastructure can be easily adapted for different use cases beyond traditional marketing. It demonstrates the same APIs and infrastructure serving two completely different verticals:

### 📚 Tab 1: Education Marketing
**Theme**: Coral/Red gradient
**Use Case**: Student engagement tracking and re-engagement campaigns

- **Data Ingested**: Course enrollments, video watches, quiz completions, forum interactions, session duration
- **Klaviyo APIs Used**: Events API, Metrics API, Segments API, Campaigns API
- **Outputs**: Engagement analytics, at-risk student segments, automated re-engagement emails, completion tracking

**Key Metrics**:
- 12,847+ active students
- 78% course completion rate
- 64% re-engagement rate via automated campaigns
- Real-time engagement scoring by course category

### 💻 Tab 2: SaaS Feature Monitoring
**Theme**: Teal/Cyan gradient
**Use Case**: Product analytics and sales intelligence (non-marketing)

- **Data Ingested**: Feature clicks, API calls, export activities, collaboration events, settings changes
- **Klaviyo APIs Used**: Events API, Metrics API, Segments API, Webhooks API
- **Outputs**: Feature analytics, power user segments, sales alerts via Slack, retention insights

**Key Metrics**:
- 8,234+ active users
- 62% power user activation rate
- 1.2M+ API calls per day
- Real-time Slack alerts on advanced feature usage

## Key Features

✅ **Dual Color Themes** - Distinct visual identity for each vertical
✅ **Data Flow Diagrams** - Shows ingestion → APIs → outputs clearly
✅ **Real-time Animations** - All stats and charts update every 5 seconds
✅ **Same Infrastructure** - Zero code changes needed, just event configuration
✅ **Live Demo** - Fully functional, no backend required

## Why This Matters

This demo proves that Klaviyo infrastructure can power **any vertical** with minimal configuration:

- Same Events API ingests student activity or product usage
- Same Metrics API generates education analytics or SaaS insights
- Same Segments API identifies at-risk students or power users
- Same automation triggers re-engagement emails or sales alerts

**The key insight**: It's not about building new infrastructure—it's about configuring the same powerful foundation for different event types and metrics.

## Technical Implementation

- Single HTML file with embedded JavaScript
- No external dependencies
- Simulated Klaviyo API responses
- Animated data visualizations
- Responsive design

## Created By

Agent-assisted development showcasing rapid prototyping capabilities.

---

**Repository**: https://github.com/klaviyo/liang_pk-agent-demo
**Shared with**: @liangzhang-prog

# Product Roadmap

## Phase 1: MVP - Core Procedures Engine (Weeks 1-4)

**Goal**: Deliver minimum viable product with essential procedure creation and execution

### Features
- **Procedure Browser**
  - List all procedures with basic metadata (name, description, step count)
  - Search and filter by procedure name
  - Quick start button to launch procedures

- **Procedure Execution**
  - Step-by-step checklist interface
  - Interactive checkboxes for each step
  - Basic controls: Start, Pause, Complete, Cancel
  - Capture start time and end time

- **Procedure Creation**
  - Simple form to create new procedures
  - Add/edit/delete/reorder steps
  - Save and update procedures

- **Data Storage**
  - CSV-based tables: `procedures.csv`, `steps.csv`, `runs.csv`
  - Pandas for data manipulation
  - Basic data validation

### Success Criteria
- Users can create a procedure with 10+ steps
- Users can execute a procedure and mark steps complete
- Basic run history is captured (date, duration)
- App loads and saves data reliably from CSV files

---

## Phase 2: History & Analytics (Weeks 5-8)

**Goal**: Add visibility into past runs and performance metrics

### Features
- **Run History View**
  - Display all past runs with key details (procedure name, date, duration, status)
  - Filter by procedure, date range, completion status
  - Sort by any column

- **Basic Analytics**
  - Average completion time per procedure
  - Completion rate (successful runs / total runs)
  - Most frequently run procedures
  - Time trend visualization (simple charts)

- **Run Notes**
  - Add optional notes during or after a run
  - Record issues, observations, or variations
  - Display notes in history view

### Success Criteria
- Users can view complete run history
- Analytics accurately reflect performance trends
- Users can identify their most time-consuming procedures
- Notes are preserved and easily accessible

---

## Phase 3: Advanced Editing & Version Control (Weeks 9-12)

**Goal**: Enable continuous procedure improvement with confidence

### Features
- **Version History**
  - Track all changes to procedures over time
  - View previous versions with diff comparison
  - Rollback to earlier versions if needed
  - Timestamp and change description for each version

- **Advanced Editing**
  - Bulk operations (duplicate steps, import from template)
  - Rich text descriptions for steps
  - Optional step-level time estimates
  - Step dependencies (optional: certain steps only shown conditionally)

- **Labels & Organization**
  - Tag procedures with labels (e.g., "household", "weekly", "training")
  - Filter procedures by label
  - Color-coded labels for visual organization

### Success Criteria
- Version history accurately tracks all procedure changes
- Users can confidently edit procedures knowing they can revert
- Labels help users organize growing procedure libraries
- Advanced editing features speed up procedure creation

---

## Phase 4: Collaboration & Export (Weeks 13-16)

**Goal**: Enable sharing and external integration

### Features
- **Export Capabilities**
  - Export run history to CSV for external analysis
  - Export individual procedures as PDF or Markdown
  - Batch export all procedures

- **Import Templates**
  - Import procedures from standardized format (JSON/CSV)
  - Pre-built template library (common household/business procedures)
  - Community-contributed templates (optional)

- **Multi-User Support** (optional, based on feedback)
  - Basic user accounts
  - Shared procedures across household/team
  - Individual run tracking per user

### Success Criteria
- Data export works reliably in multiple formats
- Users can share procedures with others
- Template library accelerates adoption for new users

---

## Phase 5: Mobile & Enhanced UX (Weeks 17-24)

**Goal**: Improve accessibility and user experience

### Features
- **Mobile-Responsive Design**
  - Optimize Streamlit UI for mobile browsers
  - Or build dedicated mobile interface

- **Notifications & Reminders**
  - Optional reminders for scheduled procedures
  - Email or push notifications when procedures are due

- **Enhanced Analytics**
  - Performance trends over time (week/month/year)
  - Comparison across procedures
  - Identify bottleneck steps within procedures
  - Suggestions for optimization

- **UI Polish**
  - Improved visual design
  - Dark mode option
  - Keyboard shortcuts for power users

### Success Criteria
- Mobile users can execute procedures effectively
- Notifications increase procedure completion rates
- Analytics provide actionable insights for optimization

---

## Future Considerations (Post-MVP)

### Database Migration
- Move from CSV to PostgreSQL or SQLite for better performance
- Enable concurrent access for multi-user scenarios
- Improve query performance for large datasets

### Advanced Features
- **AI-Powered Insights**: Suggest procedure optimizations based on run data
- **Integrations**: Connect with calendar apps, task managers, or business tools
- **Custom Fields**: Allow users to define custom metadata per procedure
- **Photo/Video Steps**: Embed visual aids within procedure steps
- **Voice-Guided Execution**: Hands-free mode for executing procedures

### Platform Expansion
- Native mobile apps (iOS/Android)
- Desktop applications (Electron)
- Web-based multi-tenant SaaS offering
- API for third-party integrations

---

## Release Strategy

### Alpha (Phase 1)
- Internal testing with founder/close users
- Focus on core functionality stability
- CSV data format validation

### Beta (Phases 2-3)
- Limited external users (10-20 early adopters)
- Gather feedback on analytics and version control
- Iterate on UX based on real usage patterns

### v1.0 (Phase 4)
- Public release with export/import capabilities
- Marketing to target audiences (productivity enthusiasts, small business owners)
- Documentation and onboarding materials

### v2.0+ (Phase 5 and beyond)
- Enhanced features based on user feedback
- Platform expansion as demand grows
- Potential monetization (freemium model, business tier)

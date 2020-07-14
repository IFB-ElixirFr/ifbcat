# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
- **/admin** endpoint (Djano Admin is configured and tested)
- **/login** endpoint: user login (Token authentication)
- ALL model endpoints
  - authentication: only users can create/update new database objects.
  - all fields are documented (with 'help_text')
- **/api/userprofile** endpoint: user profiles (UserProfile model)
  - custom user model (uses email for authentication rather than username).
  - fields: firstname, lastname, email, orcidid, homepage
  - email validation: uniqueness
  - orcidid validation: syntax, uniqueness
  - supports creation of normal and super-users.
  - supports search/filtering (by firstname, lastname, email, orcidid)
- **/news** endpoint: user news items (NewsItem model)
  - fields: user profile (id), news_text, created_on
  - authentication: users can only update/delete their own news items.
  - a user's news items are deleted if their profile is deleted.
- **/event** endpoint: events (Event model)
  - fields: user profile (id), ...
  - a user's events are preserved if their profile is deleted.

### Added
### Changed
### Removed
### Fixed

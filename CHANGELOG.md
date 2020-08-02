## Unreleased
- [ ] General: Break dependence with Invidious API - [Reason](https://github.com/iv-org/invidious/issues/1320)
- [ ] General: Import data from JSON file.
- [ ] Database: Improve following logic.
- [ ] Configuration page: Disable retweets.
- [ ] Configuration page: Disable loading media content.
- [ ] Configuration page: Dark mode.
- [ ] Configuration page: Change Invidious / Nitter instance.
- [ ] Youtube: Follow management page.

##### Long term
- See cited posts (if any).
- Share a tweet.
- Play media from Parasitter.
- Create following lists.

## [0.2.1] - 2020-07-31
### Added
- [x] Youtube: New video page - Watch videos without exiting Parasitter.
- [x] Youtube: Improved search - You can now search for channels and videos.

### Changed
- [x] General: Improved code structure.
- [x] Efficiency: Minor improvements

## [0.2.0] - 2020-07-29
### Added
- [x] Export your followed accounts (Youtube and Twitter) to a JSON file
- [x] Youtube: follow Youtube accounts.
- [x] Youtube: Manage suscriptions
- [x] Youtube: Show video time duration

### Changed
- [x] Efficiency: improvements. ~1s reduction on fetching time.
- [x] General: Minor UI changes.

### Fixed
- [x] Twitter: Saving posts didn't work on 2020.07.24 update.

## [0.1.0] - 2020-07-19
### Added
- [x] Twitter: Ability to save posts.
- [x] Twitter: Ability to remove a saved post.
- [x] Twitter: Open the original post on Nitter.
- [x] General: Error pages: Error 500, Error 405

### Changed
- [x] Efficiency: Significant improvement on fetching feed efficiency - Parallelism applied.
- [x] General: Changelogs now using [Keep a changelog](https://keepachangelog.com/en/1.0.0/) style.

### Fixed
- [x] Twitter: "Saved" menu element logged out instead of showing saved posts.

## [0.0.2] - 2020-07-14
### Added
- [x] Twitter: First implementation of saved posts - Not working yet.
- [x] Twitter: Empty feed now shows a notice.
- [x] Twitter: Pinned posts are now marked as it.
- [x] General: Error 404 page.
- [x] General: Requirements.txt file for a better installation and update experience.

### Changed
- [x] Twitter: More flexible user search. Search by username and show a list of possible results.
- [x] General: Minor UI fixes.
- [x] Efficiency: Fetching of accounts in a slightly more efficient way.



## [0.0.1] - 2020-07-13
### Added
- [x] Ability to follow accounts.
- [x] Ability to unfollow accounts.
- [x] Ability to register users.
- [x] Ability to visit a user profile.
- [x] Search a user by its exact username.

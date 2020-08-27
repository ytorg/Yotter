## Unreleased
- [ ] Configuration page: Disable retweets.
- [ ] Configuration page: Disable loading media content.
- [ ] Configuration page: Dark mode

##### Long term
- See cited posts (if any).
- Share a tweet.
- Play media from Parasitter.
- Create following lists.

## [0.2.1] - 2020-08-25
### Changed
- [x] Twitter: Improve general UI and efficiency
- [x] Twitter & Youtube: Posts older than 15 days are not shown anymore
- [x] Youtube: All channel links now link within Parasitter
- [x] Twitter: Improve database logic
- [x] Twitter: Remove Following tab and move it to 'following number'
- [x] General: Ability to import accounts from exported JSON file

### Added
- [x] General: Welcome page
- [x] Youtube: Ability to view a channel page: /channel/<id>
- [x] Youtube: Ability to search with full text: Channels and videos.
- [x] Youtube: Ability to Follow and Unfollow a user from the channel profile.
- [x] Youtube: Manage followed accounts clicking on 'following number'
  
### Fixed
- [x] Youtube: Channel link on channel videos not working.
- [x] General: Most usernames were already taken.

## [0.2.1a] - 2020-08-16
#### Breaking dependence with Invidious.
### Changed
- [x] Get video info through `youtube-dl`
- [x] Stream video to client through local proxy.
- [x] List videos without Invidious RSS feed.
- [x] Use Video.js player.
- [x] Search no longer depends on Invidious / APIs

## [0.2.0] - 2020-07-29
### Added
- [x] Export your followed accounts (Youtube and Twitter) to a JSON file
- [x] Youtube: follow Youtube accounts.
- [x] Youtube: Manage suscriptions
- [x] Youtube: Show video time duration

### Changed
- [x] Efficiency improvements. ~1s reduction on fetching time.
- [x] Minor UI changes.

### Fixed
- [x] Saving posts didn't work on 2020.07.24 update.

## [0.1.0] - 2020-07-19
### Added
- [x] Ability to save posts.
- [x] Ability to remove a saved post.
- [x] Error pages: Error 500, Error 405
- [x] Open the original post on Nitter.

### Changed
- [x] Significant improvement on fetching feed efficiency - Parallelism applied.
- [x] Changelogs now using [Keep a changelog](https://keepachangelog.com/en/1.0.0/) style.

### Fixed
- [x] "Saved" menu element logged out instead of showing saved posts.

## [0.0.2] - 2020-07-14
### Added
- [x] First implementation of saved posts - Not working yet.
- [x] Error 404 page.
- [x] Empty feed now shows a notice.
- [x] Requirements.txt file for a better installation and update experience.
- [x] Pinned posts are now marked as it.

### Changed
- [x] More flexible user search. Search by username and show a list of possible results.
- [x] Minor UI fixes.
- [x] Fetching of accounts in a slightly more efficient way.



## [0.0.1] - 2020-07-13
### Added
- [x] Ability to follow accounts.
- [x] Ability to unfollow accounts.
- [x] Ability to register users.
- [x] Ability to visit a user profile.
- [x] Search a user by its exact username.

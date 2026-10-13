# Releases and updates

This repository uses GitHub Actions to test and publish releases. A push to main runs the tests and Windows PowerShell syntax checks, then publishes the version declared in version.json if it does not already exist. Existing releases are left unchanged. Increase version.json before publishing a new version. Matching version tags and manual workflow dispatch are also supported.

Release packages automatically include the repository address in update-channel.json. Once installed, START_WINDOWS.bat checks for newer stable GitHub releases before starting the factory. It verifies the downloaded ZIP against GitHub's SHA-256 digest, validates the version and repository, and backs up replaced app files. Settings, installed dependencies, models, media and logs are preserved. Network failures leave the current app available. Updates apply at startup, never during active production.

No model files or generated media are stored in this repository. To disable online update checks, set enabled to false in update-channel.json. The public repository can be read by anyone; a random name does not make it private.

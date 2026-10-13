# Local media workbench

A local Windows production tool. See the setup and operating instructions below. Download the release ZIP rather than the GitHub source archive for an installation or update.

The release updater checks GitHub on startup after the configured package is installed once. Existing settings, models and generated media stay on the computer.

# True Science Stories — local factory v0.1

A working starter application for Windows, with no paid APIs or hosting. Python's standard library serves the interface on 127.0.0.1. Your RTX 3060 12 GB can run local image models; speed has not been benchmarked on your hardware.

## One-command Windows setup (v0.3)

Extract the ZIP fully into a writable folder on a drive with at least 40 GB free space. Double-click **SETUP_AND_START.bat**. Alternatively, open PowerShell in that folder and run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\SETUP.ps1
```

The execution-policy option applies only to this process; it does not change your permanent Windows policy. The script installs missing Python 3.11, FFmpeg, Ollama and 7-Zip through Windows winget, creates a private Python environment for Piper, downloads the LJSpeech high voice and Stable Diffusion 1.5 checkpoint, downloads official ComfyUI NVIDIA portable, sets configuration paths, pulls qwen2.5:7b, starts local services and opens the interface. Downloads can be many GB. Windows may request installation permissions. Windows 10/11 x64 with working winget/App Installer and an up-to-date NVIDIA driver is required.

Next time, double-click **START_WINDOWS.bat**; model downloads are not repeated. Setup can be re-run after a failure. Completed downloads are reused; unfinished downloads restart. Setup logs are in logs/bootstrap.log. Services remain running after the app closes; rebooting stops services started by this launcher, while Ollama may run as its installed desktop app. Nothing is configured to auto-publish or run the factory at Windows startup.

Setup checks the voice with an actual synthesis and checks FFmpeg, the installed script model, ComfyUI CUDA and the image checkpoint. It does not run a complete AI documentary as an installation test. If setup stops, its final message identifies the failing stage. It does not silently ignore errors. Some pre-existing installations or enterprise policies may need manual intervention.

The Windows setup has been reviewed but has not been executed in the Linux build environment. Python compilation and three NC unit tests pass; the previous FFmpeg demo render passed. This is an automated setup candidate, not a verified Windows installer.

After the interface opens, enter a topic. Leave the notes box blank for automatic Wikipedia research, or add your own notes to bypass retrieval. Use the demo checkbox for a short placeholder-image/test-tone assembly test; uncheck it for real AI generation. Videos and NC reports are in outputs/. All outputs still require review.

## Model and software references

- Ollama: https://ollama.com ; Qwen2.5 model: https://ollama.com/library/qwen2.5
- ComfyUI: https://github.com/Comfy-Org/ComfyUI — official portable NVIDIA release. CUDA compatibility depends on your driver.
- Image checkpoint: https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5 — CreativeML OpenRAIL-M license and model use restrictions apply. Setup validates its SHA-256 against Hugging Face repository metadata.
- Piper: https://github.com/OHF-Voice/piper1-gpl — GPL-3.0; voice: https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/ljspeech/high . Model-specific terms apply. The earlier Lessac voice recommendation is replaced by LJSpeech in automated setup.
- FFmpeg: https://www.gyan.dev/ffmpeg/builds/ ; 7-Zip: https://www.7-zip.org/ ; Python: https://www.python.org/

No models or third-party installers are bundled in this ZIP. They are fetched by your PC from official repositories/distributors. Their license terms apply independently. No paid cloud API is configured.

## Implemented
- Serial production queue and progress logs; requests and results saved per job.
- Ollama structured scripts with up to two schema repair retries and model unloading after generation.
- ComfyUI image generation with bounded polling and saved images.
- Piper narration, FFmpeg 720p documentary, 720x1280 Shorts with padded images and normalized audio.
- Chronological, sentence-aligned Short narration synthesized separately. These are not exact audio cuts of the documentary. Total Short count depends on scene lengths and filtering.
- NC heuristics: duplicates within a job, incomplete sentences, context-dependent opening, limited substance, duration; rejected Shorts remain in review.json and are not rendered.
- Repair: sentence grouping merges small scene tails; malformed script JSON retries; scene render retries once. Technical output duration checked.
- Review report, script and intermediate assets; queued jobs survive as records. Interrupted jobs are marked interrupted on restart; automatic queue replay is not implemented.

## Current limits
This remains a starter build, not an unattended publishing system. It retrieves Wikipedia source articles but does not independently validate scientific facts, inspect image anatomy, check cross-job originality, or decide YouTube policy eligibility. The policy/rights/disclosure review is manual. It does not upload videos. It does not yet add motion, captions, music, sophisticated transitions, batch topic generation, a settings editor or a resume button. Existing assets are reusable through Factory.produce on the same job folder; the UI starts new jobs.

Duration is a prompt target, not a guarantee. The report flags substantial misses. Scripts may be too short, scene-tail merging may make a Short longer than the configured maximum, and NC clips are omitted rather than repeatedly rewritten. All results have REVIEW_REQUIRED status. Automatic repair does not mean automatic policy clearance.

Automatically retrieved Wikipedia extracts, or your supplied notes, are the source material. Illustrations should be reviewed and identified appropriately rather than treated as real wildlife footage. YouTube's rules on repetitive/mass-produced content apply at channel level and cannot be solved by a per-clip filter: https://support.google.com/youtube/answer/1311392

## Test
`python -m unittest discover -s tests -v`

Six unit tests exercise duplicates, NC reasons, sentence grouping, research attribution/caching, empty results and disambiguation filtering. A real FFmpeg demo render was also tested in the build environment. Ollama, ComfyUI and Piper integration code requires validation with your installed models on Windows; those engines and their model files are not bundled.

## Output
outputs/JOB_ID/documentary.mp4, short-*.mp4 (accepted technical candidates only), script.json and review.json. Nothing is published automatically. Generated media and model files are stored on your computer. Use Ctrl+C to stop the app.

## Launcher closes immediately

The revised launchers always pause, including on successful exit, so early errors remain visible. Extract the entire ZIP before launching; a launcher run directly inside the ZIP does not have access to its companion files. BOOTSTRAP.ps1 captures early setup errors in logs/bootstrap.log. If your system blocks the batch launcher itself, open Command Prompt in the extracted project folder and run `SETUP_AND_START.bat`. The terminal will preserve any error.

## Update an existing installation — automatic research

Close the factory command window first. Extract the new ZIP into a separate folder, then copy these four files into the existing installed true-science-factory folder, choosing Replace when asked:
- app.py
- factory.py
- research.py (new file)
- index.html

Keep the installed config.json, workflow.json, runtime/, models/ and outputs/ in place. No reinstall or new model download is needed. Launch your existing START_WINDOWS.bat and refresh the browser with Ctrl+F5.

Enter a topic, leave research notes blank, uncheck Test pipeline and queue production. Research progress appears in the job log. The local script model first proposes concise searches; the app retrieves up to four Wikipedia articles and saves research.json, research-notes.txt and sources.txt in the job folder. Script scene source IDs are checked against the retrieved IDs; this is not claim verification. The model is instructed to paraphrase and use relevant sources. Search matches can still be irrelevant or incomplete. Internet is required for automatic retrieval; offline users can supply their own notes.

This research implementation currently uses Wikipedia, not a broad multi-site academic search. Wikipedia text attribution and CC BY-SA considerations are recorded with sources; review reuse terms and scientific claims before publication. Neither source retrieval nor NC filtering guarantees accuracy. Retrieved text is treated as untrusted evidence in the script prompt.

Live Wikipedia retrieval could not be validated in the restricted build environment; research tests use realistic mocked API responses. Live local model production still needs Windows testing.

## Easy updates (v0.4)

Future updates: download a newer True-Science-Stories-Factory ZIP into your usual Downloads folder. Close the factory's command window and run START_WINDOWS.bat. The launcher applies the newer downloaded version automatically, then launches the app. No extraction or reinstall. For Downloads in another location, drag the ZIP onto UPDATE_FACTORY.bat.

The updater applies an allowlist of application files only. config.json, workflow.json, runtime dependencies, models and outputs are preserved. Existing app files are backed up under runtime/update-backups; file replacement errors roll back changed files. An active factory prevents updating. New Python files are checked for syntax errors before replacement. Unsafe paths and unexpected archive layouts are rejected. Same or older versions are skipped.

This is a downloaded-package updater, not a remote update service. It cannot discover a release until you download its ZIP. Use factory ZIPs provided in this conversation; a checksum records the applied download but does not authenticate its publisher. No Windows policy or scheduled task is added.

## v0.4.1 — script generation repair

Script generation now uses Ollama JSON-schema structured output instead of a single JSON-only request for an entire documentary. It produces a short outline, then validates each narration section separately. Research context is bounded per source to reduce context overflow. Source IDs use an explicit allowed list. Failed sections log the exact validation reason and save raw responses under the job's script-diagnostics/. Completed sections are recorded in script-progress.json for inspection; automatic resume from this file is not yet implemented. The script model stays loaded while drafting and unloads before image production. Duration remains approximate. Twelve automated tests pass, including schema usage, source-ID repair and saved diagnostics. Local Ollama/Windows production has not been reproduced in the build environment.

Download this updated ZIP, close the running factory command window and launch your installed START_WINDOWS.bat to apply it through the v0.4 updater. Queue a fresh production job afterward. If the updater is not installed yet, use the one-time upgrade command previously supplied. No new model install is required.

## v0.5.0 — GitHub release updates

See GITHUB_SETUP.md for the prepared publishing workflow. The update channel is configured for this repository. Once the real repository is published, its release workflow builds a package with a configured update channel. Installing that release once enables automatic online update checks at factory startup, with downloaded-ZIP updates still available. Fifteen local tests pass; GitHub CI and a live release update remain unverified until publication. The new tests cover valid remote updates, checksum rejection and operation without a configured repository.

## v0.6.0 — smoother narration and automatic captions

New jobs use Kokoro ONNX instead of Piper. Michael (American male) is the default; Heart (American female) and George (British male) are available in the interface. The pace control ranges from 0.85 to 1.20. These are local Kokoro voices, not ElevenLabs voices or clones. The first real production installs kokoro-onnx, soundfile and faster-whisper from PyPI, downloads the Kokoro model and voice bank from the official kokoro-onnx release, and downloads Whisper small.en on first caption use. This can take several minutes. Later use is local with no voice credits or paid API. CPU inference leaves VRAM available for images. Piper assets are preserved.

Shorts automatically get bold uppercase captions, black outlines and yellow active-word highlighting in short phrases near the lower-middle safe area. Documentary scenes use normal sentence-case phrase captions. Caption word times come from local Whisper transcription, not uniform timing guesses. Captions display the original script wording; a few unmatched words may receive interpolated timings marked estimated in the saved word JSON. Large transcript mismatches are NC and stop the affected render instead of inventing timing. Check scientific spellings and timing before publishing. ASS styled captions and SRT text sidecars are saved beside videos. Each scene's captioned video is concatenated into the documentary.

Drafting instructions favor conversational wording, natural contractions, varied sentence length, direct explanations and factual hooks while preserving source requirements. This does not guarantee factual accuracy, a human-sounding performance on every term, or any view count. The change applies to newly queued jobs; existing exported videos are not rewritten.

## v0.6.1 — development preview and update visibility

The interface now reports the running server version and explicitly shows documentary and Shorts captions ON. Every new job logs its narrator and caption mode. The Test new voice + documentary captions button creates a short landscape documentary preview with real Kokoro narration and burned-in captions, plus a vertical highlighted-caption preview, without research or script generation. The finished documentary preview can be played directly in the job card.

HTML and API responses disable browser caching. The updater now identifies an already-running factory rather than describing the blocked update as a network failure. Closing a browser tab does not stop its Python server: close the factory command window before restarting the launcher. A launch check also refuses to silently reopen an old server when newer application files are installed. Previously exported videos are never rewritten by an update.

To verify the change, restart the installed launcher, refresh the page and confirm the running-version banner is v0.6.1 or later. Choose a voice and use the development preview before producing a full documentary. The legacy Test pipeline checkbox uses a test tone and placeholder image and does not test the new narrator; use the dedicated development preview button instead.

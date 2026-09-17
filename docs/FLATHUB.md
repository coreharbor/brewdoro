# Flathub preparation

Brewdoro has not been published to Flathub by these changes.

## Manifests

- `flatpak/io.github.coreharbor.Brewdoro.yml` builds the working tree for development.
- `flathub/io.github.coreharbor.Brewdoro.yml` builds the published `v0.5.0` tag,
  pinned to commit `12ed866b1fcd2fe8679b3418ae954bfafd6ca348`.

The release manifest does **not** include uncommitted changes or future fixes.
After publishing a new stable release, update both `tag` and `commit`, then
rebuild the release manifest. Do not move an existing release tag.
The external data checker is configured to track stable `vMAJOR.MINOR.PATCH` tags.

GNOME 51 supplies the runtime and SDK. Confirm it is still the latest stable
GNOME runtime before submission. Both x86_64 and aarch64 are intended targets;
the CI workflow builds both manifests on both architectures.

## Local validation

Install Flatpak using your distribution's package manager. On Ubuntu:

```bash
sudo apt install flatpak flatpak-builder
flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user flathub org.flatpak.Builder org.gnome.Platform//51 org.gnome.Sdk//51
```

Run these commands from the project root:

```bash
flatpak run --command=flatpak-builder-lint org.flatpak.Builder manifest flathub/io.github.coreharbor.Brewdoro.yml
flatpak run --command=flatpak-builder-lint org.flatpak.Builder appstream data/io.github.coreharbor.Brewdoro.metainfo.xml
flatpak run --command=flathub-build org.flatpak.Builder --install flathub/io.github.coreharbor.Brewdoro.yml
ostree commit --repo=repo --canonical-permissions --branch=screenshots/x86_64 builddir/files/share/app-info/media
flatpak run --command=flatpak-builder-lint org.flatpak.Builder repo repo
flatpak run io.github.coreharbor.Brewdoro
```

The builder installs the release, runs its unit tests and exports the package.
The `ostree` command exports the mirrored screenshots; use `screenshots/aarch64`
when building on ARM64. Install the `ostree` package if the command is unavailable.
Build outputs are not submission files. The GitHub Actions build is an additional
check; it does not replace testing desktop behavior inside the sandbox.

## Desktop checks before submission

Record results for the actual release package, on Wayland and X11 where available:

- Launch from the application menu; verify the icon and all three languages.
- Set a one-minute focus session; start, pause, resume and reset it.
- Complete at least two stages; verify sound plays each time and notifications
  arrive through the desktop portal without direct notification bus access.
- Check short and long breaks, the fourth focus session and auto-start.
- Close and reopen while running and while paused; check saved progress.
- Suspend and resume; verify completion and that no duplicate stage is counted.
- Check keyboard shortcuts, large text, and readable settings on a small display.

Current release limitations identified during source review:

- Closing the window ends the process; completion is reported on the next launch.
  Keep the window open or minimized to receive an on-time notification.
- Changing the system clock affects the running timer.
- A settings file with invalid UTF-8 is not recovered gracefully.

These limitations have not been fixed by the packaging changes. Assess them
before declaring the release ready; fixes require a new upstream release and
an updated release manifest.

## Maintainer submission

Read the current official [requirements](https://docs.flathub.org/docs/for-app-authors/requirements)
and [submission procedure](https://docs.flathub.org/docs/for-app-authors/submission).
After successful builds and desktop testing, the maintainer submits only the
release manifest at the root of a branch based on `flathub/flathub:new-pr`.
Application source, screenshots, CI files and this document stay upstream.
Do not submit the development manifest with its local directory source.

Flathub's current generative AI policy requires disclosure of known AI-generated
code, documentation, packaging and other included material, identifying the
affected parts and approximate extent.

The policy prohibits AI agents from opening or automating submission PRs and
from generating their commit messages, descriptions, review comments or replies.
The maintainer must personally perform those steps and must not request an
AI-agent review. No submission text is provided here.

After acceptance, enable GitHub 2FA, accept the app repository invitation,
and follow the [verification guide](https://docs.flathub.org/docs/for-app-authors/verification)
to verify ownership of the GitHub-based application ID.

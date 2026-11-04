# Android package

This is the existing `christmas-sneak-peek` kiosk, packaged for a phone or Chromecast with Google TV. It serves the same HTML, CSS, films and artwork already on this branch. It does not replace the Python kiosk on the Pi or desktop.

From this folder, with the Android SDK installed:

```sh
gradle assembleDebug
```

The installable package is `app/build/outputs/apk/debug/app-debug.apk`. Version `1.1.0-sneak.1`.

Weather lookup, music import, the hidden camera and GitHub release downloads stay on the Python server. The dashboard, arrival film, dog and Grinch visits, countdown, gifts and the December 9 party card run from the bundled pages.

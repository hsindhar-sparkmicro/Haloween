package com.sparkmicro.halloweenhub;

import android.content.res.AssetManager;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Serves the christmas-sneak-peek static hub and the JSON the existing page already expects. */
public class HubServer {
    static final int PORT = 8765;
    private final AssetManager assets;
    private final ExecutorService pool = Executors.newCachedThreadPool();
    private ServerSocket socket;

    HubServer(AssetManager assets) {
        this.assets = assets;
    }

    void start() {
        try {
            socket = new ServerSocket(PORT, 32, InetAddress.getByName("127.0.0.1"));
        } catch (IOException error) {
            return;
        }
        pool.execute(() -> {
            while (socket != null && !socket.isClosed()) {
                try {
                    Socket client = socket.accept();
                    pool.execute(() -> handle(client));
                } catch (IOException ignored) {
                    break;
                }
            }
        });
    }

    void close() {
        try {
            if (socket != null) socket.close();
        } catch (IOException ignored) {
        }
        pool.shutdownNow();
    }

    private void handle(Socket client) {
        try (Socket ignored = client) {
            InputStream in = client.getInputStream();
            ByteArrayOutputStream head = new ByteArrayOutputStream();
            int seen = 0;
            while (seen < 4) {
                int b = in.read();
                if (b < 0) return;
                head.write(b);
                byte[] buf = head.toByteArray();
                int n = buf.length;
                if (n >= 4 && buf[n - 4] == '\r' && buf[n - 3] == '\n' && buf[n - 2] == '\r' && buf[n - 1] == '\n') break;
                if (n > 65536) return;
            }
            String header = head.toString(StandardCharsets.ISO_8859_1);
            String[] lines = header.split("\r\n");
            if (lines.length == 0) return;
            String[] request = lines[0].split(" ");
            if (request.length < 2) return;
            String method = request[0];
            String target = request[1];
            int q = target.indexOf('?');
            String path = q >= 0 ? target.substring(0, q) : target;
            long rangeStart = 0;
            Long rangeEnd = null;
            int contentLength = 0;
            for (String line : lines) {
                String lower = line.toLowerCase(Locale.US);
                if (lower.startsWith("range: bytes=")) {
                    String spec = line.substring(line.indexOf('=') + 1).trim();
                    int dash = spec.indexOf('-');
                    if (dash > 0) {
                        rangeStart = Long.parseLong(spec.substring(0, dash));
                        if (dash + 1 < spec.length()) rangeEnd = Long.parseLong(spec.substring(dash + 1));
                    }
                } else if (lower.startsWith("content-length:")) {
                    contentLength = Integer.parseInt(line.substring(15).trim());
                }
            }
            while (contentLength > 0) {
                long skipped = in.skip(contentLength);
                if (skipped <= 0) break;
                contentLength -= (int) skipped;
            }
            OutputStream out = new BufferedOutputStream(client.getOutputStream());
            if ("/api/state".equals(path) || "/api/health".equals(path) || "/api/window".equals(path)
                    || "/api/logs".equals(path) || path.startsWith("/api/")) {
                byte[] body = api(method, path);
                write(out, 200, "application/json; charset=utf-8", body, 0, body.length, false);
                return;
            }
            String asset = assetPath(path);
            if (asset == null) {
                write(out, 404, "text/plain", "Not found".getBytes(StandardCharsets.UTF_8), 0, 9, false);
                return;
            }
            byte[] file;
            try (InputStream data = assets.open(asset)) {
                file = data.readAllBytes();
            } catch (IOException missing) {
                write(out, 404, "text/plain", "Not found".getBytes(StandardCharsets.UTF_8), 0, 9, false);
                return;
            }
            int status = 200;
            int start = 0;
            int end = file.length - 1;
            boolean partial = false;
            if (rangeStart > 0 || rangeEnd != null) {
                start = (int) Math.min(rangeStart, file.length);
                end = rangeEnd == null ? file.length - 1 : (int) Math.min(rangeEnd, file.length - 1);
                status = 206;
                partial = true;
            }
            int length = Math.max(0, end - start + 1);
            String mime = mime(asset);
            String extra = partial
                    ? "Content-Range: bytes " + start + "-" + end + "/" + file.length + "\r\nAccept-Ranges: bytes\r\n"
                    : "Accept-Ranges: bytes\r\n";
            String response = "HTTP/1.1 " + status + (status == 206 ? " Partial Content" : " OK") + "\r\n"
                    + "Content-Type: " + mime + "\r\n"
                    + "Content-Length: " + length + "\r\n"
                    + extra
                    + "Connection: close\r\n\r\n";
            out.write(response.getBytes(StandardCharsets.US_ASCII));
            out.write(file, start, length);
            out.flush();
        } catch (Exception ignored) {
        }
    }

    private static void write(OutputStream out, int status, String mime, byte[] body, int offset, int length, boolean unused) throws IOException {
        String text = "HTTP/1.1 " + status + (status == 200 ? " OK" : " Not Found") + "\r\n"
                + "Content-Type: " + mime + "\r\n"
                + "Content-Length: " + length + "\r\n"
                + "Connection: close\r\n\r\n";
        out.write(text.getBytes(StandardCharsets.US_ASCII));
        out.write(body, offset, length);
        out.flush();
    }

    private static String assetPath(String path) {
        if (path.contains("..")) return null;
        if ("/".equals(path)) return "index.html";
        if (path.startsWith("/static/")) return path.substring("/static/".length());
        return null;
    }

    private static String mime(String path) {
        if (path.endsWith(".html")) return "text/html; charset=utf-8";
        if (path.endsWith(".css")) return "text/css; charset=utf-8";
        if (path.endsWith(".js")) return "text/javascript; charset=utf-8";
        if (path.endsWith(".json")) return "application/json";
        if (path.endsWith(".png")) return "image/png";
        if (path.endsWith(".jpg") || path.endsWith(".jpeg")) return "image/jpeg";
        if (path.endsWith(".svg")) return "image/svg+xml";
        if (path.endsWith(".mp4")) return "video/mp4";
        if (path.endsWith(".webm")) return "video/webm";
        if (path.endsWith(".wav")) return "audio/wav";
        if (path.endsWith(".ttf")) return "font/ttf";
        return "application/octet-stream";
    }

    private byte[] api(String method, String path) throws Exception {
        if ("/api/health".equals(path)) {
            return new JSONObject().put("status", "ok").put("version", "1.1.0-sneak.1").put("hardware", "simulated").toString().getBytes(StandardCharsets.UTF_8);
        }
        if ("/api/window".equals(path)) {
            return new JSONObject().put("available", false).put("reason", "Use the Android system controls on this device.").toString().getBytes(StandardCharsets.UTF_8);
        }
        if ("/api/logs".equals(path)) {
            return new JSONObject().put("detections", new JSONArray()).toString().getBytes(StandardCharsets.UTF_8);
        }
        if ("/api/state".equals(path) || "GET".equals(method)) {
            return state().toString().getBytes(StandardCharsets.UTF_8);
        }
        if ("/api/haunt".equals(path)) return haunt().toString().getBytes(StandardCharsets.UTF_8);
        if ("/api/scan".equals(path)) return scan().toString().getBytes(StandardCharsets.UTF_8);
        if (path.startsWith("/api/encounter")) return new JSONObject().put("active", false).put("id", 0).toString().getBytes(StandardCharsets.UTF_8);
        return new JSONObject().put("ok", true).toString().getBytes(StandardCharsets.UTF_8);
    }

    private JSONObject state() throws Exception {
        ZoneId zone = ZoneId.of("America/Toronto");
        ZonedDateTime now = ZonedDateTime.now(zone);
        JSONObject settings = new JSONObject();
        settings.put("timezone", "America/Toronto");
        settings.put("units", "C");
        settings.put("location", JSONObject.NULL);
        settings.put("volume", 40);
        settings.put("rotation", false);
        settings.put("music_shuffle", true);
        settings.put("reduced_motion", false);
        settings.put("jumpscares", false);
        settings.put("flicker", false);
        settings.put("auto_download_updates", false);
        settings.put("quality", "auto");
        settings.put("party_date", "");
        settings.put("sensitivity", "medium");
        settings.put("camera_area", "center");
        settings.put("camera_threshold", 4);
        settings.put("camera_cooldown", 45);
        settings.put("camera_scan_seconds", 180);
        settings.put("visitor_mode", "choose");

        JSONObject body = new JSONObject();
        body.put("settings", settings);
        body.put("updates", updates());
        body.put("candy", 0);
        body.put("countdown", countdown(now.withMonth(10).withDayOfMonth(31).withHour(0).withMinute(0).withSecond(0).withNano(0), now));
        body.put("party_countdown", countdown(now.withMonth(10).withDayOfMonth(31).withHour(0).withMinute(0).withSecond(0).withNano(0), now));
        body.put("sneak_peek", sneak(now));
        body.put("records", new JSONArray());
        body.put("tracks", new JSONArray());
        body.put("effects", new JSONArray());
        body.put("detections", new JSONArray());
        body.put("weather", new JSONObject().put("status", "unset"));
        body.put("camera", new JSONObject()
                .put("available", false).put("enabled", false).put("armed", false).put("capture_active", false)
                .put("status", "Off").put("error", JSONObject.NULL).put("motion_percent", 0).put("cooldown", 0)
                .put("triggers", 0).put("scans", 0).put("scan_remaining", 0).put("temperature", JSONObject.NULL)
                .put("temperature_source", JSONObject.NULL)
                .put("mode", "Hidden local motion detection; no images or video exported"));
        body.put("cutscene", new JSONObject().put("available", false).put("url", "/api/cutscene").put("webm_url", JSONObject.NULL).put("items", new JSONArray()));
        body.put("backgrounds", new JSONArray());
        JSONArray scenes = new JSONArray();
        for (String name : new String[]{"Quiet shadows", "Purple mist", "Pumpkin parade", "Transylvania vampire", "Ghostbuster encounter", "Witch’s swamp", "Graveyard awakening", "Phantom train"}) {
            scenes.put(name);
        }
        body.put("scenes", scenes);
        body.put("haunt", haunt());
        body.put("scan", scan());
        body.put("welcome", new JSONObject().put("active", false).put("id", 0));
        return body;
    }

    private JSONObject countdown(ZonedDateTime target, ZonedDateTime now) throws Exception {
        if (now.toLocalDate().isAfter(target.toLocalDate())) target = target.plusYears(1);
        long seconds = Math.max(0, ChronoUnit.SECONDS.between(now, target));
        return new JSONObject().put("seconds", seconds).put("target", target.toOffsetDateTime().toString()).put("now", now.toOffsetDateTime().toString());
    }

    private JSONObject sneak(ZonedDateTime now) throws Exception {
        ZoneId zone = now.getZone();
        ZonedDateTime november = now.withMonth(11).withDayOfMonth(1).truncatedTo(ChronoUnit.DAYS);
        ZonedDateTime christmas = now.withMonth(12).withDayOfMonth(25).truncatedTo(ChronoUnit.DAYS);
        int span = (int) ChronoUnit.DAYS.between(november.toLocalDate(), now.toLocalDate());
        int defrost = Math.max(0, Math.min(100, (int) (span / 30.0 * 100)));
        ZonedDateTime party = ZonedDateTime.of(2026, 12, 9, 17, 0, 0, 0, ZoneId.of("America/Toronto"));
        JSONObject peek = new JSONObject();
        peek.put("christmas", phase(christmas, now));
        peek.put("defrost_percent", defrost);
        peek.put("timezone", zone.getId());
        JSONObject spark = phase(party, now.withZoneSameInstant(party.getZone()));
        spark.put("timezone", "America/Toronto");
        peek.put("spark_party", spark);
        return peek;
    }

    private JSONObject phase(ZonedDateTime target, ZonedDateTime now) throws Exception {
        String phase = now.toLocalDate().isEqual(target.toLocalDate()) ? "today" : now.toLocalDate().isAfter(target.toLocalDate()) ? "past" : "upcoming";
        long seconds = Math.max(0, ChronoUnit.SECONDS.between(now, target));
        long days = Math.max(0, ChronoUnit.DAYS.between(now.toLocalDate(), target.toLocalDate()));
        return new JSONObject().put("target", target.toOffsetDateTime().toString()).put("seconds", seconds).put("days", days).put("phase", phase);
    }

    private JSONObject haunt() throws Exception {
        return new JSONObject()
                .put("active", false).put("stage", "Quiet shadows").put("room", 60).put("porch", 80).put("fog", 0)
                .put("sound", 40).put("motion", false).put("scene", "Quiet shadows").put("audio", "quiet-scene.wav")
                .put("progress", 0).put("run_id", 0).put("seed", 0).put("source", "manual");
    }

    private JSONObject scan() throws Exception {
        return new JSONObject()
                .put("active", false).put("emf", 0).put("temperature", 18.6)
                .put("rooms", new JSONArray().put(0).put(0).put(0).put(0)).put("peak", 0);
    }

    private JSONObject updates() throws Exception {
        return new JSONObject()
                .put("status", "idle")
                .put("message", "This Android build is the christmas-sneak-peek kiosk.")
                .put("current_version", "1.1.0-sneak.1")
                .put("repository", "hsindhar-sparkmicro/Haloween")
                .put("latest_version", JSONObject.NULL)
                .put("progress", 0)
                .put("checked_at", JSONObject.NULL)
                .put("busy", false)
                .put("download_url", JSONObject.NULL)
                .put("filename", JSONObject.NULL)
                .put("local_controls", false);
    }
}

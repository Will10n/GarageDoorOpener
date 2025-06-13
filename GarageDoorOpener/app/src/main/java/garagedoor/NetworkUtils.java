package garagedoor;

import android.util.Log;

import androidx.annotation.NonNull;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class NetworkUtils {

    private static final ExecutorService executor = Executors.newSingleThreadExecutor();

    public static void sendSignal(double latitude, double longitude, TransitionState state) {
        executor.execute(() -> {
            HttpURLConnection conn = null;
            try {
                conn = getHttpURLConnection(); // start a connection
                // Set timeouts
                conn.setConnectTimeout(10000); // 10 seconds
                conn.setReadTimeout(10000); // 10 seconds

                // create new json object to populate data with
                JSONObject jsonmsg = new JSONObject();
                jsonmsg.put("latitude", latitude);
                jsonmsg.put("longitude", longitude);
                jsonmsg.put("transition type", state.getValue());

                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = jsonmsg.toString().getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                    os.flush();
                    Log.d("Message to Lambda", "Message sent successfully");
                }

                // get response code from other side
                int responseCode = conn.getResponseCode();
                if (responseCode == HttpURLConnection.HTTP_OK) { // connection is fine
                    try (BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream(), StandardCharsets.UTF_8))) {
                        StringBuilder response = new StringBuilder();
                        String line;
                        while ((line = reader.readLine()) != null) {
                            response.append(line);
                        }
                        Log.d("Lambda Response", "Response: " + response.toString());
                    }
                } else {
                    Log.e("Lambda Response", "Connection failed with response code: " + responseCode);
                }
            } catch (IOException e) {
                Log.e("Lambda Error", "IOException sending message: " + e.getMessage(), e);
            } catch (JSONException e) {
                Log.e("Lambda Error", "JSONException creating message: " + e.getMessage(), e);
            } catch (Exception e) {
                Log.e("Lambda Error", "Unexpected error: " + e.getMessage(), e);
            } finally {
                if (conn != null) {
                    conn.disconnect(); // Explicitly close the connection
                    Log.d("NetworkUtils", "Connection closed");
                }
            }
        });
    }

    private static @NonNull HttpURLConnection getHttpURLConnection() throws IOException {
        URL url = new URL(MainActivity.httpURL);

        // start the connection
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; utf-8");
        conn.setRequestProperty("Accept", "application/json");
        conn.setDoOutput(true);
        return conn;
    }

}

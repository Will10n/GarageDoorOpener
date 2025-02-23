package com.example.locationtrack;

import android.util.Log;


import androidx.annotation.NonNull;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class NetworkUtils {
    public static <string> void sendSignal(double latitude, double longitude, string state) {
        new Thread(() -> {
            try{
                HttpURLConnection conn = getHttpURLConnection();

                JSONObject jsonmsg = new JSONObject();
                jsonmsg.put("latitude", latitude);
                jsonmsg.put("longitude", longitude);
                jsonmsg.put("transition type", state);

                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = jsonmsg.toString().getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                    Log.d("Message to Lambda", "Message to Lambda successful");
                }
                int responseCode = conn.getResponseCode();
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    try (InputStream is = conn.getInputStream()) {
                        BufferedReader reader = new BufferedReader(new InputStreamReader(is, StandardCharsets.UTF_8));
                        StringBuilder response = new StringBuilder();
                        String line;
                        while ((line = reader.readLine()) != null) {
                            response.append(line);
                        }
                        Log.d("Lambda Response", "Response: " + response.toString());
                    }
                } else {
                    Log.d("Lambda Response", "Connection Failed " + responseCode);
                }
            }
            catch (Exception e){
                Log.e("Lambda Error", "Error sending message: " + e.getMessage());
            }
        }).start();
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




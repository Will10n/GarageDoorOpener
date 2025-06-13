package garagedoor;

import android.annotation.SuppressLint;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.widget.Toast;

import com.google.android.gms.location.Geofence;
import com.google.android.gms.location.GeofencingClient;
import com.google.android.gms.location.GeofencingRequest;
import com.google.android.gms.location.LocationServices;

public class GeoFence {


    private final Context context;
    private final PendingIntent geofencePendingIntent;
    private final GeofencingClient geofencingClient;
    private Geofence geofence;

    public GeoFence(Context context) {
        this.context = context;
        this.geofencingClient = LocationServices.getGeofencingClient(context);
        geofencePendingIntent = this.getGeofencePendingIntent();
    }

    @SuppressLint("MissingPermission")
    public void setupGeofence(double latitude, double longitude, float radius) {
        try {

            geofence = new Geofence.Builder()
                    .setRequestId("hme")
                    .setCircularRegion(latitude, longitude, radius)
                    .setTransitionTypes(Geofence.GEOFENCE_TRANSITION_ENTER | Geofence.GEOFENCE_TRANSITION_EXIT | Geofence.GEOFENCE_TRANSITION_DWELL)
                    .setLoiteringDelay(60000) // dwell after a minute will close door
                    .setExpirationDuration(Geofence.NEVER_EXPIRE)
                    .build();

            // Add geofence
            geofencingClient.addGeofences(geofencingRequest(), geofencePendingIntent)
                    .addOnSuccessListener(unused -> Toast.makeText(context, "Geofence added successfully", Toast.LENGTH_SHORT).show())
                    .addOnFailureListener(e -> {
                        Toast.makeText(context, "Failed to add geofence: " + e.getMessage(), Toast.LENGTH_LONG).show();
                    });
        } catch (Exception e) {
            Toast.makeText(context, "Error setting up geofence: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private GeofencingRequest geofencingRequest() {
        // create a request
        GeofencingRequest.Builder builder = new GeofencingRequest.Builder();
        builder.setInitialTrigger(GeofencingRequest.INITIAL_TRIGGER_ENTER | GeofencingRequest.INITIAL_TRIGGER_DWELL);
        builder.addGeofence(geofence);
        return builder.build();
    }

    private PendingIntent getGeofencePendingIntent() {
        Intent intent = new Intent(context, GeofenceBroadcastReceiver.class);
        return PendingIntent.getBroadcast(
                context,
                0,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_MUTABLE
        );
    }
}
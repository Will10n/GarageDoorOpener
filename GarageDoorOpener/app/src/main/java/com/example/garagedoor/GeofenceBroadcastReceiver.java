package com.example.garagedoor;

import android.app.NotificationChannel;
import androidx.core.app.NotificationCompat;
import android.app.NotificationManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.net.Network;
import android.util.Log;

import com.example.garagedoor.NetworkUtils;
import com.example.garagedoor.TransitionState;
import com.google.android.gms.location.Geofence;
import com.google.android.gms.location.GeofenceStatusCodes;
import com.google.android.gms.location.GeofencingEvent;

import org.json.JSONException;

import java.io.IOException;
import java.util.Objects;

public class GeofenceBroadcastReceiver extends BroadcastReceiver {

    private static final String TAG = "GeofenceBroadcastReceiver";

    @Override
    public void onReceive(Context context, Intent intent){
        GeofencingEvent event = GeofencingEvent.fromIntent(intent);

        if (event == null) { // checking for null
            Log.e(TAG, "GeofencingEvent is null");
            return;
        }

        if (event.hasError()){ // in case of error
            String errorMsg = GeofenceStatusCodes.getStatusCodeString(event.getErrorCode());
            Log.e(TAG, errorMsg);
        }

        int geofenceTransition = event.getGeofenceTransition(); // get transition
        double latitude = Objects.requireNonNull(event.getTriggeringLocation()).getLatitude();
        double longitude = event.getTriggeringLocation().getLongitude();


        if (geofenceTransition == Geofence.GEOFENCE_TRANSITION_ENTER){
            NetworkUtils.sendSignal(latitude, longitude, TransitionState.ENTER);
            sendNotification(context, "Entered");
        }
        else if (geofenceTransition == Geofence.GEOFENCE_TRANSITION_EXIT){
            NetworkUtils.sendSignal(latitude, longitude, TransitionState.EXIT);
            sendNotification(context, "Exited");
        }
        else if (geofenceTransition == Geofence.GEOFENCE_TRANSITION_DWELL){
            NetworkUtils.sendSignal(latitude, longitude, TransitionState.DWELL);
            sendNotification(context, "Dwell");
        }
    }

    private void sendNotification(Context context, String message){
        String channelId = "geofenceChannel";
        String channelName = "Geofence Notification";

        NotificationManager notificationManager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);

        // Create the NotificationChannel
        NotificationChannel channel = new NotificationChannel(channelId, channelName, NotificationManager.IMPORTANCE_LOW);
        channel.setDescription("Notifications for geofence transitions");
        notificationManager.createNotificationChannel(channel);

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
                .setSmallIcon(android.R.drawable.ic_notification_overlay)
                .setContentTitle("Geofence Transition")
                .setContentText(message)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setAutoCancel(true);

        notificationManager.notify(0, builder.build());
    }

}

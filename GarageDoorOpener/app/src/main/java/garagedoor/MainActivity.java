package garagedoor;

import android.Manifest;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.example.garagedoor.BuildConfig;
import com.example.garagedoor.R;


public class MainActivity extends AppCompatActivity {

    public static String httpURL = BuildConfig.httpURL;
    private GeoFence geoFence;

    private final static double LATITUDE = BuildConfig.GEOFENCE_LATITUDE;
    private final static double LONGITUDE = BuildConfig.GEOFENCE_LONGITUDE;
    private final static float RADIUS = BuildConfig.GEOFENCE_RADIUS;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);

        geoFence = new GeoFence(this);

        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        Button activateButton = findViewById(R.id.Activate); // get the button
        activateButton.setOnClickListener(v -> {
            Log.d("BUTTONS", "User pressed activate");
            Toast.makeText(MainActivity.this, "button pressed", Toast.LENGTH_SHORT).show();
            NetworkUtils.sendSignal(LATITUDE, LONGITUDE, TransitionState.BUTTON);
        });

        // Request permissions to set up geofence
        requestPermission();
    }

    private void requestPermission() {
        // Create instance to request permissions
        ActivityResultLauncher<String[]> locationPermissionRequest = registerForActivityResult(
                new ActivityResultContracts.RequestMultiplePermissions(),
                result -> {
                    // Get the permission results
                    Boolean fineLocation = result.getOrDefault(Manifest.permission.ACCESS_FINE_LOCATION, false);
                    Boolean coarseLocation = result.getOrDefault(Manifest.permission.ACCESS_COARSE_LOCATION, false);
                    Boolean backgroundLocation = result.getOrDefault(Manifest.permission.ACCESS_BACKGROUND_LOCATION, false);

                    if (Boolean.TRUE.equals(fineLocation) && Boolean.TRUE.equals(coarseLocation) && Boolean.TRUE.equals(backgroundLocation)) {
                        geoFence.setupGeofence(LATITUDE, LONGITUDE, RADIUS); // Setup geofence
                        Toast.makeText(this, "Permissions granted, geofence setup initiated", Toast.LENGTH_SHORT).show();
                    } else {
                        Toast.makeText(this, "Permissions denied, geofence not set up", Toast.LENGTH_SHORT).show();
                    }
                });

        // Launch permission request
        locationPermissionRequest.launch(new String[] {
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION,
                Manifest.permission.ACCESS_BACKGROUND_LOCATION
        });
    }
}
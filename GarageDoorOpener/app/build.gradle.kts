plugins {
    alias(libs.plugins.android.application)
}

android {

    buildFeatures{
        buildConfig = true
    }

    namespace = "com.example.garagedoor"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.garagedoor"
        minSdk = 34
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {

        debug{
            buildConfigField("double", "GEOFENCE_LATITUDE", "-37.87696")
            buildConfigField("double", "GEOFENCE_LONGITUDE", "145.26397")
            buildConfigField("float", "GEOFENCE_RADIUS", "80")
            buildConfigField("String", "httpURL", "\"https://bwwqsfjkfe.execute-api.us-east-1.amazonaws.com/postTransition\"")
        }

        release {
            buildConfigField("double", "GEOFENCE_LATITUDE", "-37.87696")
            buildConfigField("double", "GEOFENCE_LONGITUDE", "145.26397")
            buildConfigField("float", "GEOFENCE_RADIUS", "80")
            buildConfigField("String", "httpURL", "\"https://bwwqsfjkfe.execute-api.us-east-1.amazonaws.com/postTransition\"")

            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }

    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
}

dependencies {

    implementation(libs.appcompat)
    implementation(libs.material)
    implementation(libs.activity)
    implementation(libs.constraintlayout)
    implementation(libs.play.services.location)
    testImplementation(libs.junit)
    androidTestImplementation(libs.ext.junit)
    androidTestImplementation(libs.espresso.core)
}
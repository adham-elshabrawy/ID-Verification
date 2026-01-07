package com.kiosk.settings

import android.content.Context
import android.content.SharedPreferences
import android.provider.Settings

object DeviceSettings {
    
    private const val PREFS_NAME = "kiosk_device_settings"
    private const val KEY_DEVICE_ID = "device_id"
    private const val KEY_LOCATION_NAME = "location_name"
    private const val KEY_IS_REGISTERED = "is_registered"
    private const val KEY_FACE_THRESHOLD = "face_threshold"
    
    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }
    
    fun getDeviceId(context: Context): String {
        val prefs = getPrefs(context)
        var deviceId = prefs.getString(KEY_DEVICE_ID, null)
        
        if (deviceId == null) {
            deviceId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
            prefs.edit().putString(KEY_DEVICE_ID, deviceId).apply()
        }
        
        return deviceId!!
    }
    
    fun setLocationName(context: Context, locationName: String) {
        getPrefs(context).edit()
            .putString(KEY_LOCATION_NAME, locationName)
            .apply()
    }
    
    fun getLocationName(context: Context): String? {
        return getPrefs(context).getString(KEY_LOCATION_NAME, null)
    }
    
    fun setIsRegistered(context: Context, isRegistered: Boolean) {
        getPrefs(context).edit()
            .putBoolean(KEY_IS_REGISTERED, isRegistered)
            .apply()
    }
    
    fun isRegistered(context: Context): Boolean {
        return getPrefs(context).getBoolean(KEY_IS_REGISTERED, false)
    }
    
    fun getFaceThreshold(context: Context): Float {
        return getPrefs(context).getFloat(KEY_FACE_THRESHOLD, 0.65f)
    }
    
    fun setFaceThreshold(context: Context, threshold: Float) {
        getPrefs(context).edit()
            .putFloat(KEY_FACE_THRESHOLD, threshold)
            .apply()
    }
}


package com.kiosk.settings

import android.content.Context
import android.util.Log
import com.kiosk.encryption.KeystoreHelper
import com.kiosk.network.ApiClient
import com.kiosk.network.model.DeviceRegisterRequest
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

object DeviceRegistration {
    
    private const val TAG = "DeviceRegistration"
    
    suspend fun registerDevice(
        context: Context,
        locationName: String,
        deviceName: String? = null
    ): Result<String> = withContext(Dispatchers.IO) {
        try {
            val deviceId = DeviceSettings.getDeviceId(context)
            val apiService = ApiClient.getApiService(context)
            
            val request = DeviceRegisterRequest(
                deviceId = deviceId,
                locationName = locationName,
                name = deviceName
            )
            
            val response = apiService.registerDevice(request)
            
            if (response.isSuccessful && response.body() != null) {
                val registerResponse = response.body()!!
                
                // Store API key securely
                val keystoreHelper = KeystoreHelper(context)
                keystoreHelper.saveApiKey(registerResponse.apiKey)
                
                // Update settings
                DeviceSettings.setLocationName(context, locationName)
                DeviceSettings.setIsRegistered(context, true)
                
                Log.d(TAG, "Device registered successfully")
                Result.success(registerResponse.apiKey)
            } else {
                val errorMsg = response.errorBody()?.string() ?: "Registration failed"
                Log.e(TAG, "Registration failed: $errorMsg")
                Result.failure(Exception(errorMsg))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Registration error", e)
            Result.failure(e)
        }
    }
    
    fun isDeviceRegistered(context: Context): Boolean {
        return DeviceSettings.isRegistered(context) && 
               KeystoreHelper(context).hasApiKey()
    }
}


package com.kiosk

import android.app.Activity
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.os.Build
import android.view.WindowManager

class KioskManager(private val activity: Activity) {
    
    private var isAdminMode = false
    
    fun enableKioskMode() {
        if (isAdminMode) {
            return
        }
        
        activity.window.addFlags(
            WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD or
            WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
            WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON or
            WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
        )
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            activity.window.attributes.layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
        }
        
        // Enable lock task mode if device admin is enabled
        try {
            val devicePolicyManager =
                activity.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
            val componentName = ComponentName(activity, KioskDeviceAdminReceiver::class.java)
            
            if (devicePolicyManager.isDeviceOwnerApp(activity.packageName)) {
                activity.setLockTaskMode(true)
            }
        } catch (e: Exception) {
            // Lock task mode requires device owner, ignore if not available
        }
    }
    
    fun disableKioskMode() {
        try {
            activity.setLockTaskMode(false)
        } catch (e: Exception) {
            // Ignore
        }
    }
    
    fun setAdminMode(enabled: Boolean) {
        isAdminMode = enabled
        if (!enabled) {
            enableKioskMode()
        } else {
            disableKioskMode()
        }
    }
    
    fun isAdminMode(): Boolean {
        return isAdminMode
    }
}


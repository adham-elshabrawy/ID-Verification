package com.kiosk

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    
    val kioskManager: KioskManager by lazy { KioskManager(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        kioskManager.enableKioskMode()
    }

    override fun onResume() {
        super.onResume()
        kioskManager.enableKioskMode()
    }

    override fun onBackPressed() {
        // Prevent back button in kiosk mode
        // Only allow if in admin mode
        if (!kioskManager.isAdminMode()) {
            return
        }
        super.onBackPressed()
    }
}

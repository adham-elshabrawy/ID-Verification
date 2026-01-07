package com.kiosk.database.entities

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "time_events")
data class TimeEventEntity(
    @PrimaryKey
    val id: String,
    val employeeId: String,
    val eventType: String, // "IN" or "OUT"
    val method: String, // "FACE" or "PIN"
    val eventTime: Date,
    val synced: Boolean = false,
    val createdAt: Date = Date()
)

